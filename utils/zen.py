import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup as bs
from time import sleep
from database.sql import SQL
from utils import error, message

with open('accounts/zen.txt') as f:
    acc_zen = f.readlines()

user_agent = {
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 '
                  'Safari/537.36 '
}

bd = SQL('database/bd.db')
pattern = r'(https://www\.youtube\.com/embed/)(.*)(\?.+)'


def get_date():
    date = datetime.today().strftime(f'%H:%M:%S |')
    return date


def check_zen():
    try:
        global driver
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        for url in acc_zen:  # переходим на аккаунт
            driver.get(url)
            print(f'{get_date()} Переходим на аккаунт {url}')
            sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            post = driver.find_element_by_id('zen-row-0')
            post_name = post.text.split('\n')[1]  # название первого поста

            if not bd.post_zen_exists(post_name):
                print(f'{get_date()} Найден новый пост "{post_name}"')
                bd.write_zen(url, post_name)
                soup = bs(driver.page_source, 'html.parser')

                for el in soup.find('div', id='zen-row-0'):
                    href = el.find('div', class_='card-image-2-view__content').find('a').get('href')

                urls_media = scrap_post(href)
                print(f'{get_date()} Отправляем в телеграм')
                message.send_message(urls_media)
                sleep(10)

        driver.quit()
    except Exception as err:
        error.write_error(f"{get_date()} Zen, func = check_zen, err = {err}\n")
        print(f'Zen | Возникла ошибка при проверке аккаунта Yandex Zen.')
        print(err)


def scrap_post(href):
    info = {'img': [], 'video': []}
    print(f'{get_date()} Собираем медиа')
    urls_img = []
    urls_video = []
    driver.get(href)
    count_scroll = 0
    pause_scroll = 3
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(pause_scroll)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
        count_scroll += 1
        if count_scroll >= 5:
            break

    soup = bs(driver.page_source, 'html.parser')
    try:
        for el in soup.find_all('img', itemprop='image'):
            # urls_img.append(el.get('src'))
            info['img'].append(el.get('src'))
    except Exception as err:
        error.write_error(f"{get_date()} zen, func = scrap_post, {err}")
        print(f'ZEN | Изображения не найдены.\nПост: {href}')
    try:
        for el in soup.select('.youtube-embed__iframe'):
            src = el.get('src')
            link_video = re.sub(pattern, r'\2', src)
            # urls_video.append('https://www.youtube.com/watch?v=' + link_video)
            info['video'].append('https://www.youtube.com/watch?v=' + link_video)
    except Exception as err:
        error.write_error(f"{get_date()} zen, func = scrap_post, {err}")
        print(f'ZEN | Видео не найдены.\nПост: {href}')
    return info
