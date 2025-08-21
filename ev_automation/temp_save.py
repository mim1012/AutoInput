#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
임시저장 기능 모듈 - 자동화 감지 우회
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ev_automation.verification_code import extract_code_smart, input_reversed_code

def wait_for_temp_save_button(driver, timeout=10):
    """
    임시저장 버튼이 클릭 가능할 때까지 대기
    """
    try:
        print("🔍 임시저장 버튼 찾기 시작...")
        
        # 1. 먼저 정확한 ID나 클래스로 찾기
        exact_selectors = [
            "#tempSave",
            "#temp_save", 
            "#btnTempSave",
            "#btn_temp_save",
            ".tempSave",
            ".temp_save",
            ".btnTempSave",
            ".btn_temp_save",
            ".btn-blue[onclick*='goSave']",
            "button[onclick*='goSave']",
            "input[onclick*='goSave']",
            "button[onclick*='tempSave']",
            "button[onclick*='temp_save']",
            "input[onclick*='tempSave']",
            "input[onclick*='temp_save']"
        ]
        
        for selector in exact_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    print(f"✅ 정확한 선택자로 찾음: {selector}")
                    return element
            except:
                continue
        
        # 2. 텍스트 기반으로 찾기
        text_selectors = [
            "//button[contains(text(), '임시저장')]",
            "//input[@value='임시저장']",
            "//a[contains(text(), '임시저장')]",
            "//button[contains(text(), '저장')]",
            "//input[@value='저장']",
            "//button[contains(text(), 'temp')]",
            "//input[@value='temp']"
        ]
        
        for xpath in text_selectors:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ 텍스트 기반으로 찾음: {xpath}")
                        return element
            except:
                continue
        
        # 3. 모든 버튼과 입력 필드 검사
        print("🔍 모든 버튼과 입력 필드 검사 중...")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        all_elements = all_buttons + all_inputs + all_links
        
        for element in all_elements:
            try:
                if not element.is_displayed():
                    continue
                    
                text = (element.text or '').lower()
                value = (element.get_attribute('value') or '').lower()
                onclick = (element.get_attribute('onclick') or '').lower()
                class_name = (element.get_attribute('class') or '').lower()
                id_name = (element.get_attribute('id') or '').lower()
                
                # 임시저장 관련 키워드 확인
                save_keywords = ['임시저장', 'temp', 'save', '저장']
                for keyword in save_keywords:
                    if (keyword in text or keyword in value or 
                        keyword in onclick or keyword in class_name or 
                        keyword in id_name):
                        print(f"✅ 키워드 기반으로 찾음: {keyword}")
                        print(f"   - 텍스트: {text}")
                        print(f"   - 값: {value}")
                        print(f"   - 클래스: {class_name}")
                        print(f"   - ID: {id_name}")
                        return element
                        
            except Exception as e:
                continue
        
        # 4. 폼 하단의 버튼들 확인 (임시저장은 보통 하단에 있음)
        print("🔍 폼 하단 버튼 확인 중...")
        try:
            # 페이지 하단으로 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # 하단의 모든 버튼 확인
            bottom_buttons = driver.find_elements(By.CSS_SELECTOR, "button, input[type='button'], input[type='submit']")
            
            for button in bottom_buttons:
                try:
                    if not button.is_displayed():
                        continue
                        
                    text = (button.text or '').lower()
                    value = (button.get_attribute('value') or '').lower()
                    
                    if '저장' in text or '저장' in value:
                        print(f"✅ 하단 버튼으로 찾음: {text or value}")
                        return button
                        
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ 하단 버튼 확인 중 오류: {e}")
        
        print("❌ 임시저장 버튼을 찾을 수 없습니다")
        return None
        
    except Exception as e:
        print(f"❌ 임시저장 버튼 찾기 실패: {e}")
        return None

