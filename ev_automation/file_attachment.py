import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def attach_pdf_files(driver, user_name, pdf_folder_path):
    """PDF 파일 4개 자동 첨부 (하나의 파일을 여러 항목에 사용)"""
    try:
        print(f"[FILE] {user_name} PDF 파일 첨부 시작")
        
        # 첨부할 파일 목록 (4개 항목) - 역순으로 처리
        file_types = [
            "기타서류",  # 4번째
            "소득증빙",  # 3번째
            "신분증",    # 2번째
            "계약서"     # 1번째
        ]
        
        # 하나의 PDF 파일 경로 찾기 (여러 방법 시도)
        pdf_file_path = find_pdf_file(pdf_folder_path, user_name)
        
        if not pdf_file_path:
            print(f"[ERROR] {user_name}의 PDF 파일을 찾을 수 없습니다")
            return False
        
        print(f"[FILE] 사용할 PDF 파일: {pdf_file_path}")
        
        # 페이지 이동 후 충분한 대기
        print(f"[FILE] 파일 첨부 페이지 로딩 대기 중...")
        time.sleep(5)  # 페이지 로딩 대기
        
        # 페이지가 완전히 로드될 때까지 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'], .file-upload, #fileUpload"))
            )
            print(f"[FILE] 파일 첨부 요소 로딩 완료")
        except:
            print(f"[WARNING] 파일 첨부 요소를 찾을 수 없습니다. 계속 진행합니다.")
        
        attached_count = 0
        
        # 역순으로 처리 (기타서류부터 계약서까지)
        for i, file_type in enumerate(file_types):
            print(f"[FILE] {file_type} 항목에 파일 첨부 시도 ({i+1}/4)")
            
            # 파일 첨부 버튼 찾기 및 클릭
            attach_success = attach_single_file(driver, pdf_file_path, file_type)
            
            if attach_success:
                attached_count += 1
                print(f"[SUCCESS] {file_type} 항목 첨부 완료")
                
                # 첨부 후 확인 버튼 클릭 및 대기
                if click_confirm_button(driver, file_type):
                    print(f"[SUCCESS] {file_type} 확인 버튼 클릭 완료")
                    time.sleep(3)  # 확인 후 대기
                else:
                    print(f"[WARNING] {file_type} 확인 버튼 클릭 실패")
                    time.sleep(2)  # 기본 대기
            else:
                print(f"[ERROR] {file_type} 항목 첨부 실패")
                time.sleep(1)  # 실패 시 짧은 대기
        
        print(f"[FILE] 총 {attached_count}/4개 항목 첨부 완료")
        return attached_count >= 2  # 최소 2개 이상 첨부되면 성공으로 간주
        
    except Exception as e:
        print(f"[ERROR] 파일 첨부 중 오류: {e}")
        return False

def find_pdf_file(pdf_folder_path, user_name):
    """사용자의 PDF 파일 찾기 (여러 방법 시도)"""
    try:
        # 방법 1: 사용자명으로 시작하는 PDF 파일
        for file in os.listdir(pdf_folder_path):
            if file.lower().endswith('.pdf') and file.startswith(user_name):
                return os.path.join(pdf_folder_path, file)
        
        # 방법 2: 사용자명이 포함된 PDF 파일
        for file in os.listdir(pdf_folder_path):
            if file.lower().endswith('.pdf') and user_name in file:
                return os.path.join(pdf_folder_path, file)
        
        # 방법 3: 첫 번째 PDF 파일 사용
        for file in os.listdir(pdf_folder_path):
            if file.lower().endswith('.pdf'):
                return os.path.join(pdf_folder_path, file)
        
        return None
        
    except Exception as e:
        print(f"[ERROR] PDF 파일 찾기 실패: {e}")
        return None

