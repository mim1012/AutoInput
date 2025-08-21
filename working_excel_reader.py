import pandas as pd
import re
from datetime import datetime

def read_user_sheet(excel_file, sheet_name):
    """실제 엑셀 파일 구조에 맞는 사용자 데이터 읽기"""
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # 데이터 추출
        user_data = {}
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # 열 12(인덱스 12)에 필드명, 열 13(인덱스 13)에 값이 있음
            field_name = str(row.iloc[12]) if pd.notna(row.iloc[12]) else ""
            field_value = str(row.iloc[13]) if pd.notna(row.iloc[13]) else ""
            
            if field_name and field_value and field_name != 'nan':
                # 특수 처리
                if field_name == '생년월일':
                    # Excel 날짜 형식을 변환
                    try:
                        if field_value.isdigit():
                            excel_date = int(field_value)
                            # Excel의 1900년 기준 날짜를 변환
                            date_obj = datetime(1900, 1, 1) + pd.Timedelta(days=excel_date-2)
                            field_value = date_obj.strftime('%Y-%m-%d')
                    except:
                        pass
                
                elif field_name == '성별':
                    # '여'를 '여자'로 변환
                    if field_value == '여':
                        field_value = '여자'
                    elif field_value == '남':
                        field_value = '남자'
                
                elif field_name == '주소':
                    # 주소에 시도 정보 추가
                    if '제천시' in field_value and not field_value.startswith('충청북도'):
                        field_value = '충청북도 ' + field_value
                
                user_data[field_name] = field_value
        
        # 필수 필드 확인
        required_fields = ['성명', '휴대전화', '생년월일', '성별', '주소']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            print(f"[WARNING] {sheet_name} 시트에서 누락된 필드: {missing_fields}")
        
        return user_data
        
    except Exception as e:
        print(f"[ERROR] {sheet_name} 시트 읽기 실패: {e}")
        return None
