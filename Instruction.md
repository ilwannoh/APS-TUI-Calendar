# APS 웹 애플리케이션 개발 환경 지침서

## 📋 핵심 개발 지침

### 1. 웹 서버 경로 설정
```
C:\xampp\htdocs\mysite 폴더는 http://localhost를 가리켜. 
따라서 http://localhost 접속시 C:\xampp\htdocs\mysite 폴더의 인덱스 파일이 뜨게 돼.
```

**현재 프로젝트 적용:**
- 실제 경로: `C:\MYCLAUDE_PROJECT\NEW_APS_WEB`
- 프론트엔드: `http://localhost:3000` → `frontend/index.html`
- 백엔드 API: `http://localhost:8000` → FastAPI 서버

### 2. 로그 관리 전략
```
로그 정보가 C:\xampp\htdocs\mysite\logs 이곳에 쌓이도록 PHP 개발을 진행해야 해. 
그리고 너는 logs 폴더의 내용을 통해 오류 확인해야 해.
```

**현재 구현 상태:**
- 백엔드 로그: `C:\MYCLAUDE_PROJECT\NEW_APS_WEB\backend\logs\`
  - `api_server.log` - API 서버 메인 로그
  - `test_results.json` - 자동 테스트 결과
- 프론트엔드 로그: 브라우저 콘솔 (Console API)

### 3. JavaScript 로깅 규칙
```
자바스크립트 작성 시, 이벤트마다 콘솔에 로그를 남겨야 해. 
그래야 에러 발생시 원인을 찾을 수 있어.
```

**구현된 로깅 패턴:**
```javascript
// 이벤트 로깅
console.log('[Event] View button clicked:', this.dataset.view);
console.log('[Event] File selected:', e.target.files[0]?.name);

// API 호출 로깅
console.log('[API] Loading equipment list...');
console.log('[API] Equipment loaded:', equipment.length, 'items');

// 에러 로깅
console.error('[ERROR] Failed to load initial data:', error);

// 액션 로깅
console.log('[Action] Generate schedule button clicked');
```

### 4. 디버깅 프로세스
```
디버깅 시, 콘솔의 로그를 찾아봐.
```

**디버깅 워크플로우:**
1. 브라우저 개발자 도구 열기 (F12)
2. Console 탭에서 로그 확인
3. Network 탭에서 API 요청/응답 확인
4. 서버 로그 파일 확인 (`backend/logs/`)

## 🔧 개발 환경 구성

### 백엔드 (Python/FastAPI)

#### 로깅 설정
```python
# main_simple.py
import logging
from pathlib import Path

# 로그 디렉토리 설정
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

#### API 엔드포인트 로깅
```python
@app.get("/api/equipment")
async def get_equipment():
    logger.info("Equipment list requested")
    # ... 로직 처리
    logger.info(f"Returned {len(equipment_data)} equipment items")
    return equipment_data
```

### 프론트엔드 (JavaScript)

#### 초기화 로깅
```javascript
document.addEventListener('DOMContentLoaded', function() {
    console.log('[APS] DOM Content Loaded - Initializing application');
    console.log('[APS] Initializing calendar...');
    console.log('[APS] Setting up event listeners...');
    console.log('[APS] Loading initial data...');
});
```

#### API 통신 로깅
```javascript
async function loadInitialData() {
    try {
        console.log('[API] Loading equipment list...');
        const equipment = await getEquipment();
        console.log('[API] Equipment loaded:', equipment.length, 'items');
    } catch (error) {
        console.error('[ERROR] Failed to load initial data:', error);
    }
}
```

## 🧪 자동 테스트 시스템

### 테스트 스크립트 (`test_aps_system.py`)

**주요 기능:**
1. API 헬스 체크
2. 엔드포인트 응답 검증
3. 스케줄 생성 및 검증
4. 로그 파일 존재 확인
5. 테스트 리포트 생성

**실행 방법:**
```bash
cd C:\MYCLAUDE_PROJECT\NEW_APS_WEB
python test_aps_system.py
```

**테스트 결과 예시:**
```
==================================================
APS SYSTEM TEST REPORT
==================================================
Test Date: 2025-08-03 16:18:35
Total Tests: 8
Passed: 7
Failed: 1
Success Rate: 87.5%
==================================================
```

## 📁 디렉토리 구조

```
C:\MYCLAUDE_PROJECT\NEW_APS_WEB\
├── backend/
│   ├── logs/                    # 서버 로그 저장 위치
│   │   ├── api_server.log      # API 서버 로그
│   │   └── test_results.json   # 테스트 결과
│   ├── main_simple.py          # FastAPI 서버 (로깅 포함)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js              # 메인 앱 (콘솔 로깅 포함)
│       ├── api.js              # API 통신 모듈
│       └── calendar.js         # TUI Calendar 설정
└── test_aps_system.py          # 자동 테스트 스크립트
```

## 🚀 실행 순서

1. **백엔드 서버 시작**
   ```bash
   cd backend
   python main_simple.py
   ```

2. **프론트엔드 서버 시작**
   ```bash
   cd frontend
   python -m http.server 3000
   ```

3. **브라우저에서 접속**
   - http://localhost:3000

4. **자동 테스트 실행**
   ```bash
   python test_aps_system.py
   ```

## 🔍 디버깅 체크리스트

### 문제 발생 시 확인 사항:

1. **서버가 실행 중인가?**
   - 백엔드: http://localhost:8000
   - 프론트엔드: http://localhost:3000

2. **브라우저 콘솔 확인**
   - F12 → Console 탭
   - 에러 메시지 확인
   - API 호출 로그 확인

3. **서버 로그 확인**
   ```bash
   cat backend/logs/api_server.log
   ```

4. **네트워크 요청 확인**
   - F12 → Network 탭
   - API 요청 상태 코드 확인
   - 요청/응답 데이터 확인

5. **자동 테스트 실행**
   ```bash
   python test_aps_system.py
   ```

## 💡 AI 개발 이점

이 구조를 통해 AI는:

1. **자동 문제 진단**: 로그를 읽어 문제 원인 파악
2. **증거 기반 디버깅**: 추측이 아닌 로그 데이터로 해결
3. **반복 가능한 테스트**: 일관된 테스트 환경 제공
4. **빠른 피드백 루프**: 즉시 결과 확인 및 수정

## 📝 추가 권장사항

1. **환경 변수 사용**
   ```python
   LOG_DIR = os.getenv('APS_LOG_DIR', 'logs')
   API_PORT = os.getenv('APS_API_PORT', 8000)
   ```

2. **로그 레벨 설정**
   ```python
   # 개발: DEBUG
   # 운영: INFO 또는 WARNING
   LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
   ```

3. **로그 로테이션**
   ```python
   from logging.handlers import RotatingFileHandler
   
   handler = RotatingFileHandler(
       'api_server.log',
       maxBytes=10*1024*1024,  # 10MB
       backupCount=5
   )
   ```

이 지침서를 따르면 AI와 개발자 모두 효율적으로 APS 시스템을 개발하고 디버깅할 수 있습니다.