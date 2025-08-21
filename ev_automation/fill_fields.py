def debug_model_selection(driver, model: str) -> dict:
    """
    차종 선택 디버깅을 위한 헬퍼 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        model: 선택하려는 차종명
        
    Returns:
        디버깅 정보 딕셔너리
    """
    debug_info = {
        'model_to_select': model,
        'available_options': [],
        'element_found': False,
        'element_id': None,
        'element_name': None,
        'element_type': None,
        'current_value': None,
        'error': None
    }
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        
        # 드롭다운 요소 찾기
        try:
            model_select = driver.find_element(By.ID, 'model_cd')
            debug_info['element_found'] = True
            debug_info['element_id'] = model_select.get_attribute('id')
            debug_info['element_name'] = model_select.get_attribute('name')
            debug_info['element_type'] = model_select.get_attribute('type')
            debug_info['current_value'] = model_select.get_attribute('value')
            
            # 사용 가능한 옵션들 확인
            select_element = Select(model_select)
            for option in select_element.options:
                option_text = option.text.strip()
                option_value = option.get_attribute('value')
                option_selected = option.is_selected()
                debug_info['available_options'].append({
                    'text': option_text,
                    'value': option_value,
                    'selected': option_selected
                })
                
        except Exception as e:
            debug_info['error'] = f"드롭다운 요소 찾기 실패: {e}"
            
            # 대안: 다른 선택자로 찾기
            try:
                # name 속성으로 찾기
                model_select = driver.find_element(By.NAME, "model_cd")
                debug_info['element_found'] = True
                debug_info['element_name'] = model_select.get_attribute('name')
                debug_info['current_value'] = model_select.get_attribute('value')
            except:
                try:
                    # CSS 선택자로 찾기
                    model_select = driver.find_element(By.CSS_SELECTOR, "select[name*='model']")
                    debug_info['element_found'] = True
                    debug_info['element_name'] = model_select.get_attribute('name')
                    debug_info['current_value'] = model_select.get_attribute('value')
                except Exception as e2:
                    debug_info['error'] = f"모든 방법으로 찾기 실패: {e2}"
        
        # 페이지의 모든 select 요소 확인
        try:
            all_selects = driver.find_elements(By.TAG_NAME, "select")
            debug_info['all_selects'] = []
            for i, select in enumerate(all_selects):
                select_info = {
                    'index': i,
                    'id': select.get_attribute('id'),
                    'name': select.get_attribute('name'),
                    'class': select.get_attribute('class'),
                    'options_count': len(select.find_elements(By.TAG_NAME, "option"))
                }
                debug_info['all_selects'].append(select_info)
        except Exception as e:
            debug_info['error'] = f"전체 select 요소 확인 실패: {e}"
            
    except Exception as e:
        debug_info['error'] = f"디버깅 중 오류: {e}"
    
    return debug_info

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
    개선된 순서와 검증 로직 포함
    
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
        
        # 입력 결과 추적
        input_results = {}
        
        # 1단계: 필수 기본 정보 (가장 안정적인 필드들부터)
        print("\n📝 1단계: 기본 정보 입력")
        basic_fields = [
            ('req_nm', name, '성명'),
            ('mobile', phone, '휴대전화'),
            ('email', email, '이메일'),
            ('phone', tel, '전화'),
            ('req_cnt', count, '신청대수')
        ]
        
        for field_id, value, desc in basic_fields:
            if value:
                try:
                    element = wait.until(EC.presence_of_element_located((By.ID, field_id)))
                    element.clear()
                    element.send_keys(value)
                    
                    # 입력 검증
                    actual_value = element.get_attribute('value')
                    if actual_value == value:
                        print(f"✅ {desc} 입력 완료: {value}")
                        input_results[desc] = True
                    else:
                        print(f"⚠️ {desc} 값 불일치: 입력={value}, 실제={actual_value}")
                        input_results[desc] = False
                except Exception as e:
                    print(f"❌ {desc} 입력 실패: {e}")
                    input_results[desc] = False
        
        # 2단계: 드롭다운 선택 (페이지 로드 후)
        print("\n📝 2단계: 드롭다운 선택")
        
        # 신청유형 선택 (개인)
        try:
            select_element = Select(driver.find_element(By.ID, 'req_kind'))
            select_element.select_by_value('P')
            print("✅ 신청유형 선택 완료: 개인")
            input_results['신청유형'] = True
        except Exception as e:
            print(f"❌ 신청유형 선택 실패: {e}")
            input_results['신청유형'] = False
        
        # 차종 선택 (강화된 로직)
        if model:
            print(f"🔍 차종 선택 시작: {model}")
            
            try:
                # 드롭다운 요소 찾기
                model_select = driver.find_element(By.ID, 'model_cd')
                select_element = Select(model_select)
                
                # 현재 사용 가능한 옵션들 확인
                available_options = []
                for option in select_element.options:
                    option_text = option.text.strip()
                    option_value = option.get_attribute('value')
                    available_options.append((option_text, option_value))
                    print(f"  📋 사용 가능한 옵션: {option_text} (값: {option_value})")
                
                # 차종 매핑 로직 (더 정확한 매칭)
                model_code = None
                model_lower = model.lower()
                
                # 1단계: 정확한 매칭
                for option_text, option_value in available_options:
                    if model_lower in option_text.lower() or option_text.lower() in model_lower:
                        model_code = option_value
                        print(f"✅ 정확한 매칭 발견: {option_text} → {option_value}")
                        break
                
                # 2단계: 부분 매칭 (정확한 매칭이 없을 경우)
                if not model_code:
                    if 'ev3' in model_lower and '스탠다드' in model_lower:
                        for option_text, option_value in available_options:
                            if 'ev3' in option_text.lower() and '스탠다드' in option_text.lower():
                                model_code = option_value
                                print(f"✅ EV3 스탠다드 매칭: {option_text} → {option_value}")
                                break
                    elif 'ev3' in model_lower and '롱레인지' in model_lower:
                        for option_text, option_value in available_options:
                            if 'ev3' in option_text.lower() and '롱레인지' in option_text.lower():
                                model_code = option_value
                                print(f"✅ EV3 롱레인지 매칭: {option_text} → {option_value}")
                                break
                    elif '레이' in model_lower:
                        for option_text, option_value in available_options:
                            if '레이' in option_text.lower():
                                model_code = option_value
                                print(f"✅ 레이EV 매칭: {option_text} → {option_value}")
                                break
                
                # 3단계: 기본값 매칭 (매칭이 없을 경우)
                if not model_code and available_options:
                    # 첫 번째 옵션을 기본값으로 선택
                    model_code = available_options[0][1]
                    print(f"⚠️ 매칭 없음, 기본값 선택: {available_options[0][0]} → {model_code}")
                
                # 차종 선택 실행
                if model_code:
                    try:
                        # 기존 선택 해제
                        select_element.deselect_all()
                        time.sleep(0.5)
                        
                        # 새 값 선택
                        select_element.select_by_value(model_code)
                        time.sleep(0.5)
                        
                        # 선택 확인
                        selected_option = select_element.first_selected_option
                        if selected_option and selected_option.get_attribute('value') == model_code:
                            print(f"✅ 차종 선택 완료: {selected_option.text} (값: {model_code})")
                            input_results['신청차종'] = True
                        else:
                            print(f"⚠️ 차종 선택 확인 실패")
                            input_results['신청차종'] = False
                            
                    except Exception as e:
                        print(f"❌ 차종 선택 실행 실패: {e}")
                        input_results['신청차종'] = False
                        
                        # JavaScript로 재시도
                        try:
                            js_script = f"""
                            try {{
                                const select = document.getElementById('model_cd');
                                if (select) {{
                                    select.value = '{model_code}';
                                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    console.log('차종 선택 완료 (JavaScript):', select.value);
                                    return true;
                                }}
                                return false;
                            }} catch(e) {{
                                console.error('차종 선택 실패:', e);
                                return false;
                            }}
                            """
                            result = driver.execute_script(js_script)
                            if result:
                                print(f"✅ 차종 선택 완료 (JavaScript): {model_code}")
                                input_results['신청차종'] = True
                            else:
                                print(f"❌ JavaScript 차종 선택도 실패")
                                input_results['신청차종'] = False
                        except Exception as e2:
                            print(f"❌ JavaScript 차종 선택 실패: {e2}")
                            input_results['신청차종'] = False
                else:
                    print(f"❌ 차종 매칭 실패: {model}")
                    input_results['신청차종'] = False
                    
            except Exception as e:
                print(f"❌ 차종 선택 중 오류: {e}")
                input_results['신청차종'] = False
                
                # 디버깅 정보 출력
                print("🔍 차종 선택 디버깅 정보:")
                debug_info = debug_model_selection(driver, model)
                print(f"  선택하려는 차종: {debug_info['model_to_select']}")
                print(f"  요소 발견: {debug_info['element_found']}")
                if debug_info['element_found']:
                    print(f"  요소 ID: {debug_info['element_id']}")
                    print(f"  요소 Name: {debug_info['element_name']}")
                    print(f"  현재 값: {debug_info['current_value']}")
                
                if debug_info['available_options']:
                    print("  사용 가능한 옵션들:")
                    for option in debug_info['available_options']:
                        status = "✅ 선택됨" if option['selected'] else "  "
                        print(f"    {status} {option['text']} (값: {option['value']})")
                
                if debug_info.get('all_selects'):
                    print("  페이지의 모든 select 요소:")
                    for select in debug_info['all_selects']:
                        print(f"    {select['index']}. id={select['id']}, name={select['name']}, 옵션수={select['options_count']}")
                
                if debug_info['error']:
                    print(f"  오류: {debug_info['error']}")
        
        # 3단계: readonly 필드들 (JavaScript 처리)
        print("\n📝 3단계: readonly 필드 처리")
        
        readonly_fields = [
            ('addr', addr, '주소'),
            ('contract_day', contract, '계약일자'),
            ('delivery_sch_day', delivery, '출고예정일자')
        ]
        
        for field_id, value, desc in readonly_fields:
            if value:
                success = fill_readonly_field_selenium(driver, field_id, value)
                if success:
                    print(f"✅ {desc} 입력 완료: {value}")
                    input_results[desc] = True
                else:
                    print(f"❌ {desc} 입력 실패")
                    input_results[desc] = False
        
        # 4단계: 상세주소 (일반 입력)
        if addr_detail:
            try:
                element = driver.find_element(By.ID, 'addr_detail')
                element.clear()
                element.send_keys(addr_detail)
                print(f"✅ 상세주소 입력 완료: {addr_detail}")
                input_results['상세주소'] = True
            except Exception as e:
                print(f"❌ 상세주소 입력 실패: {e}")
                input_results['상세주소'] = False
        
        # 5단계: 생년월일 (가장 복잡한 필드)
        print("\n📝 5단계: 생년월일 처리")
        if birth:
            birth_success = False
            
            # birth 필드 (일반)
            try:
                element = driver.find_element(By.ID, 'birth')
                element.clear()
                element.send_keys(birth)
                actual_value = element.get_attribute('value')
                if actual_value == birth:
                    print(f"✅ 생년월일(birth) 입력 완료: {birth}")
                    birth_success = True
                else:
                    print(f"⚠️ 생년월일(birth) 값 불일치: 입력={birth}, 실제={actual_value}")
            except Exception as e:
                print(f"❌ 생년월일(birth) 입력 실패: {e}")
            
            # birth1 필드 (readonly)
            birth1_success = fill_readonly_field_selenium(driver, 'birth1', birth)
            if birth1_success:
                print(f"✅ 생년월일(birth1) 입력 완료: {birth}")
                birth_success = birth_success or True
            
            input_results['생년월일'] = birth_success
            
            # 재시도 로직
            if not birth_success:
                print("🔄 생년월일 재시도 중...")
                time.sleep(2)
                try:
                    js_script = f"""
                    try {{
                        const birthField = document.getElementById('birth');
                        const birth1Field = document.getElementById('birth1');
                        
                        if (birthField) {{
                            birthField.value = '{birth}';
                            birthField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            birthField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                        
                        if (birth1Field) {{
                            birth1Field.removeAttribute('readonly');
                            birth1Field.value = '{birth}';
                            birth1Field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            birth1Field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            birth1Field.setAttribute('readonly', 'readonly');
                        }}
                        
                        return true;
                    }} catch(e) {{
                        console.error('생년월일 재입력 실패:', e);
                        return false;
                    }}
                    """
                    result = driver.execute_script(js_script)
                    if result:
                        print(f"✅ 생년월일 재입력 완료")
                        input_results['생년월일'] = True
                except Exception as e:
                    print(f"❌ 생년월일 재입력 실패: {e}")
        
        # 6단계: 성별 선택 (마지막에 처리)
        print("\n📝 6단계: 성별 선택")
        if gender:
            gender_success = False
            gender_id = 'req_sex1' if gender == '남자' else 'req_sex2'
            
            try:
                # 요소 찾기
                gender_element = None
                
                # 방법 1: ID로 찾기
                try:
                    gender_element = driver.find_element(By.ID, gender_id)
                except:
                    pass
                
                # 방법 2: name 속성으로 찾기
                if not gender_element:
                    try:
                        gender_elements = driver.find_elements(By.NAME, "req_sex")
                        for elem in gender_elements:
                            elem_value = elem.get_attribute('value')
                            if (gender == '남자' and elem_value == 'M') or (gender == '여자' and elem_value == 'F'):
                                gender_element = elem
                                break
                    except:
                        pass
                
                # 방법 3: 라디오 버튼으로 찾기
                if not gender_element:
                    try:
                        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                        for radio in radio_buttons:
                            radio_id = radio.get_attribute('id') or ''
                            if 'sex' in radio_id.lower():
                                if (gender == '남자' and '1' in radio_id) or (gender == '여자' and '2' in radio_id):
                                    gender_element = radio
                                    break
                    except:
                        pass
                
                # 성별 선택 실행
                if gender_element:
                    # 스크롤하여 요소를 화면에 표시
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gender_element)
                    time.sleep(1)
                    
                    # 클릭 시도
                    try:
                        gender_element.click()
                        gender_success = True
                    except:
                        # JavaScript로 클릭 시도
                        driver.execute_script("arguments[0].click();", gender_element)
                        gender_success = True
                    
                    if gender_success:
                        print(f"✅ 성별 선택 완료: {gender}")
                        input_results['성별'] = True
                    else:
                        print(f"❌ 성별 선택 실패: {gender}")
                        input_results['성별'] = False
                else:
                    print(f"❌ 성별 요소를 찾을 수 없습니다: {gender}")
                    input_results['성별'] = False
                    
            except Exception as e:
                print(f"❌ 성별 선택 중 오류: {e}")
                input_results['성별'] = False
        
        # 7단계: 최종 검증
        print("\n📝 7단계: 입력 결과 검증")
        print("=" * 50)
        success_count = 0
        total_count = len(input_results)
        
        for field_name, success in input_results.items():
            status = "✅ 성공" if success else "❌ 실패"
            print(f"{field_name}: {status}")
            if success:
                success_count += 1
        
        print("=" * 50)
        print(f"📊 입력 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        if success_count >= total_count * 0.8:  # 80% 이상 성공
            print("🎉 필드 입력이 성공적으로 완료되었습니다!")
            return True
        else:
            print("⚠️ 일부 필드 입력에 실패했습니다. 수동 확인이 필요합니다.")
            return False
        
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


