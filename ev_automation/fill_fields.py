import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def debug_model_selection(driver, model: str) -> dict:
    """
    차종 선택 디버깅을 위한 헬퍼 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        model: 선택하려는 차종명
        
    Returns:
        디버깅 정보 딕셔너리
    """
    debug_info = {
        'model_to_select': model,
        'available_options': [],
        'element_found': False,
        'element_id': None,
        'element_name': None,
        'element_type': None,
        'current_value': None,
        'error': None
    }
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        
        # 드롭다운 요소 찾기
        try:
            model_select = driver.find_element(By.ID, 'model_cd')
            debug_info['element_found'] = True
            debug_info['element_id'] = model_select.get_attribute('id')
            debug_info['element_name'] = model_select.get_attribute('name')
            debug_info['element_type'] = model_select.get_attribute('type')
            debug_info['current_value'] = model_select.get_attribute('value')
            
            # 사용 가능한 옵션들 확인
            select_element = Select(model_select)
            for option in select_element.options:
                option_text = option.text.strip()
                option_value = option.get_attribute('value')
                option_selected = option.is_selected()
                debug_info['available_options'].append({
                    'text': option_text,
                    'value': option_value,
                    'selected': option_selected
                })
                
        except Exception as e:
            debug_info['error'] = f"드롭다운 요소 찾기 실패: {e}"
            
            # 대안: 다른 선택자로 찾기
            try:
                # name 속성으로 찾기
                model_select = driver.find_element(By.NAME, "model_cd")
                debug_info['element_found'] = True
                debug_info['element_name'] = model_select.get_attribute('name')
                debug_info['current_value'] = model_select.get_attribute('value')
            except:
                try:
                    # CSS 선택자로 찾기
                    model_select = driver.find_element(By.CSS_SELECTOR, "select[name*='model']")
                    debug_info['element_found'] = True
                    debug_info['element_name'] = model_select.get_attribute('name')
                    debug_info['current_value'] = model_select.get_attribute('value')
                except Exception as e2:
                    debug_info['error'] = f"모든 방법으로 찾기 실패: {e2}"
        
        # 페이지의 모든 select 요소 확인
        try:
            all_selects = driver.find_elements(By.TAG_NAME, "select")
            debug_info['all_selects'] = []
            for i, select in enumerate(all_selects):
                select_info = {
                    'index': i,
                    'id': select.get_attribute('id'),
                    'name': select.get_attribute('name'),
                    'class': select.get_attribute('class'),
                    'options_count': len(select.find_elements(By.TAG_NAME, "option"))
                }
                debug_info['all_selects'].append(select_info)
        except Exception as e:
            debug_info['error'] = f"전체 select 요소 확인 실패: {e}"
            
    except Exception as e:
        debug_info['error'] = f"디버깅 중 오류: {e}"
    
    return debug_info

def fill_readonly_field_selenium(driver, field_id: str, value: str) -> bool:
    """
    Selenium을 사용해서 readonly 필드에 값을 입력
    JavaScript에서 성공한 방식을 Python으로 구현
    
    Args:
        driver: Selenium WebDriver 인스턴스
        field_id: HTML 필드 ID
        value: 입력할 값
        
    Returns:
        성공 여부
    """
    try:
        # JavaScript 실행으로 readonly 필드 처리 + 필수 이벤트 디스패치 (arguments 사용)
        script = """
        const field = document.getElementById(arguments[0]);
        if (field) {
            field.removeAttribute('readonly');
            try {
                const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
                setter.call(field, arguments[1]);
            } catch(e) {
                field.value = arguments[1];
            }
            try { field.dispatchEvent(new Event('input', { bubbles: true })); } catch(e) {}
            try { field.dispatchEvent(new Event('change', { bubbles: true })); } catch(e) {}
            field.setAttribute('readonly', 'readonly');
            return true;
        }
        return false;
        """
        result = driver.execute_script(script, field_id, value)
        return bool(result)
    except Exception as e:
        print(f"❌ {field_id} 필드 입력 실패: {e}")
        return False

def human_like_typing(element, text, min_delay=0.03, max_delay=0.08):
    """
    사람처럼 자연스럽게 타이핑하는 함수
    각 문자마다 랜덤한 지연시간을 두어 자동화 감지를 우회
    
    Args:
        element: 입력할 요소
        text: 입력할 텍스트
        min_delay: 최소 지연시간 (초)
        max_delay: 최대 지연시간 (초)
    """
    try:
        # 기존 내용 삭제
        element.clear()
        time.sleep(random.uniform(0.05, 0.15))
        
        # 각 문자를 하나씩 입력
        for char in text:
            element.send_keys(char)
            # 랜덤한 지연시간
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            
            # 가끔 더 긴 지연시간 (사람이 생각하는 것처럼)
            if random.random() < 0.08:  # 8% 확률로 줄임
                time.sleep(random.uniform(0.1, 0.3))
        
        # 입력 완료 후 짧은 대기
        time.sleep(random.uniform(0.05, 0.1))
        
    except Exception as e:
        print(f"❌ 자연스러운 타이핑 실패: {e}")
        # 실패 시 일반적인 방법으로 재시도
        element.clear()
        element.send_keys(text)

def _dispatch_input_change_blur(driver, element):
    """해당 요소에 input/change/blur 이벤트를 순서대로 디스패치"""
    try:
        driver.execute_script(
            """
            const el = arguments[0];
            if (!el) return;
            try { el.dispatchEvent(new Event('input', {{ bubbles: true }})); } catch(e) {}
            try { el.dispatchEvent(new Event('change', {{ bubbles: true }})); } catch(e) {}
            try { el.blur && el.blur(); } catch(e) {}
            """,
            element,
        )
    except Exception:
        pass