def click_confirm_button(driver, file_type):
    """파일 첨부 후 확인 버튼 클릭"""
    try:
        print(f"[CONFIRM] {file_type} 확인 버튼 찾기")
        
        # 다양한 확인 버튼 셀렉터
        confirm_selectors = [
            "button[onclick*='확인']",
            "button[onclick*='confirm']",
            "button:contains('확인')",
            "button:contains('OK')",
            "input[type='button'][value*='확인']",
            "input[type='submit'][value*='확인']",
            ".btn-confirm",
            ".btn-ok",
            "#confirmBtn",
            "#okBtn"
        ]
        
        for selector in confirm_selectors:
            try:
                if selector.startswith("button:contains("):
                    # jQuery 스타일 셀렉터는 JavaScript로 처리
                    js_script = f"""
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const targetButton = buttons.find(btn => 
                        btn.textContent.includes('{selector.split("'")[1]}')
                    );
                    if (targetButton) {{
                        targetButton.scrollIntoView({{block: 'center'}});
                        targetButton.click();
                        return true;
                    }}
                    return false;
                    """
                    result = driver.execute_script(js_script)
                    if result:
                        print(f"[SUCCESS] {file_type} 확인 버튼 클릭 완료 (JavaScript)")
                        return True
                else:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    if button and button.is_displayed() and button.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(1)  # 스크롤 후 대기
                        button.click()
                        print(f"[SUCCESS] {file_type} 확인 버튼 클릭 완료: {selector}")
                        return True
            except:
                continue
        
        # 확인 버튼을 찾지 못한 경우, 팝업이나 모달 확인
        try:
            # 팝업 확인
            popup_selectors = [
                ".modal .btn-primary",
                ".popup .btn-ok",
                ".dialog .btn-confirm",
                "[role='dialog'] button"
            ]
            
            for selector in popup_selectors:
                try:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    if button and button.is_displayed():
                        button.click()
                        print(f"[SUCCESS] {file_type} 팝업 확인 버튼 클릭 완료")
                        return True
                except:
                    continue
        except:
            pass
        
        print(f"[WARNING] {file_type} 확인 버튼을 찾을 수 없습니다")
        return False
        
    except Exception as e:
        print(f"[ERROR] {file_type} 확인 버튼 클릭 실패: {e}")
        return False

def attach_single_file(driver, file_path, file_type):
    """단일 파일 첨부"""
    try:
        print(f"[FILE] {file_type} 파일 첨부 시작")
        
        # 파일 첨부 버튼 찾기 (여러 방법 시도)
        file_input = None
        
        # 방법 1: type="file" input 찾기
        file_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        print(f"[FILE] 발견된 file input 수: {len(file_inputs)}")
        
        if file_inputs:
            # 각 file input의 정보 출력
            for i, inp in enumerate(file_inputs):
                inp_id = inp.get_attribute('id') or 'no-id'
                inp_name = inp.get_attribute('name') or 'no-name'
                inp_class = inp.get_attribute('class') or 'no-class'
                print(f"[FILE]   {i+1}. id={inp_id}, name={inp_name}, class={inp_class}")
            
            # 첫 번째 file input 사용
            file_input = file_inputs[0]
            print(f"[FILE] 첫 번째 file input 선택: {file_input.get_attribute('id') or 'no-id'}")
        
        # 방법 2: 특정 ID나 클래스로 찾기
        if not file_input:
            selectors = [
                '#fileUpload',
                '.file-upload',
                'input[name*="file"]',
                'input[id*="file"]',
                'input[name*="upload"]',
                'input[id*="upload"]'
            ]
            for selector in selectors:
                try:
                    file_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"[FILE] 특정 셀렉터로 file input 발견: {selector}")
                    break
                except:
                    continue
        
        if file_input:
            # 파일 경로 입력
            print(f"[FILE] 파일 경로 입력: {file_path}")
            file_input.send_keys(file_path)
            print(f"[FILE] {file_type} 항목에 파일 경로 입력 완료")
            
            # 첨부 완료 대기
            time.sleep(3)
            
            # 첨부 성공 확인
            success = check_attachment_success(driver, file_type)
            if success:
                print(f"[SUCCESS] {file_type} 파일 첨부 성공 확인")
            else:
                print(f"[WARNING] {file_type} 파일 첨부 확인 실패")
            
            return success
        else:
            print(f"[ERROR] 파일 첨부 input을 찾을 수 없음")
            return False
            
    except Exception as e:
        print(f"[ERROR] 파일 첨부 실패: {e}")
        return False

def check_attachment_success(driver, file_type):
    """파일 첨부 성공 여부 확인"""
    try:
        # 첨부된 파일 목록에서 확인
        success_indicators = [
            f'//span[contains(text(), "{file_type}")]',
            f'//div[contains(text(), "{file_type}")]',
            '//span[contains(@class, "file-name")]',
            '//div[contains(@class, "attached-file")]'
        ]
        
        for indicator in success_indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                if element:
                    return True
            except:
                continue
        
        # 파일 input의 value 확인
        file_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        for file_input in file_inputs:
            if file_input.get_attribute('value'):
                return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] 첨부 확인 실패: {e}")
        return False

