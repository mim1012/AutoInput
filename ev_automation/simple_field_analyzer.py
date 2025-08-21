#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 필드 매핑 분석기
"""

def analyze_gui_automation():
    """GUI 자동화에서 데이터-필드 매핑 분석"""
    
    print("🔍 GUI 자동화 필드 매핑 분석")
    print("=" * 60)
    
    # 데이터-필드 매핑 테이블
    field_mappings = [
        ("성명", "req_nm", "텍스트 입력", "일반 입력"),
        ("휴대전화", "mobile", "휴대폰 번호", "일반 입력"),
        ("이메일", "email", "이메일", "일반 입력"),
        ("전화", "phone", "전화번호", "일반 입력"),
        ("주소", "addr", "주소", "readonly 제거 후 입력"),
        ("상세주소", "addr_detail", "상세주소", "이벤트 발생"),
        ("계약일자", "contract_day", "날짜", "readonly 제거 후 입력"),
        ("생년월일", "birth", "생년월일", "일반 입력"),
        ("생년월일", "birth1", "생년월일 (readonly)", "readonly 제거 후 입력"),
        ("출고예정일자", "delivery_sch_day", "출고예정일자", "readonly 제거 후 입력"),
        ("성별", "req_sex1", "성별 라디오 (남자)", "라디오 버튼 선택"),
        ("성별", "req_sex2", "성별 라디오 (여자)", "라디오 버튼 선택"),
        ("신청차종", "model_cd", "차종 선택", "드롭다운 선택 (조건부)"),
        ("신청대수", "req_cnt", "신청대수", "일반 입력")
    ]
    
    # 고정값 필드들
    fixed_fields = [
        ("신청유형", "req_kind", "신청유형 선택", "고정값: P (개인)")
    ]
    
    print("\n📊 데이터-필드 매핑 테이블")
    print("-" * 60)
    print(f"{'순서':<4} {'데이터 키':<12} {'필드 ID':<15} {'필드 타입':<15} {'처리 방식'}")
    print("-" * 60)
    
    for i, (data_key, field_id, field_type, handling) in enumerate(field_mappings, 1):
        print(f"{i:<4} {data_key:<12} {field_id:<15} {field_type:<15} {handling}")
    
    print("\n🔧 고정값 필드")
    print("-" * 60)
    for data_key, field_id, field_type, handling in fixed_fields:
        print(f"{data_key:<12} {field_id:<15} {field_type:<15} {handling}")
    
    print("\n⚙️ 특별 처리 로직")
    print("-" * 60)
    special_handling = {
        "readonly 필드": ["addr", "contract_day", "birth1", "delivery_sch_day"],
        "라디오 버튼": ["req_sex1", "req_sex2"],
        "드롭다운": ["req_kind", "model_cd"],
        "이벤트 발생": ["addr_detail", "birth1", "contract_day", "delivery_sch_day", "req_sex1", "req_sex2", "req_kind", "model_cd"]
    }
    
    for handling_type, fields in special_handling.items():
        print(f"{handling_type}: {', '.join(fields)}")
    
    print("\n📈 처리 순서")
    print("-" * 60)
    processing_order = [
        "1. 기본 정보 입력 (성명, 휴대전화, 이메일, 전화)",
        "2. 주소 정보 입력 (주소, 상세주소)",
        "3. 신청대수 입력",
        "4. 계약일자 입력 (readonly 처리)",
        "5. 생년월일 입력 (두 필드 모두)",
        "6. 출고예정일자 입력 (readonly 처리)",
        "7. 성별 선택 (라디오 버튼)",
        "8. 신청유형 선택 (고정값: 개인)",
        "9. 차종 선택 (조건부 매핑)"
    ]
    
    for step in processing_order:
        print(step)
    
    print("\n🎯 차종 매핑 로직")
    print("-" * 60)
    model_mapping = {
        "EV3 스탠다드": "EV3_2WD_S",
        "레이EV / 레이 EV": "RAY_4_R", 
        "EV3 롱레인지": "EV3_2WD_L17"
    }
    
    for model_name, model_code in model_mapping.items():
        print(f"{model_name:<20} → {model_code}")
    
    print("\n📋 요약")
    print("-" * 60)
    print(f"총 데이터 필드: {len(set([m[0] for m in field_mappings]))}개")
    print(f"총 HTML 필드: {len(set([m[1] for m in field_mappings]))}개")
    print(f"특별 처리 필드: {len([m for m in field_mappings if m[3] != '일반 입력'])}개")
    print(f"readonly 필드: {len(special_handling['readonly 필드'])}개")

if __name__ == "__main__":
    analyze_gui_automation()
