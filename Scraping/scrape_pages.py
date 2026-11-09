import argparse
from pathlib import Path

if __package__:
    from .static_scraper import scrape_static_site
else:
    from static_scraper import scrape_static_site

BASE_DIR = Path(__file__).resolve().parent.parent

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



def main():
    parser = argparse.ArgumentParser(
        description="Scrape configured school basketball statistics."
    )

    parser.add_argument(
        "school",
        choices=["all"] + list(school_configs.keys()),
        nargs="?",
        default="all",
        help="School to scrape, or all schools."
    )

    args = parser.parse_args()

    schools_to_scrape = (
        school_configs.items()
        if args.school == "all"
        else [(args.school, school_configs[args.school])]
    )

    for school, config in schools_to_scrape:
        print(f"\nScraping {school}...")

        output_path = BASE_DIR / f"{school}_stats.xlsx"

        try:
            if config["type"] == "static":
                scrape_static_site(
                    config["url"],
                    config["prefix"],
                    output_path
                )
            else:
                if __package__:
                    from .playwright_scraper import scrape_dynamic_site
                else:
                    from playwright_scraper import scrape_dynamic_site

                scrape_dynamic_site(
                    config["url"],
                    config["prefix"],
                    output_path
                )

            print(f"Finished scraping {school}")

        except Exception as error:
            print(f"Failed to scrape {school}: {error}")


if __name__ == "__main__":
    main()