def ensure_edit_mode(driver) -> None:
    """편집모드(수 정 버튼)로 전환. 이미 가능하면 무시"""
    wait = WebDriverWait(driver, 10)
    try:
        # 이미 입력 가능하면 스킵
        try:
            el = driver.find_element(By.ID, "req_nm")
            if el.is_enabled():
                return
        except Exception:
            pass

        # 수 정 버튼 클릭 시도 (사이트 셀렉터에 맞춰 범용 시도)
        candidates = [
            (By.CSS_SELECTOR, ".btn_step100[onclick*='changeMode']"),
            (By.CSS_SELECTOR, "button[onclick*='changeMode']"),
            (By.XPATH, "//button[contains(@onclick,'changeMode')]")
        ]
        clicked = False
        for by_, sel in candidates:
            try:
                btn = wait.until(EC.element_to_be_clickable((by_, sel)))
                btn.click()
                clicked = True
                break
            except Exception:
                continue

        if clicked:
            # 입력 가능 상태 대기
            wait.until(lambda d: d.find_element(By.ID, "req_nm").is_enabled())
    except Exception:
        # 편집모드 전환 실패는 치명적이지 않으니 무시
        pass

def cdp_click_element(driver, element) -> bool:
    """CDP를 사용해 요소의 중심 좌표에 실제 클릭 이벤트를 보냄"""
    try:
        # 요소 중앙 좌표 계산을 위해 스크롤
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        box = element.rect
        center_x = int(box.get('x', 0) + box.get('width', 0) / 2)
        center_y = int(box.get('y', 0) + box.get('height', 0) / 2)
        # 마우스 이동/다운/업 순서로 디스패치
        for typ in ("mouseMoved", "mousePressed", "mouseReleased"):
            params = {
                "type": typ,
                "x": center_x,
                "y": center_y,
                "button": "left",
                "clickCount": 1,
            }
            if typ == "mousePressed":
                params["buttons"] = 1
            driver.execute_cdp_cmd('Input.dispatchMouseEvent', params)
        return True
    except Exception:
        return False

def pick_date(driver, input_css: str, yyyy: int, mm: int, dd: int) -> bool:
    """달력 위젯 선택: 1) 공식 API → 4) DOM 클릭 → 3) CDP 좌표 클릭(백업) 순"""
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    date_str = f"{yyyy:04d}-{mm:02d}-{dd:02d}"
    # 1) jQuery UI / flatpickr 공식 API 시도
    try:
        api_result = driver.execute_script(
            """
            try {
                const sel = arguments[0];
                const dateStr = arguments[1];
                const el = document.querySelector(sel);
                if (!el) return false;
                // jQuery UI
                if (window.jQuery && typeof jQuery(el).datepicker === 'function') {
                    jQuery(el).datepicker('setDate', dateStr);
                    jQuery(el).trigger('change');
                    return true;
                }
                // flatpickr
                if (el._flatpickr && typeof el._flatpickr.setDate === 'function') {
                    el._flatpickr.setDate(dateStr, true);
                    return true;
                }
                return false;
            } catch(e) { return false; }
            """,
            input_css,
            date_str,
        )
        if api_result:
            return True
    except Exception:
        pass
    # 4) 위젯 DOM 실제 클릭
    try:
        inp = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, input_css)))
        actions.move_to_element(inp).pause(random.uniform(0.1, 0.2)).click().perform()
        # 달력 위젯 대기 (범용 셀렉터)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-datepicker, .datepicker")))
        day = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//table[contains(@class,'datepicker') or contains(@class,'ui-datepicker-calendar')]//a[normalize-space(text())='" + str(int(dd)) + "']",
        )))
        try:
            actions.move_to_element(day).pause(0.05).click().perform()
            return True
        except Exception:
            # 3) 실패 시 CDP 좌표 클릭 백업
            return cdp_click_element(driver, day)
    except Exception:
        return False

def format_phone_number(raw: str) -> str:
    """휴대폰/전화 마스크 적용: 010-1234-5678 형태로 보정"""
    if not raw:
        return raw
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("010"):
        return f"010-{digits[3:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return raw

def normalize_date_string(date_text: str) -> str | None:
    """여러 날짜 포맷을 YYYY-MM-DD로 정규화. 실패 시 None"""
    if not date_text:
        return None
    s = str(date_text).strip()
    
    # 0) Excel 날짜 숫자 처리 (예: 29269 → 1980-02-18)
    try:
        import datetime
        excel_date_num = float(s)
        if 1 <= excel_date_num <= 100000:  # Excel 날짜 범위
            # Excel의 기준일 (1900-01-01)부터 계산
            base_date = datetime.datetime(1900, 1, 1)
            target_date = base_date + datetime.timedelta(days=int(excel_date_num) - 2)  # Excel은 1900년을 윤년으로 계산
            return target_date.strftime("%Y-%m-%d")
    except (ValueError, OverflowError):
        pass
    
    # 3) 한국어 날짜 형식: "1980년 02월 18일", "1980년 2월 18일" 등
    korean_pattern = r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일"
    korean_match = re.search(korean_pattern, s)
    if korean_match:
        try:
            y, m, d = int(korean_match.group(1)), int(korean_match.group(2)), int(korean_match.group(3))
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            pass
    
    # 1) YYYY-MM-DD / YYYY.MM.DD / YYYY/MM/DD
    for sep in ("-", ".", "/"):
        parts = s.split(sep)
        if len(parts) == 3 and all(parts):
            try:
                y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                return f"{y:04d}-{m:02d}-{d:02d}"
            except Exception:
                pass
    # 2) 8자리 숫자 YYYYMMDD
    digits = re.sub(r"\D", "", s)
    if len(digits) == 8:
        try:
            y, m, d = int(digits[:4]), int(digits[4:6]), int(digits[6:])
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            return None
    return None

