
from pathlib import Path
import re

from django.http import JsonResponse
from openpyxl import load_workbook


BASE_DIR = Path(__file__).resolve().parent.parent

# All 12 Horizon League school workbooks
SCHOOL_WORKBOOKS = {
    "detroit": BASE_DIR / "detroit_stats.xlsx",
    "nku": BASE_DIR / "nku_stats.xlsx",
    "gbp": BASE_DIR / "gbp_stats.xlsx",
    "csu": BASE_DIR / "csu_stats.xlsx",
    "iui": BASE_DIR / "iui_stats.xlsx",
    "mke": BASE_DIR / "mke_stats.xlsx",
    "niu": BASE_DIR / "niu_stats.xlsx",
    "oakland": BASE_DIR / "oakland_stats.xlsx",
    "rmu": BASE_DIR / "rmu_stats.xlsx",
    "wsu": BASE_DIR / "wsu_stats.xlsx",
    "pfu": BASE_DIR / "pfu_stats.xlsx",
    "ysu": BASE_DIR / "ysu_stats.xlsx",
}


# Standard dashboard fields and accepted workbook column names
PLAYER_FIELDS = {
    "number": ["#", "PLAYER UNIFORM_#"],
    "name": ["PLAYER", "PLAYER NAME_PLAYER"],
    "games_played": ["GP", "GP_GP"],
    "minutes": ["MIN", "MINUTES_MIN"],
    "field_goal_percentage": ["FG%", "FG_FG%"],
    "three_point_percentage": ["3PT%", "3PT_3PT%"],
    "free_throw_percentage": ["FT%", "FT_FT%"],
    "offensive_rebounds": ["OREB", "REBOUNDS_OFF"],
    "defensive_rebounds": ["DREB", "REBOUNDS_DEF"],
    "rebounds": ["REB", "REBOUNDS_TOT"],
    "assists": ["AST", "AST_AST"],
    "steals": ["STL", "STL_STL"],
    "blocks": ["BLK", "BLK_BLK"],
    "points": ["PTS", "SCORING_PTS"],
}


TEAM_STAT_FIELDS = {
    "points_per_game": ["PPG", "POINTS PER GAME"],
    "rebounds_per_game": ["RPG", "REBOUNDS PER GAME"],
    "assists_per_game": ["APG", "ASSISTS PER GAME"],
    "field_goal_percentage": ["FG%", "FG: PERCENTAGE"],
    "three_point_percentage": ["3PT%", "3PT: PERCENTAGE"],
    "free_throw_percentage": ["FT%", "FT: PERCENTAGE"],
}


def _workbook_path(request):
    school = request.GET.get("school", "nku").lower()
    path = SCHOOL_WORKBOOKS.get(school)

    if path is None:
        return None, JsonResponse(
            {"error": f"Unsupported school: {school}"},
            status=400,
        )

    if not path.exists():
        return None, JsonResponse(
            {"error": f"Statistics workbook is not available for {school}"},
            status=404,
        )

    return path, None


def _normalize_header(value):
    if value is None:
        return ""
    return str(value).strip().upper()


def _find_player_sheet(workbook):
    # Static workbooks use Player Averages.
    if "Player Averages" in workbook.sheetnames:
        return workbook["Player Averages"]

    # Dynamic workbooks use Stats_1.
    if "Stats_1" in workbook.sheetnames:
        return workbook["Stats_1"]

    return None


def _find_header_row(sheet):
    for index, row in enumerate(
        sheet.iter_rows(min_row=1, max_row=5, values_only=True),
        start=1,
    ):
        headers = [_normalize_header(value) for value in row]

        has_name = (
            "PLAYER" in headers
            or "PLAYER NAME_PLAYER" in headers
        )

        has_games = "GP" in headers or "GP_GP" in headers
        has_points = "PTS" in headers or "SCORING_PTS" in headers

        if has_name and has_games and has_points:
            return headers, index

    return None, None


def _find_column_indexes(headers):
    indexes = {}

    for field, aliases in PLAYER_FIELDS.items():
        for alias in aliases:
            if alias in headers:
                indexes[field] = headers.index(alias)
                break

    return indexes


def players_list(request):
    workbook_path, error_response = _workbook_path(request)

    if error_response:
        return error_response

    workbook = load_workbook(
        workbook_path,
        read_only=True,
        data_only=True,
    )

    try:
        sheet = _find_player_sheet(workbook)

        if sheet is None:
            return JsonResponse(
                {"error": "Player statistics sheet not found"},
                status=500,
            )

        headers, header_index = _find_header_row(sheet)

        if headers is None:
            return JsonResponse(
                {"error": "Player statistics headers are not recognized"},
                status=500,
            )

        column_indexes = _find_column_indexes(headers)

        if "name" not in column_indexes:
            return JsonResponse(
                {"error": "Player name column not found"},
                status=500,
            )

        players = []

        for row in sheet.iter_rows(
            min_row=header_index + 1,
            values_only=True,
        ):
            name_index = column_indexes["name"]

            if name_index >= len(row):
                continue

            player_name = row[name_index]

            if not player_name:
                continue

            name = re.sub(
                r"^\d+\s+",
                "",
                str(player_name).split("  ")[0].strip(),
            )

            if name.lower() in ("total", "opponents"):
                continue

            player = {"name": name}

            for field, column_index in column_indexes.items():
                if field == "name" or column_index >= len(row):
                    continue

                value = row[column_index]

                if field == "number" and value is not None:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass

                player[field] = value

            players.append(player)

        return JsonResponse(players, safe=False)

    finally:
        workbook.close()


def _find_team_sheet(workbook):
    # Static workbooks use a Team Stats sheet.
    for name in workbook.sheetnames:
        if name.startswith("Team Stats"):
            return workbook[name]

    # Dynamic workbooks use Stats_2.
    if "Stats_2" in workbook.sheetnames:
        return workbook["Stats_2"]

    return None



def _identify_team_stat(label, category=""):
    label = str(label).strip().upper()
    category = str(category).strip().upper()

    for field, aliases in TEAM_STAT_FIELDS.items():
        for alias in aliases:
            if alias in label:
                return field

    if label == "PER GAME":
        if "REBOUND" in category:
            return "rebounds_per_game"
        if "ASSIST" in category:
            return "assists_per_game"

    return None




def team_stats(request):
    workbook_path, error_response = _workbook_path(request)

    if error_response:
        return error_response

    workbook = load_workbook(
        workbook_path,
        read_only=True,
        data_only=True,
    )

    try:
        sheet = _find_team_sheet(workbook)

        if sheet is None:
            return JsonResponse(
                {"error": "Team statistics sheet not found"},
                status=500,
            )

        stats = {}
        current_category = ""

        for row in sheet.iter_rows(values_only=True):
            if len(row) < 2:
                continue

            label = row[0]
            value = row[1]

            if not label:
                continue

            normalized_label = str(label).strip().upper()

            # Remember the current category for dynamic workbooks.
            if normalized_label in [
                "SCORING",
                "SHOOTING",
                "REBOUNDING",
                "ASSISTS",
                "TURNOVERS",
            ]:
                current_category = normalized_label
                continue

            if value is None:
                continue

            field = _identify_team_stat(label, current_category)

            if field is None:
                continue

            try:
                stats[field] = float(value)
            except (ValueError, TypeError):
                continue

        if not stats:
            return JsonResponse(
                {"error": "No team statistics were recognized"},
                status=500,
            )

        return JsonResponse(stats)

    finally:
        workbook.close()
