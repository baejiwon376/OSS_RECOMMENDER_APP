# OSS_RECOMMENDER_APP

GitHub 공개 저장소를 기반으로 한 사이드 프로젝트 추천 웹 앱입니다.

사용자가 관심 분야, 선호 언어, 프로젝트 활동성, 프로젝트 목적, 프로젝트 규모를 선택하면 조건에 맞는 GitHub 저장소를 추천합니다.

Streamlit은 화면을 담당합니다.
FastAPI는 추천 처리를 담당합니다.
Docker Compose로 두 서비스를 분리해서 실행합니다.
AWS EC2에서 배포했습니다.

---

## 프로젝트 주제

GitHub 사이드 프로젝트 추천 앱

사이드 프로젝트를 해보고 싶을 때 어떤 저장소를 참고하면 좋을지 고르는 용도로 만들었습니다.

단순히 무작위로 추천하지는 않습니다.
사용자가 입력한 조건을 기준으로 CSV 데이터를 필터링합니다.
그 뒤 Star, Fork, 활동성, Issue 수를 기준으로 추천 점수를 계산합니다.
점수가 높은 저장소를 먼저 보여줍니다.

---

## 사용 기술

* Python
* Streamlit
* FastAPI
* Pandas
* Docker
* Docker Compose
* AWS EC2

---

## 전체 구조

```text
사용자 입력
→ Streamlit
→ FastAPI 요청
→ CSV 데이터 필터링
→ 추천 점수 계산
→ JSON 응답 반환
→ Streamlit 결과 출력
```

---

## 폴더 구조

```text
OSS_RECOMMENDER_APP/
├── back/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── front/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── side_project_repositories.csv
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 주요 기능

### 1. 사용자 입력

Streamlit 화면에서 아래 조건을 선택할 수 있습니다.

* 관심 분야
* 선호 언어
* 프로젝트 활동성
* 프로젝트 목적
* 프로젝트 규모
* 한 번에 추천받을 프로젝트 수

---

### 2. FastAPI 추천 처리

Streamlit은 입력값을 FastAPI로 보냅니다.

FastAPI는 입력값을 받아 CSV 데이터를 검색합니다.
조건에 맞는 저장소를 찾습니다.
추천 점수를 계산합니다.
추천 결과를 JSON 형태로 반환합니다.

---

### 3. 추천 점수 기준

추천 점수는 다음 기준을 사용했습니다.

```text
Star 점수
Fork 점수
활동성 점수
Issue 점수
```

Star와 Fork는 저장소의 관심도와 활용도를 보기 위해 사용했습니다.
활동성은 최근 관리 여부를 보기 위해 사용했습니다.
Issue 수는 프로젝트 관리 부담을 보기 위해 사용했습니다.

최종 결과는 추천 점수가 높은 순서로 정렬됩니다.

---

## 실행 방법

Docker Compose를 사용합니다.

프로젝트 폴더에서 아래 명령어를 실행합니다.

```bash
docker compose up -d --build
```

실행 상태 확인:

```bash
docker ps
```

FastAPI 확인:

```bash
curl http://localhost:8000/health
```

Streamlit 접속:

```text
http://localhost:8501
```

---

## API 예시

FastAPI의 `/health` 요청 결과는 다음과 같은 JSON 형태로 나옵니다.

```json
{
  "status": "ok",
  "rows": 13289,
  "dataset_path": "/app/data/side_project_repositories.csv"
}
```

추천 요청은 `/recommend`에서 처리됩니다.
Streamlit이 요청을 보내고, FastAPI가 추천 결과를 JSON으로 반환합니다.

---

## 데이터

데이터는 GitHub 공개 저장소 정보를 기반으로 구성했습니다.

CSV 파일에는 저장소 이름, 설명, 언어, Star 수, Fork 수, Issue 수, 저장소 크기, 활동성, 카테고리 등이 포함되어 있습니다.

이 데이터는 FastAPI에서 읽어 추천 결과를 만드는 데 사용됩니다.

---

## 실행 포트

```text
Streamlit: 8501
FastAPI: 8000
```

Docker와 EC2를 이용해 로컬이 아닌 서버 환경에서도 실행되도록 구성했습니다.
