"""
전기차 신청서 메인 자동화 시스템
- 스텔스 브라우저 사용
- 개선된 임시저장 기능
- 자동화 감지 우회
"""

import os
import time
from ev_automation.browser import create_stealth_browser, wait_for_page_load
from ev_automation.fill_fields import fill_fields_selenium
from ev_automation.temp_save import force_temp_save_with_retry
from ev_automation.excel_loader import load_users_from_excel

class EVAutomation:
    def __init__(self):
        self.driver = None
        
    def create_browser(self):
        """스텔스 브라우저 생성"""
        self.driver = create_stealth_browser()
        if self.driver:
            print("[BROWSER] 스텔스 브라우저 생성 완료")
        else:
            print("[ERROR] 브라우저 생성 실패")
        
    def get_test_data(self):
        """테스트 데이터"""
        return {
            '성명': '장원',
            '휴대전화': '010-9199-6844',
            '생년월일': '1990-01-01',
            '성별': '여자',
            '주소': '충청북도 제천시 의림지로 171',
            '계약일자': '2025-08-16',
            '신청차종': 'EV3 스탠다드',
            '이메일': 'test@test.com',
            '전화': '010-9199-6844',
            '상세주소': '123-45',
            '출고예정일자': '2025-09-16',
            '신청대수': '1'
        }
    
    def wait_for_application_page(self):
        """신청서 페이지 대기"""
        print("[WAIT] 신청서 페이지 대기")
        print("수동으로 로그인 후 https://ev.or.kr/ev_ps/ps/seller/sellerApplyform 이동")
        
        while True:
            try:
                current_url = self.driver.current_url
                if 'sellerApplyform' in current_url:
                    print("[SUCCESS] 신청서 페이지 감지!")
                    
                    # 페이지 완전 로딩 대기
                    wait_for_page_load(self.driver)
                    return True
                    
                print(f"현재: {current_url[:50]}...")
                input("신청서 페이지 이동 후 Enter: ")
                
            except:
                print("[ERROR] 브라우저 연결 끊어짐")
                return False
    
    def auto_fill_all_fields(self, user_data):
        """모든 필드 자동 입력 (개선된 버전)"""
        print(f"🚀 {user_data.get('성명', 'Unknown')} 자동 입력 시작")
        
        # 필드 입력
        success = fill_fields_selenium(self.driver, user_data)
        
        if success:
            print("✅ 필드 입력 완료")
            return True
        else:
            print("❌ 필드 입력 실패")
            return False
    
    def auto_temp_save(self):
        """자동 임시저장 (개선된 버전)"""
        print("💾 임시저장 시작...")
        
        # 개선된 임시저장 함수 사용
        success = force_temp_save_with_retry(self.driver, max_retries=3)
        
        if success:
            print("✅ 임시저장 성공!")
            return True
        else:
            print("❌ 임시저장 실패")
            return False
    
    def run_automation(self, user_data):
        """전체 자동화 실행"""
        print(f"\n{'='*60}")
        print(f"🎯 {user_data.get('성명', 'Unknown')} 자동화 시작")
        print(f"{'='*60}")
        
        # 1. 필드 입력
        fill_success = self.auto_fill_all_fields(user_data)
        
        if not fill_success:
            print("❌ 필드 입력 실패로 중단")
            return False
        
        # 2. 임시저장
        save_success = self.auto_temp_save()
        
        if save_success:
            print("🎉 자동화 완료!")
            return True
        else:
            print("⚠️ 임시저장 실패 - 수동 확인 필요")
            return False
    
    def run_batch_automation(self, excel_file_path):
        """Excel 파일에서 데이터를 읽어 배치 자동화 실행"""
        try:
            users = load_users_from_excel(excel_file_path)
            print(f"📊 총 {len(users)}명의 사용자 데이터 로드 완료")
            
            success_count = 0
            total_count = len(users)
            
            for i, user_data in enumerate(users, 1):
                print(f"\n📝 진행률: {i}/{total_count}")
                
                try:
                    success = self.run_automation(user_data)
                    if success:
                        success_count += 1
                    
                    # 다음 사용자 전 대기
                    if i < total_count:
                        print("⏳ 다음 사용자 처리 전 대기...")
                        time.sleep(3)
                        
                except Exception as e:
                    print(f"❌ 사용자 {user_data.get('성명', 'Unknown')} 처리 중 오류: {e}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"📊 배치 자동화 완료")
            print(f"성공: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ 배치 자동화 실패: {e}")

def main():
    """메인 실행 함수"""
    automation = EVAutomation()
    
    print("🚀 전기차 신청서 자동화 시스템 시작")
    print("1. 단일 사용자 테스트")
    print("2. Excel 파일 배치 처리")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    # 브라우저 생성
    automation.create_browser()
    if not automation.driver:
        print("❌ 브라우저 생성 실패")
        return
    
    try:
        if choice == "1":
            # 단일 사용자 테스트
            test_data = automation.get_test_data()
            
            # 신청서 페이지 대기
            if not automation.wait_for_application_page():
                print("❌ 신청서 페이지 접근 실패")
                return
            
            # 자동화 실행
            automation.run_automation(test_data)
            
        elif choice == "2":
            # Excel 파일 배치 처리
            excel_file = input("Excel 파일 경로를 입력하세요: ").strip()
            
            if not os.path.exists(excel_file):
                print(f"❌ 파일을 찾을 수 없습니다: {excel_file}")
                return
            
            # 신청서 페이지 대기
            if not automation.wait_for_application_page():
                print("❌ 신청서 페이지 접근 실패")
                return
            
            # 배치 자동화 실행
            automation.run_batch_automation(excel_file)
            
        else:
            print("❌ 잘못된 선택입니다")
            
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
    finally:
        if automation.driver:
            input("브라우저를 닫으려면 Enter를 누르세요...")
            automation.driver.quit()

if __name__ == "__main__":
    main()