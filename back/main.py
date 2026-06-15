from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "side_project_repositories.csv"


def size_group(kb):
    kb = float(kb or 0)
    if kb < 30000:
        return "small"
    if kb < 150000:
        return "medium"
    return "large"


def load_data():
    df = pd.read_csv(DATA_PATH).fillna("")

    num_cols = ["stars", "forks", "open_issues", "watchers", "recommendation_score", "repo_size_kb"]
    text_cols = [
        "name", "full_name", "html_url", "description", "category", "language",
        "topics", "activity_level", "project_type", "project_size"
    ]

    for col in num_cols:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in text_cols:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype(str).fillna("")

    df["project_size"] = df["repo_size_kb"].apply(size_group)
    return df


df = load_data()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    categories: List[str]
    languages: List[str]
    project_size: str = "Any"
    activity_level: Optional[str] = "Any"
    goal: Optional[str] = "learning"
    min_stars: int = 0
    top_n: int = 5
    offset: int = 0


def ordered(values, order):
    values = [v for v in values if str(v).strip()]
    return [x for x in order if x in values] + sorted([x for x in values if x not in order])


@app.get("/")
def root():
    return {"message": "API running"}


@app.get("/health")
def health():
    return {"status": "ok", "rows": len(df), "dataset_path": str(DATA_PATH)}


@app.get("/options")
def options():
    return {
        "categories": ordered(
            df["category"].unique().tolist(),
            ["web_app", "ai_ml", "data_analysis", "automation", "mobile_app", "game"],
        ),
        "languages": ordered(
            df["language"].unique().tolist(),
            ["Python", "JavaScript", "TypeScript", "Jupyter Notebook", "HTML", "CSS", "Java", "C", "C++", "C#", "Go", "Rust", "Kotlin", "Swift", "Dart", "Unknown"],
        ),
        "activities": ordered(
            df["activity_level"].unique().tolist(),
            ["inactive", "moderate", "active", "very_active", "unknown"],
        ),
        "goals": ["learning", "portfolio", "contribution", "quick_build"],
    }


def score(row):
    star = min(row["stars"] / 500 * 30, 30)
    fork = min(row["forks"] / 100 * 30, 30)

    activity = {
        "inactive": 5,
        "moderate": 10,
        "active": 15,
        "very_active": 20,
        "unknown": 8,
    }.get(row["activity_level"], 10)

    issue = 20 if row["open_issues"] < 50 else 10

    return round(star + fork + activity + issue, 1)


def reason(row):
    category = {
        "web_app": "웹 서비스",
        "ai_ml": "AI / 머신러닝",
        "data_analysis": "데이터 분석",
        "automation": "자동화 / 봇",
        "mobile_app": "모바일 앱",
        "game": "게임",
    }.get(row["category"], row["category"])

    size = {
        "small": "소규모",
        "medium": "중규모",
        "large": "대규모",
    }.get(row["project_size"], row["project_size"])

    return [
        f"{category} 분야의 GitHub 공개 프로젝트입니다.",
        f"저장소 용량 기준 {size} 프로젝트입니다.",
        f"주요 언어는 {row['language']}입니다.",
        f"Star {int(row['stars'])}개, Fork {int(row['forks'])}개를 가진 저장소입니다.",
    ]


@app.post("/recommend")
def recommend(req: RecommendRequest):
    data = df.copy()

    data = data[data["category"].isin(req.categories)]
    data = data[data["language"].isin(req.languages)]
    data = data[data["stars"] >= req.min_stars]

    if req.project_size != "Any":
        data = data[data["project_size"] == req.project_size]

    if req.activity_level != "Any":
        data = data[data["activity_level"] == req.activity_level]

    if data.empty:
        data = df[df["category"].isin(req.categories)].copy()

    data["final_score"] = data.apply(score, axis=1)
    data = data.sort_values("final_score", ascending=False)

    start = max(req.offset, 0)
    end = start + req.top_n
    page = data.iloc[start:end]

    results = []

    for _, row in page.iterrows():
        results.append({
            "name": row["name"],
            "full_name": row["full_name"],
            "url": row["html_url"],
            "description": row["description"],
            "category": row["category"],
            "language": row["language"],
            "stars": int(row["stars"]),
            "forks": int(row["forks"]),
            "open_issues": int(row["open_issues"]),
            "watchers": int(row["watchers"]),
            "repo_size_kb": int(row["repo_size_kb"]),
            "topics": row["topics"],
            "project_size": row["project_size"],
            "activity_level": row["activity_level"],
            "project_type": row["project_type"],
            "final_score": row["final_score"],
            "reason": reason(row),
        })

    return {
        "message": "추천 결과를 생성했습니다.",
        "count": len(results),
        "total_candidates": len(data),
        "offset": start,
        "next_offset": end,
        "has_more": end < len(data),
        "results": results,
    }