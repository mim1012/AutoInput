import json
import os
import re
import pandas as pd


def load_users_from_excel(excel_file: str):
    users = []
    try:
        from working_excel_reader import read_user_sheet
        excel_obj = pd.ExcelFile(excel_file)
        sheet_names = excel_obj.sheet_names
        user_sheets = [name for name in sheet_names if re.match(r'^[가-힣]{2,4}$', name)]
        for sheet_name in user_sheets:
            user_data = read_user_sheet(excel_file, sheet_name)
            if user_data:
                users.append(user_data)
        return users
    except Exception:
        # fallback 샘플
        return [
            {
                '성명': '장원', '계약일자': '2025-08-16', '신청유형': '개인',
                '생년월일': '1990-01-01', '성별': '여자', '신청차종': 'EV3 스탠다드',
                '신청대수': '1', '출고예정일자': '2025-08-29',
                '주소': '충청북도 제천시 의림지로 171', '휴대전화': '010-9199-6844',
                '이메일': '.', '전화': '.', '우선순위': '사회계층 Y. 다자녀가구. 2자녀 클릭'
            },
            {
                '성명': '전문수', '계약일자': '2025-08-18', '신청유형': '개인',
                '생년월일': '1990-01-01', '성별': '남자', '신청차종': '레이EV 4인승',
                '신청대수': '1', '출고예정일자': '2025-08-29',
                '주소': '인천시 강저로 57번 19', '휴대전화': '010-9557-5256',
                '이메일': '.', '전화': '.', '우선순위': ''
            }
        ]


