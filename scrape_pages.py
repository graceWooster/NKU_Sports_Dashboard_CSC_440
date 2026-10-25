from static_scraper import scrape_static_site
from playwright_scraper import scrape_dynamic_site

# Example user selection logic
school_configs = {
    "detroit": {
        "url": "https://detroittitans.com/sports/mens-basketball/stats/2025-26",
        "prefix": "dmtMensBasketballStats",
        "type": "static"
    },
    "nku": {
        "url": "https://nkunorse.com/sports/mens-basketball/stats?path=mbball",
        "prefix": "nkuMensBasketballStats",
        "type": "static"
    },
    "csu": {
        "url": "https://csuvikings.com/sports/mens-basketball/stats",
        "prefix": "csuMensBasketballStats",
        "type": "static"
    },
    "ysu": {
        "url": "https://ysusports.com/sports/mens-basketball/stats/2025-26",
        "prefix": "ysuMensBasketballStats",
        "type": "dynamic"
    }
}

user_choice = "detroit"  # This comes from your UI/selection page
config = school_configs[user_choice]

if config["type"] == "static":
    scrape_static_site(config["url"], config["prefix"])
else:
    scrape_dynamic_site(config["url"], config["prefix"])