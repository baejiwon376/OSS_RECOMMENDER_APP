import os
import requests
import streamlit as st


API = os.getenv("API_URL", "http://127.0.0.1:8000")

CAT = {
    "web_app": "웹 서비스",
    "ai_ml": "AI / 머신러닝",
    "data_analysis": "데이터 분석",
    "automation": "자동화 / 봇",
    "mobile_app": "모바일 앱",
    "game": "게임",
}

SIZE = {"Any": "전체", "small": "소규모", "medium": "중규모", "large": "대규모"}

ACT = {
    "Any": "상관없음",
    "inactive": "낮음",
    "moderate": "보통",
    "active": "활발",
    "very_active": "매우 활발",
    "unknown": "알 수 없음",
}

GOAL = {
    "learning": "학습용",
    "portfolio": "포트폴리오용",
    "contribution": "오픈소스 기여용",
    "quick_build": "빠른 구현용",
}

DEFAULT = {
    "categories": list(CAT),
    "languages": ["Python", "JavaScript", "TypeScript", "Jupyter Notebook", "HTML", "CSS", "Java", "Unknown"],
    "activities": ["inactive", "moderate", "active", "very_active", "unknown"],
    "goals": list(GOAL),
}


st.set_page_config(page_title="GitHub 사이드 프로젝트 추천 앱", layout="wide")


def label(dic, x):
    return dic.get(x, x)


def short(x, n=30):
    x = str(x)
    return x[:n] + "..." if len(x) > n else x


def num(x):
    try:
        return int(float(x))
    except Exception:
        return 0


def get_options():
    try:
        data = requests.get(f"{API}/options", timeout=30).json()
    except Exception:
        data = {}

    return {k: data.get(k) or v for k, v in DEFAULT.items()}


def get_health():
    try:
        return requests.get(f"{API}/health", timeout=30).json()
    except Exception:
        return {"status": "error", "rows": "확인 불가"}


def get_recommend(data):
    r = requests.post(f"{API}/recommend", json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def payload():
    return {
        "categories": categories,
        "languages": languages,
        "project_size": project_size,
        "activity_level": activity,
        "goal": goal,
        "min_stars": 0,
        "top_n": int(top_n),
        "offset": int(st.session_state.offset),
    }


def search():
    try:
        st.session_state.result = get_recommend(payload())
    except Exception as e:
        st.error("추천 요청 실패")
        st.write(e)


def card(p, i):
    with st.container(border=True):
        st.markdown(f"### {i}. {short(p.get('name', '이름 없음'))}")
        st.caption(f"저장소: {p.get('full_name', '')}")
        st.write(p.get("description") or "설명이 등록되지 않은 저장소입니다.")

        st.write(
            f"**분야:** {label(CAT, p.get('category', ''))} | "
            f"**규모:** {label(SIZE, p.get('project_size', ''))} | "
            f"**언어:** {p.get('language', 'Unknown')} | "
            f"**활동성:** {label(ACT, p.get('activity_level', 'unknown'))}"
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Star", num(p.get("stars", 0)))
        c2.metric("Fork", num(p.get("forks", 0)))
        c3.metric("Issue", num(p.get("open_issues", 0)))
        c4.metric("용량(KB)", num(p.get("repo_size_kb", 0)))
        c5.metric("추천 점수", p.get("final_score", 0))

        with st.expander("추천 이유 보기"):
            for r in p.get("reason", []):
                st.write(f"- {r}")

        if p.get("topics"):
            with st.expander("Topics 보기"):
                st.write(p["topics"])

        if p.get("url"):
            st.link_button("GitHub 저장소 열기", p["url"])


for key, val in {"offset": 0, "result": None, "last_filter": None}.items():
    if key not in st.session_state:
        st.session_state[key] = val


options = get_options()

st.title("GitHub 사이드 프로젝트 추천 앱")

left, right = st.columns([1, 2])


with left:
    st.header("1. API 연결")
    st.write(f"API 주소: `{API}`")

    if st.button("API 연결 상태 확인", use_container_width=True):
        h = get_health()
        if h.get("status") == "ok":
            st.success("FastAPI 연결 성공")
            st.write(f"데이터 행 수: **{h.get('rows')}개**")
        else:
            st.error("FastAPI 연결 실패")

    st.header("2. 추천 조건")

    categories = st.multiselect(
        "관심 분야",
        options["categories"],
        default=["web_app"],
        format_func=lambda x: label(CAT, x),
    )

    languages = st.multiselect(
        "선호 언어",
        options["languages"],
        default=["Python"],
    )

    activity = st.selectbox(
        "프로젝트 활동성",
        ["Any"] + options["activities"],
        format_func=lambda x: label(ACT, x),
    )

    goal = st.selectbox(
        "프로젝트 목적",
        options["goals"],
        format_func=lambda x: label(GOAL, x),
    )

    project_size = st.radio(
        "프로젝트 규모",
        ["Any", "small", "medium", "large"],
        horizontal=True,
        format_func=lambda x: label(SIZE, x),
    )

    top_n = st.slider("한 번에 추천받을 프로젝트 수", 3, 10, 5)

    now = {
        "categories": categories,
        "languages": languages,
        "activity": activity,
        "goal": goal,
        "project_size": project_size,
        "top_n": top_n,
    }

    if now != st.session_state.last_filter:
        st.session_state.offset = 0
        st.session_state.result = None
        st.session_state.last_filter = now

    if st.button("추천 요청하기", type="primary", use_container_width=True):
        st.session_state.offset = 0
        search()

    with st.expander("FastAPI 요청 데이터 보기"):
        st.json(payload())


with right:
    st.header("3. 추천 결과")

    c1, c2 = st.columns(2)

    if c1.button("◀ 이전 페이지", use_container_width=True):
        st.session_state.offset = max(0, st.session_state.offset - int(top_n))
        search()

    if c2.button("다음 페이지 ▶", use_container_width=True):
        st.session_state.offset += int(top_n)
        search()

    result = st.session_state.result

    if result is None:
        st.info("추천 조건을 선택한 뒤 추천 요청하기를 누르세요.")
    else:
        count = result.get("count", 0)
        total = result.get("total_candidates", 0)
        offset = result.get("offset", 0)

        st.success(result.get("message"))

        if count:
            st.write(f"전체 후보 **{total}개** 중 **{offset + 1}번째 ~ {offset + count}번째** 추천입니다.")
        else:
            st.warning("조건에 맞는 프로젝트가 없습니다.")

        with st.expander("FastAPI JSON 응답 원본 보기"):
            st.json(result)

        for i, p in enumerate(result.get("results", []), offset + 1):
            card(p, i)

        if result.get("has_more") is False:
            st.info("더 이상 추천할 프로젝트가 없습니다.")


st.divider()