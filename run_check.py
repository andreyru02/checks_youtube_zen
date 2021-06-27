from threading import Thread
from utils import youtube


def run():
    # TODO: Будет цикл while с ожиданием
    Thread(target=youtube.check_youtube()).start()


if __name__ == '__main__':
    run()
