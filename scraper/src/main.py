from time import sleep
import requests
from os import environ

from queue import SimpleQueue


def check_readiness():
    sleep(1)
    while not requests.get(f"http://{environ['SELENIUM']}:4444/wd/hub/status").json()["value"]["ready"]:
        print("Waiting...")
        sleep(0.5)


def main():
    url = r"https://www.allrecipes.com/cook/thiswifecooks/reviews/"
    url_empty = r"https://www.allrecipes.com/cook/22195726/reviews/"
    url_404 = r"https://www.allrecipes.com/cook/12696989/reviews"
    main_seed = r"https://www.allrecipes.com/cook/16007298/"
    profile_id_queue: SimpleQueue = SimpleQueue()
    viewed_profiles: set = set()
    review_set: set = set()
    recipe_set: set = set()

    check_readiness()

    from lib import profile_scraper  # Imported only after readiness check.

    profile_scraper(url, profile_id_queue, viewed_profiles, review_set, recipe_set)
    profile_scraper(url_empty, profile_id_queue, viewed_profiles, review_set, recipe_set)
    profile_scraper(url_404, profile_id_queue, viewed_profiles, review_set, recipe_set)

    print("Reviews:")
    print(review_set)
    print("*" * 60)
    print("viewed_profiles:")
    print(viewed_profiles)
    print("*" * 60)
    print("Queued profiles:")
    while not profile_id_queue.empty():
        print(profile_id_queue.get_nowait())


if __name__ == '__main__':
    main()
