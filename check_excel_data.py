"""
엑셀 데이터 확인 스크립트
"""

from ev_automation.excel_loader import load_users_from_excel

def check_excel_data():
    """엑셀 데이터 확인"""
    print("🔍 엑셀 데이터 확인")
    
    excel_file = r"C:\Users\PC_1M\Documents\카카오톡 받은 파일\전기차연습(김찬미).xlsx"
    
    try:
        users_data = load_users_from_excel(excel_file)
        
        print(f"총 {len(users_data)}명의 사용자 로드됨")
        
        # 전문수 데이터 찾기
        for i, user in enumerate(users_data):
            if user['성명'] == '전문수':
                print(f"\n✅ 전문수 데이터 발견 (인덱스: {i})")
                print("=" * 50)
                
                # 모든 필드 출력
                for key, value in user.items():
                    print(f"{key}: {value}")
                
                # 특별히 확인할 필드들
                print("\n🔍 중요 필드 확인:")
                print(f"성별: '{user.get('성별', '없음')}'")
                print(f"생년월일: '{user.get('생년월일', '없음')}'")
                print(f"출고예정일자: '{user.get('출고예정일자', '없음')}'")
                print(f"계약일자: '{user.get('계약일자', '없음')}'")
                print(f"주소: '{user.get('주소', '없음')}'")
                print(f"신청차종: '{user.get('신청차종', '없음')}'")
                
                break
        else:
            print("❌ 전문수를 찾을 수 없습니다")
            
            # 모든 사용자 이름 출력
            print("\n📋 모든 사용자 목록:")
            for i, user in enumerate(users_data):
                print(f"{i+1}. {user['성명']}")
        
    except Exception as e:
        print(f"❌ 엑셀 로드 실패: {e}")

if __name__ == "__main__":
    check_excel_data()
