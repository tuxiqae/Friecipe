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
    print("Initializing driver...")
    options = FirefoxOptions()
    # Disable CSS
    # options.set_preference('permissions.default.stylesheet', 2)
    # Disable images
    # options.set_preference('permissions.default.image', 2)
    # Disable Flash
    # options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    # options.add_argument("--headless")  # TODO: Remove or not
    remote_host = f'http://{environ["SELENIUM"]}:4444/wd/hub'

    remote = webdriver.Remote(command_executor=remote_host,
                              keep_alive=False,  # TODO: Remove
                              options=options,
                              desired_capabilities=DesiredCapabilities.FIREFOX)
    print("Finished initializing driver...")
    return remote


DRIVER = init_driver()


def wait_for_load() -> None:
    WebDriverWait(DRIVER, 10).until(invisibility_of_element_located((By.CLASS_NAME, "loading-indicator")))


def scroll_down_page() -> None:
    more_btn = DRIVER.find_element_by_id("moreBtn")

    while True:
        try:
            more_btn.click()
        except ElementNotInteractableException:
            return None
        sleep(1)  # TODO: check if sleep time can be reduced


def scrape_profile_reviews(review_set: set, profile_id: str) -> None:
    wait_for_load()
    scroll_down_page()

    count = 0
    for card in DRIVER.find_element_by_class_name("profile-wrapper").find_elements_by_class_name("profile-review-card"):
        count += 1
        if count % 100 == 0:
            print(f"Scraped {count} reviews.")
        review_set.add(get_review_from_card(card, profile_id))

    print(f"{count} reviews were collected.")


def format_profile_link(profile_id: str, route: str):
    return f"https://www.allrecipes.com/cook/{profile_id}/{route}/"


def scrape_contacts(profile_queue: SimpleQueue, profile_id: str, peer_type: str):
    url = format_profile_link(profile_id, peer_type)
    DRIVER.get(url)
    wait_for_load()
    scroll_down_page()

    count = 0
    for contact in DRIVER.find_elements(By.CLASS_NAME, "cook-tile"):
        contact_id = get_id_from_url(contact.find_element(By.TAG_NAME, "a").get_property("href"))
        count += 1
        if count % 100 == 0:
            print(f"Scraped {count} contacts")
        profile_queue.put(contact_id)

    print(f"{count} {peer_type.rstrip('s') + 's'} were collected.")


def is_profile_empty() -> bool:
    return DRIVER.find_element_by_class_name("empty-page-header").is_displayed()


def is_valid_profile() -> bool:
    try:
        DRIVER.find_element(By.CLASS_NAME, "error-page")
    except NoSuchElementException:
        return True

    return False


def navigate_profile(profile_id: str) -> None:
    url = format_profile_link(profile_id, "reviews")

    try:
        DRIVER.get(url)
    except WebDriverException as err:
        print("Could not open", url, "error:", str(err))


def append_if_unknown(item: str, viewed: set) -> bool:
    prev_len = len(viewed)
    viewed.add(item)

    if prev_len == len(viewed):  # Check if item in set
        return False
    return True


def get_id_from_url(url: str) -> str:
    return url.split("/")[4]


def profile_scraper(profile_id: str,
                    profiles: SimpleQueue[str],
                    viewed_profiles: set[str],
                    reviews: set[Review],
                    recipes: set) -> bool:
    print(f"Started scraping profile: '{profile_id}'")
    navigate_profile(profile_id)

    if not append_if_unknown(profile_id, viewed_profiles) or not is_valid_profile():
        return False

    if not is_profile_empty():
        scrape_profile_reviews(review_set=reviews, profile_id=profile_id)

    scrape_contacts(profiles, profile_id, "followers")
    scrape_contacts(profiles, profile_id, "following")

    print(f"Finished scraping profile: '{profile_id}'")
    print("*" * 60)


def get_review_from_card(review: WebElement, user_id) -> Review:
    recipe_id = review.find_element_by_tag_name("a").get_property("href").split("/")[4]
    try:
        text = review.find_element_by_class_name("rated-review-text").get_property("innerHTML")
    except NoSuchElementException:
        text = None
    stars = review.find_element_by_class_name("stars").get_attribute("data-ratingstars")

    return Review(recipe_id=recipe_id, profile_id=user_id, text=text, stars=stars)
