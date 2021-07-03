import datetime
import sys
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pickle
import random
from bs4 import BeautifulSoup as bs
from database.sql import SQL
from utils import error, message
from instascrape import *


BASE_URL = 'https://www.instagram.com'
bd = SQL('database/bd.db')

with open('accounts/instagram.txt') as f:
    acc_instagram = f.readlines()

with open('./config.ini', 'r') as f:
    data = f.read().splitlines()
    login = data[5].split(' = ')[1]
    password = data[6].split(' = ')[1]


def get_date():
    date = datetime.datetime.today().strftime(f'%H:%M:%S |')
    return date


def check_instagram():
    options = FirefoxOptions()
    options.add_argument("--headless")
    global driver
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Firefox()
    auth_inst()

    for url in acc_instagram:
        info = {'img': [], 'video': []}
        print(f'{get_date()} Выполняется проверка Instagram канала {url}')

        driver.get(url)
        sleep(5)
        soup = bs(driver.page_source, 'html.parser')
        try:
            for elem in soup.select('.ySN3v'):
                inst_post = elem.find('a')
                link_post = BASE_URL + inst_post.get('href')

                if not bd.post_instagram_exists(link_post):
                    print(f'{get_date()} Найден новый пост "{link_post}"')
                    bd.write_instagram(url, link_post)

                    if inst_post.find('div', class_='u7YqG'):  # ищем пост видео
                        info['video'].append(link_post)
                        print(f'{get_date()} Отправляю видео в телеграм.')
                    else:
                        info['img'].append(link_post)
                        print(f'{get_date()} Отправляю изображение в телеграм.')

                    path = download_post(info)
                    message.send_message(path, True)
            sleep(20)
        except Exception as err:
            error.write_error(f"{get_date()} Instagram, func = check_instagram, message = {err.args}\n")
            print(err)

    driver.quit()


def download_post(inf):
    info = {'img': [], 'video': []}
    for type_, elem in inf.items():
        if type_ == 'img' and len(elem) != 0:
            for img in elem:
                img_post = Post(img)
                img_post.scrape(webdriver=driver)
                img_post.download('utils/inst_post/img.jpg')
                info['img'].append('utils/inst_post/img.jpg')
                return info
        elif type_ == 'video' and len(elem) != 0:
            for video in elem:
                video_post = Post(video)
                video_post.scrape()
                video_post.download('utils/inst_post/video.mp4')
                info['video'].append('utils/inst_post/video.mp4')
                return info


def auth_inst():
    try:
        print(datetime.datetime.today().strftime(f'%H:%M:%S | Выполняется авторизация в Instagram.'))
        load_cookies()
        driver.get(BASE_URL)
        time.sleep(random.randrange(3, 5))
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'piCib')))
        print(datetime.datetime.today().strftime(f'%H:%M:%S | Авторизация выполнена с помощью cookie.'))
    except TimeoutException:
        print(datetime.datetime.today().strftime(f'%H:%M:%S | Выполняется авторизация в Instagram.'))
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'username')))
        driver.find_element_by_name('username').send_keys(login)
        passwd = driver.find_element_by_name('password')
        passwd.send_keys(password)
        passwd.send_keys(Keys.ENTER)
        time.sleep(3)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div['
                                                                                      '1]/section/nav/div['
                                                                                      '2]/div/div/div[2]/div[1]')))
            print(datetime.datetime.today().strftime(f'%H:%M:%S | Авторизация в Instagram выполнена.'))
            save_cookies()
            sleep(10)
        except TimeoutException:
            driver.quit()
            sys.exit(datetime.datetime.today().strftime(f'%H:%M:%S | Авторизация в Instagram НЕ выполнена.'))


def load_cookies():
    try:
        driver.get('https://www.instagram.com/')
        cookies = pickle.load(open('cookie.bin', "rb"))
        driver.delete_all_cookies()

        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()
    except EOFError:
        pass


def save_cookies():
    pickle.dump(driver.get_cookies(), open('cookie.bin', "wb"))
