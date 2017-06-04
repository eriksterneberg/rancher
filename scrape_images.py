import os
import shutil
import sys
import requests
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of


"""
Installation instructions

1. $ sudo pip install selenium

2. Install driver
http://selenium-python.readthedocs.io/installation.html

"""

# Settings
target_address = "https://www.instagram.com/justinbieber/"
# END Settings


def find_thumbnails(driver):
    return driver.find_elements_by_xpath("//article/div/div/div/a")


def scrape_item(driver, folder, elem):
    # Open modal
    elem.click()

    # Wait to render

    # Find images to download
    import ipdb; ipdb.set_trace()
    image_elem = driver.find_element_by_xpath("//article/div/div/div/div/img")
    image_src = image_elem.get_property('src')
    response = requests.get(image_src, stream=True)
    output_filepath = "{}/{}".format(folder, os.path.basename(image_src))
    with open(output_filepath, 'wb') as output_file:
        shutil.copyfileobj(response.raw, output_file)
    del response

    print 'Downloaded file', output_filepath

    # Find videos to downloads

    # Print result to terminal

    # Return


if __name__ == "__main__":
    # Setup output folder
    file_dir = os.path.dirname(os.path.realpath(__file__))
    output_folder = "{}/{}".format(file_dir, "downloaded")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Initialize driver
    driver = webdriver.Firefox()

    # Log on to target site
    driver.get(target_address)

    # Click 'Load more' to see more images
    try:
        load_more_btn = driver.find_element_by_xpath("//*[contains(text(), 'Load more')]")
    except NoSuchElementException:
        print 'Could not find "Load more" button.'
        sys.exit()
    load_more_btn.click()

    # Wait for 'Load more' button to disappear
    # try:
    #     timeout = 5
    #     WebDriverWait(driver, 5).until(staleness_of(load_more_btn))
    # except TimeoutException:
    #     print 'Reached timeout when waiting for "Load more" button to disappear.'
    #     sys.exit()

    # Grab all visible pictures
    thumbnail_elements = find_thumbnails(driver)
    for elem in thumbnail_elements[:1]:
        scrape_item(driver, output_folder, elem)

    # Loop: scroll down, wait until new pictures have rendered, grab more
