import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_browser(profile_id: int, reuse_existing: bool = True):
    """Chrome 브라우저 생성 (기존 세션 유지)"""
    
    # 고정된 프로필 경로 사용 (세션 유지)
    profile_path = f"D:\\ChromeProfiles\\Final_{profile_id}"
    
    if reuse_existing:
        # 기존 브라우저 재사용 시도 (디버깅 포트 사용)
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            try:
                driver = webdriver.Chrome(options=chrome_options)
                print("[INFO] 기존 브라우저에 연결 성공")
                return driver
            except Exception as e:
                print(f"[INFO] 기존 브라우저 연결 실패: {e}")
                print("[INFO] 새 브라우저를 시작합니다...")
        except Exception:
            pass
    
    # 새 브라우저 생성
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