def simulate_human_temp_save(driver):
    """
    인간과 유사한 임시저장 행동 시뮬레이션
    """
    try:
        print("🚀 임시저장 시작...")
        
        # 1. 페이지 완전 로딩 대기
        time.sleep(random.uniform(2, 3))
        
        # 2. 임시저장 버튼 찾기
        temp_save_button = wait_for_temp_save_button(driver)
        
        if not temp_save_button:
            print("❌ 임시저장 버튼을 찾을 수 없습니다")
            return False
        
        # 3. 버튼 정보 출력
        button_text = temp_save_button.text or (temp_save_button.get_attribute('value') or '')
        button_tag = temp_save_button.tag_name
        button_type = (temp_save_button.get_attribute('type') or '')
        
        print(f"🔍 임시저장 버튼 발견:")
        print(f"   - 태그: {button_tag}")
        print(f"   - 타입: {button_type}")
        print(f"   - 텍스트: {button_text}")
        print(f"   - 표시됨: {temp_save_button.is_displayed()}")
        print(f"   - 활성화됨: {temp_save_button.is_enabled()}")
        
        # 4. 폼 하단까지 충분히 스크롤한 후 버튼이 화면에 보이도록 다시 스크롤
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.4)
        except Exception:
            pass
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", temp_save_button)
        time.sleep(0.3)
        
        # 5. 인간과 유사한 행동 시뮬레이션
        simulate_human_behavior(driver)
        
        # 6. 클릭 시도
        print("🖱️ 임시저장 버튼 클릭 시도...")
        
        try:
            # 일반 클릭 시도
            temp_save_button.click()
            print("✅ 일반 클릭 성공")
        except Exception as e:
            print(f"⚠️ 일반 클릭 실패: {e}")
            try:
                # JavaScript 클릭 시도
                driver.execute_script("arguments[0].click();", temp_save_button)
                print("✅ JavaScript 클릭 성공")
            except Exception as e2:
                print(f"⚠️ JavaScript 클릭 실패: {e2}")
                try:
                    # ActionChains 클릭 시도
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(temp_save_button).click().perform()
                    print("✅ ActionChains 클릭 성공")
                except Exception as e3:
                    print(f"❌ 모든 클릭 방법 실패: {e3}")
                    return False
        
        # 7. 팝업(자식창/iframe/모달) 처리: 확인코드 추출→역순 입력→확인
        try:
            main = driver.current_window_handle
        except Exception:
            main = None

        # 7-a) alert 우선 수락
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            a = driver.switch_to.alert
            print(f"🛎️ 확인창: {a.text}")
            a.accept()
            time.sleep(0.2)
        except Exception:
            pass

        # 7-b) 자식창 처리
        try:
            handles = driver.window_handles
            if main and len(handles) > 1:
                child = [h for h in handles if h != main][0]
                driver.switch_to.window(child)
                print("🔄 자식창 전환 (임시저장 확인코드)")
                code = extract_code_smart(driver)
                if code:
                    ok = input_reversed_code(driver, code)
                    print(f"🔑 확인코드 처리: {ok}")
                try:
                    driver.close()
                except Exception:
                    pass
                driver.switch_to.window(main)
        except Exception as e:
            print(f"⚠️ 자식창 처리 실패: {e}")

        # 7-c) iframe/모달 여분 처리 (best-effort)
        try:
            code = extract_code_smart(driver)
            if code:
                input_reversed_code(driver, code)
        except Exception:
            pass

        # 8. 저장 완료 대기
        print("⏳ 저장 완료 대기 중...")
        return wait_for_save_completion(driver)
        
    except Exception as e:
        print(f"❌ 임시저장 실패: {e}")
        return False

