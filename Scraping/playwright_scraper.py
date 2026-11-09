
from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright


def scrape_dynamic_site(url, filename, output_path=None):

    print("Initializing Playwright and launching browser...")

    all_tables = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print(f"Navigating to: {url}")

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            try:
                page.wait_for_load_state(
                    "networkidle",
                    timeout=20000
                )
            except Exception:
                print("Network did not become idle. Continuing...")

            page.wait_for_timeout(3000)

            print("Checking for HTML tables...")

            table_count = page.locator("table").count()
            print(f"Tables found: {table_count}")

            if table_count > 0:
                try:
                    all_tables = pd.read_html(
                        StringIO(page.content())
                    )
                except ValueError:
                    print("Could not parse page tables.")

            if not all_tables:
                tab_locator = page.locator(".s-tab button")
                tab_count = tab_locator.count()

                print(f"Tabs found: {tab_count}")

                for i in range(tab_count):
                    tab = tab_locator.nth(i)
                    tab_name = tab.inner_text().strip()

                    print(f"Checking tab: {tab_name}")

                    tab.click()
                    page.wait_for_timeout(1500)

                    try:
                        tables = pd.read_html(
                            StringIO(page.content())
                        )
                        all_tables.extend(tables)
                    except ValueError:
                        print(f"No tables found under {tab_name}")

            if not all_tables:
                diagnostic_file = Path(f"{filename}_debug.html")
                diagnostic_file.write_text(
                    page.content(),
                    encoding="utf-8"
                )
                print(f"No tables found. Saved: {diagnostic_file}")

        finally:
            browser.close()

    print(f"Total tables collected: {len(all_tables)}")

    if not all_tables:
        print("Scraping unsuccessful. No Excel file created.")
        return None

    date_time = datetime.today().strftime("%Y%m%d-%H%M%S")

    if output_path is None:
        output_path = Path(f"{filename}_{date_time}.xlsx")
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Export tables to Excel
    with pd.ExcelWriter(
        output_path,
        engine="openpyxl"
    ) as writer:

        sheets_written = 0

        for index, df in enumerate(all_tables):

            df = df.dropna(how="all")

            if df.empty:
                continue

            # Flatten multi-level column headers
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [
                    "_".join(
                        str(level).strip()
                        for level in column
                        if str(level) != "nan"
                        and str(level).strip()
                    )
                    for column in df.columns
                ]

            sheet_name = f"Stats_{index + 1}"

            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

            sheets_written += 1

        if sheets_written == 0:
            pd.DataFrame(
                {"Message": ["No statistics tables available"]}
            ).to_excel(
                writer,
                sheet_name="No Data",
                index=False
            )

    print(f"Success! Statistics saved to {output_path}")

    return output_path

