"""
전기차 신청서 메인 자동화 시스템
- 실시간 요소 감지
- 모든 필드 자동 입력
- 임시저장 + 새 창 처리
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

class EVAutomation:
    def __init__(self):
        self.driver = None
        
    def create_browser(self):
        """브라우저 생성"""
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=D:\\ChromeProfiles\\EV")
        chrome_options.add_argument("--window-size=1000,900")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        os.makedirs("D:\\ChromeProfiles\\EV", exist_ok=True)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("[BROWSER] 브라우저 생성 완료")
        
    def get_test_data(self):
        """테스트 데이터"""
        return {
            'name': '장원',
            'mobile': '010-9199-6844',
            'birth': '1990-01-01',
            'gender': '여자',
            'address': '충청북도 제천시 의림지로 171',
            'contract_date': '2025-08-16',
            'car_model': 'EV3 스탠다드',
            'priority': '사회계층 Y. 다자녀가구. 2자녀'
        }
    
    def wait_for_application_page(self):
        """신청서 페이지 대기"""
        print("[WAIT] 신청서 페이지 대기")
        print("수동으로 로그인 후 https://ev.or.kr/ev_ps/ps/seller/sellerApplyform 이동")
        
        while True:
            try:
                current_url = self.driver.current_url
                if 'sellerApplyform' in current_url:
                    print("[SUCCESS] 신청서 페이지 감지!")
                    return True
                    
                print(f"현재: {current_url[:50]}...")
                input("신청서 페이지 이동 후 Enter: ")
                
            except:
                print("[ERROR] 브라우저 연결 끊어짐")
                return False
    
    def auto_fill_all_fields(self, user_data):
        """모든 필드 자동 입력"""
        js_code = f"""
        console.log('=== {user_data['name']} 자동 입력 시작 ===');
        
        // 실시간 모니터링 설정
        window.checkStatus = function() {{
            const status = {{
                성명: document.getElementById('req_nm')?.value || '없음',
                휴대전화: document.getElementById('mobile')?.value || '없음',
                생년월일: document.getElementById('birth1')?.value || '없음',
                성별: document.querySelector('input[name="req_sex"]:checked')?.value || '없음',
                주소: document.querySelector('input[name="addr"]')?.value || '없음'
            }};
            console.log('필드 상태:', status);
            return status;
        }};
        
        try {{
            // 1. 기본 필드들
            document.getElementById('req_nm').value = '{user_data['name']}';
            document.getElementById('mobile').value = '{user_data['mobile']}';
            document.getElementById('email').value = '.';
            document.getElementById('phone').value = '.';
            document.getElementById('req_cnt').value = '1';
            
            // 2. 계약일자
            const contract = document.getElementById('contract_day');
            if (contract) {{
                contract.removeAttribute('readonly');
                contract.value = '{user_data['contract_date']}';
                contract.setAttribute('readonly', 'readonly');
            }}
            
            // 3. 생년월일 (강화 처리)
            const hiddenBirth = document.getElementById('birth');
            const birth = document.getElementById('birth1');
            
            if (hiddenBirth) hiddenBirth.value = '{user_data['birth']}';
            if (birth) {{
                birth.removeAttribute('readonly');
                birth.focus();
                birth.value = '';
                birth.value = '{user_data['birth']}';
                birth.dispatchEvent(new Event('input', {{ bubbles: true }}));
                birth.dispatchEvent(new Event('change', {{ bubbles: true }}));
                birth.setAttribute('readonly', 'readonly');
                console.log('생년월일 입력:', birth.value);
            }}
            
            // 4. 성별 (강화 처리)
            const allGender = document.querySelectorAll('input[name="req_sex"]');
            allGender.forEach(r => r.checked = false);
            
            const targetGender = document.getElementById('{user_data['gender']}' === '남자' ? 'req_sex1' : 'req_sex2');
            if (targetGender) {{
                targetGender.checked = true;
                targetGender.click();
                targetGender.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                const label = document.querySelector(`label[for="${{targetGender.id}}"]`);
                if (label) label.click();
                
                console.log('성별 선택:', targetGender.checked);
            }}
            
            // 5. 주소 (강화 처리)
            const addr = document.querySelector('input[name="addr"]') || document.getElementById('addr');
            if (addr) {{
                addr.removeAttribute('readonly');
                addr.value = '{user_data['address']}';
                addr.dispatchEvent(new Event('input', {{ bubbles: true }}));
                console.log('주소 입력:', addr.value);
            }}
            
            // 6. 드롭다운들
            const reqKind = document.getElementById('req_kind');
            if (reqKind) {{
                reqKind.value = 'P';
                reqKind.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            const model = document.getElementById('model_cd');
            if (model) {{
                const targetValue = '{user_data['car_model']}'.includes('스탠다드') ? 'EV3_2WD_S' : 'RAY_4_R';
                model.value = targetValue;
                model.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            console.log('기본 입력 완료');
            
        }} catch (error) {{
            console.log('입력 오류:', error.message);
        }}
        
        // 우선순위 설정 (2초 후)
        setTimeout(() => {{
            const hasSocial = '{user_data['priority']}'.includes('사회계층');
            
            if (hasSocial) {{
                document.getElementById('social_yn1').checked = true;
                setTimeout(() => {{
                    document.getElementById('social_kind').value = '3';
                    setTimeout(() => {{
                        document.getElementById('children_cnt').value = '2';
                    }}, 1000);
                }}, 1000);
            }} else {{
                document.getElementById('social_yn2').checked = true;
            }}
            
            document.getElementById('first_buy_yn1').checked = true;
            document.getElementById('poverty_yn2').checked = true;
            document.getElementById('taxi_yn2').checked = true;
            document.getElementById('exchange_yn2').checked = true;
            document.getElementById('ls_user_yn2').checked = true;
            
            console.log('=== 모든 입력 완료 ===');
            window.inputCompleted = true;
        }}, 2000);
        """
        
        self.driver.execute_script(js_code)
        print(f"[AUTO] {user_data['name']} 자동 입력 실행")
        
        # 완료 대기
        for i in range(10):
            try:
                completed = self.driver.execute_script("return window.inputCompleted === true;")
                if completed:
                    print("[SUCCESS] 모든 필드 입력 완료!")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("[TIMEOUT] 입력 완료 대기 시간 초과")
        return False
    
    def handle_temp_save(self):
        """임시저장 처리"""
        try:
            print("[TEMP_SAVE] 임시저장 시작")
            
            # 필수 필드 검증
            valid = self.driver.execute_script("""
            const required = ['req_nm', 'mobile', 'birth1'];
            const gender = document.querySelector('input[name="req_sex"]:checked');
            
            let allOk = true;
            required.forEach(id => {
                const el = document.getElementById(id);
                if (!el || !el.value) {
                    console.log('누락:', id);
                    allOk = false;
                }
            });
            
            if (!gender) {
                console.log('성별 미선택');
                allOk = false;
            }
            
            return allOk;
            """)
            
            if not valid:
                print("[ERROR] 필수 필드 누락 - 임시저장 불가")
                return False
            
            # 임시저장 버튼 클릭
            save_result = self.driver.execute_script("""
            const saveBtn = Array.from(document.querySelectorAll('button')).find(btn => 
                btn.textContent.includes('저장')
            );
            if (saveBtn) {
                saveBtn.click();
                return true;
            }
            return false;
            """)
            
            if not save_result:
                print("[ERROR] 저장 버튼 없음")
                return False
            
            time.sleep(2)
            
            # 확인 팝업
            self.driver.execute_script("""
            const confirmBtn = Array.from(document.querySelectorAll('button')).find(btn => 
                btn.textContent.includes('확인')
            );
            if (confirmBtn) confirmBtn.click();
            """)
            
            time.sleep(3)
            
            # 새 창 처리
            main_window = self.driver.current_window_handle
            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
            
            # 새 창으로 전환
            for window in self.driver.window_handles:
                if window != main_window:
                    self.driver.switch_to.window(window)
                    break
            
            # 확인코드 처리
            code = self.driver.execute_script("""
            const elements = document.querySelectorAll('*');
            for (let el of elements) {
                const text = el.textContent?.trim();
                if (/^[A-Za-z0-9]{6,15}$/.test(text)) {
                    return text;
                }
            }
            return null;
            """)
            
            if code:
                reversed = code[::-1]
                print(f"[CODE] {code} → {reversed}")
                
                self.driver.execute_script(f"""
                const input = document.querySelector('input[type="text"]');
                if (input) {{
                    input.value = '{reversed}';
                    setTimeout(() => {{
                        const submitBtn = document.querySelector('button');
                        if (submitBtn) submitBtn.click();
                    }}, 1000);
                }}
                """)
                
                time.sleep(3)
                self.driver.switch_to.window(main_window)
                print("[SUCCESS] 임시저장 완료!")
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] 임시저장 실패: {e}")
            return False
    
    def run(self):
        """메인 실행"""
        print("=== 전기차 신청서 자동화 ===")
        
        try:
            # 브라우저 생성
            self.create_browser()
            
            # 테스트 데이터
            user_data = self.get_test_data()
            print(f"테스트 대상: {user_data['name']}")
            
            # 신청서 페이지 대기
            if not self.wait_for_application_page():
                return
            
            # 자동 입력
            if self.auto_fill_all_fields(user_data):
                # 브라우저에서 상태 확인
                self.driver.execute_script("checkStatus();")
                
                # 임시저장 진행
                choice = input("임시저장 진행? (y/N): ")
                if choice.lower() == 'y':
                    self.handle_temp_save()
            
        except Exception as e:
            print(f"[ERROR] 실행 실패: {e}")
        finally:
            input("브라우저 유지하려면 Enter...")
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    automation = EVAutomation()
    automation.run()