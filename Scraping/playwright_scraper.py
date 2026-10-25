from datetime import datetime

import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_dynamic_site(url, filename):

    print("Initializing Playwright and launching browser...")
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Navigating to: {url}")
        # Load the page and wait for network activity to settle (ensures JS-rendered data loads)
        page.goto(url, wait_until="networkidle")

        tab_locator = page.locator(".s-tab button")
        tab_count = tab_locator.count()
        print(f"Tab count: {tab_count}")

        all_tables = []

        for i in range(tab_count):
            tab = tab_locator.nth(i)
            tab_name = tab.inner_text().strip()

            # Click the tab to reveal its content
            tab.click()

            # Wait a moment for the table to render or update
            page.wait_for_timeout(1000)  # or wait for a specific table selector to appear

            # Parse tables visible on the page after clicking the tab
            try:
                tables_on_tab = pd.read_html(page.content())
                for df in tables_on_tab:
                    # Optionally tag or store them with their tab name
                    all_tables.append(df)
            except ValueError:
                print(f"No standard HTML tables found under tab: {tab_name}")
        browser.close()

    print("Parsing rendered HTML tables into DataFrames...")


    print(f"Found {len(all_tables)} table(s). Exporting to multi-sheet Excel...")

    # create filename based on the title of the page
    date_time = datetime.today().strftime("%Y%m%d-%H%M%S")
    page_name = filename + "_" + date_time
    print("page name is:", page_name)

    # Write each table into a separate sheet in a single Excel file
    with pd.ExcelWriter(page_name, engine="openpyxl") as writer:
        for index, df in enumerate(all_tables):
            # Excel sheet names have a strict 31-character limit and cannot contain special characters like / or \
            sheet_name = f"Stat_Table_{index + 1}"

            # Clean up the DataFrame slightly (e.g., removing entirely empty rows/columns if any)
            df = df.dropna(how="all")

            # Write the DataFrame to its own tab
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Success! All tables saved to '{page_name}'.")


if __name__ == "__main__":
    scrape_ysu_basketball_stats()