def wait_for_save_completion(driver, timeout=30):
    """
    저장 완료 대기
    """
    try:
        start_time = time.time()
        print(f"⏰ 저장 완료 대기 시작 (최대 {timeout}초)")
        
        while time.time() - start_time < timeout:
            # 저장 중 메시지 확인
            try:
                # "저장중입니다" 메시지 찾기
                loading_selectors = [
                    "text=저장중입니다",
                    "text=저장 중",
                    "text=Saving",
                    "text=처리중",
                    "text=Processing",
                    ".loading",
                    "#loading",
                    "[class*='loading']",
                    "[id*='loading']"
                ]
                
                loading_found = False
                for selector in loading_selectors:
                    try:
                        if selector.startswith("text="):
                            text = selector[5:]
                            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                            for element in elements:
                                if element.is_displayed():
                                    loading_found = True
                                    print(f"⏳ 저장 중... ({text})")
                                    break
                            if loading_found:
                                break
                        else:
                            element = driver.find_element(By.CSS_SELECTOR, selector)
                            if element and element.is_displayed():
                                loading_found = True
                                print(f"⏳ 저장 중... ({selector})")
                                break
                    except:
                        continue
                
                if not loading_found:
                    # 저장 완료 메시지 확인
                    success_selectors = [
                        "text=저장되었습니다",
                        "text=저장 완료",
                        "text=Saved",
                        "text=완료",
                        "text=성공",
                        ".success",
                        "#success",
                        "[class*='success']",
                        "[id*='success']"
                    ]
                    
                    for selector in success_selectors:
                        try:
                            if selector.startswith("text="):
                                text = selector[5:]
                                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                                for element in elements:
                                    if element.is_displayed():
                                        print(f"✅ 저장 완료: {text}")
                                        return True
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                                if element and element.is_displayed():
                                    print(f"✅ 저장 완료: {selector}")
                                    return True
                        except:
                            continue
                    
                    # 오류 메시지 확인
                    error_selectors = [
                        "text=오류",
                        "text=에러",
                        "text=Error",
                        "text=실패",
                        "text=Failed",
                        ".error",
                        "#error",
                        "[class*='error']",
                        "[id*='error']"
                    ]
                    
                    for selector in error_selectors:
                        try:
                            if selector.startswith("text="):
                                text = selector[5:]
                                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                                for element in elements:
                                    if element.is_displayed():
                                        print(f"❌ 저장 오류: {text}")
                                        return False
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                                if element and element.is_displayed():
                                    print(f"❌ 저장 오류: {selector}")
                                    return False
                        except:
                            continue
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ 저장 상태 확인 중 오류: {e}")
                time.sleep(1)
        
        print("⚠️ 저장 완료 대기 시간 초과")
        return False
        
    except Exception as e:
        print(f"❌ 저장 완료 대기 실패: {e}")
        return False

def simulate_human_behavior(driver):
    """
    인간과 유사한 행동 시뮬레이션
    """
    import random
    
    # 랜덤 스크롤
    scroll_amount = random.randint(50, 150)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(random.uniform(0.3, 0.8))
    
    # 랜덤 마우스 움직임
    driver.execute_script("""
        const event = new MouseEvent('mousemove', {
            'view': window,
            'bubbles': true,
            'cancelable': true,
            'clientX': Math.random() * window.innerWidth,
            'clientY': Math.random() * window.innerHeight
        });
        document.dispatchEvent(event);
    """)
    
    time.sleep(random.uniform(0.2, 0.5))

def force_temp_save_with_retry(driver, max_retries=3):
    """
    재시도 로직이 포함된 강제 임시저장
    """
    for attempt in range(max_retries):
        print(f"🔄 임시저장 시도 {attempt + 1}/{max_retries}")
        
        try:
            # 1. 페이지 완전 로딩 대기
            time.sleep(random.uniform(2, 4))
            
            # 2. 필수 필드 입력 확인 (선택적)
            print("🔍 필수 필드 입력 상태 확인...")
            required_fields = ['req_nm', 'mobile', 'birth', 'addr']
            missing_fields = []
            
            for field_id in required_fields:
                try:
                    element = driver.find_element(By.ID, field_id)
                except Exception:
                    # 요소가 없으면 누락으로 간주하지 않고 통과 (페이지 구조 차이 허용)
                    print(f"   - {field_id}: 찾을 수 없음 (무시)")
                    continue
                try:
                    value = (element.get_attribute('value') or '').strip()
                    if not value:
                        missing_fields.append(field_id)
                        print(f"   - {field_id}: 비어있음")
                    else:
                        print(f"   - {field_id}: {value[:10]}...")
                except Exception:
                    print(f"   - {field_id}: 값 읽기 실패 (무시)")
            
            if missing_fields:
                print(f"⚠️ 누락된 필드: {missing_fields}")
                if attempt < max_retries - 1:
                    print("🔄 필드 입력 후 재시도...")
                    time.sleep(3)
                    continue
            else:
                print("✅ 모든 필수 필드가 입력되었습니다")
            
            # 3. 임시저장 시도
            success = simulate_human_temp_save(driver)
            
            if success:
                print("🎉 임시저장 성공!")
                return True
            else:
                print(f"❌ 임시저장 실패 (시도 {attempt + 1})")
                if attempt < max_retries - 1:
                    print("🔄 재시도 대기 중...")
                    time.sleep(random.uniform(3, 5))
                
        except Exception as e:
            print(f"❌ 임시저장 중 오류: {e}")
            if attempt < max_retries - 1:
                print("🔄 오류 후 재시도 대기 중...")
                time.sleep(3)
    
    print("❌ 모든 임시저장 시도 실패")
    return False


