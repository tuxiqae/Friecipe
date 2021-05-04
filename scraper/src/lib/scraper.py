from os import environ
from queue import SimpleQueue
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import invisibility_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from .review import Review


def init_driver() -> WebDriver:
    options = FirefoxOptions()
    # options.add_argument("--headless")  # TODO: Remove or not
    remote_host = f'http://{environ["SELENIUM"]}:4444/wd/hub'

    return webdriver.Remote(command_executor=remote_host,
                            keep_alive=False,  # TODO: Remove
                            options=options,
                            desired_capabilities=DesiredCapabilities.FIREFOX)


DRIVER = init_driver()


def wait_for_load() -> None:
    WebDriverWait(DRIVER, 10).until(invisibility_of_element_located((By.CLASS_NAME, "loading-indicator")))


def scroll_down_page() -> bool:
    more_btn = DRIVER.find_element_by_id("moreBtn")

    while True:
        try:
            more_btn.click()
        except ElementNotInteractableException:
            return True
        sleep(1)  # TODO: check if sleep time can be reduced


def scrape_profile_reviews(review_set: set, profile_id: str) -> bool:
    wait_for_load()

    if not scroll_down_page():
        return False

    for card in DRIVER.find_element_by_class_name("profile-wrapper").find_elements_by_class_name("profile-review-card"):
        review_set.add(get_review_from_card(card, profile_id))

    return True


def scrape_contacts(profile_queue: SimpleQueue, profile_id: str, peer_type: str):
    DRIVER.get(f"https://www.allrecipes.com/cook/{profile_id}/{peer_type}/")
    wait_for_load()
    scroll_down_page()

    for contact in DRIVER.find_elements(By.CLASS_NAME, "cook-tile"):
        profile_queue.put(get_id_from_url(contact.find_element(By.TAG_NAME, "a").get_property("href")))


def is_profile_empty() -> bool:
    return DRIVER.find_element_by_class_name("empty-page-header").is_displayed()


def is_valid_profile() -> bool:
    try:
        DRIVER.find_element(By.CLASS_NAME, "error-page")
    except NoSuchElementException:
        return True

    return False


def load_page(url: str):
    try:
        DRIVER.get(url)
    except WebDriverException as err:
        print("Could not open", url, "error:", str(err))


def is_known_profile(profile_id: str, viewed_profiles: set) -> bool:
    old_len = len(viewed_profiles)
    viewed_profiles.add(profile_id)

    if old_len == len(viewed_profiles):  # Check if profile_id in set
        return True
    return False


def get_id_from_url(url: str) -> str:
    return url.split("/")[4]


def profile_scraper(url: str,
                    profiles: SimpleQueue,
                    viewed_profiles: set,
                    reviews: set,
                    recipes: set) -> bool:
    load_page(url)
    profile_id = get_id_from_url(DRIVER.current_url)

    if is_known_profile(profile_id, viewed_profiles) or not is_valid_profile():
        return False

    if not is_profile_empty():
        scrape_profile_reviews(review_set=reviews, profile_id=profile_id)

    scrape_contacts(profiles, profile_id, "followers")
    scrape_contacts(profiles, profile_id, "following")

    print(f"Finished scraping profile: '{profile_id}'")


def get_review_from_card(review: WebElement, user_id) -> Review:
    recipe_id = review.find_element_by_tag_name("a").get_property("href").split("/")[4]
    try:
        text = review.find_element_by_class_name("rated-review-text").get_property("innerHTML")
    except NoSuchElementException:
        text = None
    stars = review.find_element_by_class_name("stars").get_attribute("data-ratingstars")

    return Review(recipe_id=recipe_id, user_id=user_id, text=text, stars=stars)
