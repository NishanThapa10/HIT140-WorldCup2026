"""
common.py - shared helpers for HIT140 Assessment 3 (Objective 2)

Every team member's notebook imports from here, so the fixtures are cleaned in
ONE place and everybody works from identical match data.

Project layout (paths are found automatically, whichever folder you run from):
    HIT140-WorldCup2026/
      data/raw/         original inputs (never edited by code)
      data/clean/       files produced by our code
      notebooks/        one notebook per team member
      src/              shared code (this file)
      outputs/          figures/ and results/ produced by the notebooks
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# Paths (relative to the project root, i.e. the folder above /src)
# ------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "clean"
FIGURES = BASE / "outputs" / "figures"
RESULTS = BASE / "outputs" / "results"
for folder in (PROCESSED, FIGURES, RESULTS):
    folder.mkdir(parents=True, exist_ok=True)

# Shared modelling constants
SEED = 42
# Neutral prior for goals per team per match: the 2022 World Cup averaged
# 2.69 goals per match, i.e. 1.345 per team. Known BEFORE the 2026 tournament,
# so it can be used without leaking any 2026 information.
PRIOR_GOALS = 1.35

# ------------------------------------------------------------------
# Fixtures cleaning
# ------------------------------------------------------------------
NAME_FIX = {                      # spelling standardised so all files merge
    "Bosnia–Herz": "Bosnia-Herz",
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Curaçao": "Curacao",
    "Türkiye": "Turkiye",
}
STAGE_LEVEL = {"Group stage": 1, "Round of 32": 2, "Round of 16": 3,
               "Quarter-finals": 4, "Semi-finals": 5,
               "Third-place match": 5, "Final": 6}
_SCORE = re.compile(r"^(?:\((\d+)\)\s*)?(\d+)[–-](\d+)(?:\s*\((\d+)\))?$")


def _clean_home(name):
    """'Mexico mx' -> 'Mexico' (FBref appends a country code to home teams)."""
    return re.sub(r"\s+[a-z]{2,3}$", "", name.strip())


def _clean_away(name):
    """'za South Africa' -> 'South Africa' (code is a prefix for away teams)."""
    return re.sub(r"^[a-z]{2,3}\s+", "", name.strip())


def _parse_score(text):
    """'2–0' -> (2, 0, False); '(3) 1–1 (4)' -> (1, 1, True) (penalty shoot-out)."""
    m = _SCORE.match(str(text).strip())
    if not m:
        raise ValueError(f"Unparseable score: {text!r}")
    pen_a, goals_a, goals_b, _ = m.groups()
    return int(goals_a), int(goals_b), pen_a is not None


def load_matches():
    """One row per match (104 rows). Goals are goals in play (90 min + extra
    time); penalty shoot-out goals are NOT counted."""
    raw = pd.read_csv(RAW / "fixtures_raw.csv")
    raw["Team_A"] = raw["Home"].apply(_clean_home).replace(NAME_FIX)
    raw["Team_B"] = raw["Away"].apply(_clean_away).replace(NAME_FIX)

    parsed = raw["Score"].apply(_parse_score)
    raw["Goals_A"] = [p[0] for p in parsed]
    raw["Goals_B"] = [p[1] for p in parsed]
    raw["Shootout"] = [p[2] for p in parsed]
    raw["Extra_Time"] = raw["Notes"].fillna("").str.contains("extra time", case=False)

    raw["Date"] = pd.to_datetime(raw["Date"])
    raw["Stage_Level"] = raw["Round"].map(STAGE_LEVEL)
    raw["Knockout"] = (raw["Round"] != "Group stage").astype(int)
    raw["Match_ID"] = np.arange(1, len(raw) + 1)          # FBref lists matches in date order
    raw["Goal_Diff"] = raw["Goals_A"] - raw["Goals_B"]

    keep = ["Match_ID", "Round", "Stage_Level", "Knockout", "Date", "Venue",
            "Team_A", "Team_B", "Goals_A", "Goals_B", "Goal_Diff",
            "Extra_Time", "Shootout"]
    matches = raw[keep].sort_values(["Date", "Match_ID"]).reset_index(drop=True)
    assert len(matches) == 104, f"expected 104 matches, found {len(matches)}"
    return matches


def load_team_matches():
    """One row per team per match (208 rows), sorted by team then date."""
    m = load_matches()
    common_cols = ["Match_ID", "Round", "Stage_Level", "Knockout", "Date", "Venue"]
    side_a = m[common_cols].assign(Team=m["Team_A"], Opponent=m["Team_B"],
                                   Goals_For=m["Goals_A"], Goals_Against=m["Goals_B"])
    side_b = m[common_cols].assign(Team=m["Team_B"], Opponent=m["Team_A"],
                                   Goals_For=m["Goals_B"], Goals_Against=m["Goals_A"])
    tm = pd.concat([side_a, side_b], ignore_index=True)
    tm = tm.sort_values(["Team", "Date", "Match_ID"]).reset_index(drop=True)
    assert len(tm) == 208 and tm["Team"].nunique() == 48
    return tm


# ------------------------------------------------------------------
# Self-test: run  python src/common.py  to check the fixtures load correctly
# ------------------------------------------------------------------
if __name__ == "__main__":
    m = load_matches()
    t = load_team_matches()
    print(f"Matches: {len(m)} | Team-match rows: {len(t)} | Teams: {t['Team'].nunique()}")
    print(m.head(3)[["Match_ID", "Round", "Date", "Team_A", "Goals_A", "Goals_B", "Team_B"]].to_string(index=False))