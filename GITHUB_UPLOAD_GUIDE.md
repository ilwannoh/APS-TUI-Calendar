# GitHub 업로드 가이드

## 방법 1: GitHub 웹사이트 사용 (가장 간단)

1. **GitHub에서 새 리포지토리 생성**
   - https://github.com/new 접속
   - Repository name: `APS-TUI-Calendar`
   - Description: `TUI Calendar 기반 생산계획 스케줄링 시스템 (APS)`
   - **Public** 선택
   - ⚠️ **"Add a README file" 체크하지 않기** (중요!)
   - **Create repository** 클릭

2. **생성 후 나오는 화면에서**
   - "…or push an existing repository from the command line" 섹션의 명령어 복사
   - 또는 아래 명령어 사용:

```bash
cd C:\MYCLAUDE_PROJECT\NEW_APS_WEB
git remote remove origin
git remote add origin https://github.com/ilwannoh/APS-TUI-Calendar.git
git push -u origin main
```

## 방법 2: GitHub Desktop 사용

1. GitHub Desktop 다운로드: https://desktop.github.com/
2. 설치 후 GitHub 계정 로그인
3. File → Add Local Repository
4. `C:\MYCLAUDE_PROJECT\NEW_APS_WEB` 폴더 선택
5. Publish repository 클릭
6. Name: `APS-TUI-Calendar`
7. Description: `TUI Calendar 기반 생산계획 스케줄링 시스템 (APS)`
8. Keep this code private 체크 해제 (Public으로 만들기)
9. Publish repository 클릭

## 업로드될 내용

### 📁 프로젝트 구조
```
APS-TUI-Calendar/
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # 메인 API 서버
│   ├── models.py           # 데이터베이스 모델
│   └── scheduler_service.py # 스케줄링 로직
├── frontend/               # TUI Calendar 프론트엔드
│   ├── index.html         # 메인 페이지
│   ├── css/               # 스타일시트
│   └── js/                # JavaScript 모듈
├── test_aps_system.py     # 자동 테스트
├── Instruction.md         # 개발 가이드
└── README.md              # 프로젝트 설명
```

### 🚀 주요 기능
- TUI Calendar를 활용한 생산 스케줄 관리
- 드래그 앤 드롭으로 일정 조정
- 판매계획 기반 자동 스케줄 생성
- 장비별 캘린더 뷰
- 실시간 로그 모니터링

## 문제 해결

### 인증 오류가 발생하는 경우
1. GitHub 계정 로그인 확인
2. Personal Access Token 생성:
   - https://github.com/settings/tokens/new
   - repo 권한 체크
   - Generate token
3. git push 시 비밀번호 대신 토큰 사용

### push 거부되는 경우
```bash
git push -f origin main  # 강제 푸시 (주의!)
```

## 완료 후 확인
- 리포지토리 URL: https://github.com/ilwannoh/APS-TUI-Calendar
- 모든 파일이 업로드되었는지 확인
- README.md가 메인 페이지에 표시되는지 확인