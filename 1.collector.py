import json
import os
import time

from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slugify import slugify

from utils import get_chromedriver, timeit

load_dotenv()

email = os.environ["email"]
password = os.environ["password"]

assert email
assert password

story_divs = []
total_data = []

post_urls_filename = "post_urls.txt"

output_filename = "output.txt"


@timeit
def collect_image_links():
    post_urls = []

    # blocker postids:
    # 54458579, 51177340 # video only
    # 52800184 # different format: title, not date
    postid_to_restart_from = ""  # TODO change this to full post_url instead of postid so no need to parse below

    driver = get_chromedriver(headless=True)
    assert driver

    login_url = "https://app.storypark.com"
    story_url = "https://app.storypark.com/children/2106370/stories"

    try:
        driver.get(login_url)
    except TimeoutException:
        print("TimeoutException")
        driver.quit()

    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user_password")))
    except NoSuchElementException:
        print("NoSuchElementException")
        return
    time.sleep(3)

    try:
        driver.find_element(by=By.ID, value="user_email").send_keys(email)
        driver.find_element(by=By.ID, value="user_password").send_keys(password)
        driver.find_element(by=By.XPATH, value='//a[@data-action="signin"]').click()
    except NoSuchElementException:
        print("NoSuchElementException")
        return

    time.sleep(4)

    try:
        driver.get(story_url)

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@commentdetails]"))
            )
        except NoSuchElementException:
            print("NoSuchElementException")
            return
        time.sleep(3)

        with open("post_urls.txt", "r") as file:
            post_urls = file.readlines()
        post_urls = [url.replace("\n", "") for url in post_urls]

        # if post_urls not saved in file, scroll and scrape post_urls
        if len(post_urls) == 0:
            print("post_urls not in file, start scrolling")
            scroll_count = 0

            with open(post_urls_filename, "w") as file:
                while True:
                    story_divs = driver.find_elements(by=By.XPATH, value="//div[@commentdetails]")
                    if len(story_divs) == 0:
                        print("story_divs empty")
                        break

                    prev_height = story_divs[-1].location["y"]

                    # scroll
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(5)
                    scroll_count += 1

                    story_divs = driver.find_elements(by=By.XPATH, value="//div[@commentdetails]")
                    new_height = story_divs[-1].location["y"]

                    print(f"scroll_count: {scroll_count}, height: {new_height}")

                    for div in story_divs:
                        post_id = div.get_attribute("storyparkid")
                        post_url = f"https://app.storypark.com/activity/?post_id={post_id}"
                        if post_url not in post_urls:
                            post_urls.append(post_url)
                            print(f"{post_url} saved")
                            file.writelines(f"{post_url}\n")

                    if prev_height == new_height:
                        print(f"reached the end after {scroll_count} scrolls at {new_height}")
                        break

        print(f"post_urls: {len(post_urls)}")

        with open(output_filename, "a") as file:
            for post_url in post_urls:

                if postid_to_restart_from:
                    this_postid = post_url.split("=")[-1]
                    print(f"skipping {this_postid} until postid: {postid_to_restart_from}")
                    if this_postid == postid_to_restart_from:
                        postid_to_restart_from = ""
                    else:
                        continue

                print(f"visiting: {post_url}")
                driver.get(post_url)
                try:
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-item="media-thumb-list"] li img'))
                    )
                except (NoSuchElementException, TimeoutException) as e:
                    print(f"exception finding img: {post_url}")
                    # 'div.vjs-poster' videos
                    pass

                time.sleep(6)

                try:
                    title = driver.find_element(by=By.CSS_SELECTOR, value='div[data-item="thumbnail-list"] h1').text
                    date = driver.find_element(by=By.CSS_SELECTOR, value='span[data-original-title="Story date"]').text
                    imgs = driver.find_elements(by=By.CSS_SELECTOR, value='ul[data-item="media-thumb-list"] li img')
                except NoSuchElementException:
                    try:
                        # https://app.storypark.com/activity/?post_id=52800184
                        # this post doesn't have h1 title and doesn't have date
                        title = driver.find_element(by=By.CSS_SELECTOR, value=".wysiwyg-font-size-large").text
                        date = title.replace(":", " ").split(" ")[-1]
                        imgs = driver.find_elements(
                            by=By.CSS_SELECTOR, value='ul[data-item="media-thumb-list"] li img'
                        )
                    except NoSuchElementException:
                        print("NoSuchElementException again")
                        driver.quit()

                for index, img in enumerate(imgs, start=1):
                    filename = f"{date}__{title}__{index}"
                    filename = slugify(filename, separator="_") + ".jpeg"

                    img_url = img.get_attribute("data-original-src")
                    total_data.append({"name": filename, "src": img_url})
                    file.write(json.dumps({"post_url": post_url, "name": filename, "src": img_url}))
                    file.write("\n")

    except TimeoutException:
        print("TimeoutException")
        driver.quit()


collect_image_links()
