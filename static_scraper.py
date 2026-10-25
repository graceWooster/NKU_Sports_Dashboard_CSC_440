import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_static_site(url, filename):
    response = requests.get(url)
    print("Status code:", response.status_code)

    # turns the request into html
    soup = BeautifulSoup(response.content, "html.parser")
    tables = pd.read_html(url)

    # find all the tables on the page
    table_names_tags = soup.find_all('h2', class_= "sub-heading")
    print("num tables: ", len(tables))
    table_names = [tag.text.strip() for tag in table_names_tags]
    print(table_names)
    print("num table names: ", len(table_names))

    # create filename based on the title of the page
    date_time = datetime.today().strftime("%Y%m%d-%H%M%S")
    page_name = filename + "_" + date_time
    print("page name is:", page_name)

    # save the results to an excel file with the page name
    with pd.ExcelWriter(page_name + ".xlsx") as writer:
        for i, table_name in enumerate(table_names):
            name = table_name.replace("/", "-")
            tables[i].to_excel(writer, sheet_name=name)

    print("Table successfully exported to Excel!")