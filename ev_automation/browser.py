#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브라우저 관리 모듈 - 자동화 감지 우회 기능 포함
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def create_stealth_browser():
    """
    자동화 감지를 우회하는 스텔스 브라우저 생성
    """
    try:
        # Undetected ChromeDriver 사용 시도
        try:
            import undetected_chromedriver as uc
            print("🔍 Undetected ChromeDriver 사용")
            
            options = uc.ChromeOptions()
            options.add_argument("--user-data-dir=D:\\ChromeProfiles\\EV")
            options.add_argument("--window-size=1000,900")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # 추가 스텔스 옵션
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = uc.Chrome(options=options)
            
            # JavaScript로 자동화 감지 제거
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Undetected ChromeDriver 생성 완료")
            return driver
            
        except ImportError:
            print("⚠️ Undetected ChromeDriver 없음, 일반 ChromeDriver 사용")
            return create_normal_browser()
            
    except Exception as e:
        print(f"❌ 스텔스 브라우저 생성 실패: {e}")
        return create_normal_browser()

def create_normal_browser():
    """
    일반 ChromeDriver 생성 (기존 방식)
    """
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=D:\\ChromeProfiles\\EV")
    chrome_options.add_argument("--window-size=1000,900")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 자동화 감지 우회를 위한 추가 옵션
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    os.makedirs("D:\\ChromeProfiles\\EV", exist_ok=True)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # JavaScript로 자동화 감지 제거
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("✅ 일반 ChromeDriver 생성 완료")
    return driver

def wait_for_page_load(driver, timeout=30):
    """
    페이지 로딩 완료 대기
    """
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # DOM 로딩 완료 대기
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # jQuery 로딩 완료 대기 (있는 경우)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return typeof jQuery !== 'undefined' && jQuery.active === 0")
            )
        except:
            pass  # jQuery가 없는 경우 무시
        
        print("✅ 페이지 로딩 완료")
        return True
        
    except Exception as e:
        print(f"⚠️ 페이지 로딩 대기 실패: {e}")
        return False

def simulate_human_behavior(driver):
    """
    인간과 유사한 행동 시뮬레이션
    """
    import random
    
    # 랜덤 스크롤
    scroll_amount = random.randint(100, 300)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(random.uniform(0.5, 1.5))
    
    # 랜덤 마우스 움직임 (시뮬레이션)
    driver.execute_script("""
        // 마우스 움직임 이벤트 시뮬레이션
        const event = new MouseEvent('mousemove', {
            'view': window,
            'bubbles': true,
            'cancelable': true,
            'clientX': Math.random() * window.innerWidth,
            'clientY': Math.random() * window.innerHeight
        });
        document.dispatchEvent(event);
    """)
    
    time.sleep(random.uniform(0.3, 0.8))

def safe_click_element(driver, element, description=""):
    """
    안전한 요소 클릭 (자동화 감지 우회)
    """
    try:
        # 요소가 화면에 보이도록 스크롤
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.5)
        
        # 인간과 유사한 행동 시뮬레이션
        simulate_human_behavior(driver)
        
        # 클릭 시도
        try:
            element.click()
            print(f"✅ {description} 클릭 성공")
            return True
        except:
            # JavaScript로 클릭 시도
            driver.execute_script("arguments[0].click();", element)
            print(f"✅ {description} 클릭 성공 (JavaScript)")
            return True
            
    except Exception as e:
        print(f"❌ {description} 클릭 실패: {e}")
        return False

def safe_send_keys(driver, element, text, description=""):
    """
    안전한 텍스트 입력 (자동화 감지 우회)
    """
    try:
        # 요소 포커스
        element.click()
        time.sleep(0.2)
        
        # 기존 내용 삭제
        element.clear()
        time.sleep(0.1)
        
        # 인간과 유사한 타이핑 시뮬레이션
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # 랜덤 딜레이
        
        print(f"✅ {description} 입력 완료: {text}")
        return True
        
    except Exception as e:
        print(f"❌ {description} 입력 실패: {e}")
        return False


