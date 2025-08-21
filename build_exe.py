"""
클라이언트 배포용 exe 파일 생성 스크립트
"""

import os
import subprocess
import sys

def install_pyinstaller():
    """PyInstaller 설치"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 설치 완료")
        return True
    except Exception as e:
        print(f"❌ PyInstaller 설치 실패: {e}")
        return False

def build_gui_exe():
    """GUI 버전 exe 파일 생성"""
    try:
        print("🔨 GUI 버전 exe 파일 생성 중...")
        
        cmd = [
            "pyinstaller",
            "--onefile",  # 단일 파일로 생성
            "--windowed",  # 콘솔 창 숨김
            "--name=전기차신청서자동화",  # 실행 파일명
            "--icon=icon.ico",  # 아이콘 (있는 경우)
            "--add-data=ev_automation;ev_automation",  # 모듈 포함
            "--add-data=working_excel_reader.py;.",  # 엑셀 리더 포함
            "gui_automation.py"  # 메인 파일
        ]
        
        # 아이콘이 없으면 제거
        if not os.path.exists("icon.ico"):
            cmd.remove("--icon=icon.ico")
        
        subprocess.check_call(cmd)
        print("✅ GUI 버전 exe 파일 생성 완료")
        print("📁 생성된 파일: dist/전기차신청서자동화.exe")
        return True
        
    except Exception as e:
        print(f"❌ GUI exe 파일 생성 실패: {e}")
        return False

def build_console_exe():
    """콘솔 버전 exe 파일 생성"""
    try:
        print("🔨 콘솔 버전 exe 파일 생성 중...")
        
        cmd = [
            "pyinstaller",
            "--onefile",  # 단일 파일로 생성
            "--name=전기차신청서자동화_콘솔",  # 실행 파일명
            "--add-data=ev_automation;ev_automation",  # 모듈 포함
            "--add-data=working_excel_reader.py;.",  # 엑셀 리더 포함
            "complete_automation_system.py"  # 메인 파일
        ]
        
        subprocess.check_call(cmd)
        print("✅ 콘솔 버전 exe 파일 생성 완료")
        print("📁 생성된 파일: dist/전기차신청서자동화_콘솔.exe")
        return True
        
    except Exception as e:
        print(f"❌ 콘솔 exe 파일 생성 실패: {e}")
        return False

def create_install_guide():
    """설치 가이드 생성"""
    guide_content = """
# 전기차 신청서 자동화 시스템 설치 가이드

## 시스템 요구사항
- Windows 10/11
- Chrome 브라우저 (최신 버전)
- 최소 4GB RAM

## 설치 방법

### 1. 파일 준비
1. `전기차신청서자동화.exe` 파일을 원하는 폴더에 복사
2. 엑셀 파일 준비 (사용자 정보가 포함된 .xlsx 파일)
3. PDF 파일들 준비:
   - {사용자명}_계약서.pdf
   - {사용자명}_신분증.pdf
   - {사용자명}_소득증빙.pdf
   - {사용자명}_기타서류.pdf

### 2. 실행 방법
1. `전기차신청서자동화.exe` 더블클릭
2. 엑셀 파일 선택
3. PDF 폴더 선택
4. 사용자 목록 로드
5. 처리할 사용자 선택
6. 자동화 시작

### 3. 사용 방법
1. 브라우저가 열리면 수동으로 로그인
2. 신청서 페이지로 이동
3. Enter 키를 눌러 자동화 시작
4. 자동으로 다음 과정이 진행됩니다:
   - 신청서 필드 입력
   - 임시저장
   - 확인코드 입력
   - PDF 파일 첨부
   - 지원 신청 버튼 클릭

## 주의사항
- 자동화 중에는 브라우저를 조작하지 마세요
- 인터넷 연결이 안정적이어야 합니다
- PDF 파일명은 정확히 맞춰주세요

## 문제 해결
- 브라우저가 열리지 않으면 Chrome을 재설치하세요
- 파일 첨부가 안 되면 PDF 파일명을 확인하세요
- 자동화가 중단되면 다시 시작하세요

## 지원
문제가 발생하면 로그를 확인하고 관리자에게 문의하세요.
"""
    
    try:
        with open("설치가이드.txt", "w", encoding="utf-8") as f:
            f.write(guide_content)
        print("✅ 설치 가이드 생성 완료: 설치가이드.txt")
        return True
    except Exception as e:
        print(f"❌ 설치 가이드 생성 실패: {e}")
        return False

def create_sample_files():
    """샘플 파일 생성"""
    try:
        # 샘플 PDF 폴더 생성
        sample_pdf_folder = "sample_pdf_files"
        if not os.path.exists(sample_pdf_folder):
            os.makedirs(sample_pdf_folder)
        
        # 샘플 PDF 파일들 생성 (빈 파일)
        sample_files = [
            "장원_계약서.pdf",
            "장원_신분증.pdf", 
            "장원_소득증빙.pdf",
            "장원_기타서류.pdf"
        ]
        
        for file_name in sample_files:
            file_path = os.path.join(sample_pdf_folder, file_name)
            with open(file_path, "w") as f:
                f.write("Sample PDF file")
        
        print(f"✅ 샘플 PDF 파일 생성 완료: {sample_pdf_folder}/")
        return True
        
    except Exception as e:
        print(f"❌ 샘플 파일 생성 실패: {e}")
        return False

def main():
    print("🚀 전기차 신청서 자동화 시스템 배포 패키지 생성")
    print("=" * 60)
    
    # 1. PyInstaller 설치
    if not install_pyinstaller():
        return
    
    # 2. GUI 버전 exe 생성
    if not build_gui_exe():
        return
    
    # 3. 콘솔 버전 exe 생성
    if not build_console_exe():
        return
    
    # 4. 설치 가이드 생성
    if not create_install_guide():
        return
    
    # 5. 샘플 파일 생성
    if not create_sample_files():
        return
    
    print("\n🎉 배포 패키지 생성 완료!")
    print("\n📦 생성된 파일들:")
    print("  - dist/전기차신청서자동화.exe (GUI 버전)")
    print("  - dist/전기차신청서자동화_콘솔.exe (콘솔 버전)")
    print("  - 설치가이드.txt")
    print("  - sample_pdf_files/ (샘플 PDF 파일들)")
    
    print("\n📋 배포 방법:")
    print("  1. dist 폴더의 exe 파일을 클라이언트에게 전달")
    print("  2. 설치가이드.txt 함께 전달")
    print("  3. sample_pdf_files 폴더를 참고하여 PDF 파일 준비 안내")

if __name__ == "__main__":
    main()
