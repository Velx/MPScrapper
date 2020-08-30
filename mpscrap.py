import time
import os
import base64
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def get_driver(browser: str, browser_path: str = None) -> webdriver:
    if browser.lower() == 'firefox':
        return webdriver.Firefox() if not browser_path else webdriver.Firefox(executable_path=browser_path)
    else:
        return webdriver.Chrome() if not browser_path else webdriver.Chrome(executable_path=browser_path)


def download_chapter(driver: webdriver, chapter_url: str):
    driver.get(chapter_url)  # Open chapter

    settings = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, "//div[starts-with(@class, 'Navigation-module_settingsContainer_')]")))  # Find settings button with wait
    settings.click()  # Open settings
    driver.find_elements_by_xpath("//div[starts-with(@class, 'Modal-module_quarity_')]")[2].click()  # Set image quality
    settings.click()  # Open settings again
    driver.execute_script('document.querySelector("input#mode-horizontal").removeAttribute("disabled")')  # Endble horizontal if it disabled
    driver.execute_script('document.querySelector("input#mode-horizontal").click()')  # Turn into horizontal mode
    time.sleep(3)

    title = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/div/div[2]/div[2]/div[3]/div[1]/div[2]/a/h1'))).text  # Wait for page load after refresh
    chapter = driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/p').text[1:]

    title = title.replace(':', '')

    # load all images
    pages = int(driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[2]/div[2]/p').text.split(' / ')[1])
    actions = ActionChains(driver)
    while True:
        actions.send_keys(Keys.LEFT).perform()
        time.sleep(1)
        if driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[2]/div[2]/p').text == f'{pages - 1} / {pages}' or\
                driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[2]/div[2]/p').text == f'{pages} / {pages}':
            break
    os.makedirs(os.path.dirname(f'.//{title}//{chapter}//'), exist_ok=True)
    for page, img in enumerate(driver.find_elements_by_class_name('zao-image'), start=1):
        b64 = driver.execute_script('''function getBase64Image(img)
            {
                var canvas = document.createElement("canvas");
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                var ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0);
                var dataURL = canvas.toDataURL();
                return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
            }
            return getBase64Image(arguments[0])
            ''',
                                    img)
        image_data = base64.b64decode(b64)
        with open(f'.//{title}//{chapter}//{page}.png', 'wb') as file:
            file.write(image_data)

    driver.close()


parser = argparse.ArgumentParser(description='Script to download manga chapters from MP')
parser.add_argument('--browser', '-b',
                    action='store',
                    dest='browser',
                    default='firefox',
                    type=str,
                    help='Choice browser for selenium execution. Support Firefox and Chrome browsers. '
                         'Should be in the PATH if no -p argument is given')
parser.add_argument('--path', '-p',
                    action='store',
                    dest='browser_path',
                    default=None,
                    type=str,
                    help='Path for EXE file of selected browser')
parser.add_argument('--url', '-u',
                    action='store',
                    dest='chapter_url',
                    type=str,
                    required=True,
                    help='Chapter URL on MP. Required.')
options = parser.parse_args()
driver = get_driver(options.browser, options.browser_path)
download_chapter(driver, options.chapter_url)
print('DOWNLOADED')