def human_like_select(driver, element_id, value, description=""):
    """
    사람처럼 자연스럽게 드롭다운을 선택하는 함수
    
    Args:
        driver: WebDriver 인스턴스
        element_id: 요소 ID
        value: 선택할 값
        description: 설명 (로그용)
    """
    try:
        # 요소 찾기
        element = driver.find_element(By.ID, element_id)
        
        # 클릭하기 전 짧은 대기
        time.sleep(random.uniform(0.2, 0.5))
        
        # 요소 클릭
        element.click()
        time.sleep(random.uniform(0.3, 0.7))
        
        # Select 객체 생성
        select = Select(element)
        
        # 현재 선택된 옵션 확인
        current_selection = select.first_selected_option.text if select.first_selected_option else ""
        
        # 값이 다르면 선택
        if current_selection != value:
            # 드롭다운이 열릴 때까지 대기
            time.sleep(random.uniform(0.2, 0.4))
            
            # 옵션 선택
            try:
                select.select_by_visible_text(value)
            except Exception:
                select.select_by_value(value)
            time.sleep(random.uniform(0.3, 0.6))
            
            # change 이벤트 강제 발화
            try:
                driver.execute_script("document.getElementById(arguments[0]).dispatchEvent(new Event('change', {bubbles:true}));", element_id)
            except Exception:
                pass
            
            print(f"✅ {description} 선택 완료: {value}")
            return True
        else:
            print(f"✅ {description} 이미 선택됨: {value}")
            return True
            
    except Exception as e:
        print(f"❌ {description} 선택 실패: {e}")
        return False

def human_like_fill_field(driver, field_id, value, description="", field_type="text"):
    """
    사람처럼 자연스럽게 필드를 채우는 함수
    
    Args:
        driver: WebDriver 인스턴스
        field_id: 필드 ID
        value: 입력할 값
        description: 설명 (로그용)
        field_type: 필드 타입 (text, select, readonly)
    """
    try:
        # 필드 입력 전 랜덤 대기
        time.sleep(random.uniform(0.5, 1.5))
        
        if field_type in ("text", "readonly"):
            css = f"#{field_id}"
            ok = set_input_value_strict(driver, css, value)
            if not ok:
                # 폴백: 직접 타이핑 시도
                element = driver.find_element(By.ID, field_id)
                element.click(); time.sleep(random.uniform(0.2, 0.4))
                human_like_typing(element, value)
                _dispatch_input_change_blur(driver, element)
                try:
                    element.send_keys(Keys.TAB)
                except Exception:
                    pass
            
            # 입력 검증
            element = driver.find_element(By.ID, field_id)
            actual_value = element.get_attribute('value')
            if actual_value == value or (field_id in ("mobile","phone") and actual_value.replace("-","") == value.replace("-","")):
                print(f"✅ {description} 입력 완료: {value}")
                return True
            else:
                print(f"⚠️ {description} 값 불일치: 입력={value}, 실제={actual_value}")
                return False
                
        elif field_type == "select":
            # 드롭다운 필드
            return human_like_select(driver, field_id, value, description)
            
    except Exception as e:
        print(f"❌ {description} 입력 실패: {e}")
        return False

