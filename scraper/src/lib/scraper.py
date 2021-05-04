from os import environ
from queue import SimpleQueue
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .review import Review


def init_driver() -> WebDriver:
    options = FirefoxOptions()
    # options.add_argument("--headless")  # TODO: Remove or not
    remote_host = f'http://{environ["SELENIUM"]}:4444/wd/hub'
    return webdriver.Remote(command_executor=remote_host,
                            keep_alive=False,  # TODO: Remove
                            options=options,
                            desired_capabilities=DesiredCapabilities.FIREFOX)


def scroll_down_page(driver: WebDriver) -> bool:
    more_btn = driver.find_element_by_id("moreBtn")

    while driver.find_element_by_class_name("loading-indicator").is_displayed():
        sleep(0.1)

    while True:
        try:
            more_btn.click()
        except ElementNotInteractableException:
            return True
        sleep(1)  # TODO: check if sleep time can be reduced


def scrape_profile_reviews(driver: WebDriver, review_set: set, user_id: str) -> bool:
    if not scroll_down_page(driver):
        return False

    if driver is None:
        return False

    for card in driver.find_element_by_class_name("profile-wrapper").find_elements_by_class_name("profile-review-card"):
        review_set.add(get_review_from_card(card, user_id))


def scrape_contacts(driver: WebDriver, profile_queue: SimpleQueue):
    pass
    # TODO: Implement


def is_profile_empty(driver: WebDriver) -> bool:
    pass


def profile_scraper(url: str, driver: WebDriver, profile_queue: SimpleQueue, viewed_profiles: set, review_set) -> bool:
    try:
        driver.get(url)
    except WebDriverException as err:
        print("Could not open", url, "error:", str(err))

    if driver.find_element_by_class_name("empty-page-header").is_displayed():
        return False

    user_id = driver.current_url.split("/")[4]

    if user_id in viewed_profiles:
        return False  # TODO: Change?
    else:
        viewed_profiles.add(user_id)

    scrape_profile_reviews(driver=driver, review_set=review_set, user_id=user_id)
    scrape_contacts(driver=driver, profile_queue=profile_queue)


def get_review_from_card(review: WebElement, user_id) -> Review:
    recipe_id = review.find_element_by_tag_name("a").get_property("href").split("/")[4]
    try:
        text = review.find_element_by_class_name("rated-review-text").get_property("innerHTML")
    except NoSuchElementException:
        text = None
    stars = review.find_element_by_class_name("stars").get_attribute("data-ratingstars")

    return Review(recipe_id=recipe_id, user_id=user_id, text=text, stars=stars)
