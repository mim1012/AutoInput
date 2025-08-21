import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
import importlib
import sys
from ev_automation.browser import create_stealth_browser, create_normal_browser, create_browser_with_reuse, create_browser_simple, start_chrome_with_debugging
from ev_automation.excel_loader import load_users_from_excel
from ev_automation.fill_fields import build_fill_script, fill_fields_selenium_human_like
from ev_automation.file_attachment import attach_pdf_files, find_and_click_submit_button, handle_final_popup
from selenium.webdriver.common.by import By

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("전기차 신청서 자동화 시스템")
        self.root.geometry("600x550")  # 높이를 조금 늘림
        
        # 변수들
        self.excel_path = tk.StringVar()
        self.pdf_folder_path = tk.StringVar()
        self.selected_users = []
        self.automation_running = False
        self.driver = None
        self.session_maintained = False  # 세션 유지 상태
        self.browser_reuse_started = False  # 브라우저 재사용 모드 시작 여부
        
        self.setup_ui()
    
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="전기차 신청서 자동화 시스템", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 엑셀 파일 선택
        ttk.Label(main_frame, text="엑셀 파일:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.excel_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="찾아보기", command=self.browse_excel).grid(row=1, column=2)
        
        # PDF 폴더 선택
        ttk.Label(main_frame, text="PDF 폴더:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.pdf_folder_path, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(main_frame, text="찾아보기", command=self.browse_pdf_folder).grid(row=2, column=2)
        
        # 사용자 목록
        ttk.Label(main_frame, text="처리할 사용자 선택:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        # 사용자 리스트박스 (멀티 선택)
        self.user_listbox = tk.Listbox(main_frame, height=10, selectmode=tk.MULTIPLE)
        self.user_listbox.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.user_listbox.yview)
        scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S))
        self.user_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.load_button = ttk.Button(button_frame, text="사용자 목록 로드", command=self.load_users)
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="자동화 시작", command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 준비 완료 버튼 (처음에는 숨김)
        self.ready_button = ttk.Button(button_frame, text="준비 완료", command=self.ready_for_automation, state=tk.DISABLED)
        self.ready_button.pack(side=tk.LEFT, padx=5)
        
        # 세션 유지 체크박스
        self.session_var = tk.BooleanVar()
        session_check = ttk.Checkbutton(button_frame, text="세션 유지", variable=self.session_var)
        session_check.pack(side=tk.LEFT, padx=5)
        
        # 브라우저 재사용 체크박스
        self.reuse_browser_var = tk.BooleanVar(value=True)
        reuse_check = ttk.Checkbutton(button_frame, text="브라우저 재사용", variable=self.reuse_browser_var)
        reuse_check.pack(side=tk.LEFT, padx=5)
        
        # 브라우저 재사용 시작 버튼
        self.start_reuse_button = ttk.Button(button_frame, text="브라우저 재사용 시작", command=self.start_browser_reuse)
        self.start_reuse_button.pack(side=tk.LEFT, padx=5)
        
        # 개발자 도구 버튼 (새로 추가)
        dev_frame = ttk.Frame(main_frame)
        dev_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(dev_frame, text="🔄 코드 리로드", command=self.reload_code, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(dev_frame, text="📁 파일 새로고침", command=self.refresh_files).pack(side=tk.LEFT, padx=5)
        
        # 진행 상황
        ttk.Label(main_frame, text="진행 상황:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        
        self.progress_var = tk.StringVar(value="대기 중...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=8, column=0, columnspan=3, sticky=tk.W)
        
        # 로그 출력
        ttk.Label(main_frame, text="로그:").grid(row=9, column=0, sticky=tk.W, pady=(20, 5))
        
        self.log_text = tk.Text(main_frame, height=8, width=70)
        self.log_text.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 로그 스크롤바
        log_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=10, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 개발자 모드 안내
        self.log_message("🔧 개발자 모드: 코드 변경 후 '🔄 코드 리로드' 버튼을 사용하세요")
    
    def reload_code(self):
        """코드 리로드 기능 (개발 중 사용)"""
        try:
            self.log_message("🔄 코드 리로드 중...")
            
            # ev_automation 모듈들 리로드
            modules_to_reload = [
                'ev_automation.browser',
                'ev_automation.excel_loader', 
                'ev_automation.fill_fields',
                'ev_automation.temp_save',
                'ev_automation.file_attachment'
            ]
            
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    self.log_message(f"✅ {module_name} 리로드 완료")
            
            self.log_message("🎉 모든 모듈 리로드 완료!")
            self.log_message("💡 이제 수정된 코드가 적용되었습니다")
            
        except Exception as e:
            self.log_message(f"❌ 코드 리로드 실패: {e}")
            self.log_message("💡 GUI를 완전히 재시작하는 것을 권장합니다")
    
    def refresh_files(self):
        """파일 목록 새로고침"""
        try:
            self.log_message("📁 파일 목록 새로고침 중...")
            
            # 엑셀 파일 경로가 있으면 다시 로드
            if self.excel_path.get():
                self.load_users()
            
            self.log_message("✅ 파일 목록 새로고침 완료")
            
        except Exception as e:
            self.log_message(f"❌ 파일 새로고침 실패: {e}")
    
    def browse_excel(self):
        filename = filedialog.askopenfilename(
            title="엑셀 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_path.set(filename)
            self.log_message(f"엑셀 파일 선택: {filename}")
    
    def browse_pdf_folder(self):
        folder = filedialog.askdirectory(title="PDF 폴더 선택")
        if folder:
            self.pdf_folder_path.set(folder)
            self.log_message(f"PDF 폴더 선택: {folder}")
            self.log_message("📋 PDF 파일 안내:")
            self.log_message("   - 하나의 PDF 파일을 4개 항목에 모두 사용합니다")
            self.log_message("   - 파일명 예시: 장원.pdf, 전문수.pdf")
            self.log_message("   - 사용자명으로 시작하는 PDF 파일을 자동으로 찾습니다")
    
    def load_users(self):
        if not self.excel_path.get():
            messagebox.showerror("오류", "엑셀 파일을 선택해주세요.")
            return
        
        try:
            # 사용자 목록 로드
            self.users_data = load_users_from_excel(self.excel_path.get())
            
            # 리스트박스 초기화
            self.user_listbox.delete(0, tk.END)
            
            # 사용자 목록 추가
            for i, user in enumerate(self.users_data):
                user_info = f"{i+1}. {user['성명']} - {user['휴대전화']} - {user.get('우선순위', '일반')}"
                self.user_listbox.insert(tk.END, user_info)
            
            self.log_message(f"총 {len(self.users_data)}명의 사용자 로드 완료")
            
        except Exception as e:
            messagebox.showerror("오류", f"사용자 목록 로드 실패: {str(e)}")
            self.log_message(f"오류: {str(e)}")
    
    def start_automation(self):
        if not self.excel_path.get():
            messagebox.showerror("오류", "엑셀 파일을 선택해주세요.")
            return
        
        if not self.pdf_folder_path.get():
            messagebox.showerror("오류", "PDF 폴더를 선택해주세요.")
            return
        
        # 선택된 사용자 확인
        selected_indices = self.user_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("오류", "처리할 사용자를 선택해주세요.")
            return
        
        # 브라우저 재사용 모드가 시작되었는지 확인
        if self.browser_reuse_started and not self.reuse_browser_var.get():
            self.log_message("🔧 브라우저 재사용 모드가 시작되었으므로 자동으로 활성화합니다")
            self.reuse_browser_var.set(True)
        
        # 세션 유지 확인
        if self.session_var.get():
            self.log_message("🔐 세션 유지 모드: 로그인/본인인증 완료 후 신청서 페이지에서 시작")
        else:
            self.log_message("🆕 새 세션 모드: 홈페이지부터 시작")
        
        # 자동화 시작
        self.automation_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.DISABLED)
        
        # 별도 스레드에서 자동화 실행
        self.automation_thread = threading.Thread(target=self.run_automation, args=(selected_indices,))
        self.automation_thread.daemon = True
        self.automation_thread.start()
    
    def run_automation(self, selected_indices):
        try:
            self.log_message("🚀 자동화 시작...")
            self.progress_var.set("브라우저 생성 중...")
            
            # 브라우저 생성 (재사용 옵션 적용)
            reuse_browser = self.reuse_browser_var.get()
            self.log_message(f"🔧 브라우저 재사용: {'활성화' if reuse_browser else '비활성화'}")
            
            # 브라우저 생성 (재사용 옵션 적용)
            if reuse_browser:
                # 브라우저 재사용 시도 (기존 브라우저에 연결만)
                self.log_message("🔧 기존 브라우저 연결 시도 중...")
                self.driver = create_browser_with_reuse(1, reuse_existing=True)
                if not self.driver:
                    self.log_message("❌ 기존 브라우저 연결 실패")
                    self.log_message("💡 '브라우저 재사용 시작' 버튼을 먼저 클릭하세요")
                    return
                else:
                    self.log_message("✅ 기존 브라우저 연결 성공")
            else:
                # 새 브라우저 생성 (스텔스 브라우저 우선 시도)
                self.log_message("🔍 스텔스 브라우저 생성 중...")
                self.driver = create_stealth_browser()
                if not self.driver:
                    self.log_message("❌ 스텔스 브라우저 생성 실패")
                    self.log_message("💡 일반 브라우저로 재시도...")
                    self.driver = create_normal_browser()
                    if not self.driver:
                        self.log_message("❌ 브라우저 생성 실패")
                        return
            
            # 브라우저 재사용 여부에 따른 안내 메시지
            if reuse_browser:
                self.log_message("🔧 브라우저 재사용 모드: 기존 브라우저에 연결됨")
                
                # 현재 페이지 상태 확인
                try:
                    current_url = self.driver.current_url
                    self.log_message(f"📍 현재 페이지: {current_url}")
                    
                    if 'sellerApplyform' in current_url:
                        self.log_message("✅ 이미 신청서 페이지에 있습니다!")
                        self.log_message("📋 바로 '준비 완료' 버튼을 클릭하세요")
                        # 신청서 페이지에 있으면 바로 준비 완료 버튼 활성화
                        self.root.after(0, lambda: self.ready_button.config(state=tk.NORMAL))
                        self.progress_var.set("신청서 페이지 감지됨 - '준비 완료' 버튼 클릭 가능")
                        return
                    elif 'login' in current_url.lower() or 'portal' in current_url:
                        self.log_message("📋 현재 상태:")
                        self.log_message("   1. 로그인이 필요합니다")
                        self.log_message("   2. 로그인 후 신청서 페이지로 이동하세요")
                        self.log_message("   3. 신청서 페이지에서 '준비 완료' 버튼 클릭")
                    else:
                        self.log_message("📋 현재 브라우저 상태를 확인하고:")
                        self.log_message("   1. 이미 로그인되어 있다면 → 신청서 페이지로 이동")
                        self.log_message("   2. 로그인이 필요하다면 → 로그인 후 신청서 페이지로 이동")
                        self.log_message("   3. 신청서 페이지에서 '준비 완료' 버튼 클릭")
                except Exception as e:
                    self.log_message(f"⚠️ 페이지 상태 확인 실패: {e}")
                    self.log_message("📋 신청서 페이지로 이동 후 '준비 완료' 버튼을 클릭하세요")
                
                # 브라우저 재사용 모드에서는 준비 완료 버튼 활성화
                self.root.after(0, lambda: self.ready_button.config(state=tk.NORMAL))
                self.progress_var.set("기존 브라우저 연결됨 - 신청서 페이지로 이동 후 '준비 완료' 클릭")
                
            else:
                # 새 브라우저 생성한 경우
                if not self.session_var.get():
                    self.log_message("🌐 홈페이지로 이동 중...")
                    self.driver.get("https://www.ev.or.kr/portal/apply")
                    time.sleep(3)
                    self.log_message("✅ 홈페이지 로드 완료")
                    self.log_message("📋 다음 단계를 진행해주세요:")
                    self.log_message("   1. 로그인")
                    self.log_message("   2. 본인인증")
                    self.log_message("   3. 신청서 페이지로 이동")
                    self.log_message("   4. '준비 완료' 버튼 클릭")
                else:
                    self.log_message("🔐 세션 유지 모드: 신청서 페이지에서 시작")
                    self.log_message("📋 신청서 페이지로 이동 후 '준비 완료' 버튼을 클릭해주세요")
                
                # 새 브라우저 모드에서도 준비 완료 버튼 활성화
                self.root.after(0, lambda: self.ready_button.config(state=tk.NORMAL))
                self.progress_var.set("수동 작업 완료 후 '준비 완료' 버튼 클릭")
            
            self.log_message("✅ 브라우저 생성 완료")
            
        except Exception as e:
            self.log_message(f"❌ 자동화 오류: {str(e)}")
            messagebox.showerror("오류", f"자동화 중 오류가 발생했습니다: {str(e)}")
    
    def ready_for_automation(self):
        """준비 완료 버튼 클릭 시 호출"""
        try:
            # 선택된 사용자들 처리 시작
            selected_indices = self.user_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("오류", "처리할 사용자를 선택해주세요.")
                return
            
            # 준비 완료 버튼 비활성화
            self.ready_button.config(state=tk.DISABLED)
            
            # 자동화 처리 시작
            self.process_selected_users()
            
        except Exception as e:
            self.log_message(f"❌ 준비 완료 처리 오류: {str(e)}")
            messagebox.showerror("오류", f"준비 완료 처리 중 오류가 발생했습니다: {str(e)}")
    
    def show_ready_dialog(self):
        """사용자에게 준비 완료 확인 요청"""
        result = messagebox.askyesno("준비 완료", 
                                   "로그인과 신청서 페이지 이동이 완료되었습니까?\n\n"
                                   "확인을 누르면 자동화가 시작됩니다.")
        if result:
            self.root.after(0, lambda: self.process_selected_users())
        else:
            self.log_message("⏸️ 사용자가 준비를 취소했습니다.")
            self.stop_automation()
    
    def process_selected_users(self):
        """선택된 사용자들 처리"""
        try:
            selected_indices = self.user_listbox.curselection()
            selected_users = [self.users_data[i] for i in selected_indices]
            
            self.log_message(f"📝 {len(selected_users)}명의 사용자 처리 시작")
            
            for i, user in enumerate(selected_users):
                if not self.automation_running:
                    break
                
                self.progress_var.set(f"처리 중: {user['성명']} ({i+1}/{len(selected_users)})")
                self.log_message(f"\n{'='*50}")
                self.log_message(f"👤 사용자 처리 시작: {user['성명']}")
                
                # 신청서 페이지 감지 (URL 또는 필드 존재)
                try:
                    on_form_page = False
                    try:
                        current_url = (self.driver.current_url or '').lower()
                        if any(s in current_url for s in ['sellerapplyform', 'applyform', 'apply']):
                            on_form_page = True
                    except Exception:
                        pass
                    if not on_form_page:
                        try:
                            _probe = self.driver.find_element(By.ID, 'req_nm')
                            on_form_page = _probe is not None
                        except Exception:
                            on_form_page = False
                    if on_form_page:
                        self.log_message("✅ 신청서 페이지 감지됨")
                    else:
                        cu = ''
                        try:
                            cu = self.driver.current_url
                        except Exception:
                            pass
                        self.log_message(f"❌ 신청서 페이지가 아닙니다: {cu}")
                        continue
                except Exception as e:
                    self.log_message(f"❌ 페이지 감지 실패: {e}")
                    continue
                
                # 1단계: 신청서 필드 자동 입력
                self.log_message("📝 1단계: 신청서 필드 입력 중...")
                try:
                    # Fast 모드 인적 입력
                    success = fill_fields_selenium_human_like(self.driver, user, fast_mode=True)
                    if not success:
                        self.log_message(f"⚠️ {user.get('성명', '')} 필드 입력 일부 실패 (계속 진행)")
                    
                    # 생년월일 필드 누락 확인 및 재입력
                    self.log_message("🔍 생년월일 필드 누락 확인 중...")
                    time.sleep(2)
                    
                    try:
                        # 생년월일 필드 상태 확인
                        birth_element = self.driver.find_element(By.ID, 'birth')
                        birth_value = birth_element.get_attribute('value')
                        birth1_element = self.driver.find_element(By.ID, 'birth1')
                        birth1_value = birth1_element.get_attribute('value')
                        
                        expected_birth = user.get('생년월일', '')
                        self.log_message(f"📊 생년월일 필드 상태:")
                        self.log_message(f"   - birth: {birth_value}")
                        self.log_message(f"   - birth1: {birth1_value}")
                        self.log_message(f"   - 예상값: {expected_birth}")
                        
                        # 누락된 경우 재입력
                        if not birth_value and not birth1_value:
                            self.log_message("⚠️ 생년월일 필드 누락 - 재입력 시도...")
                            
                            # JavaScript로 강제 입력
                            js_script = f"""
                            try {{
                                const birthField = document.getElementById('birth');
                                const birth1Field = document.getElementById('birth1');
                                
                                if (birthField) {{
                                    birthField.removeAttribute('readonly');
                                    birthField.value = '{expected_birth}';
                                    birthField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    birthField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                }}
                                
                                if (birth1Field) {{
                                    birth1Field.removeAttribute('readonly');
                                    birth1Field.value = '{expected_birth}';
                                    birth1Field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    birth1Field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                }}
                                
                                return true;
                            }} catch(e) {{
                                console.error('생년월일 재입력 실패:', e);
                                return false;
                            }}
                            """
                            result = self.driver.execute_script(js_script)
                            if result:
                                self.log_message("✅ 생년월일 재입력 완료")
                            else:
                                self.log_message("❌ 생년월일 재입력 실패")
                        else:
                            self.log_message("✅ 생년월일 필드 정상 입력됨")
                            
                    except Exception as e:
                        self.log_message(f"⚠️ 생년월일 필드 확인 중 오류: {e}")
                    
                    time.sleep(3)
                    self.log_message("✅ 신청서 필드 입력 완료")
                except Exception as e:
                    self.log_message(f"❌ 필드 입력 실패: {e}")
                    continue
                
<<<<<<< HEAD
                # 2단계: 임시저장 (개선된 버전)
                self.log_message("💾 2단계: 임시저장 진행 중...")
                if force_temp_save_with_retry(self.driver, max_retries=3):
                    self.log_message("✅ 임시저장 완료")
                else:
                    self.log_message("❌ 임시저장 실패")
                    continue
=======
                # 2단계: 필드 입력 완료 (임시저장부터는 수동 처리)
                self.log_message("✅ 필드 입력 완료!")
                self.log_message("📋 다음 단계는 수동으로 진행해주세요:")
                self.log_message("   1. 임시저장")
                self.log_message("   2. PDF 파일 첨부")
                self.log_message("   3. 지원 신청 버튼 클릭")
                self.log_message("   4. 최종 팝업 처리")
>>>>>>> 876adf0 (필드 입력까지만 자동화하도록 수정 - 임시저장부터는 수동 처리)
                
                self.log_message(f"🎉 {user['성명']} 필드 입력 완료!")
                
                # 다음 사용자 처리 전 대기
                if i < len(selected_users) - 1:
                    self.log_message("⏳ 다음 사용자 처리 전 3초 대기...")
                    time.sleep(3)
                
                # 다음 사용자 처리 전 대기
                if i < len(selected_users) - 1:
                    self.log_message("⏳ 다음 사용자 처리 전 3초 대기...")
                    time.sleep(3)
            
            if self.automation_running:
                self.progress_var.set("자동화 완료")
                self.log_message("\n🎊 모든 자동화 작업이 완료되었습니다!")
                messagebox.showinfo("완료", "자동화가 성공적으로 완료되었습니다.")
            
        except Exception as e:
            self.log_message(f"❌ 사용자 처리 중 오류: {str(e)}")
            messagebox.showerror("오류", f"사용자 처리 중 오류가 발생했습니다: {str(e)}")
        
        finally:
            # 버튼 상태 복원
            self.automation_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.load_button.config(state=tk.NORMAL)
            self.ready_button.config(state=tk.DISABLED)
    
    def stop_automation(self):
        self.automation_running = False
        self.progress_var.set("중지됨")
        self.log_message("⏹️ 자동화가 중지되었습니다.")
        
        # 버튼 상태 복원
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.NORMAL)
        self.ready_button.config(state=tk.DISABLED)
        
        # 브라우저 정리
        if self.driver:
            try:
                self.driver.quit()
                self.log_message("🔒 브라우저가 종료되었습니다.")
            except:
                pass
            self.driver = None
    
    def start_browser_reuse(self):
        """브라우저 재사용 모드 시작"""
        try:
            self.log_message("🔧 브라우저 재사용 모드 시작...")
            self.log_message("📋 다음 단계를 진행해주세요:")
            self.log_message("   1. Chrome이 디버깅 모드로 시작됩니다")
            self.log_message("   2. 로그인 및 본인인증을 완료하세요")
            self.log_message("   3. 신청서 페이지로 이동하세요")
            self.log_message("   4. '자동화 시작' 버튼을 클릭하세요")
            
            # Chrome 디버깅 모드로 시작
            if start_chrome_with_debugging(1):
                self.log_message("✅ Chrome 디버깅 모드 시작 완료")
                self.log_message("🔐 이제 브라우저 재사용이 가능합니다")
                
                # 브라우저 재사용 체크박스 자동 활성화
                self.reuse_browser_var.set(True)
                self.browser_reuse_started = True  # 브라우저 재사용 모드 시작됨
                self.log_message("✅ 브라우저 재사용 체크박스가 자동으로 활성화되었습니다")
                self.log_message("💡 이제 '자동화 시작' 버튼을 클릭하세요")
            else:
                self.log_message("❌ Chrome 디버깅 모드 시작 실패")
                messagebox.showerror("오류", "Chrome 디버깅 모드 시작에 실패했습니다.")
                
        except Exception as e:
            self.log_message(f"❌ 브라우저 재사용 시작 실패: {e}")
            messagebox.showerror("오류", f"브라우저 재사용 시작 중 오류가 발생했습니다: {e}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