def fill_fields_selenium_human_like(driver, user_data: dict, fast_mode: bool = True) -> bool:
    """
    사람처럼 자연스럽게 모든 필드에 데이터 입력
    자동화 감지를 우회하기 위해 랜덤한 지연시간과 타이핑 속도 적용
    
    Args:
        driver: Selenium WebDriver 인스턴스
        user_data: 입력할 사용자 데이터
        
    Returns:
        성공 여부
    """
    try:
        print("🚀 사람처럼 자연스럽게 필드 자동 입력 시작...")
        print(f"📊 입력할 데이터: {user_data}")
        
        def pause(min_s: float, max_s: float) -> None:
            if fast_mode:
                time.sleep(0.01)
            else:
                time.sleep(random.uniform(min_s, max_s))
        
        # 데이터 추출
        name = user_data.get('성명', '')
        phone = format_phone_number(user_data.get('휴대전화', ''))
        email = user_data.get('이메일', '')
        tel = format_phone_number(user_data.get('전화', ''))
        addr = user_data.get('주소', '')
        addr_detail = user_data.get('상세주소', '')
        contract = normalize_date_string(user_data.get('계약일자', '2025-01-15')) or '2025-01-15'
        birth = user_data.get('생년월일', '1990-01-01')
        delivery = normalize_date_string(user_data.get('출고예정일자', '2025-02-15')) or '2025-02-15'
        gender = user_data.get('성별', '남자')
        model = user_data.get('신청차종', '')
        count = user_data.get('신청대수', '1')
        
        # 입력 결과 추적
        input_results = {}
        
        # 시작 전 전체 대기 (사람이 페이지를 읽는 것처럼)
        print("⏳ 페이지 로딩 대기 중...")
        pause(1.0, 2.0)
        # 편집모드 전환 (noedit/disabled 해제)
        ensure_edit_mode(driver)
        
        # 0단계: 신청유형(개인) 먼저 선택
        try:
            print("\n📝 0단계: 신청유형(개인) 먼저 선택")
            success_kind_init = human_like_select(driver, 'req_kind', '개인', '신청유형')
            input_results['신청유형(초기)'] = success_kind_init
            pause(0.1, 0.2)
            
            # 신청유형 선택 완료 후 충분한 대기
            print("⏳ 신청유형 선택 완료 대기 중...")
            time.sleep(1.0)  # 충분한 대기 시간
            
        except Exception as e:
            print(f"❌ 신청유형 초기 선택 실패: {e}")
            input_results['신청유형(초기)'] = False

        # 0.1단계: 우선순위 매핑은 공동명의자 처리 후에 적용

        # 0.2단계: 공동명의자 처리 (개인 신청에서만) - 신청유형 선택 완료 후
        try:
            joint_cnt = None
            # 다양한 키 인식
            for k in ['공동명의자수', '공동명의자 수', '공동명의 수', '공동수', '공동명의인수']:
                if user_data.get(k) not in (None, ''):
                    try:
                        joint_cnt = int(str(user_data.get(k)).strip())
                        break
                    except Exception:
                        pass
            
            # 엑셀에 공동명의자 수가 없으면 처리하지 않음
            if joint_cnt is None or joint_cnt <= 0:
                print("📝 공동명의자 수가 없으므로 공동명의자 처리 건너뜀")
                # return 제거 - 나머지 필드 입력은 계속 진행
            else:
                desired_count = joint_cnt
         
                # 첫 번째 공동명의자 이름과 생년월일 데이터 준비
                nm_val = None
                br_val = None
                
                # 다양한 키로 이름 찾기
                nm_keys = ['공동1_성명', '공동명의자1_성명', '공동1 성명', '공동명의자 성명', '공동명의자성명', '공동 성명', '공동성명', '공동명의자 이름']
                for k in nm_keys:
                    if user_data.get(k):
                        nm_val = user_data.get(k)
                        break
                
                # 다양한 키로 생년월일 찾기
                br_keys = ['공동1_생년월일', '공동명의자1_생년월일', '공동1 생년월일', '공동명의자 생년월일', '공동명의자생년월일', '공동 생년월일', '공동생년월일']
                for k in br_keys:
                    if user_data.get(k):
                        br_val = normalize_date_string(user_data.get(k))
                        break
                
                # 정규화된 키로도 시도
                if not nm_val or not br_val:
                    try:
                        import re as _re
                        normalized = { _re.sub(r"\s+", "", k): k for k in user_data.keys() }
                        if not nm_val:
                            for alias in ['공동명의자성명','공동성명','공동명의자이름']:
                                if alias in normalized:
                                    v = user_data.get(normalized[alias])
                                    if v not in (None, ''):
                                        nm_val = v
                                        break
                        if not br_val:
                            for alias in ['공동명의자생년월일','공동생년월일']:
                                if alias in normalized:
                                    v = user_data.get(normalized[alias])
                                    if v not in (None, ''):
                                        br_val = normalize_date_string(v)
                                        break
                    except Exception:
                        pass
    
                print(f"🧩 공동명의자 처리 시작: 목표 {desired_count}명 (엑셀: {joint_cnt})")
                print(f"📝 이름: {nm_val}, 생년월일: {br_val}")
                
                # 디버깅: 사용 가능한 키들 출력
                print("🔍 사용 가능한 엑셀 키들:")
                for key, value in user_data.items():
                    if '공동' in key or 'joint' in key.lower():
                        print(f"  - {key}: {value}")
                
                # 디버깅: 생년월일 찾기 과정 상세 출력
                print("🔍 생년월일 찾기 과정:")
                for k in br_keys:
                    found_value = user_data.get(k)
                    print(f"  - {k}: {found_value}")
                    if found_value:
                        normalized = normalize_date_string(found_value)
                        print(f"    → 정규화: {normalized}")
                
                # execute_async_script로 타이밍 문제 해결
                js_async_joint = """
                const desired = arguments[0];
                const nm = arguments[1];
                const birth = arguments[2];
                const done = arguments[arguments.length - 1]; // async callback

                function setCountAndOpen(){
                  const cnt = document.querySelector('#jn_cnt');
                  if(!cnt){ 
                    console.log('❌ #jn_cnt not found');
                    return done('fail: #jn_cnt not found'); 
                  }
                  try{ cnt.removeAttribute('disabled'); cnt.removeAttribute('readonly'); }catch(e){}
                  cnt.value = String(desired);
                  try{ cnt.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                  try{ cnt.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                  console.log('✏️ 공동명의자 수=' + String(desired) + ' 입력');

                  const btn = document.querySelector('#t_jnInfo1 button.btn-black[type="button"], #t_jnInfo1 button[onclick*="createNewJointInfo"]');
                  if(btn) { 
                    try{ btn.click(); console.log('✅ 확인 버튼 클릭'); }catch(e){ console.log('❌ 확인 버튼 클릭 실패:', e); } 
                  }
                  try{ 
                    if(typeof window.createNewJointInfo==='function') {
                      window.createNewJointInfo(); 
                      console.log('✅ createNewJointInfo() 직접 호출'); 
                    }
                  }catch(e){}
                }

                function waitRows(n, cb){
                  const body = document.querySelector('#jnBody');
                  if (!body) {
                    console.log('❌ #jnBody not found');
                    return cb('fail: #jnBody not found');
                  }

                  const current = () => body.querySelectorAll('tr.c_jnInfo').length;
                  console.log('현재 행 수:', current(), '목표:', n);
                  
                  if (current() >= n) {
                    console.log('✅ 행 생성 완료');
                    return cb(null);
                  }

                  const obs = new MutationObserver(()=>{
                    const newCount = body.querySelectorAll('tr.c_jnInfo').length;
                    console.log('DOM 변경 감지, 현재 행 수:', newCount);
                    if (newCount >= n){ 
                      obs.disconnect(); 
                      console.log('✅ 목표 행 수 달성');
                      cb(null); 
                    }
                  });
                  obs.observe(body, {childList:true, subtree:true});
                  
                  setTimeout(()=>{ 
                    obs.disconnect(); 
                    const finalCount = body.querySelectorAll('tr.c_jnInfo').length;
                    console.log('타임아웃, 최종 행 수:', finalCount);
                    cb(finalCount>=n ? null : 'fail: timeout rows'); 
                  }, 4000);
                }

                function fillFirst(){
                  const row = document.querySelector('#jnBody tr.c_jnInfo');
                  if(!row) {
                    console.log('❌ 공동명의자 행을 찾지 못함');
                    return 'fail: no row';
                  }

                  const nameInput = row.querySelector('input[name="jn_name"]');
                  const birthInput = row.querySelector('input[name="jn_birth"]');
                  
                  console.log('🔍 찾은 입력 필드들:');
                  console.log('- nameInput:', nameInput);
                  console.log('- birthInput:', birthInput);

                  if (nameInput && nm){
                    try{ nameInput.removeAttribute('readonly'); }catch(e){}
                    nameInput.value = nm;
                    try{ nameInput.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                    try{ nameInput.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                    console.log('✏️ 성명=' + nm + ' 입력');
                  }
                  
                  if (birthInput && birth){
                    try{ birthInput.removeAttribute('readonly'); }catch(e){}
                    try{ birthInput.removeAttribute('disabled'); }catch(e){}
                    birthInput.value = birth;
                    try{ birthInput.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                    try{ birthInput.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                    console.log('✏️ 생년월일=' + birth + ' 입력');
                  } else {
                    // 생년월일 필드를 찾지 못한 경우 다른 선택자들 시도
                    console.log('⚠️ 기본 생년월일 필드를 찾지 못함, 다른 선택자 시도...');
                    const altBirthInputs = [
                      row.querySelector('input[name*="birth"]'),
                      row.querySelector('input[id*="birth"]'),
                      row.querySelector('input[name*="birthday"]'),
                      row.querySelector('input[id*="birthday"]'),
                      row.querySelector('input[type="date"]'),
                      row.querySelector('input[type="text"]')
                    ];
                    
                    for(let i = 0; i < altBirthInputs.length; i++) {
                      const altInput = altBirthInputs[i];
                      if(altInput && altInput !== nameInput) {
                        console.log('🔍 대체 생년월일 필드 발견:', altInput.name || altInput.id || altInput.type);
                        try{ altInput.removeAttribute('readonly'); }catch(e){}
                        try{ altInput.removeAttribute('disabled'); }catch(e){}
                        altInput.value = birth;
                        try{ altInput.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                        try{ altInput.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                        console.log('✏️ 생년월일(대체)=' + birth + ' 입력');
                        break;
                      }
                    }
                  }
                  
                  // 백업: 직접 input 선택자로도 시도
                  if(!birthInput || !birth) {
                    console.log('🔍 백업 생년월일 필드 탐색...');
                    const backupBirthInputs = [
                      document.querySelector('input[name="jn_birth"]'),
                      document.querySelector('input[name*="birth"]'),
                      document.querySelector('input[id*="birth"]'),
                      document.querySelector('input[name*="birthday"]'),
                      document.querySelector('input[id*="birthday"]')
                    ];
                    
                    for(let i = 0; i < backupBirthInputs.length; i++) {
                      const backupInput = backupBirthInputs[i];
                      if(backupInput && backupInput !== nameInput) {
                        console.log('🔍 백업 생년월일 필드 발견:', backupInput.name || backupInput.id);
                        try{ backupInput.removeAttribute('readonly'); }catch(e){}
                        try{ backupInput.removeAttribute('disabled'); }catch(e){}
                        backupInput.value = birth;
                        try{ backupInput.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                        try{ backupInput.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                        console.log('✏️ 생년월일(백업)=' + birth + ' 입력');
                        break;
                      }
                    }
                  }
                  
                  return 'ok';
                }

                try{
                  setCountAndOpen();
                  waitRows(Math.max(1, Number(desired)||1), (err)=>{
                    if (err) {
                      console.log('❌ 행 대기 실패:', err);
                      return done(err);
                    }
                    const res = fillFirst();
                    console.log('✅ 공동명의자 입력 완료:', res);
                    done(res);
                  });
                }catch(e){
                  console.log('❌ 전체 처리 실패:', e);
                  done('fail: ' + (e && e.message ? e.message : e));
                }
                """
                
                # 스크립트 타임아웃 설정 및 실행
                driver.set_script_timeout(15)  # 15초 타임아웃
                result = driver.execute_async_script(js_async_joint, desired_count, nm_val, br_val)
                print(f"🎯 공동명의자 처리 결과: {result}")
                
                if result and result.startswith('fail:'):
                    print(f"⚠️ 공동명의자 처리 실패: {result}")

        except Exception as e:
            print("⚠️ 공동명의자 처리 중 오류:", e)
        
        # 0.3단계: 우선순위 매핑 적용 (사회계층, 다자녀, 생애최초 등)
        try:
            priority_text = (user_data.get('우선순위') or '').strip()
            if priority_text:
                print("🛠️ 우선순위 매핑 적용 시도:", priority_text)
                has_social = ('사회계층' in priority_text and ('Y' in priority_text or '예' in priority_text))
                is_multi_child = ('다자녀' in priority_text)
                child_count = '2' if '2자녀' in priority_text else ('3' if '3자녀' in priority_text else ('4' if '4자녀' in priority_text or '4자녀 이상' in priority_text else ''))
                first_buy = ('생애최초' in priority_text)
                improve_fd = ('미세먼지' in priority_text) or ('노후경유' in priority_text) or ('택시' in priority_text)
                improve_detail1 = ('노후경유' in priority_text or '폐차' in priority_text)
                improve_detail2 = ('택시' in priority_text)
                exchange = ('폐차' in priority_text) or ('수출말소' in priority_text)

                # 사회계층 유형 코드 매핑
                social_kind = ''
                if '국가유공' in priority_text: social_kind = '1'
                elif '장애' in priority_text: social_kind = '2'
                elif '다자녀' in priority_text: social_kind = '3'
                elif '다문화' in priority_text: social_kind = '4'
                elif ('기초생활' in priority_text) or ('차상위' in priority_text): social_kind = '5'
                elif '소상공인' in priority_text: social_kind = '6'
                elif '기타' in priority_text: social_kind = '9'

                js = f"""
				(function(){{
				  const click = (id) => {{ const el = document.getElementById(id); if (!el) return false; try {{ el.click(); }} catch(e) {{ el.checked=true; }} try{{ el.dispatchEvent(new Event('change',{{bubbles:true}})); }}catch(e){{}} return true; }};
				  const selectVal = (id, v) => {{ const el = document.getElementById(id); if (!el) return false; try{{ el.disabled=false; }}catch(e){{}} el.value=v; try{{ el.dispatchEvent(new Event('change',{{bubbles:true}})); }}catch(e){{}} return true; }};
				  const show = (sel, flag) => {{ try{{ const el=document.querySelector(sel); if(el) el.style.display = flag? '' : 'none'; }}catch(e){{}} }};

				  // 사회계층
				  if ({str(has_social).lower()}) {{ click('social_yn1'); if ('{social_kind}') {{ selectVal('social_kind','{social_kind}'); }} if ('{child_count}') {{ selectVal('children_cnt','{child_count}'); }} }}

				  // 생애최초
				  if ({str(first_buy).lower()}) {{ click('first_buy_yn1'); }}

				  // 미세먼지 개선효과 관련
				  if ({str(improve_fd).lower()}) {{ click('improve_fd_yn1'); show('#div_improve_fd_yn', true); }}
				  if ({str(improve_detail1).lower()}) {{ const c=document.getElementById('improve_fd_detail1'); if(c) c.checked=true; }}
				  if ({str(improve_detail2).lower()}) {{ const c2=document.getElementById('improve_fd_detail2'); if(c2) c2.checked=true; }}

				  // 내연기관 폐차/수출말소 지원여부
				  if ({str(exchange).lower()}) {{ click('exchange_yn1'); }}

				  return true;
				}})();
				"""
                try:
                    driver.execute_script(js)
                    print("✅ 우선순위 매핑 적용 완료")
                except Exception as e:
                    print("⚠️ 우선순위 매핑 JS 실행 실패:", e)
            else:
                print("ℹ️ 우선순위 정보 없음 - 스킵")
        except Exception as e:
            print("⚠️ 우선순위 매핑 처리 중 오류:", e)

        # 1단계: 기본 정보 입력 (가장 중요한 필드들부터)
        print("\n📝 1단계: 기본 정보 입력")
        
        basic_fields = [
            ('req_nm', name, '성명'),
            ('mobile', phone, '휴대전화'),
            ('email', email, '이메일'),
            ('phone', tel, '전화'),
            ('req_cnt', count, '신청대수')
        ]
        
        for field_id, value, desc in basic_fields:
            if value:
                try:
                    success = human_like_fill_field(driver, field_id, value, desc, "text")
                    input_results[desc] = success
                    
                    # 필드 간 대기
                    pause(0.1, 0.3)
                except Exception as e:
                    print(f"❌ {desc} 입력 실패: {e}")
                    input_results[desc] = False
        
        # 중간 휴식 (사람이 정보를 확인하는 것처럼)
        print("⏳ 정보 확인 중...")
        pause(0.2, 0.4)
        
        # 2단계: 생년월일 입력
        if birth:
            print(f"\n📝 2단계: 생년월일 입력")
            try:
                # birth 필드 입력
                success1 = human_like_fill_field(driver, 'birth', birth, '생년월일(birth)', "text")
                pause(0.1, 0.2)
                
                # birth1 필드도 동일하게 입력
                success2 = human_like_fill_field(driver, 'birth1', birth, '생년월일(birth1)', "text")
                
                if success1 and success2:
                    print(f"✅ 생년월일 입력 완료: {birth}")
                    input_results['생년월일'] = True
                else:
                    print(f"⚠️ 생년월일 일부 입력 실패")
                    input_results['생년월일'] = False
                
            except Exception as e:
                print(f"❌ 생년월일 입력 실패: {e}")
                input_results['생년월일'] = False
        
        # 중간 휴식
        time.sleep(random.uniform(0.5, 1.0))
        
        # 3단계: 성별 선택
        if gender:
            print(f"\n📝 3단계: 성별 선택")
            try:
                gender_id = 'req_sex1' if gender == '남자' else 'req_sex2'
                element = driver.find_element(By.ID, gender_id)
                
                # 클릭 전 대기
                pause(0.1, 0.2)
                element.click()
                pause(0.05, 0.1)
                
                print(f"✅ 성별 선택 완료: {gender}")
                input_results['성별'] = True
                
            except Exception as e:
                print(f"❌ 성별 선택 실패: {e}")
                input_results['성별'] = False
        
        # 중간 휴식
        pause(0.1, 0.2)
        
        # 4단계: 신청유형 선택 (개인)
        print(f"\n📝 4단계: 신청유형 선택")
        try:
            success = human_like_select(driver, 'req_kind', '개인', '신청유형')
            input_results['신청유형'] = success
            
        except Exception as e:
            print(f"❌ 신청유형 선택 실패: {e}")
            input_results['신청유형'] = False
        
        # 중간 휴식
        pause(0.2, 0.4)
        
        # 5단계: 차종 선택 (가장 복잡한 부분)
        if model:
            print(f"\n📝 5단계: 차종 선택")
            try:
                # 기존 차종 선택 로직 사용 (이미 사람처럼 구현되어 있음)
                model_select = driver.find_element(By.ID, 'model_cd')
                select_element = Select(model_select)
                
                # 사용 가능한 옵션들 확인
                available_options = []
                for option in select_element.options:
                    option_text = option.text.strip()
                    option_value = option.get_attribute('value')
                    available_options.append((option_text, option_value))
                
                # 차종 매핑 로직 (기존 로직 재사용)
                model_code = None
                model_lower = model.lower()
                
                # 정확한 매칭 시도 (완전일치 우선)
                model_code = match_model_value(available_options, model)
                
                if model_code:
                    # 사람처럼 선택
                    pause(0.1, 0.2)
                    select_element.select_by_value(model_code)
                    pause(0.1, 0.2)
                    # change 발화로 프론트 검증 보강
                    try:
                        driver.execute_script("document.getElementById(arguments[0]).dispatchEvent(new Event('change', {bubbles:true}));", 'model_cd')
                    except Exception:
                        pass
                    
                    print(f"✅ 차종 선택 완료: {model}")
                    input_results['신청차종'] = True
                else:
                    print(f"❌ 차종 매칭 실패: {model}")
                    input_results['신청차종'] = False
                    
            except Exception as e:
                print(f"❌ 차종 선택 실패: {e}")
                input_results['신청차종'] = False
                
        # 중간 휴식
        pause(0.2, 0.4)
        
        # 6단계: 주소 관련 필드
        print(f"\n📝 6단계: 주소 정보 입력")
        
        # 주소 입력
        if addr:
            try:
                success = human_like_fill_field(driver, 'addr', addr, '주소', "readonly")
                input_results['주소'] = success
                pause(0.1, 0.2)
            except Exception as e:
                print(f"❌ 주소 입력 실패: {e}")
                input_results['주소'] = False
        
        # 상세주소 입력
        if addr_detail:
            try:
                success = human_like_fill_field(driver, 'addr_detail', addr_detail, '상세주소', "text")
                input_results['상세주소'] = success
                pause(0.1, 0.2)
            except Exception as e:
                print(f"❌ 상세주소 입력 실패: {e}")
                input_results['상세주소'] = False
        
        # 중간 휴식
        pause(0.2, 0.4)
        
        # 7단계: 날짜 정보 입력 (달력 우선)
        print(f"\n📝 7단계: 날짜 정보 입력")
        
        # 계약일자
        if contract:
            try:
                y, m, d = contract.split("-")
                picked = pick_date(driver, "#contract_day", int(y), int(m), int(d))
                success = True if picked else human_like_fill_field(driver, 'contract_day', contract, '계약일자', "readonly")
                # 최종 검증
                try:
                    val = driver.find_element(By.ID, 'contract_day').get_attribute('value')
                    if not val.startswith(f"{int(y):04d}-{int(m):02d}-{int(d):02d}"):
                        success = False
                except Exception:
                    pass
                input_results['계약일자'] = success
                pause(0.1, 0.2)
            except Exception as e:
                print(f"❌ 계약일자 입력 실패: {e}")
                input_results['계약일자'] = False
        
        # 출고예정일자
        if delivery:
            try:
                y2, m2, d2 = delivery.split("-")
                picked2 = pick_date(driver, "#delivery_sch_day", int(y2), int(m2), int(d2))
                success = True if picked2 else human_like_fill_field(driver, 'delivery_sch_day', delivery, '출고예정일자', "readonly")
                # 최종 검증
                try:
                    val2 = driver.find_element(By.ID, 'delivery_sch_day').get_attribute('value')
                    if not val2.startswith(f"{int(y2):04d}-{int(m2):02d}-{int(d2):02d}"):
                        success = False
                except Exception:
                    pass
                input_results['출고예정일자'] = success
                pause(0.1, 0.2)
            except Exception as e:
                print(f"❌ 출고예정일자 입력 실패: {e}")
                input_results['출고예정일자'] = False
        
        # 최종 확인 대기
        print("⏳ 최종 확인 중...")
        pause(0.2, 0.4)
        
        # 성공률 계산
        total_fields = len(input_results)
        successful_fields = sum(1 for success in input_results.values() if success)
        success_rate = (successful_fields / total_fields * 100) if total_fields > 0 else 0
        
        print(f"\n📊 입력 결과 요약:")
        print(f"   총 필드: {total_fields}")
        print(f"   성공: {successful_fields}")
        print(f"   실패: {total_fields - successful_fields}")
        print(f"   성공률: {success_rate:.1f}%")
        
        # 80% 이상 성공하면 True 반환
        if success_rate >= 80:
            print("✅ 필드 입력 완료 (80% 이상 성공)")
            return True
        else:
            print("⚠️ 필드 입력 부분 실패 (80% 미만 성공)")
            return False
        
    except Exception as e:
        print(f"❌ 필드 입력 중 오류: {e}")
        return False

