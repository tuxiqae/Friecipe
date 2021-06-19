from time import sleep
from os import environ
import requests

from queue import SimpleQueue


def check_readiness() -> None:
    print("Checking readiness...")
    sleep(5)
    while True:
        if not requests.get(f"http://{environ['SELENIUM']}:4444/wd/hub/status").json()["value"]["ready"]:
            print("Waiting...")
            sleep(0.5)
        else:
            print("Selenium is up and running.")
            return None


def main():
    print("Starting...")
    url = "thiswifecooks"
    url_empty = r"22195726"
    url_404 = r"12696989"
    url_no_followers = r"1133772"
    main_seed = r"16007298"
    profile_id_queue: SimpleQueue = SimpleQueue()
    viewed_profiles: set = set()
    review_set: set = set()
    recipe_set: set = set()

    check_readiness()

    from lib import profile_scraper  # Imported only after readiness check.

    # profile_scraper(url, profile_id_queue, viewed_profiles, review_set, recipe_set)
    # profile_scraper(url_empty, profile_id_queue, viewed_profiles, review_set, recipe_set)
    # profile_scraper(url_404, profile_id_queue, viewed_profiles, review_set, recipe_set)
    # profile_scraper(url_no_followers, profile_id_queue, viewed_profiles, review_set, recipe_set)
    profile_scraper(main_seed, profile_id_queue, viewed_profiles, review_set, recipe_set)

    print(f"Reviews count: {len(review_set)}")
    print("*" * 60)
    print(f"viewed_profiles amount: {len(viewed_profiles)}")
    print("*" * 60)
    print(f"Queued profiles amount: {profile_id_queue.qsize()}")


if __name__ == '__main__':
    main()
