from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from datetime import datetime
import re
from utils import error, message
from database.sql import SQL

bd = SQL('database/bd.db')
pattern = r'^(https:\/\/www.youtube.com\/channel\/)(.+)(\/videos)'

with open('accounts/youtube.txt') as f:
    acc_youtube = f.readlines()


def get_date():
    date = datetime.today().strftime(f'%H:%M:%S |')
    return date


def check_youtube():
    """Проверяет наличие нового видео на канале"""
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    info = {'video': []}
    for url in acc_youtube:
        channel_name = re.sub(pattern, r'\2', url)
        print(f'{get_date()} Выполняется проверка Youtube канала {channel_name}')
        try:
            driver.get(url)
            sleep(5)
            video = '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/' \
                    'ytd-two-column-browse-results-renderer/div[1]/' \
                    'ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/' \
                    'ytd-grid-video-renderer'
            item = driver.find_element_by_xpath(video)
        except Exception as err:
            error.write_error(f"{get_date()} Youtube, func = check_youtube, open channel url = {err}\n")
            print(f'Youtube | Возникла ошибка при открытии ссылки на Youtube канал.\nКанал: {url}')
            print(err)

        # получаем названия видео.
        # если видео нет, то записываем в бд и отправляем в телегу
        try:
            name = item.text.split('\n')
            if not bd.video_youtube_exists(name[1]):
                bd.write_youtube(channel_name, name[1])
                driver.find_element_by_xpath(video).click()
                print(f'{get_date()} Обнаружено новое видео на Youtube "{name[1]}", отправляю в телеграм.')
                info['video'].append(driver.current_url + '&')
                message.send_message(info)

                print(f'{get_date()} Аккаунт {channel_name} проверен. Пауза на 10 секунд.')
                sleep(10)
            sleep(10)
        except Exception as err:
            error.write_error(f"{get_date()} Youtube, func = check_youtube, get name and send message = {err}\n")
            print(f'Youtube | Возникла ошибка при получении названия видео на Youtube и отправки сообщения в ТГ.')
            print(err)

    driver.quit()
