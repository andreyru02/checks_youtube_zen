from pyrogram import Client

with open('./config.ini', 'r') as f:
    data = f.read().splitlines()
    api_id = data[1].split(' = ')[1]
    api_hash = data[2].split(' = ')[1]
    moder = data[3].split(' = ')[1]  # модерация


def send_message(url):
    """Отправляем новый пост в канал модерации"""
    app = Client("bot_python", api_id, api_hash)
    app.start()
    app.send_message(eval(moder), url)
    app.stop()
