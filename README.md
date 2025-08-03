# APS Web - TUI Calendar 기반 생산 스케줄링 시스템

## 프로젝트 개요
TUI Calendar를 활용한 웹 기반 생산계획(APS) 스케줄링 시스템

## 기술 스택
- **Frontend**: HTML5, JavaScript (ES6+), TUI Calendar
- **Backend**: Python FastAPI
- **Database**: SQLite (개발용) / PostgreSQL (운영용)
- **Scheduler**: Python (기존 APS 알고리즘 재사용)

## 프로젝트 구조
```
NEW_APS_WEB/
├── frontend/              # 프론트엔드 (TUI Calendar)
│   ├── index.html        # 메인 페이지
│   ├── css/
│   │   └── style.css     # 커스텀 스타일
│   ├── js/
│   │   ├── app.js        # 메인 애플리케이션
│   │   ├── calendar.js   # 캘린더 설정
│   │   └── api.js        # API 통신
│   └── assets/
├── backend/              # 백엔드 API 서버
│   ├── main.py          # FastAPI 앱
│   ├── models/          # 데이터 모델
│   ├── routes/          # API 라우트
│   ├── services/        # 비즈니스 로직
│   └── scheduler/       # 스케줄링 엔진
└── database/            # DB 스키마
```

## 주요 기능
1. **캘린더 뷰**
   - 월간/주간/일간 뷰
   - 장비별 타임라인
   - 드래그&드롭 일정 조정

2. **생산 스케줄링**
   - 판매계획 업로드
   - 자동 스케줄 생성
   - 제약조건 검증

3. **마스터 데이터 관리**
   - 제품/공정/장비/작업자
   - REST API CRUD

4. **실시간 업데이트**
   - WebSocket 지원
   - 다중 사용자 동시 편집