def build_fill_script(user_data: dict) -> str:
    """필드 자동 입력 JS 스크립트 생성 (중복 선언 방지 버전)"""
    name = user_data.get('성명', '')
    phone = user_data.get('휴대전화', '')
    email = user_data.get('이메일', '.')
    tel = user_data.get('전화', '.')
    addr = user_data.get('주소', '')
    addr_detail = user_data.get('상세주소', '')
    contract = user_data.get('계약일자', '2025-08-16')
    birth = user_data.get('생년월일', '1990-01-01')
    delivery = user_data.get('출고예정일자', '2025-08-29')
    gender = user_data.get('성별', '남자')
    model = user_data.get('신청차종', '')
    count = user_data.get('신청대수', '1')

    return f"""
    try {{
      console.log('자동 입력 시작...');
      
      // 기본 정보 입력
      const nm=document.getElementById('req_nm'); if(nm) {{ nm.value='{name}'; console.log('성명 입력:', '{name}'); }}
      const mb=document.getElementById('mobile'); if(mb) {{ mb.value='{phone}'; console.log('휴대폰 입력:', '{phone}'); }}
      const em=document.getElementById('email'); if(em) {{ em.value='{email}'; console.log('이메일 입력:', '{email}'); }}
      const ph=document.getElementById('phone'); if(ph) {{ ph.value='{tel}'; console.log('전화 입력:', '{tel}'); }}
      
      // 주소 입력
      const ad=document.querySelector('input[name="addr"]')||document.getElementById('addr'); 
      if(ad) {{
        ad.removeAttribute('readonly'); 
        ad.value='{addr}'; 
        ad.dispatchEvent(new Event('input', {{bubbles:true}}));
        console.log('주소 입력:', '{addr}');
      }}
      
      const ad2=document.getElementById('addr_detail'); 
      if(ad2) {{ 
        ad2.value='{addr_detail or '123'}'; 
        ad2.dispatchEvent(new Event('input', {{bubbles:true}})); 
        ad2.dispatchEvent(new Event('change', {{bubbles:true}})); 
        console.log('상세주소 입력:', '{addr_detail or '123'}');
      }}
      
      // 신청대수 입력
      const cnt=document.getElementById('req_cnt'); if(cnt) {{ cnt.value='{count}'; console.log('신청대수 입력:', '{count}'); }}
      
      // 계약일자 입력 (readonly 처리)
      const ct=document.getElementById('contract_day'); 
      if(ct) {{
        ct.removeAttribute('readonly'); 
        ct.value='{contract}'; 
        ct.setAttribute('readonly','readonly'); 
        ct.dispatchEvent(new Event('change', {{bubbles:true}}));
        console.log('계약일자 입력:', '{contract}');
      }}
      
      // 생년월일 입력 (두 필드 모두 처리)
      const hb=document.getElementById('birth'); 
      if(hb) {{ 
        hb.value='{birth}'; 
        console.log('생년월일(birth) 입력:', '{birth}');
      }}
      
      const bf=document.getElementById('birth1'); 
      if(bf) {{ 
        bf.removeAttribute('readonly'); 
        bf.value='{birth}'; 
        bf.dispatchEvent(new Event('input', {{bubbles:true}})); 
        bf.dispatchEvent(new Event('change', {{bubbles:true}})); 
        bf.setAttribute('readonly','readonly'); 
        console.log('생년월일(birth1) 입력:', '{birth}');
      }}
      
      // 출고예정일자 입력 (readonly 처리)
      const dv=document.getElementById('delivery_sch_day'); 
      if(dv) {{ 
        dv.removeAttribute('readonly'); 
        dv.value='{delivery}'; 
        dv.setAttribute('readonly','readonly'); 
        dv.dispatchEvent(new Event('change', {{bubbles:true}})); 
        console.log('출고예정일자 입력:', '{delivery}');
      }}
      
      // 성별 선택
      const gid = ('{gender}'==='남자') ? 'req_sex1' : 'req_sex2'; 
      const r=document.getElementById(gid); 
      if(r) {{ 
        r.checked=true; 
        r.click(); 
        r.dispatchEvent(new Event('change', {{bubbles:true}})); 
        console.log('성별 선택:', '{gender}');
      }}
      
      // 신청유형 선택 (개인)
      const kind=document.getElementById('req_kind'); 
      if(kind) {{ 
        kind.value='P'; 
        kind.dispatchEvent(new Event('change', {{bubbles:true}})); 
        console.log('신청유형 선택: 개인');
      }}
      
      // 차종 선택
      let modelVal='';
      if ('{model}'.includes('EV3') && '{model}'.includes('스탠다드')) modelVal='EV3_2WD_S';
      else if ('{model}'.includes('레이EV') || '{model}'.includes('레이 EV')) modelVal='RAY_4_R';
      else if ('{model}'.includes('EV3') && '{model}'.includes('롱레인지')) modelVal='EV3_2WD_L17';
      
      const modelEl=document.getElementById('model_cd'); 
      if(modelEl && modelVal) {{ 
        modelEl.value=modelVal; 
        modelEl.dispatchEvent(new Event('change', {{bubbles:true}})); 
        console.log('차종 선택:', modelVal);
      }}
      
      console.log('자동 입력 완료');
      return true;
    }} catch(e) {{ 
      console.error('자동 입력 오류:', e); 
      return false; 
    }}
    """

