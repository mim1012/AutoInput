#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브라우저 관리 모듈 - 자동화 감지 우회 기능 포함
"""

import os
import time
import subprocess
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

def create_browser_with_reuse(profile_id: int, reuse_existing: bool = True):
    """
    브라우저 재사용 기능이 포함된 브라우저 생성
    """
    # 고정된 프로필 경로 사용 (세션 유지)
    profile_path = f"D:\\ChromeProfiles\\Final_{profile_id}"
    
    if reuse_existing:
        # 기존 브라우저 재사용 시도 (디버깅 포트 사용)
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            # 디버깅 모드 연결 시에는 최소한의 옵션만 사용
            # 스텔스 옵션은 연결 후에 JavaScript로 적용
            
            try:
                driver = webdriver.Chrome(options=chrome_options)
                # 연결 성공 후 스텔스 옵션 적용
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("[INFO] 기존 브라우저에 연결 성공")
                return driver
            except Exception as e:
                print(f"[INFO] 기존 브라우저 연결 실패: {e}")
                print("[INFO] 새 브라우저를 시작합니다...")
        except Exception:
            pass
    
    # 새 브라우저 생성 (스텔스 브라우저 우선 시도)
    try:
        driver = create_stealth_browser()
        if driver:
            return driver
    except:
        pass
    
    # 스텔스 브라우저 실패 시 일반 브라우저 생성
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument(f"--window-position={profile_id * 950},0")
    chrome_options.add_argument("--window-size=950,900")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # 추가 안정성 옵션
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    os.makedirs(profile_path, exist_ok=True)

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"[ERROR] 브라우저 생성 실패: {e}")
        if reuse_existing:
            print(f"[INFO] 브라우저 재사용 모드에서 실패했습니다.")
            print(f"[INFO] 브라우저 재사용을 해제하고 다시 시도해주세요.")
        else:
            print(f"[INFO] 기존 브라우저가 실행 중일 수 있습니다. 브라우저를 모두 닫고 다시 시도해주세요.")
        return None

def create_browser_simple(profile_id: int):
    """간단한 브라우저 생성 (기존 브라우저와 충돌 방지)"""
    chrome_options = Options()
    
    # 고정된 프로필 경로 사용 (세션 유지)
    profile_path = f"D:\\ChromeProfiles\\Final_{profile_id}"
    
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument(f"--window-position={profile_id * 950},0")
    chrome_options.add_argument("--window-size=950,900")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 기존 브라우저와 충돌 방지를 위한 추가 옵션
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # 기존 브라우저가 실행 중이어도 새로 시작할 수 있도록
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")

    os.makedirs(profile_path, exist_ok=True)

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"[ERROR] 브라우저 생성 실패: {e}")
        print(f"[INFO] 기존 브라우저를 닫고 다시 시도해주세요.")
        return None

def start_chrome_with_debugging(profile_id: int = 1):
    """디버깅 모드로 Chrome 시작 (기존 브라우저 재사용용)"""
    import subprocess
    import time
    import os
    
    profile_path = f"D:\\ChromeProfiles\\Final_{profile_id}"
    
    # Chrome 경로 찾기
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
        "chrome.exe"  # PATH에서 찾기
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        print("[ERROR] Chrome 실행 파일을 찾을 수 없습니다")
        return False
    
    # Chrome 디버깅 모드로 시작
    chrome_cmd = [
        chrome_exe,
        f"--user-data-dir={profile_path}",
        "--remote-debugging-port=9222",
        "--no-first-run",
        "--no-default-browser-check",
        f"--window-position={profile_id * 950},0",
        "--window-size=950,900"
    ]
    
    try:
        subprocess.Popen(chrome_cmd)
        time.sleep(3)  # 브라우저 시작 대기
        print("[INFO] Chrome 디버깅 모드로 시작됨")
        return True
    except Exception as e:
        print(f"[ERROR] Chrome 시작 실패: {e}")
        return False

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


