from lib import init_driver, profile_scraper

from queue import SimpleQueue


def main():
    driver = init_driver()
    url = r"https://www.allrecipes.com/cook/thiswifecooks/reviews/"
    url_empty = r"https://www.allrecipes.com/cook/22195726/reviews/"
    profile_id_queue: SimpleQueue = SimpleQueue()
    viewed_profiles: set = set()
    review_set: set = set()
    profile_scraper(url, driver, profile_id_queue, viewed_profiles, review_set)
    profile_scraper(url_empty, driver, profile_id_queue, viewed_profiles, review_set)

    print(review_set)
    print("*" * 60)
    print(viewed_profiles)


if __name__ == '__main__':
    main()
