from static_scraper import scrape_static_site
from Scraping.playwright_scraper import scrape_dynamic_site

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
    "gbp": {
        "url": "https://greenbayphoenix.com/sports/mens-basketball/stats/2025-26",
        "prefix": "gbpMensBasketballStats",
        "type": "static"
    },
    "csu": {
        "url": "https://csuvikings.com/sports/mens-basketball/stats",
        "prefix": "csuMensBasketballStats",
        "type": "static"
    },
    "iui": {
        "url": "https://iuindyjags.com/sports/mens-basketball/stats/2025-2026",
        "prefix": "iuijMensBasketballStats",
        "type": "static"
    },
    "mke": {
        "url": "https://mkepanthers.com/sports/mens-basketball/stats/2025-26",
        "prefix": "mkeMensBasketballStats",
        "type": "static"
    },
    "niu": {
        "url": "https://niuhuskies.com/sports/mens-basketball/stats",
        "prefix": "niuMensBasketballStats",
        "type": "static"
    },
    "oakland": {
        "url": "https://goldengrizzlies.com/sports/mens-basketball/stats",
        "prefix": "ouMensBasketballStats",
        "type": "static"
    },
    "rmu": {
        "url": "https://rmucolonials.com/sports/mens-basketball/stats/2025-26?path=mbball",
        "prefix": "rmuMensBasketballStats",
        "type": "static"
    },
    "wsu": {
        "url": "https://wsuraiders.com/sports/mens-basketball/stats/2025-26",
        "prefix": "wsuMensBasketballStats",
        "type": "dynamic"
    },
    "pfu": {
        "url": "https://gomastodons.com/sports/mens-basketball/stats/2025-26",
        "prefix": "pfuMensBasketballStats",
        "type": "dynamic"
    },
    "ysu": {
        "url": "https://ysusports.com/sports/mens-basketball/stats/2025-26",
        "prefix": "ysuMensBasketballStats",
        "type": "dynamic"
    }
}

user_choice = "detroit"
config = school_configs[user_choice]

if config["type"] == "static":
    scrape_static_site(config["url"], config["prefix"])
else:
    scrape_dynamic_site(config["url"], config["prefix"])