def set_input_value_strict(driver, css: str, value: str) -> bool:
    """disabled/readonly를 잠시 해제하고 네이티브 setter로 값 설정 + input/change/blur 발화 후 원복"""
    js = """
    try {
      const el = document.querySelector(arguments[0]);
      if (!el) return false;
      const wasDisabled = !!el.disabled;
      const wasReadonly = el.hasAttribute('readonly');
      if (wasDisabled) el.disabled = false;
      if (wasReadonly) el.removeAttribute('readonly');
      try {
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        setter.call(el, arguments[1]);
      } catch(e) {
        el.value = arguments[1];
      }
      try { el.dispatchEvent(new Event('input', {bubbles:true})); } catch(e) {}
      try { el.dispatchEvent(new Event('change', {bubbles:true})); } catch(e) {}
      if (el.blur) { try { el.blur(); } catch(e) {} }
      if (wasReadonly) el.setAttribute('readonly','readonly');
      if (wasDisabled) el.disabled = true;
      return true;
    } catch(e) { return false; }
    """
    try:
        return bool(driver.execute_script(js, css, value))
    except Exception:
        return False

def force_enable_all_inputs(driver) -> None:
    """필요 시 모든 입력 요소의 disabled/readonly를 해제 (긴급 우회용)"""
    try:
        driver.execute_script(
            """
            document.querySelectorAll('input,select,textarea').forEach(el=>{
              if (el.disabled) el.disabled = false;
              if (el.hasAttribute('readonly')) el.removeAttribute('readonly');
            });
            """
        )
    except Exception:
        pass

