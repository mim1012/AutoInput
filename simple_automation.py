"""
간단한 전기차 신청서 자동화
- 변수 중복 오류 해결
- 직관적인 처리 과정
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SimpleEVAutomation:
    def __init__(self):
        self.driver = None
        
    def create_browser(self):
        """브라우저 생성"""
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=D:\\ChromeProfiles\\Simple")
        chrome_options.add_argument("--window-size=1000,900")
        chrome_options.add_argument("--no-sandbox")
        
        os.makedirs("D:\\ChromeProfiles\\Simple", exist_ok=True)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("[BROWSER] 브라우저 생성 완료")
        
    def wait_for_page(self):
        """신청서 페이지 대기"""
        print("[WAIT] 수동으로 로그인 후 신청서 페이지 이동")
        input("신청서 페이지 도달 후 Enter: ")
        
        url = self.driver.current_url
        if 'sellerApplyform' in url:
            print("[SUCCESS] 신청서 페이지 감지!")
            return True
        else:
            print(f"[ERROR] 신청서 페이지 아님: {url}")
            return False
    
    def fill_all_fields(self):
        """모든 필드 입력"""
        print("[AUTO] 모든 필드 자동 입력 시작")
        
        # 간단하고 안전한 JavaScript
        js_code = """
        console.log('=== 자동 입력 시작 ===');
        
        // 1. 기본 필드들
        if (document.getElementById('req_nm')) {
            document.getElementById('req_nm').value = '장원';
            console.log('1. 성명: OK');
        }
        
        if (document.getElementById('mobile')) {
            document.getElementById('mobile').value = '010-9199-6844';
            console.log('2. 휴대전화: OK');
        }
        
        if (document.getElementById('email')) {
            document.getElementById('email').value = '.';
            console.log('3. 이메일: OK');
        }
        
        if (document.getElementById('phone')) {
            document.getElementById('phone').value = '.';
            console.log('4. 전화: OK');
        }
        
        // 2. 주소
        const addr1 = document.querySelector('input[name="addr"]');
        if (addr1) {
            addr1.value = '충청북도 제천시 의림지로 171';
            console.log('5. 주소: OK');
        }
        
        const addrDetail1 = document.getElementById('addr_detail');
        if (addrDetail1) {
            addrDetail1.value = '123';
            console.log('6. 상세주소: OK');
        }
        
        // 3. 생년월일
        const birth2 = document.getElementById('birth');
        if (birth2) {
            birth2.value = '1990-01-01';
        }
        
        const birth1_2 = document.getElementById('birth1');
        if (birth1_2) {
            birth1_2.removeAttribute('readonly');
            birth1_2.value = '1990-01-01';
            birth1_2.setAttribute('readonly', 'readonly');
            console.log('7. 생년월일: OK');
        }
        
        // 4. 성별 (여자)
        const female1 = document.getElementById('req_sex2');
        if (female1) {
            document.getElementById('req_sex1').checked = false;
            document.getElementById('req_sex2').checked = false;
            female1.checked = true;
            female1.click();
            console.log('8. 성별: OK');
        }
        
        // 5. 신청대수
        if (document.getElementById('req_cnt')) {
            document.getElementById('req_cnt').value = '1';
            console.log('9. 신청대수: OK');
        }
        
        // 6. 계약일자
        const contract1 = document.getElementById('contract_day');
        if (contract1) {
            contract1.removeAttribute('readonly');
            contract1.value = '2025-08-16';
            contract1.setAttribute('readonly', 'readonly');
            console.log('10. 계약일자: OK');
        }
        
        // 7. 출고예정일자
        const delivery1 = document.getElementById('delivery_sch_day');
        if (delivery1) {
            delivery1.removeAttribute('readonly');
            delivery1.value = '2025-08-29';
            delivery1.setAttribute('readonly', 'readonly');
            console.log('11. 출고예정일자: OK');
        }
        
        console.log('=== 기본 입력 완료 ===');
        """
        
        self.driver.execute_script(js_code)
        time.sleep(2)
        
        # 드롭다운 처리
        dropdown_js = """
        // 신청유형
        const reqKind1 = document.getElementById('req_kind');
        if (reqKind1) {
            reqKind1.value = 'P';
            reqKind1.dispatchEvent(new Event('change', { bubbles: true }));
            console.log('12. 신청유형: OK');
        }
        
        // 신청차종
        const model1 = document.getElementById('model_cd');
        if (model1) {
            model1.value = 'EV3_2WD_S';
            model1.dispatchEvent(new Event('change', { bubbles: true }));
            console.log('13. 신청차종: OK');
        }
        
        console.log('=== 드롭다운 완료 ===');
        """
        
        self.driver.execute_script(dropdown_js)
        time.sleep(2)
        
        # 우선순위 처리
        priority_js = """
        // 우선순위 (장원: 사회계층 Y, 다자녀가구, 2자녀)
        document.getElementById('social_yn1').checked = true;
        document.getElementById('social_yn1').dispatchEvent(new Event('change', { bubbles: true }));
        console.log('14. 사회계층: Y');
        
        setTimeout(() => {
            const socialKind1 = document.getElementById('social_kind');
            if (socialKind1) {
                socialKind1.value = '3';
                socialKind1.dispatchEvent(new Event('change', { bubbles: true }));
                console.log('15. 사회계층유형: 다자녀가구');
                
                setTimeout(() => {
                    const children1 = document.getElementById('children_cnt');
                    if (children1) {
                        children1.value = '2';
                        children1.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('16. 자녀수: 2');
                    }
                }, 1000);
            }
        }, 1000);
        
        // 기타 조건들
        setTimeout(() => {
            document.getElementById('first_buy_yn1').checked = true;
            document.getElementById('poverty_yn2').checked = true;
            document.getElementById('taxi_yn2').checked = true;
            document.getElementById('exchange_yn2').checked = true;
            document.getElementById('ls_user_yn2').checked = true;
            
            console.log('17. 기타 우선순위 완료');
            console.log('=== 모든 입력 완료! ===');
            
            window.allFieldsCompleted = true;
        }, 3000);
        """
        
        self.driver.execute_script(priority_js)
        
        # 완료 대기
        for i in range(10):
            try:
                completed = self.driver.execute_script("return window.allFieldsCompleted === true;")
                if completed:
                    print("[SUCCESS] 모든 필드 입력 완료!")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("[PARTIAL] 일부 필드 입력 완료")
        return True
    
    def handle_temp_save_simple(self):
        """간단한 임시저장 처리"""
        try:
            print("[TEMP_SAVE] 임시저장 처리 시작")
            
            # 임시저장 버튼 찾기
            save_js = """
            console.log('=== 임시저장 버튼 찾기 ===');
            
            const buttons = Array.from(document.querySelectorAll('button'));
            console.log('전체 버튼 개수:', buttons.length);
            
            // 모든 버튼 출력
            buttons.forEach((btn, i) => {
                const text = btn.textContent ? btn.textContent.trim() : '';
                const onclick = btn.onclick ? 'function' : 'none';
                console.log(`  ${i}: "${text}" onclick: ${onclick}`);
            });
            
            // 임시저장 버튼 찾기
            const saveBtn = buttons.find(btn => 
                btn.textContent.includes('임시저장') || 
                btn.textContent.includes('저장') ||
                (btn.onclick && btn.onclick.toString().includes('goSave'))
            );
            
            if (saveBtn) {
                console.log('임시저장 버튼 발견:', saveBtn.textContent);
                saveBtn.click();
                console.log('✅ 임시저장 버튼 클릭!');
                return true;
            } else {
                console.log('❌ 임시저장 버튼 없음');
                return false;
            }
            """
            
            if not self.driver.execute_script(save_js):
                print("[ERROR] 임시저장 버튼 없음")
                return False
            
            print("[POPUP] 팝업 대기 중...")
            time.sleep(2)
            
            # Alert 처리
            try:
                alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                print(f"[POPUP] 팝업 감지: {alert.text}")
                alert.accept()  # Enter 역할
                print("[POPUP] 자동 Enter 완료")
            except:
                print("[POPUP] JavaScript alert 없음")
            
            time.sleep(3)
            
            # 새 창 처리
            print("[NEW_WINDOW] 새 창 감지 중...")
            main_window = self.driver.current_window_handle
            
            try:
                WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
                print("[NEW_WINDOW] 새 창 감지 성공!")
                
                # 새 창으로 전환
                for window in self.driver.window_handles:
                    if window != main_window:
                        self.driver.switch_to.window(window)
                        break
                
                time.sleep(2)
                
                # 확인코드 추출
                code_js = """
                console.log('=== 확인코드 추출 ===');
                
                const spans = document.querySelectorAll('span');
                let foundCode = null;
                
                spans.forEach(span => {
                    const text = span.textContent ? span.textContent.trim() : '';
                    if (/^[A-Za-z0-9]{6,15}$/.test(text) && text !== '123' && text !== '321') {
                        console.log('확인코드 발견:', text);
                        if (!foundCode) foundCode = text;
                    }
                });
                
                return foundCode;
                """
                
                code = self.driver.execute_script(code_js)
                
                if code:
                    reversed_code = code[::-1]
                    print(f"[CODE] {code} → {reversed_code}")
                    
                    # 입력 및 제출
                    input_js = f"""
                    const input1 = document.getElementById('randeomChk');
                    if (input1) {{
                        input1.value = '{reversed_code}';
                        console.log('확인코드 입력 완료');
                        
                        setTimeout(() => {{
                            const confirmBtn = document.querySelector('button[onclick*="goCompare"]') ||
                                             Array.from(document.querySelectorAll('button')).find(btn => 
                                                 btn.textContent.includes('확인')
                                             );
                            if (confirmBtn) {{
                                confirmBtn.click();
                                console.log('확인 버튼 클릭 완료');
                            }}
                        }}, 1000);
                    }}
                    """
                    
                    self.driver.execute_script(input_js)
                    time.sleep(3)
                    
                    # 메인 창 복귀
                    self.driver.switch_to.window(main_window)
                    print("[SUCCESS] 임시저장 완료!")
                    return True
            
            except Exception as e:
                print(f"[ERROR] 새 창 처리 실패: {e}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 임시저장 실패: {e}")
            return False
    
    def run(self):
        """실행"""
        print("=== 간단한 전기차 자동화 ===")
        
        try:
            # 브라우저 생성
            self.create_browser()
            
            # 신청서 페이지 대기
            if not self.wait_for_page():
                return
            
            # 모든 필드 입력
            if self.fill_all_fields():
                print("[COMPLETE] 모든 필드 입력 완료!")
                
                # 임시저장 진행
                choice = input("임시저장을 진행하시겠습니까? (y/N): ")
                if choice.lower() == 'y':
                    self.handle_temp_save_simple()
            
            print("[DONE] 처리 완료!")
            
        except Exception as e:
            print(f"[ERROR] 실행 실패: {e}")
        finally:
            input("브라우저 유지하려면 Enter...")
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    automation = SimpleEVAutomation()
    automation.run()