def find_and_click_submit_button(driver):
    """지원 신청 버튼 찾기 및 클릭"""
    try:
        print("[SUBMIT] 지원 신청 버튼 찾기")
        
        # 다양한 셀렉터로 버튼 찾기
        button_selectors = [
            "button[onclick*='submit']",
            "button[onclick*='apply']",
            "button[onclick*='신청']",
            "button[onclick*='지원']",
            "input[type='submit'][value*='신청']",
            "input[type='submit'][value*='지원']",
            "button:contains('지원 신청')",
            "button:contains('신청 완료')",
            "button:contains('최종 제출')",
            ".btn-submit",
            ".btn-apply",
            "#submitBtn",
            "#applyBtn"
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith("button:contains("):
                    # jQuery 스타일 셀렉터는 JavaScript로 처리
                    js_script = f"""
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const targetButton = buttons.find(btn => 
                        btn.textContent.includes('{selector.split("'")[1]}')
                    );
                    if (targetButton) {{
                        targetButton.scrollIntoView({{block: 'center'}});
                        targetButton.click();
                        return true;
                    }}
                    return false;
                    """
                    result = driver.execute_script(js_script)
                    if result:
                        print(f"[SUCCESS] 지원 신청 버튼 클릭 완료 (JavaScript)")
                        return True
                else:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    if button:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        button.click()
                        print(f"[SUCCESS] 지원 신청 버튼 클릭 완료: {selector}")
                        return True
            except:
                continue
        
        # XPath로도 시도
        xpath_selectors = [
            "//button[contains(text(), '지원 신청')]",
            "//button[contains(text(), '신청 완료')]",
            "//button[contains(text(), '최종 제출')]",
            "//input[@type='submit' and contains(@value, '신청')]",
            "//input[@type='submit' and contains(@value, '지원')]"
        ]
        
        for xpath in xpath_selectors:
            try:
                button = driver.find_element(By.XPATH, xpath)
                if button:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    button.click()
                    print(f"[SUCCESS] 지원 신청 버튼 클릭 완료 (XPath): {xpath}")
                    return True
            except:
                continue
        
        print("[ERROR] 지원 신청 버튼을 찾을 수 없음")
        return False
        
    except Exception as e:
        print(f"[ERROR] 지원 신청 버튼 클릭 실패: {e}")
        return False

def handle_final_popup(driver):
    """최종 제출 후 팝업 처리 (여러 단계 처리)"""
    try:
        print("[POPUP] 최종 제출 후 팝업 처리 시작")
        
        # 첫 번째 팝업 대기 (더 긴 대기 시간)
        print("[POPUP] 첫 번째 팝업 대기 중...")
        time.sleep(3)  # 팝업이 나타날 때까지 충분히 대기
        
        # JavaScript alert 처리 (첫 번째 팝업)
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"[POPUP] 첫 번째 알림 메시지: {alert_text}")
            alert.accept()
            print("[POPUP] 첫 번째 알림 확인 완료")
            time.sleep(2)  # 팝업 닫힘 대기
        except:
            print("[POPUP] 첫 번째 JavaScript 알림 없음")
        
        # 두 번째 팝업 대기 (문자 역순 입력 후 나타나는 팝업)
        print("[POPUP] 두 번째 팝업 대기 중...")
        time.sleep(3)  # 두 번째 팝업이 나타날 때까지 대기
        
        # 두 번째 JavaScript alert 처리
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"[POPUP] 두 번째 알림 메시지: {alert_text}")
            alert.accept()
            print("[POPUP] 두 번째 알림 확인 완료")
            time.sleep(2)  # 팝업 닫힘 대기
        except:
            print("[POPUP] 두 번째 JavaScript 알림 없음")
        
        # HTML 팝업 버튼 처리 (여러 번 시도)
        popup_buttons = [
            "button:contains('확인')",
            "button:contains('OK')",
            "button:contains('완료')",
            "button:contains('닫기')",
            ".btn-confirm",
            ".btn-ok",
            ".btn-close"
        ]
        
        # 여러 번 팝업 버튼 찾기 시도
        for attempt in range(3):
            print(f"[POPUP] HTML 팝업 버튼 찾기 시도 {attempt + 1}/3")
            
            for selector in popup_buttons:
                try:
                    if selector.startswith("button:contains("):
                        js_script = f"""
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const targetButton = buttons.find(btn => 
                            btn.textContent.includes('{selector.split("'")[1]}')
                        );
                        if (targetButton) {{
                            targetButton.click();
                            return true;
                        }}
                        return false;
                        """
                        result = driver.execute_script(js_script)
                        if result:
                            print(f"[SUCCESS] 팝업 버튼 클릭 완료: {selector}")
                            time.sleep(1)  # 클릭 후 대기
                            break
                    else:
                        button = driver.find_element(By.CSS_SELECTOR, selector)
                        if button:
                            button.click()
                            print(f"[SUCCESS] 팝업 버튼 클릭 완료: {selector}")
                            time.sleep(1)  # 클릭 후 대기
                            break
                except:
                    continue
            
            # 다음 시도 전 대기
            if attempt < 2:
                time.sleep(2)
        
        print("[POPUP] 팝업 처리 완료")
        return True
        
    except Exception as e:
        print(f"[ERROR] 팝업 처리 실패: {e}")
        return False
