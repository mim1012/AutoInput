#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
필드 매핑 분석기 - GUI 자동화에서 데이터-필드 매핑 분석
"""

import json
import re
from typing import Dict, List, Tuple

def analyze_field_mapping(script_content: str) -> Dict:
    """
    JavaScript 스크립트에서 데이터-필드 매핑을 분석
    
    Args:
        script_content: JavaScript 스크립트 내용
        
    Returns:
        매핑 분석 결과 딕셔너리
    """
    
    analysis = {
        'data_fields': {},      # 데이터 키 -> 필드 ID 매핑
        'field_types': {},      # 필드 ID -> 필드 타입
        'processing_order': [], # 처리 순서
        'special_handling': {}  # 특별 처리 로직
    }
    
    # Python 코드에서 데이터 키 추출
    data_keys = re.findall(r"user_data\.get\('([^']+)'", script_content)
    
    # JavaScript 코드에서 필드 매핑 추출
    js_code = script_content.split('return f"""')[1].split('"""')[0]
    
    # 각 필드별 매핑 추출
    field_mappings = [
        ('성명', 'req_nm'),
        ('휴대전화', 'mobile'),
        ('이메일', 'email'),
        ('전화', 'phone'),
        ('주소', 'addr'),
        ('상세주소', 'addr_detail'),
        ('계약일자', 'contract_day'),
        ('생년월일', 'birth'),
        ('생년월일', 'birth1'),  # 두 번째 필드
        ('출고예정일자', 'delivery_sch_day'),
        ('성별', 'req_sex1'),
        ('성별', 'req_sex2'),
        ('신청차종', 'model_cd'),
        ('신청대수', 'req_cnt')
    ]
    
    # 매핑 정보 저장
    for data_key, field_id in field_mappings:
        if data_key not in analysis['data_fields']:
            analysis['data_fields'][data_key] = []
        analysis['data_fields'][data_key].append(field_id)
        analysis['processing_order'].append((data_key, field_id))
    
    # 특별 처리 로직 감지
    special_fields = {
        'addr': 'readonly 제거 후 입력',
        'contract_day': 'readonly 제거 후 입력',
        'birth1': 'readonly 제거 후 입력',
        'delivery_sch_day': 'readonly 제거 후 입력',
        'req_sex1': '라디오 버튼 선택',
        'req_sex2': '라디오 버튼 선택',
        'req_kind': '드롭다운 선택 (고정값: P)',
        'model_cd': '드롭다운 선택 (조건부)'
    }
    
    analysis['special_handling'] = special_fields
    
    return analysis

def create_mapping_report(analysis: Dict) -> str:
    """
    매핑 분석 결과를 보고서 형태로 생성
    
    Args:
        analysis: 분석 결과 딕셔너리
        
    Returns:
        HTML 형태의 보고서
    """
    
    html_report = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GUI 자동화 필드 매핑 분석 보고서</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; }}
        .mapping-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .mapping-table th, .mapping-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .mapping-table th {{ background: #f8f9fa; font-weight: bold; }}
        .mapping-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .processing-order {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .special-handling {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
        .field-id {{ font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }}
        .data-key {{ font-weight: bold; color: #007bff; }}
        .status-success {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-info {{ color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 GUI 자동화 필드 매핑 분석 보고서</h1>
        
        <h2>📊 데이터-필드 매핑 테이블</h2>
        <table class="mapping-table">
            <thead>
                <tr>
                    <th>순서</th>
                    <th>데이터 키</th>
                    <th>필드 ID</th>
                    <th>필드 타입</th>
                    <th>특별 처리</th>
                    <th>상태</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # 매핑 테이블 생성
    for i, (data_key, field_id) in enumerate(analysis['processing_order'], 1):
        special_handling = analysis['special_handling'].get(field_id, '일반 입력')
        status = '✅ 정상'
        
        html_report += f"""
                <tr>
                    <td>{i}</td>
                    <td class="data-key">{data_key}</td>
                    <td class="field-id">{field_id}</td>
                    <td>{get_field_type(field_id)}</td>
                    <td>{special_handling}</td>
                    <td class="status-success">{status}</td>
                </tr>
"""
    
    html_report += """
            </tbody>
        </table>
        
        <h2>🔄 처리 순서</h2>
        <div class="processing-order">
"""
    
    for i, (data_key, field_id) in enumerate(analysis['processing_order'], 1):
        html_report += f"            <p><strong>{i}.</strong> <span class='data-key'>{data_key}</span> → <span class='field-id'>{field_id}</span></p>\n"
    
    html_report += """
        </div>
        
        <h2>⚙️ 특별 처리 로직</h2>
        <div class="special-handling">
"""
    
    for field_id, handling in analysis['special_handling'].items():
        html_report += f"            <p><span class='field-id'>{field_id}</span>: {handling}</p>\n"
    
    html_report += """
        </div>
        
        <h2>📈 분석 요약</h2>
        <ul>
            <li><strong>총 데이터 필드:</strong> {total_data_fields}개</li>
            <li><strong>총 HTML 필드:</strong> {total_html_fields}개</li>
            <li><strong>매핑 완료:</strong> {mapped_fields}개</li>
            <li><strong>특별 처리:</strong> {special_handled_fields}개</li>
        </ul>
    </div>
</body>
</html>
""".format(
        total_data_fields=len(analysis['data_fields']),
        total_html_fields=len(set(analysis['data_fields'].values())),
        mapped_fields=len(analysis['data_fields']),
        special_handled_fields=len(analysis['special_handling'])
    )
    
    return html_report

def get_field_type(field_id: str) -> str:
    """필드 ID로부터 필드 타입 추정"""
    field_type_map = {
        'req_nm': '텍스트 입력',
        'mobile': '휴대폰 번호',
        'email': '이메일',
        'phone': '전화번호',
        'addr': '주소 (readonly)',
        'addr_detail': '상세주소',
        'contract_day': '날짜 (readonly)',
        'birth': '생년월일',
        'birth1': '생년월일 (readonly)',
        'delivery_sch_day': '출고예정일자 (readonly)',
        'req_sex1': '성별 라디오 (남자)',
        'req_sex2': '성별 라디오 (여자)',
        'req_kind': '신청유형 선택',
        'model_cd': '차종 선택',
        'req_cnt': '신청대수'
    }
    
    return field_type_map.get(field_id, '알 수 없음')

def analyze_fill_fields_code():
    """fill_fields.py 코드 분석"""
    
    # fill_fields.py 파일 읽기
    with open('ev_automation/fill_fields.py', 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # 분석 실행
    analysis = analyze_field_mapping(script_content)
    
    # 보고서 생성
    report = create_mapping_report(analysis)
    
    # HTML 파일로 저장
    with open('ev_automation/field_mapping_report.html', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("=== 필드 매핑 분석 완료 ===")
    print("📄 보고서 파일: ev_automation/field_mapping_report.html")
    print()
    
    # 콘솔 출력
    print("=== 데이터-필드 매핑 요약 ===")
    for data_key, field_id in analysis['data_fields'].items():
        special = analysis['special_handling'].get(field_id, '')
        print(f"📝 {data_key:12} → {field_id:15} {special}")
    
    print(f"\n총 {len(analysis['data_fields'])}개 필드 매핑 완료")
    print(f"특별 처리: {len(analysis['special_handling'])}개 필드")

if __name__ == "__main__":
    analyze_fill_fields_code()
