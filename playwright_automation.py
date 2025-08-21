import os
import time
import json
import threading
from typing import Dict, Optional, Tuple

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class PlaywrightEVAutomation:
    """Playwright 기반 EV 신청서 자동화 (학습 모드 + 재생 모드)

    - 학습 모드: 사용자가 클릭/입력한 폼 요소의 id/셀렉터를 기록하여 data/selectors_profile_*.jsonl 저장
    - 재생 모드: 기록된 셀렉터 맵과 기본 id 셀렉터를 사용해 자동 입력/검증/임시저장 처리
    """

    def __init__(self, profile_id: int = 1):
        self.profile_id = profile_id
        self.pw = None
        self.context = None
        self.page = None
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event: Optional[threading.Event] = None
        self.selector_map: Dict[str, Dict[str, str]] = {}

    # ---------- 브라우저 제어 ----------
    def launch(self) -> None:
        self.pw = sync_playwright().start()
        user_data_dir = f"D:/ChromeProfiles/PL_{self.profile_id}"
        os.makedirs(user_data_dir, exist_ok=True)

        # Persistent context로 세션 유지
        self.context = self.pw.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=[
                f"--window-position={self.profile_id * 950},0",
                "--window-size=950,900",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        self.page = self.context.new_page()

        # navigator.webdriver 은폐
        self.page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

    def close(self) -> None:
        try:
            if self.context:
                self.context.close()
        finally:
            if self.pw:
                self.pw.stop()

    # ---------- 기록(학습) ----------
    def inject_click_recorder(self) -> None:
        def save_event(ev: dict):
            try:
                os.makedirs('data', exist_ok=True)
                out_path = os.path.join('data', f'selectors_profile_{self.profile_id}.jsonl')
                with open(out_path, 'a', encoding='utf-8') as f:
                    json.dump(ev, f, ensure_ascii=False)
                    f.write('\n')
            except Exception:
                pass

        # Python 콜백 노출
        self.page.expose_function("__saveEvent", save_event)

        record_js = """
        (function(){
            try {
                if (window.__clickRecorderInstalled) return;
                window.__clickRecorderInstalled = true;

                function getUniqueSelector(el){
                    if (!el || !el.tagName) return '';
                    if (el.id) return '#' + el.id;
                    const parts=[]; let node=el;
                    while(node && node.nodeType===1 && parts.length<8){
                        let part=node.tagName.toLowerCase();
                        if(node.id){ part += '#' + node.id; parts.unshift(part); break; }
                        const cls=(node.className||'').toString().trim().split(/\s+/).slice(0,2).filter(Boolean).join('.');
                        if (cls) part += '.' + cls.replace(/\.+/g,'.');
                        let nth=1, sib=node; while(sib = sib.previousElementSibling){ if(sib.tagName===node.tagName) nth++; }
                        part += `:nth-of-type(${nth})`;
                        parts.unshift(part); node=node.parentElement;
                        if(node && node.tagName && node.tagName.toLowerCase()==='html') break;
                    }
                    return parts.join(' > ');
                }

                function getLabelText(el){
                    try{
                        if (!el) return '';
                        if (el.labels && el.labels.length) {
                            const t = Array.from(el.labels).map(l=>l.textContent.trim()).find(Boolean);
                            if (t) return t;
                        }
                        if (el.id){
                            const byFor = document.querySelector(`label[for="${el.id}"]`);
                            if (byFor && byFor.textContent.trim()) return byFor.textContent.trim();
                        }
                        const ph = el.getAttribute && (el.getAttribute('placeholder') || el.getAttribute('aria-label'));
                        if (ph) return ph.trim();
                        let p = el.parentElement;
                        for (let i=0;i<4 && p;i++){
                            const lbl=p.querySelector && p.querySelector('label');
                            if (lbl && lbl.textContent.trim()) return lbl.textContent.trim();
                            const legend=p.querySelector && p.querySelector('legend');
                            if (legend && legend.textContent.trim()) return legend.textContent.trim();
                            p = p.parentElement;
                        }
                    }catch(e){}
                    return '';
                }

                function pushEvent(target, type){
                    try{
                        if (!target || !target.tagName) return;
                        const tag = target.tagName.toLowerCase();
                        if (!['input','select','textarea','button'].includes(tag)) return;
                        const rec = {
                            ts: Date.now(),
                            event: type,
                            tag: tag,
                            id: target.id || '',
                            name: target.name || '',
                            typeAttr: target.type || '',
                            classes: (target.className || '').toString(),
                            selector: getUniqueSelector(target) || '',
                            labelText: getLabelText(target) || '',
                            value: (tag==='input' || tag==='textarea') ? (target.value||'') : '',
                            checked: (target.type==='checkbox' || target.type==='radio') ? !!target.checked : undefined
                        };
                        if (window.__saveEvent) window.__saveEvent(rec);
                    }catch(e){}
                }

                document.addEventListener('click',  e=>pushEvent(e.target,'click'),  true);
                document.addEventListener('change', e=>pushEvent(e.target,'change'), true);
                document.addEventListener('focusin',e=>pushEvent(e.target,'focus'),  true);
                console.log('📝 Playwright 기록기 설치 완료');
            } catch(err) {
                console.log('기록기 설치 오류:', err && err.message);
            }
        })();
        """
        self.page.add_init_script(record_js)
        # 이미 열린 페이지에도 주입
        try:
            self.page.evaluate(record_js)
        except Exception:
            pass

    def build_selector_map_from_logs(self) -> Dict[str, Dict[str, str]]:
        def infer_key(rec: dict) -> Optional[str]:
            text = (rec.get('labelText') or rec.get('id') or rec.get('name') or '').lower()
            idv = (rec.get('id') or '').strip()
            namev = (rec.get('name') or '').strip()
            known = {
                'req_nm': '성명', 'mobile': '휴대전화', 'birth1': '생년월일', 'birth': '생년월일',
                'contract_day': '계약일자', 'delivery_sch_day': '출고예정일자', 'email': '이메일',
                'phone': '전화', 'req_cnt': '신청대수', 'req_kind': '신청유형', 'model_cd': '신청차종',
                'addr': '주소'
            }
            if idv in known:
                return known[idv]
            if namev in known:
                return known[namev]
            t = text or (rec.get('selector') or '').lower()
            def has(*keys):
                return any(k in t for k in keys)
            if has('성명','이름','name') and not has('회사','법인'):
                return '성명'
            if has('휴대','연락처','핸드폰','mobile','phone') and not has('유선'):
                return '휴대전화'
            if has('생년월일','생일','birth'):
                return '생년월일'
            if has('주소','address'):
                return '주소'
            if has('계약'):
                return '계약일자'
            if has('출고','예정'):
                return '출고예정일자'
            if has('이메일','email'):
                return '이메일'
            if has('전화') and not has('휴대'):
                return '전화'
            if has('대수','신청대수','count','cnt'):
                return '신청대수'
            if has('성별','gender') or (rec.get('typeAttr') in ('radio','checkbox') and (rec.get('name')=='req_sex')):
                return '성별'
            if has('유형','신청유형','kind'):
                return '신청유형'
            if has('차종','모델','model'):
                return '신청차종'
            return None

        collected: Dict[str, Dict[str, str]] = {}
        data_dir = 'data'
        if not os.path.isdir(data_dir):
            self.selector_map = {}
            return {}
        for fname in os.listdir(data_dir):
            if not fname.startswith('selectors_profile_') or not fname.endswith('.jsonl'):
                continue
            fpath = os.path.join(data_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        key = infer_key(rec)
                        if not key:
                            continue
                        entry = collected.get(key, {})
                        if (rec.get('id') and not entry.get('id')):
                            entry['id'] = rec['id']
                        if (rec.get('selector') and not entry.get('selector')):
                            entry['selector'] = rec['selector']
                        collected[key] = entry
            except Exception:
                continue

        self.selector_map = collected
        return collected

    # ---------- 자동 입력 ----------
    def _fill_text(self, sel: str, value: str) -> None:
        try:
            self.page.fill(sel, value)
        except Exception:
            # readonly 등 우회
            self.page.evaluate(
                "(s,v)=>{const el=document.querySelector(s); if(!el) return; el.removeAttribute('readonly'); el.value=v; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); el.setAttribute('readonly','readonly');}",
                sel,
                value,
            )

    def auto_fill(self, user: Dict[str, str]) -> None:
        # id 우선 → selector 폴백
        def sel_for(key: str, default_id: Optional[str]) -> Optional[str]:
            entry = self.selector_map.get(key) or {}
            if default_id:
                return f"#{entry.get('id', default_id)}" if entry.get('id') or default_id else (entry.get('selector') or None)
            return entry.get('selector') or (f"#{entry.get('id')}" if entry.get('id') else None)

        # 기본 텍스트
        mapping = [
            (sel_for('성명', 'req_nm'), user.get('성명','')),
            (sel_for('휴대전화', 'mobile'), user.get('휴대전화','')),
            (sel_for('이메일', 'email'), user.get('이메일','.')),
            (sel_for('전화', 'phone'), user.get('전화','.')),
            (sel_for('주소', None) or 'input[name="addr"]', user.get('주소','')),
            (sel_for('신청대수', 'req_cnt'), user.get('신청대수','1')),
        ]
        for selector, value in mapping:
            if not selector:
                continue
            try:
                self.page.wait_for_selector(selector, timeout=3000)
                self._fill_text(selector, value)
            except PlaywrightTimeoutError:
                pass

        # 날짜 필드 처리 (readonly 우회)
        contract_val = user.get('계약일자', '2025-08-16')
        delivery_val = user.get('출고예정일자', '2025-08-29')
        birth_val = user.get('생년월일', '1990-01-01')
        self.page.evaluate(
            "(contract,birth,delivery)=>{\n"
            " const c=document.getElementById('contract_day'); if(c){c.removeAttribute('readonly'); c.value=contract; c.setAttribute('readonly','readonly'); c.dispatchEvent(new Event('change',{bubbles:true}));}\n"
            " const hb=document.getElementById('birth'); if(hb){hb.value=birth;}\n"
            " const b=document.getElementById('birth1'); if(b){b.removeAttribute('readonly'); b.value=birth; b.setAttribute('readonly','readonly'); b.dispatchEvent(new Event('input',{bubbles:true})); b.dispatchEvent(new Event('change',{bubbles:true}));}\n"
            " const d=document.getElementById('delivery_sch_day'); if(d){d.removeAttribute('readonly'); d.value=delivery; d.setAttribute('readonly','readonly'); d.dispatchEvent(new Event('change',{bubbles:true}));}\n"
            "}",
            contract_val,
            birth_val,
            delivery_val,
        )

        # 성별 라디오
        gender = user.get('성별', '남자')
        target_id = 'req_sex1' if gender == '남자' else 'req_sex2'
        try:
            self.page.check(f"#{target_id}")
        except Exception:
            self.page.evaluate(
                "(id)=>{const r=document.getElementById(id); if(!r) return; r.checked=true; r.click(); r.dispatchEvent(new Event('change',{bubbles:true}));}",
                target_id,
            )

        # 드롭다운 선택
        try:
            self.page.select_option('#req_kind', value='P')
        except Exception:
            pass

        # 차종 매핑
        model = user.get('신청차종','')
        model_val = ''
        if 'EV3' in model and '스탠다드' in model:
            model_val = 'EV3_2WD_S'
        elif '레이' in model:
            model_val = 'RAY_4_R'
        elif 'EV3' in model and '롱레인지' in model:
            model_val = 'EV3_2WD_L17'
        if model_val:
            try:
                self.page.select_option('#model_cd', value=model_val)
            except Exception:
                pass

    # ---------- 검증/임시저장 ----------
    def validate_required(self) -> bool:
        return bool(self.page.evaluate(
            "()=>{\n"
            " const required=[\n"
            "  {id:'req_nm',name:'성명'}, {id:'mobile',name:'휴대전화'}, {id:'birth1',name:'생년월일'},\n"
            "  {selector:'input[name=\\'req_sex\\']:checked',name:'성별'}, {id:'req_kind',name:'신청유형',isSelect:true}, {id:'model_cd',name:'신청차종',isSelect:true}\n"
            " ];\n"
            " let ok=true;\n"
            " for (const f of required){\n"
            "  let el=f.selector?document.querySelector(f.selector):document.getElementById(f.id);\n"
            "  if(!el){ ok=false; break; }\n"
            "  if(f.isSelect){ if(!el.value){ ok=false; break; } } else { if(!el.value){ ok=false; break; } }\n"
            " }\n"
            " return ok; }"
        ))

    def temp_save_flow(self) -> bool:
        # 버튼 클릭
        clicked = self.page.evaluate(
            "()=>{\n"
            " const cands=[...document.querySelectorAll('button'),...document.querySelectorAll('input[type=\\'button\\']')];\n"
            " const btn=cands.find(b=>{const t=(b.textContent||b.value||''); return t.includes('임시저장')||t.includes('저장');});\n"
            " if(btn){ btn.click(); return true; } return false; }"
        )
        if not clicked:
            return False

        # 확인 버튼 처리 (대기 후 클릭 시도)
        time.sleep(1.5)
        try:
            self.page.evaluate(
                "()=>{\n"
                " const btns=[...document.querySelectorAll('button, input[type=\\'button\\']')];\n"
                " const ok=btns.find(b=>{const t=(b.textContent||b.value||''); return t.includes('확인')||t.includes('OK')||t.includes('예');});\n"
                " if(ok) ok.click(); }"
            )
        except Exception:
            pass

        # 새 팝업 처리
        new_page = None
        try:
            new_page = self.context.wait_for_event('page', timeout=10000)
        except PlaywrightTimeoutError:
            pass
        if not new_page:
            return False

        time.sleep(1.5)
        extracted = new_page.evaluate(
            "()=>{\n"
            " const els=document.querySelectorAll('span,div,p,strong,td,label,h1,h2,h3');\n"
            " let code=null;\n"
            " for(const el of els){ const t=(el.textContent||'').trim(); if(/^[A-Za-z0-9]{6,15}$/.test(t) && !['submit','button','input','form'].includes(t)){ code=t; break; } }\n"
            " return code; }"
        )
        code = extracted or "945451216"
        reversed_code = code[::-1]

        ok = new_page.evaluate(
            "(val)=>{\n"
            " const inp=document.querySelector('input[type=text],input[type=password]'); if(!inp) return false;\n"
            " inp.value=val; inp.dispatchEvent(new Event('input',{bubbles:true})); inp.dispatchEvent(new Event('change',{bubbles:true}));\n"
            " setTimeout(()=>{ const btn=[...document.querySelectorAll('button,input[type=submit],input[type=button]')].find(b=>{const t=(b.textContent||b.value||''); return t.includes('확인')||t.includes('제출')||t.includes('OK');}); if(btn) btn.click(); }, 500);\n"
            " return true; }",
            reversed_code,
        )
        if ok:
            time.sleep(3)
        try:
            new_page.close()
        except Exception:
            pass
        return ok

    # ---------- 상위 플로우 ----------
    def run(self, user: Dict[str, str], record_mode: bool = False) -> bool:
        self.launch()
        try:
            print("[INFO] 브라우저가 열렸습니다. 로그인 후 신청서 페이지로 이동하세요: https://ev.or.kr/ev_ps/ps/seller/sellerApplyform")
            while True:
                current_url = self.page.url
                if 'sellerApplyform' in (current_url or ''):
                    print("[DETECT] 신청서 페이지 감지됨")
                    break
                input("신청서 페이지 도달 후 Enter: ")

            if record_mode:
                print("[LEARN] 학습 모드 시작: 자동화에 필요한 필드를 클릭/입력해 주세요. 종료는 Enter.")
                self.inject_click_recorder()
                input("[LEARN] 종료하려면 Enter...")
                self.build_selector_map_from_logs()

            # 자동 입력
            self.auto_fill(user)
            time.sleep(5)

            # 검증 + 임시저장 여부
            if not self.validate_required():
                print("[WARN] 필수 필드가 일부 미완료입니다. 수동 확인 후 Enter.")
                input("")

            choice = input("임시저장을 진행하시겠습니까? (y/N): ")
            if choice.lower() == 'y':
                ok = self.temp_save_flow()
                print("[TEMP_SAVE] 완료" if ok else "[TEMP_SAVE] 실패")
            return True
        finally:
            self.close()


if __name__ == "__main__":
    sample_user = {
        '성명': '장원', '계약일자': '2025-08-16', '신청유형': '개인',
        '생년월일': '1990-01-01', '성별': '여자', '신청차종': 'EV3 스탠다드',
        '신청대수': '1', '출고예정일자': '2025-08-29',
        '주소': '충청북도 제천시 의림지로 171', '휴대전화': '010-9199-6844',
        '이메일': '.', '전화': '.', '우선순위': '사회계층 Y. 다자녀가구. 2자녀 클릭'
    }
    app = PlaywrightEVAutomation(profile_id=1)
    app.run(sample_user, record_mode=False)


