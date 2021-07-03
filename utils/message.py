from pyrogram import Client

with open('./config.ini', 'r') as f:
    data = f.read().splitlines()
    api_id = data[1].split(' = ')[1]
    api_hash = data[2].split(' = ')[1]
    moder = data[3].split(' = ')[1]  # модерация


def send_message(urls, is_video_path=None):
    """Отправляем новый пост в канал модерации"""
    app = Client("bot_python", api_id, api_hash)
    app.start()
    for type_, elem in urls.items():
        if type_ == 'img':
            for img in elem:
                app.send_photo(moder, img)
        elif type_ == 'video' and is_video_path:
            for video in elem:
                app.send_video(moder, video)
        elif type_ == 'video':
            for video in elem:
                app.send_message(moder, video)

    app.stop()
