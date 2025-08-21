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
        # JavaScript 실행으로 readonly 필드 처리
        script = f"""
        const field = document.getElementById('{field_id}');
        if (field) {{
            field.removeAttribute('readonly');
            field.value = '{value}';
            console.log('{field_id} 입력 후 값:', field.value);
            field.setAttribute('readonly', 'readonly');
            return true;
        }}
        return false;
        """
        
        result = driver.execute_script(script)
        return result
        
    except Exception as e:
        print(f"❌ {field_id} 필드 입력 실패: {e}")
        return False

def fill_fields_selenium(driver, user_data: dict) -> bool:
    """
    Selenium을 사용해서 모든 필드에 데이터 입력
    JavaScript에서 성공한 방식을 Python으로 구현
    
    Args:
        driver: Selenium WebDriver 인스턴스
        user_data: 입력할 사용자 데이터
        
    Returns:
        성공 여부
    """
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        print("🚀 Selenium으로 필드 자동 입력 시작...")
        print(f"📊 입력할 데이터: {user_data}")
        
        # 페이지의 모든 입력 필드 확인 (디버깅용)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"🔍 페이지의 모든 input 필드 수: {len(all_inputs)}")
            
            for i, inp in enumerate(all_inputs[:10]):  # 처음 10개만 출력
                field_id = inp.get_attribute('id') or 'no-id'
                field_name = inp.get_attribute('name') or 'no-name'
                field_type = inp.get_attribute('type') or 'no-type'
                field_value = inp.get_attribute('value') or 'no-value'
                print(f"  {i+1}. id={field_id}, name={field_name}, type={field_type}, value={field_value}")
        except Exception as e:
            print(f"❌ 필드 확인 실패: {e}")
        
        # 데이터 추출
        name = user_data.get('성명', '')
        phone = user_data.get('휴대전화', '')
        email = user_data.get('이메일', '')
        tel = user_data.get('전화', '')
        addr = user_data.get('주소', '')
        addr_detail = user_data.get('상세주소', '')
        contract = user_data.get('계약일자', '2025-01-15')
        birth = user_data.get('생년월일', '1990-01-01')
        delivery = user_data.get('출고예정일자', '2025-02-15')
        gender = user_data.get('성별', '남자')
        model = user_data.get('신청차종', '')
        count = user_data.get('신청대수', '1')
        
        wait = WebDriverWait(driver, 10)
        
        # 1. 기본 정보 입력
        fields = [
            ('req_nm', name, '성명'),
            ('mobile', phone, '휴대전화'),
            ('email', email, '이메일'),
            ('phone', tel, '전화'),
            ('req_cnt', count, '신청대수')
        ]
        
        for field_id, value, desc in fields:
            if value:
                try:
                    element = wait.until(EC.presence_of_element_located((By.ID, field_id)))
                    element.clear()
                    element.send_keys(value)
                    print(f"✅ {desc} 입력 완료: {value}")
                except Exception as e:
                    print(f"❌ {desc} 입력 실패: {e}")
        
        # 2. 주소 입력 (readonly 처리)
        if addr:
            success = fill_readonly_field_selenium(driver, 'addr', addr)
            if success:
                print(f"✅ 주소 입력 완료: {addr}")
        
        # 3. 상세주소 입력
        if addr_detail:
            try:
                element = driver.find_element(By.ID, 'addr_detail')
                element.clear()
                element.send_keys(addr_detail)
                print(f"✅ 상세주소 입력 완료: {addr_detail}")
            except Exception as e:
                print(f"❌ 상세주소 입력 실패: {e}")
        
        # 4. 계약일자 입력 (readonly 처리)
        if contract:
            success = fill_readonly_field_selenium(driver, 'contract_day', contract)
            if success:
                print(f"✅ 계약일자 입력 완료: {contract}")
        
        # 5. 생년월일 입력 (두 필드 모두 처리)
        if birth:
            print(f"🔍 생년월일 입력 시작: {birth}")
            
            # birth 필드 (일반)
            birth_success = False
            try:
                element = driver.find_element(By.ID, 'birth')
                print(f"✅ birth 필드 발견")
                
                # 기존 값 확인
                old_value = element.get_attribute('value')
                print(f"📊 기존 값: {old_value}")
                
                element.clear()
                element.send_keys(birth)
                
                # 입력 후 값 확인
                new_value = element.get_attribute('value')
                print(f"📊 입력 후 값: {new_value}")
                
                if new_value == birth:
                    print(f"✅ 생년월일(birth) 입력 완료: {birth}")
                    birth_success = True
                else:
                    print(f"⚠️ 생년월일(birth) 값 불일치: 입력={birth}, 실제={new_value}")
                    
            except Exception as e:
                print(f"❌ 생년월일(birth) 입력 실패: {e}")
            
            # birth1 필드 (readonly) - JavaScript 방식 사용
            print(f"🔍 birth1 필드 처리 시작")
            birth1_success = fill_readonly_field_selenium(driver, 'birth1', birth)
            if birth1_success:
                print(f"✅ 생년월일(birth1) 입력 완료: {birth}")
            else:
                print(f"❌ 생년월일(birth1) 입력 실패")
            
            # 생년월일 입력 상태 확인 및 재시도
            if not birth_success and not birth1_success:
                print(f"⚠️ 생년월일 입력 실패 - 재시도 중...")
                time.sleep(2)
                
                # 재시도: JavaScript 방식으로 강제 입력
                try:
                    js_script = f"""
                    try {{
                        // birth 필드 재시도
                        const birthField = document.getElementById('birth');
                        if (birthField) {{
                            birthField.removeAttribute('readonly');
                            birthField.value = '{birth}';
                            birthField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            birthField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            console.log('생년월일 재입력 완료 (birth):', birthField.value);
                        }}
                        
                        // birth1 필드 재시도
                        const birth1Field = document.getElementById('birth1');
                        if (birth1Field) {{
                            birth1Field.removeAttribute('readonly');
                            birth1Field.value = '{birth}';
                            birth1Field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            birth1Field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            console.log('생년월일 재입력 완료 (birth1):', birth1Field.value);
                        }}
                        
                        return true;
                    }} catch(e) {{
                        console.error('생년월일 재입력 실패:', e);
                        return false;
                    }}
                    """
                    result = driver.execute_script(js_script)
                    if result:
                        print(f"✅ 생년월일 재입력 완료 (JavaScript)")
                    else:
                        print(f"❌ 생년월일 재입력 실패")
                except Exception as e:
                    print(f"❌ 생년월일 재입력 중 오류: {e}")
        else:
            print(f"⚠️ 생년월일 데이터가 없습니다: {birth}")
        
        # 6. 출고예정일자 입력 (readonly 처리)
        if delivery:
            success = fill_readonly_field_selenium(driver, 'delivery_sch_day', delivery)
            if success:
                print(f"✅ 출고예정일자 입력 완료: {delivery}")
        
        # 7. 성별 선택
        if gender:
            print(f"🔍 성별 선택 시작: {gender}")
            
            # 성별 라디오 버튼 찾기 (여러 방법 시도)
            gender_element = None
            gender_id = 'req_sex1' if gender == '남자' else 'req_sex2'
            
            # 방법 1: ID로 찾기
            try:
                gender_element = driver.find_element(By.ID, gender_id)
                print(f"✅ 성별 요소 발견 (ID): {gender_id}")
            except Exception as e:
                print(f"❌ ID로 성별 요소 찾기 실패: {gender_id}, 오류: {e}")
            
            # 방법 2: name 속성으로 찾기
            if not gender_element:
                try:
                    gender_elements = driver.find_elements(By.NAME, "req_sex")
                    for elem in gender_elements:
                        elem_value = elem.get_attribute('value')
                        if (gender == '남자' and elem_value == 'M') or (gender == '여자' and elem_value == 'F'):
                            gender_element = elem
                            print(f"✅ 성별 요소 발견 (name): {elem_value}")
                            break
                except Exception as e:
                    print(f"❌ name으로 성별 요소 찾기 실패: {e}")
            
            # 방법 3: 라디오 버튼으로 찾기
            if not gender_element:
                try:
                    radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    print(f"🔍 발견된 라디오 버튼 수: {len(radio_buttons)}")
                    
                    for radio in radio_buttons:
                        radio_id = radio.get_attribute('id') or ''
                        radio_name = radio.get_attribute('name') or ''
                        radio_value = radio.get_attribute('value') or ''
                        print(f"  라디오: id={radio_id}, name={radio_name}, value={radio_value}")
                        
                        if 'sex' in radio_id.lower() or 'sex' in radio_name.lower():
                            if (gender == '남자' and ('1' in radio_id or 'M' in radio_value)) or \
                               (gender == '여자' and ('2' in radio_id or 'F' in radio_value)):
                                gender_element = radio
                                print(f"✅ 성별 요소 발견 (라디오): {radio_id}")
                                break
                except Exception as e:
                    print(f"❌ 라디오 버튼으로 성별 요소 찾기 실패: {e}")
            
            # 성별 선택 실행
            if gender_element:
                try:
                    # 요소 상태 확인
                    is_displayed = gender_element.is_displayed()
                    is_enabled = gender_element.is_enabled()
                    print(f"📊 요소 상태: 표시={is_displayed}, 활성화={is_enabled}")
                    
                    # 스크롤하여 요소를 화면에 표시
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gender_element)
                    time.sleep(1)
                    
                    # 클릭 시도
                    gender_element.click()
                    print(f"✅ 성별 선택 완료: {gender}")
                    
                    # 클릭 후 상태 확인
                    is_selected = gender_element.is_selected()
                    print(f"📊 클릭 후 선택 상태: {is_selected}")
                    
                except Exception as e:
                    print(f"❌ 성별 선택 실패: {e}")
                    # JavaScript로 클릭 시도
                    try:
                        script = """
                        arguments[0].click();
                        console.log('성별 선택 완료 (JavaScript)');
                        return true;
                        """
                        driver.execute_script(script, gender_element)
                        print(f"✅ 성별 선택 완료 (JavaScript): {gender}")
                    except Exception as e2:
                        print(f"❌ JavaScript 클릭도 실패: {e2}")
            else:
                print(f"❌ 성별 요소를 찾을 수 없습니다: {gender}")
        else:
            print(f"⚠️ 성별 데이터가 없습니다: {gender}")
        
        # 8. 신청유형 선택 (개인)
        try:
            select_element = Select(driver.find_element(By.ID, 'req_kind'))
            select_element.select_by_value('P')
            print("✅ 신청유형 선택 완료: 개인")
        except Exception as e:
            print(f"❌ 신청유형 선택 실패: {e}")
        
        # 9. 차종 선택
        if model:
            model_code = ''
            if 'EV3' in model and '스탠다드' in model:
                model_code = 'EV3_2WD_S'
            elif '레이EV' in model or '레이 EV' in model:
                model_code = 'RAY_4_R'
            elif 'EV3' in model and '롱레인지' in model:
                model_code = 'EV3_2WD_L17'
            
            if model_code:
                try:
                    select_element = Select(driver.find_element(By.ID, 'model_cd'))
                    select_element.select_by_value(model_code)
                    print(f"✅ 차종 선택 완료: {model} → {model_code}")
                except Exception as e:
                    print(f"❌ 차종 선택 실패: {e}")
        
        print("🎉 모든 필드 입력 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 필드 입력 중 오류 발생: {e}")
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


