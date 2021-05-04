from lib import init_driver, profile_scraper

from queue import Queue


def main():
    driver = init_driver()
    url = r"https://www.allrecipes.com/cook/thiswifecooks/reviews/"
    profile_queue: Queue = Queue()
    viewed_profiles: set = set()
    review_set: set = set()
    profile_scraper(url, driver, profile_queue, viewed_profiles, review_set)

    print(review_set)
    print("*" * 60)
    print(viewed_profiles)


if __name__ == '__main__':
    main()
