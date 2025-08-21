"""
완전한 전기차 신청서 자동화 시스템
- 엑셀 데이터 로드 → 신청서 입력 → 임시저장 → 코드 입력 → 파일 첨부 → 지원 신청
"""

import os
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ev_automation.browser import create_browser
from ev_automation.excel_loader import load_users_from_excel
from ev_automation.fill_fields import build_fill_script
from ev_automation.temp_save import run_temp_save, finalize_temp_save
from ev_automation.file_attachment import attach_pdf_files, find_and_click_submit_button, handle_final_popup

class CompleteAutomationSystem:
    """완전한 자동화 시스템"""
    
    def __init__(self, excel_file, pdf_folder_path):
        self.excel_file = excel_file
        self.pdf_folder_path = pdf_folder_path
        self.users_data = []
        self.drivers = []
        self.automation_running = False
    
    def load_users_from_excel(self):
        """엑셀에서 사용자 데이터 로드"""
        try:
            self.users_data = load_users_from_excel(self.excel_file)
            print(f"총 {len(self.users_data)}명의 사용자 로드 완료")
            return True
        except Exception as e:
            print(f"엑셀 로드 실패: {e}")
            return False
    
    def create_browser(self, profile_id):
        """브라우저 생성"""
        try:
            driver = create_browser(profile_id)
            print(f"[BROWSER] 프로필 {profile_id} 브라우저 생성")
            return driver
        except Exception as e:
            print(f"[ERROR] 브라우저 생성 실패: {e}")
            return None
    
    def complete_user_process(self, user_data, profile_id):
        """단일 사용자 완전 처리"""
        try:
            print(f"\n🚀 프로필 {profile_id} 시작: {user_data['성명']}")
            print(f"   휴대전화: {user_data['휴대전화']}")
            print(f"   우선순위: {user_data.get('우선순위', '일반')}")
            
            # 브라우저 생성
            driver = self.create_browser(profile_id)
            if not driver:
                return False
            
            self.drivers.append(driver)
            
            # 수동 네비게이션 안내
            print(f"[MANUAL] 프로필 {profile_id} 수동 네비게이션 시작")
            print(f"[INFO] 브라우저가 열렸습니다.")
            print(f"[TODO] 수동으로 다음 작업을 하세요:")
            print(f"  1. 로그인")
            print(f"  2. 신청서 페이지로 이동: https://ev.or.kr/ev_ps/ps/seller/sellerApplyform")
            print(f"[WAIT] 신청서 페이지 도달 후 Enter를 누르세요...")
            
            input("신청서 페이지 도달 후 Enter: ")
            
            # URL 확인
            try:
                current_url = driver.current_url
                if 'sellerApplyform' in current_url:
                    print(f"[DETECT] 신청서 페이지 감지됨!")
                    print(f"[URL] {current_url}")
                else:
                    print(f"[ERROR] 신청서 페이지가 아닙니다: {current_url}")
                    return False
            except Exception as session_error:
                print(f"[ERROR] 세션 오류: {session_error}")
                return False
            
            # 1단계: 신청서 필드 자동 입력
            print(f"[STEP 1] {user_data['성명']} 신청서 필드 입력")
            try:
                driver.execute_script(build_fill_script(user_data))
                time.sleep(3)
                print(f"[SUCCESS] 신청서 필드 입력 완료")
            except Exception as e:
                print(f"[ERROR] 필드 입력 실패: {e}")
                return False
            
            # 2단계: 임시저장
            print(f"[STEP 2] 임시저장 진행")
            if run_temp_save(driver, profile_id):
                if finalize_temp_save(driver):
                    print(f"[SUCCESS] 임시저장 완료")
                else:
                    print(f"[ERROR] 임시저장 실패")
                    return False
            else:
                print(f"[ERROR] 임시저장 실패")
                return False
            
            # 3단계: PDF 파일 첨부
            print(f"[STEP 3] PDF 파일 첨부")
            if attach_pdf_files(driver, user_data['성명'], self.pdf_folder_path):
                print(f"[SUCCESS] PDF 파일 첨부 완료")
            else:
                print(f"[WARNING] PDF 파일 첨부 실패 (계속 진행)")
            
            # 4단계: 지원 신청 버튼 클릭
            print(f"[STEP 4] 지원 신청 버튼 클릭")
            if find_and_click_submit_button(driver):
                print(f"[SUCCESS] 지원 신청 버튼 클릭 완료")
                
                # 5단계: 최종 팝업 처리
                print(f"[STEP 5] 최종 팝업 처리")
                if handle_final_popup(driver):
                    print(f"[SUCCESS] 최종 팝업 처리 완료")
                else:
                    print(f"[WARNING] 팝업 처리 실패 (계속 진행)")
                
                print(f"🎉 프로필 {profile_id} ({user_data['성명']}) 완전 처리 완료!")
                return True
            else:
                print(f"[ERROR] 지원 신청 버튼 클릭 실패")
                return False
            
        except Exception as e:
            print(f"❌ 프로필 {profile_id} 실패: {e}")
            return False
    
    def run_automation(self, selected_user_indices=None):
        """자동화 실행"""
        print("🎯 완전한 전기차 신청서 자동화 시스템")
        print("=" * 60)
        
        # 데이터 로드
        if not self.load_users_from_excel():
            print("처리할 데이터가 없습니다.")
            return
        
        # 처리할 사용자 선택
        if selected_user_indices is None:
            print(f"\n처리 가능한 사용자:")
            for i, user in enumerate(self.users_data):
                priority_info = user.get('우선순위', '일반')
                print(f"  {i+1}. {user['성명']} - {user['휴대전화']} - {priority_info}")
            
            # 기본적으로 첫 번째 사용자만 처리
            selected_user_indices = [0]
        
        selected_users = [self.users_data[i] for i in selected_user_indices]
        print(f"\n{len(selected_users)}명을 처리합니다.")
        
        # 순차 처리 (단일 컴퓨터, 단일 계정)
        success_count = 0
        for i, user in enumerate(selected_users):
            if not self.automation_running:
                break
            
            print(f"\n{'='*50}")
            print(f"사용자 {i+1}/{len(selected_users)} 처리 중...")
            
            if self.complete_user_process(user, i+1):
                success_count += 1
            
            # 다음 사용자 처리 전 대기
            if i < len(selected_users) - 1:
                print(f"\n다음 사용자 처리 전 5초 대기...")
                time.sleep(5)
        
        print(f"\n🎊 전체 처리 완료! 성공: {success_count}/{len(selected_users)}")
    
    def stop_automation(self):
        """자동화 중지"""
        self.automation_running = False
        print("자동화가 중지되었습니다.")
    
    def cleanup(self):
        """정리"""
        if self.drivers:
            print(f"\n[CLEANUP] {len(self.drivers)}개 브라우저 정리")
            for i, driver in enumerate(self.drivers):
                try:
                    driver.quit()
                    print(f"브라우저 {i+1} 종료")
                except:
                    pass

def main():
    # 설정
    excel_file = r"C:\Users\PC_1M\Documents\카카오톡 받은 파일\전기차연습(김찬미).xlsx"
    pdf_folder_path = r"D:\Project\AutoClick\pdf_files"  # PDF 파일들이 저장된 폴더
    
    # PDF 폴더가 없으면 생성
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)
        print(f"PDF 폴더 생성: {pdf_folder_path}")
        print("PDF 파일들을 이 폴더에 넣어주세요:")
        print("  - {사용자명}_계약서.pdf")
        print("  - {사용자명}_신분증.pdf")
        print("  - {사용자명}_소득증빙.pdf")
        print("  - {사용자명}_기타서류.pdf")
    
    # 자동화 시스템 생성
    automation = CompleteAutomationSystem(excel_file, pdf_folder_path)
    automation.automation_running = True
    
    try:
        # 자동화 실행
        automation.run_automation()
        
        input("모든 작업 완료. Enter로 종료...")
    except KeyboardInterrupt:
        print("\n사용자 중단")
        automation.stop_automation()
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main()
