# HIT140 World Cup 2026: Foundations of Data Science

Group project analysing the 2026 FIFA World Cup (48 teams, 104 matches) in Python.
Team: Arpan Adhikari, Nishan Thapa, Supriya Budhathoki, Abishek Bista.

Assessment 3 (Objective 2): two linear regression tasks, each with exactly 8 pre-match explanatory variables and at most 4 shared between them.
- Task 2.1: predict goal difference (Team A − Team B), 104 matches. Notebook 10.
- Task 2.2: predict goals scored by a team in a match, 208 team-matches. Notebook 11.

## Setup

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

Open the notebooks in VS Code or JupyterLab with the `venv` kernel.

## Repository structure
- `data/raw/`: source data (FBref fixtures and squad ages, FIFA ranking of 11 June 2026); see `data/raw/README.txt` for sources and access dates
- `data/clean/`: feature files and the two regression datasets produced by the notebooks
- `src/common.py`: shared paths, constants, and loaders for the match tables
- `notebooks/`: analysis, to be run in numerical order
- `outputs/figures/`, `outputs/results/`: charts and result tables written by the notebooks

## Notebooks
| Notebook | Purpose |
|---|---|
| 00_shared_data_prep | Loads and checks the raw fixtures; builds the match tables |
| 01-04 | Objective 1 statistical analyses (possession, shots, cards, corners/crosses) |
| 05_arpan_previous_performance | Pre-match team form (shrunk tournament-to-date averages, no look-ahead) |
| 06_nishan_fifa_rating | FIFA ranking and points features |
| 07_supriya_recent_form | Rest days and last-match result features |
| 08_abhi_context_opponent | Host-country advantage, squad age, confederation features |
| 09_team_merge | Merges features into the two model datasets; enforces 8 variables per task, at most 4 shared |
| 10_task21_goal_diff | Task 2.1: hypotheses, EDA, OLS, repeated CV, diagnostics, feature performance, optimisation |
| 11_task22_goals_scored | Task 2.2: the same, with match-grouped CV and clustered p-values |

## Method notes
- All explanatory variables are known before kick-off; early-tournament averages are computed without look-ahead.
- Goals exclude penalty shoot-outs. Team A/Team B follows FBref's listing order; all matches are neutral-site.
- Cross-validation for Task 2.2 is grouped by `Match_ID`, so both rows of a match stay in the same fold.
- Random seed: 42 (`src/common.py`).
