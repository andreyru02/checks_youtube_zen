import sqlite3


class SQL:
    def __init__(self, database):
        """Подключение к БД"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table_youtube()
        self.create_table_zen()
        self.create_table_instagram()
        self.create_table_pinterest()

    def create_table_youtube(self):
        """Создание таблицы для хранения видео youtube"""
        with self.connection:
            return self.cursor.execute("CREATE TABLE IF NOT EXISTS youtube "
                                       "('channel' TEXT NOT NULL, 'video' TEXT NOT NULL UNIQUE)")

    def create_table_zen(self):
        """Создание таблицы для хранения постов yandex zen"""
        with self.connection:
            return self.cursor.execute("CREATE TABLE IF NOT EXISTS zen "
                                       "('channel' TEXT NOT NULL, 'post' TEXT NOT NULL UNIQUE)")

    def create_table_instagram(self):
        """Создание таблицы для хранения постов instagram"""
        with self.connection:
            return self.cursor.execute("CREATE TABLE IF NOT EXISTS instagram "
                                       "('channel' TEXT NOT NULL, 'post' TEXT NOT NULL UNIQUE)")

    def post_instagram_exists(self, post):
        """Проверяет существование поста в БД"""
        with self.connection:
            result = self.cursor.execute("SELECT post FROM instagram WHERE post=?",
                                         (post,)).fetchall()
            return bool(len(result))

    def write_instagram(self, channel, post):
        """Записывает название канала и поста"""
        with self.connection:
            return self.cursor.execute("INSERT INTO instagram VALUES (?,?)", (channel, post,))

    def create_table_pinterest(self):
        """Создание таблицы для хранения постов instagram"""
        with self.connection:
            return self.cursor.execute("CREATE TABLE IF NOT EXISTS pinterest "
                                       "('channel' TEXT NOT NULL, 'post' TEXT NOT NULL UNIQUE)")

    def post_pinterest_exists(self, post):
        """Проверяет существование поста в БД"""
        with self.connection:
            result = self.cursor.execute("SELECT post FROM pinterest WHERE post=?",
                                         (post,)).fetchall()
            return bool(len(result))

    def write_pinterest(self, channel, post):
        """Записывает название канала и поста"""
        with self.connection:
            return self.cursor.execute("INSERT INTO pinterest VALUES (?,?)", (channel, post,))

    def video_youtube_exists(self, video):
        """Проверяет существование видео в БД"""
        with self.connection:
            result = self.cursor.execute("SELECT video FROM youtube WHERE video=?",
                                         (video,)).fetchall()
            return bool(len(result))

    def write_youtube(self, channel, video):
        """Записывает название канала и видео"""
        with self.connection:
            return self.cursor.execute("INSERT INTO youtube VALUES (?,?)", (channel, video,))

    def post_zen_exists(self, post):
        """Проверяет существование поста в БД"""
        with self.connection:
            result = self.cursor.execute("SELECT post FROM zen WHERE post=?",
                                         (post,)).fetchall()
            return bool(len(result))

    def write_zen(self, channel, post):
        """Записывает название канала и поста"""
        with self.connection:
            return self.cursor.execute("INSERT INTO zen VALUES (?,?)", (channel, post,))
