from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


def _sheet_name(name, used_names):
    cleaned = name.replace("/", "-").replace("\\", "-")
    cleaned = cleaned[:31] or "Stats"
    candidate = cleaned
    suffix = 2

    while candidate in used_names:
        ending = f" ({suffix})"
        candidate = f"{cleaned[:31 - len(ending)]}{ending}"
        suffix += 1

    used_names.add(candidate)
    return candidate


def scrape_static_site(url, filename, output_path=None):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    tables = pd.read_html(StringIO(response.text))

    table_names = [
        tag.get_text(strip=True)
        for tag in soup.find_all("h2", class_="sub-heading")
    ]

    if not table_names:
        raise ValueError(f"No statistics tables found at {url}")

    if output_path is None:
        date_time = datetime.today().strftime("%Y%m%d-%H%M%S")
        output_path = Path(f"{filename}_{date_time}.xlsx")
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    used_names = set()

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for table_name, table in zip(table_names, tables):
            exported_table = table.copy()
            if isinstance(exported_table.columns, pd.MultiIndex):
                exported_table.columns = [
                    str(column[-1]).strip()
                    for column in exported_table.columns
                ]
            exported_table.to_excel(
                writer,
                sheet_name=_sheet_name(table_name, used_names),
                index=False,
            )

    print(f"Statistics workbook saved to {output_path}")
    return output_path