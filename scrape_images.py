import os
import shutil
import requests
import uuid
import codecs
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


TARGET_ADDRESS = "https://www.instagram.com/justinbieber/"

RELATIVE_OUTPUT_FOLDER = "download"


def create_folder_if_not_exists():
    file_dir = os.path.dirname(os.path.realpath(__file__))
    output_folder = "{}/{}".format(file_dir, RELATIVE_OUTPUT_FOLDER)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    return output_folder


def dumb_wait(fn, *args, **kwargs):
    """
    Naive implementation of wait: sleeps for 1 second between tries
    """
    tries = 10
    while tries > 0:
        result = fn(*args, **kwargs)
        if result:
            return result
        else:
            time.sleep(1)
            tries -= 1
    return []


def find_thumbnails(driver):
    return driver.find_elements_by_xpath("(//article/div/div/div/a)[position()>last()-12]")


def find_images(driver):
    return driver.find_elements_by_xpath("(//article[last()])/div/div/div/div/img")


def find_comments(driver):
    comment_nodes = driver.find_elements_by_xpath("//article/div/div/ul/li")
    return comment_nodes[1:] if comment_nodes else []


def parse_comments(comment_nodes):
    comments = []
    for comment_node in comment_nodes:

        if comment_node.text == 'load more comments':
            continue

        # Each comment has a name in the 'title' attribute in an <a>
        a_node = comment_node.find_element_by_xpath("a")
        commenter_name = a_node.get_property('title')

        # And the comment in a <span>
        comment_str = comment_node.text

        # Todo: also include any @name
        comment = '\t'.join([commenter_name, comment_str])
        comments.append(comment)
    return comments


def save_comments(folder, comments, unique_id):
    output_filepath = "{folder}/{unique_id}_comments.txt".format(
        folder=folder, unique_id=unique_id)
    data = '\n'.join(comments)
    with codecs.open(output_filepath, "w", "utf-8") as file_handle:
        file_handle.write(data)


def scrape_item(driver, folder, elem):
    # Open modal
    elem.click()

    # Get a unique ID for file naming
    unique_id = uuid.uuid1()

    # Get and save images
    image_elems = dumb_wait(find_images, driver)

    for elem in image_elems:
        image_src = elem.get_property('src')
        response = requests.get(image_src, stream=True)
        output_filepath = "{folder}/{unique_id}_{file_base_name}".format(
            folder=folder,
            unique_id=unique_id,
            file_base_name=os.path.basename(image_src),
        )
        with open(output_filepath, 'wb') as output_file:
            shutil.copyfileobj(response.raw, output_file)
        print 'Downloaded file', output_filepath

    # Get and save comments
    comment_nodes = find_comments(driver)
    comments = parse_comments(comment_nodes)
    save_comments(folder, comments, unique_id)

    # Todo: handle videos (currently skip)
    # Todo: handle multiple images (currently saves only first)

    # Return to main
    elem.send_keys(Keys.ESCAPE)


def download_12_items(driver, output_folder):
    for elem in find_thumbnails(driver):
        scrape_item(driver, output_folder, elem)


def main():
    # 1. Setup output folder
    output_folder = create_folder_if_not_exists()

    # 2. Initialize driver
    driver = webdriver.Firefox()

    # 3. Log on to target site
    driver.get(TARGET_ADDRESS)

    # 4. Loop: download 12 items (will automatically lazy load 12 more)
    while True:
        download_12_items(driver, output_folder)


if __name__ == "__main__":
    main()
