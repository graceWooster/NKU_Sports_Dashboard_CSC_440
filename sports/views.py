
from pathlib import Path
import re

from django.http import JsonResponse
from openpyxl import load_workbook


BASE_DIR = Path(__file__).resolve().parent.parent
WORKBOOK_PATH = BASE_DIR / "norse_stats.xlsx"
SCHOOL_WORKBOOKS = {
    "nku": WORKBOOK_PATH,
    "detroit": BASE_DIR / "detroit_stats.xlsx",
}

PLAYER_FIELDS = {
    "#": "number",
    "PLAYER": "name",
    "GP": "games_played",
    "MIN": "minutes",
    "FG%": "field_goal_percentage",
    "3PT%": "three_point_percentage",
    "FT%": "free_throw_percentage",
    "OREB": "offensive_rebounds",
    "DREB": "defensive_rebounds",
    "REB": "rebounds",
    "AST": "assists",
    "STL": "steals",
    "BLK": "blocks",
    "PTS": "points",
}

TEAM_STAT_FIELDS = {
    "PPG": "points_per_game",
    "RPG": "rebounds_per_game",
    "APG": "assists_per_game",
    "FG%": "field_goal_percentage",
    "3PT%": "three_point_percentage",
    "FT%": "free_throw_percentage",
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
        if "Player Averages" not in workbook.sheetnames:
            return JsonResponse(
                {"error": "Player Averages sheet not found"},
                status=500,
            )

        sheet = workbook["Player Averages"]
        header_row = None
        header_index = None

        for index, row in enumerate(
            sheet.iter_rows(min_row=1, max_row=5, values_only=True),
            start=1,
        ):
            headers = [
                str(value).strip().upper() if value is not None else ""
                for value in row
            ]
            if {"PLAYER", "GP", "PTS"}.issubset(headers):
                header_row = headers
                header_index = index
                break

        if header_row is None:
            return JsonResponse(
                {"error": "Player Averages headers are not recognized"},
                status=500,
            )

        column_indexes = {
            field: header_row.index(header)
            for header, field in PLAYER_FIELDS.items()
            if header in header_row
        }
        players = []

        for row in sheet.iter_rows(min_row=header_index + 1, values_only=True):
            player_name = row[column_indexes["name"]]

            if not player_name or player_name in ("Total", "Opponents"):
                continue

            name = re.sub(
                r"^\d+\s+",
                "",
                str(player_name).split("  ")[0].strip(),
            )
            player = {"name": name}
            for field, column_index in column_indexes.items():
                if field == "name":
                    continue
                value = row[column_index]
                if field == "number" and isinstance(value, float) and value.is_integer():
                    value = int(value)
                player[field] = value
            players.append(player)

        return JsonResponse(players, safe=False)

    finally:
        workbook.close()


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
        sheet_name = next(
            (name for name in workbook.sheetnames if name.startswith("Team Stats")),
            None,
        )
        if sheet_name is None:
            return JsonResponse(
                {"error": "Team statistics sheet not found"},
                status=500,
            )

        stat_codes = TEAM_STAT_FIELDS
        stats = {}

        sheet = workbook[sheet_name]
        statistic_column = None
        team_column = None

        for row in sheet.iter_rows(min_row=1, max_row=5, values_only=True):
            headers = [
                str(value).strip().upper() if value is not None else ""
                for value in row
            ]
            if "STATISTIC" in headers:
                statistic_column = headers.index("STATISTIC")
                team_column = statistic_column + 1
                break

        if statistic_column is None or team_column is None:
            return JsonResponse(
                {"error": "Team statistics headers are not recognized"},
                status=500,
            )

        for row in sheet.iter_rows(values_only=True):
            label = row[statistic_column]
            if not label:
                continue

            code = str(label).split("  ")[-1]
            if code in stat_codes:
                value = row[team_column]
                if value is not None:
                    stats[stat_codes[code]] = float(value)

        if len(stats) != len(stat_codes):
            return JsonResponse(
                {"error": "Team statistics are incomplete in the workbook"},
                status=500,
            )

        return JsonResponse(stats)

    finally:
        workbook.close()
