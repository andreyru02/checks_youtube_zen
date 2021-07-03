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
import requests
import wget
import datetime
import sys
import re
from time import sleep
from database.sql import SQL
from utils import error, message

BASE_URL = 'https://www.pinterest.com'
bd = SQL('database/bd.db')
pattern = r'(https://i.pinimg.com/)(\d*)(.*)'

with open('accounts/pinterest.txt') as f:
    acc_pinterest = f.readlines()

with open('./config.ini', 'r') as f:
    data = f.read().splitlines()
    login = data[7].split(' = ')[1]
    password = data[8].split(' = ')[1]


def get_date():
    date = datetime.datetime.today().strftime(f'%H:%M:%S |')
    return date


def check_pinterest():
    options = FirefoxOptions()
    options.add_argument("--headless")
    global driver
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Firefox()
    auth_pinterest()

    for url in acc_pinterest:
        info = {'img': [], 'video': []}
        print(f'{get_date()} Выполняется проверка Pinterest канала {url}')

        driver.get(url)
        sleep(5)

        soup = bs(driver.page_source, 'html.parser')
        try:
            for elem in soup.select('.Hb7'):
                link_post = BASE_URL + elem.find('a', class_='LIa').get('href')
                is_video = elem.find('div', class_='__gestaltThemeVideo')
                break

            if not bd.post_pinterest_exists(link_post):
                print(f'{get_date()} Найден новый пост "{link_post}"')
                bd.write_pinterest(url, link_post)

                # проверка на наличие видео, если видео, то запускаем функцию скачивания и отправляем в ТГ
                if is_video:
                    path = download_video(link_post)
                    info['video'].append(path)
                    message.send_message(info, True)
                    continue

                driver.get(link_post)
                sleep(5)

                soup = bs(driver.page_source, 'html.parser')
                img_l = []
                for img in soup.find_all('img', class_='MIw'):
                    img_l.append(img.get('src'))

                sort_size_img = {}
                for img in img_l:
                    size = re.sub(pattern, r'\2', img)
                    sort_size_img[img] = int(size)

                sort_list = list(sort_size_img.items())
                sort_list.sort(key=lambda i: i[1])

                info['img'].append(sort_list[-1][0])

                print(f'{get_date()} Отправляем в телеграм')
                message.send_message(info)
            sleep(20)
        except Exception as err:
            error.write_error(f"{get_date()} Pinterest, func = check_pinterest, message = {err.args}\n")
            print(err)

    driver.quit()


def download_video(link):
    resp = requests.get('https://pinterest-video-api.herokuapp.com/' + link)
    wget.download(resp, 'utils/pinterest_post/video.mp4')

    return 'utils/pinterest_post/video.mp4'


def auth_pinterest():
    try:
        print(datetime.datetime.today().strftime(f'%H:%M:%S | Выполняется авторизация в Pinterest.'))
        load_cookies()
        driver.get(BASE_URL)
        sleep(random.randrange(3, 5))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'appContent')))
        print(datetime.datetime.today().strftime(f'%H:%M:%S | Авторизация выполнена с помощью cookie.'))
    except TimeoutException:
        print(datetime.datetime.today().strftime(f'%H:%M:%S | Выполняется авторизация в Pinterest.'))
        button_login = '/html/body/div[1]/div[1]/div/div/div/div[1]/div[1]/div[2]/div[2]/button'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, button_login)))
        driver.find_element_by_xpath(button_login).click()  # кликаем войти
        driver.find_element_by_id('email').send_keys(login)
        passwd = driver.find_element_by_id('password')
        passwd.send_keys(password)
        passwd.send_keys(Keys.ENTER)
        sleep(3)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'appContent')))
            print(datetime.datetime.today().strftime(f'%H:%M:%S | Авторизация в Pinterest выполнена.'))
            save_cookies()
            sleep(10)
        except TimeoutException:
            driver.quit()
            sys.exit(datetime.datetime.today().strftime(f'%H:%M:%S | Авторизация в Pinterest НЕ выполнена.'))


def load_cookies():
    try:
        driver.get(BASE_URL)
        cookies = pickle.load(open('cookie_pinterest.bin', "rb"))
        driver.delete_all_cookies()

        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()
    except EOFError:
        pass


def save_cookies():
    pickle.dump(driver.get_cookies(), open('cookie_pinterest.bin', "wb"))
