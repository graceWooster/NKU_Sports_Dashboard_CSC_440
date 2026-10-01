import requests
from bs4 import BeautifulSoup

# website to scrape
url = "https://nkunorse.com/sports/mens-basketball/stats?path=mbball"

response = requests.get(url)
print("Status code:", response.status_code)

# turns the request into html
soup = BeautifulSoup(response.content, "html.parser")
print(soup.prettify())