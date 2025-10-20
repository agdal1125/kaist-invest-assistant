# Invest Assistant

AI 기반 투자 어시스턴트 시스템입니다. 주식 거래, 환전, 포트폴리오 관리 등의 기능을 제공하는 웹 애플리케이션입니다.

## 📁 프로젝트 구조

```
invest_assistant/
├── invest_agent/           # AI 에이전트 핵심 모듈
│   └── agent/
│       ├── agent.py        # InvestAgent 클래스
│       └── prompt/         # 프롬프트 및 함수 정의
│           ├── prompt.py   # 시스템 프롬프트
│           └── functions.py # 함수 호출 정의
├── website/                # 웹 인터페이스
│   ├── app.py             # Flask 웹 서버
│   └── templates/
│       └── index.html     # 웹 페이지 템플릿
├── benchmark/              # 성능 평가 도구
│   ├── run.py             # 벤치마크 실행 스크립트
│   └── functioncall_single.json # 테스트 데이터
├── requirements.txt        # Python 의존성
└── setup.py               # 패키지 설정
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd invest_assistant

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
pip install -e .
```

### 2. 환경 변수 설정

프로젝트 루트 폴더에 `.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3. 웹 애플리케이션 실행

```bash
# 웹 서버 실행
cd website
python app.py
```

웹 브라우저에서 `http://localhost:5000`으로 접속하여 투자 어시스턴트를 사용할 수 있습니다.

## 💡 주요 기능

### 1. 주식 거래
- **국내주식 주문**: 스마트 주문/KRX/NXT 거래소 지원
- **해외주식 주문**: 미국, 일본 등 해외 주식 거래
- **주문 유형**: 보통가, 시장가, 프리마켓, 애프터마켓, 주간거래

### 2. 시세 조회
- **국내주식 현재가**: 종목코드로 실시간 가격 조회
- **해외주식 현재가**: 국가별 주식 시세 확인

### 3. 거래 내역
- **해외주식 체결내역**: 매수/매도 내역 조회
- **환전내역**: 통화별 환전 기록 확인

### 4. 환전
- **통화 환전**: KRW, USD, JPY, EUR 등 다양한 통화 지원
- **환전 내역**: 기간별 환전 기록 조회

### 5. 배당 관리
- **배당 확인**: 주식별 배당 정보 조회

## 🤖 AI 에이전트 사용법

### 기본 사용법

```python
from invest_agent.agent import InvestAgent

# 에이전트 초기화
agent = InvestAgent(model="gpt-4.1-mini")
agent.reset()

# 질문하기
response = agent.generate("삼성전자 현재가 알려줘")
print(response["content"])
```

### 지원하는 모델
- `gpt-4.1-mini`: 기본 모델 (권장)
- `gpt-4.1-nano`: 빠른 응답
- `gpt-4.1`: 고성능 모델

### 예시 명령어

```
# 주식 시세 조회
"삼성전자 현재가 알려줘"
"TSLA 주가 확인해줘"

# 주식 주문
"삼성전자 10주 시장가로 매수해줘"
"애플 주식 5주 150달러에 매도해줘"

# 환전
"100만원을 달러로 환전해줘"
"환전 내역 확인해줘"

# 거래 내역
"오늘 매수한 주식 내역 보여줘"
```

## 📊 벤치마크 실행

AI 에이전트의 성능을 평가하려면:

```bash
cd benchmark
python run.py
```

벤치마크는 `functioncall_single.json` 파일의 테스트 케이스를 사용하여 함수 호출 정확도를 측정합니다.

## 🔧 개발 가이드

### 새로운 함수 추가

1. `invest_agent/agent/prompt/functions.py`에 함수 정의 추가
2. `invest_agent/agent/agent.py`의 `parse_tool_calls` 메서드에서 함수 처리 로직 구현

### 프롬프트 수정

`invest_agent/agent/prompt/prompt.py`에서 시스템 프롬프트를 수정할 수 있습니다.

### 릴리즈 노트

2025.8.27 ver2
시간과 거래가가 주어졌을떄 자동으로 거래소룰 결정하는 에이전트