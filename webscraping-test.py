import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

# website to scrape
url = "https://nkunorse.com/sports/mens-basketball/stats?path=mbball"

response = requests.get(url)
print("Status code:", response.status_code)

# turns the request into html
soup = BeautifulSoup(response.content, "html.parser")
# print(soup.prettify())
#
# num_tables = len(soup.find_all('table'))
# table_data = np.array(num_tables)
#
# for table in soup.find_all("table"):
#     table_name = table.find("caption").get_text()
#     table_headers = table.find_all("th")
#     df = pd.DataFrame(table_headers)
#     for tr in table.find_all("tr"):
#         row_data = tr.find_all("td")
#
#
# print("Number of Tables: ", num_tables)
#
tables = pd.read_html(url)

table_names_tags = soup.find_all('h2', class_= "sub-heading")
print("num tables: ", len(tables))
table_names = [tag.text.strip() for tag in table_names_tags]
print(table_names)
print("num table names: ", len(table_names))

with pd.ExcelWriter("norse_stats.xlsx") as writer:
    for i, table_name in enumerate(table_names):
        name = table_name.replace("/", "-")
        tables[i].to_excel(writer, sheet_name=name)

print("Table successfully exported to Excel!")