# AutoClick - 웹 자동화 시스템

웹 브라우저 자동화를 위한 Python 기반 시스템입니다. Selenium과 Playwright를 사용하여 웹 페이지의 필드를 자동으로 채우고 상호작용할 수 있습니다.

## 주요 기능

- **웹 자동화**: Selenium과 Playwright를 통한 웹 페이지 자동화
- **Excel 데이터 연동**: Excel 파일에서 데이터를 읽어와 자동 입력
- **필드 매핑**: 웹 페이지의 필드를 자동으로 분석하고 매핑
- **GUI 인터페이스**: 사용자 친화적인 그래픽 인터페이스
- **파일 첨부**: 자동 파일 업로드 기능
- **검증 코드**: 자동 입력 데이터 검증

## 설치 방법

1. 저장소를 클론합니다:
```bash
git clone https://github.com/mim1012/AutoInput.git
cd AutoInput
```

2. 가상환경을 생성하고 활성화합니다:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

4. Playwright 브라우저를 설치합니다:
```bash
playwright install
```

## 사용 방법

### 기본 실행
```bash
python main_automation.py
```

### GUI 모드
```bash
python gui_automation.py
```

### Playwright 모드
```bash
python playwright_automation.py
```

## 프로젝트 구조

```
AutoClick/
├── ev_automation/          # 핵심 자동화 모듈
│   ├── browser.py         # 브라우저 관리
│   ├── excel_loader.py    # Excel 데이터 로더
│   ├── field_mapping_analyzer.py  # 필드 매핑 분석
│   ├── fill_fields.py     # 필드 채우기
│   ├── file_attachment.py # 파일 첨부
│   └── verification_code.py # 검증 코드
├── main_automation.py     # 메인 실행 파일
├── gui_automation.py      # GUI 인터페이스
├── playwright_automation.py # Playwright 자동화
├── requirements.txt       # 의존성 패키지
└── README.md             # 프로젝트 문서
```

## 주요 모듈 설명

### ev_automation.browser
웹 브라우저 제어를 담당하는 모듈입니다.

### ev_automation.excel_loader
Excel 파일에서 데이터를 읽어오는 모듈입니다.

### ev_automation.field_mapping_analyzer
웹 페이지의 필드를 분석하고 매핑하는 모듈입니다.

### ev_automation.fill_fields
분석된 필드에 데이터를 자동으로 채우는 모듈입니다.

## 설정

### Excel 파일 형식
- 첫 번째 행은 헤더로 사용됩니다
- 데이터는 두 번째 행부터 시작됩니다
- 필드명과 웹 페이지의 필드가 매칭되어야 합니다

### 환경 변수
필요한 경우 `.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.