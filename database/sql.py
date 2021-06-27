import sqlite3


class SQL:
    def __init__(self, database):
        """Подключение к БД"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table_youtube()

    def create_table_youtube(self):
        """Создание таблицы для хранения видео youtube"""
        with self.connection:
            return self.cursor.execute("CREATE TABLE IF NOT EXISTS youtube "
                                       "('channel' TEXT NOT NULL, 'video' TEXT NOT NULL UNIQUE)")

    def video_youtube_exists(self, video):
        """Проверяет существование видео в БД"""
        with self.connection:
            result = self.cursor.execute("SELECT video FROM youtube WHERE video=?",
                                         (video,)).fetchall()
            return bool(len(result))

    def get_last_rowid(self):
        """Получение последнего ROWID"""
        with self.connection:
            return self.cursor.execute("SELECT ROWID, * FROM messages LIMIT 1 OFFSET (SELECT COUNT(*) FROM messages)-1")

    def get_data_in_table(self, message):
        """Получение записи о посте в таблице"""
        with self.connection:
            return self.cursor.execute(f"SELECT * FROM messages WHERE ROWID = {message.text}")

    def write_youtube(self, channel, video):
        """Записывает название канала и видео"""
        with self.connection:
            return self.cursor.execute("INSERT INTO youtube VALUES (?,?)", (channel, video,))

    def add_message_id(self, username, message_id):
        """Добавление message_id"""
        with self.connection:
            return self.cursor.execute("INSERT INTO messages VALUES (?,?)", (username, message_id,))
