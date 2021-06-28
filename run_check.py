from time import sleep
from utils import youtube, zen

with open('./config.ini', 'r') as f:
    data = f.read().splitlines()
    wait = data[4].split(' = ')[1]


def run():
    while True:
        youtube.check_youtube()
        print(f'Все аккаунты Youtube проверены.')
        zen.check_zen()
        print(f'Все аккаунты Yandex Zen проверены.')
        sleep(int(wait))


if __name__ == '__main__':
    run()