def match_model_value(options, user_text: str):
    """차종 텍스트를 옵션 목록에 매핑. 완전일치 > 토큰 교집합 > 부분포함 순"""
    tx = (user_text or "").lower().strip()
    if not tx:
        return None
    norm = (
        tx.replace("더뉴", "").replace("the new", "").replace(" ", "")
    )
    # 후보 전처리
    options_lc = [((t or "").lower().strip(), v) for t, v in options]
    # 1) 완전일치 (공백 제거 버전 포함)
    exact = [v for t, v in options_lc if t == tx or t.replace(" ", "") == norm]
    if exact:
        return exact[0]
    # 2) 토큰 기반 교집합(가중치): 숫자/영문/한글 토큰 나눠 점수화
    def tokenize(s: str) -> set[str]:
        return set(re.findall(r"[a-zA-Z]+|[0-9]+|[가-힣]+", s))
    user_tokens = tokenize(tx)
    best = None
    best_score = 0
    for t, v in options_lc:
        score = len(user_tokens.intersection(tokenize(t)))
        if score > best_score:
            best_score = score
            best = v
    if best and best_score > 0:
        return best
    # 3) 부분 포함
    contains = [v for t, v in options_lc if norm in t.replace(" ", "") or t.replace(" ", "") in norm]
    return contains[0] if contains else None


