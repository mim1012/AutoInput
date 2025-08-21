#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
임시저장 기능 테스트 스크립트
"""

import time
from ev_automation.browser import create_stealth_browser, create_normal_browser
from ev_automation.temp_save import force_temp_save_with_retry, wait_for_temp_save_button
from selenium.webdriver.common.by import By

def test_temp_save():
    """임시저장 기능 테스트"""
    driver = None
    try:
        print("🚀 임시저장 테스트 시작...")
        
        # 브라우저 생성
        print("🔍 스텔스 브라우저 생성 중...")
        driver = create_stealth_browser()
        if not driver:
            print("❌ 스텔스 브라우저 생성 실패")
            print("💡 일반 브라우저로 재시도...")
            driver = create_normal_browser()
            if not driver:
                print("❌ 브라우저 생성 실패")
                return False
        
        # 신청서 페이지로 이동
        print("🌐 신청서 페이지로 이동 중...")
        driver.get("https://www.ev.or.kr/ev_ps/ps/seller/sellerApplyform")
        time.sleep(5)
        
        # 현재 URL 확인
        current_url = driver.current_url
        print(f"📍 현재 페이지: {current_url}")
        
        if 'sellerApplyform' not in current_url:
            print("❌ 신청서 페이지가 아닙니다")
            print("💡 로그인이 필요할 수 있습니다")
            return False
        
        # 임시저장 버튼 찾기 테스트
        print("\n🔍 임시저장 버튼 찾기 테스트...")
        temp_save_button = wait_for_temp_save_button(driver)
        
        if temp_save_button:
            print("✅ 임시저장 버튼을 찾았습니다!")
            
            # 버튼 정보 출력
            button_text = temp_save_button.text or temp_save_button.get_attribute('value', '')
            button_tag = temp_save_button.tag_name
            button_type = temp_save_button.get_attribute('type', '')
            
            print(f"   - 태그: {button_tag}")
            print(f"   - 타입: {button_type}")
            print(f"   - 텍스트: {button_text}")
            print(f"   - 표시됨: {temp_save_button.is_displayed()}")
            print(f"   - 활성화됨: {temp_save_button.is_enabled()}")
            
            # 임시저장 테스트
            print("\n🚀 임시저장 테스트...")
            success = force_temp_save_with_retry(driver, max_retries=2)
            
            if success:
                print("🎉 임시저장 테스트 성공!")
                return True
            else:
                print("❌ 임시저장 테스트 실패")
                return False
        else:
            print("❌ 임시저장 버튼을 찾을 수 없습니다")
            
            # 페이지의 모든 버튼 정보 출력
            print("\n📋 페이지의 모든 버튼 정보:")
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            
            print(f"총 버튼 수: {len(all_buttons)}")
            print(f"총 입력 필드 수: {len(all_inputs)}")
            
            for i, button in enumerate(all_buttons[:10]):  # 처음 10개만
                try:
                    text = button.text or button.get_attribute('value', '')
                    button_type = button.get_attribute('type', '')
                    button_id = button.get_attribute('id', '')
                    button_class = button.get_attribute('class', '')
                    
                    print(f"   버튼 {i+1}: {text} (type={button_type}, id={button_id}, class={button_class})")
                except:
                    print(f"   버튼 {i+1}: 정보 읽기 실패")
            
            return False
            
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        return False
        
    finally:
        if driver:
            print("\n🔒 브라우저 종료...")
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    print("=" * 50)
    print("임시저장 기능 테스트")
    print("=" * 50)
    
    success = test_temp_save()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 테스트 성공!")
    else:
        print("❌ 테스트 실패!")
    print("=" * 50)
