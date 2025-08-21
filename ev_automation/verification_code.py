import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_code_smart(driver):
    js = """
    const found=[];
    const rows=document.querySelectorAll('table tr');
    rows.forEach((row,idx)=>{
      const cells=row.querySelectorAll('td,th');
      if(cells.length>=2){
        const t=cells[1].textContent.trim();
        if(/^[A-Za-z0-9]{6,15}$/.test(t) && t!=='123' && t!=='321'){ found.push(t); }
      }
    });
    const spans=document.querySelectorAll('span');
    spans.forEach(s=>{ const t=(s.textContent||'').trim(); if(/^[A-Za-z0-9]{6,15}$/.test(t) && t!=='123' && t!=='321'){ found.push(t); } });
    return found[0]||null;
    """
    try:
        return driver.execute_script(js)
    except Exception:
        return None


def input_reversed_code(driver, code: str) -> bool:
    """확인코드 역순 입력 및 확인 버튼 클릭"""
    try:
        rev = code[::-1]
        print(f"[REVERSE] 코드 변환: {code} → {rev}")
        
        js = f"""
        console.log('=== 확인코드 역순 입력 ===');
        console.log('원본: {code}');
        console.log('역순: {rev}');
        
        // 입력 필드 찾기 (여러 방법)
        let codeInput = document.getElementById('randeomChk') ||
                       document.querySelector('input[type="text"]') ||
                       document.querySelector('input[type="password"]') ||
                       document.querySelector('input[placeholder*="코드"]') ||
                       document.querySelector('input[title*="코드"]');
        
        if (codeInput) {{
            codeInput.focus();
            codeInput.select();
            codeInput.value = '';
            codeInput.value = '{rev}';
            
            // 여러 이벤트 발생
            codeInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            codeInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            codeInput.dispatchEvent(new Event('keyup', {{ bubbles: true }}));
            
            console.log('✅ 확인코드 입력 완료:', codeInput.value);
            
            // 제출 버튼 찾기 및 클릭 (2초 후)
            setTimeout(() => {{
                // 정확한 확인 버튼 찾기 (goCompare 버튼 우선)
                const confirmButton = document.querySelector('button[onclick*="goCompare"]') ||
                                    document.querySelector('button.btn-blue[onclick*="goCompare"]') ||
                                    document.querySelector('button[type="button"][onclick*="goCompare"]') ||
                                    document.querySelector('button[type="submit"]') ||
                                    Array.from(document.querySelectorAll('button')).find(btn => 
                                        btn.textContent.includes('확인') || 
                                        btn.textContent.includes('제출') ||
                                        btn.textContent.includes('OK')
                                    );
                
                if (confirmButton) {{
                    console.log('확인 버튼 발견:', confirmButton.outerHTML);
                    console.log('확인 버튼 클릭:', confirmButton.textContent);
                    confirmButton.scrollIntoView({{block: 'center'}});
                    confirmButton.click();
                    window.codeSubmitted = true;
                }} else {{
                    console.log('❌ 확인 버튼을 찾을 수 없음');
                    
                    // 모든 버튼 출력 (디버깅용)
                    const allButtons = document.querySelectorAll('button');
                    console.log('페이지의 모든 버튼:');
                    allButtons.forEach((btn, i) => {{
                        console.log(`  ${{i}}: "${{btn.textContent}}" onclick="${{btn.onclick}}" class="${{btn.className}}"`);
                    }});
                }}
            }}, 2000);
            
            return true;
        }} else {{
            console.log('❌ 코드 입력 필드를 찾을 수 없음');
            return false;
        }}
        """
        
        result = driver.execute_script(js)
        
        if result:
            # 제출 완료 대기 (최대 10초)
            print(f"[WAIT] 확인 버튼 클릭 후 결과 대기 중...")
            for i in range(10):
                try:
                    submitted = driver.execute_script("return window.codeSubmitted === true;")
                    if submitted:
                        print(f"[SUCCESS] 확인코드 제출 완료")
                        time.sleep(2)  # 추가 대기
                        return True
                except:
                    pass
                time.sleep(1)
            
            print(f"[TIMEOUT] 제출 완료 확인 시간 초과")
            time.sleep(2)  # 기본 대기
            return True  # 일단 성공으로 처리
        else:
            print(f"[ERROR] 확인코드 입력 실패")
            return False
            
    except Exception as e:
        print(f"[ERROR] 역순 입력 실패: {e}")
        return False


