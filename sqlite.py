import json
import sqlite3 as sql

class SQLite:
    """Класс, позволяющий проще взоимодействовать с бд"""

    def __init__(self, database):
        self.connection = sql.connect(database, check_same_thread=False, timeout=20)
        self.cursor = self.connection.cursor()

    def get_all_books(self) -> list[list]:
        """Возвращает список с данными о книгах (автор, название, описание, жанр)"""
        return self.cursor.execute("SELECT * FROM books").fetchall()

    def fetch_book(self, author: str, title: str) -> list[str]:
        """Возвращает данные книги по автору и названию"""
        return self.cursor.execute("SELECT * FROM books WHERE author = ? AND title = ?",
                                   (author, title)).fetchone()

    def add_new_book(self, author: str, title: str, description: str, genre: str) -> None:
        """Добавляет новую книгу"""
        self.cursor.execute("INSERT INTO books (author, title, description, genre) "
                            "VALUES(?, ?, ?, ?)", (author, title, description, genre))

    def remove_book(self, author: str, title: str):
        """Удаляет книгу по автору и названию"""
        self.cursor.execute("DELETE FROM books WHERE author = ? AND title = ?", (author, title))

    def get_genres(self) -> list[str]:
        """Возвращает весь список жанров из бд"""
        with self.connection:
            return json.loads(self.cursor.execute("SELECT value FROM cache WHERE key = ?",
                                                  ('genres_list',)).fetchone()[0])

    def add_new_genre(self, genre: str) -> None:
        """Добавляет новый жанр в базу данных"""
        o = self.get_genres()
        o.append(genre)
        with self.connection:
            self.cursor.execute("UPDATE cache SET value = ? WHERE key = ?",
                                (json.dumps(o), 'genres_list'))

    def remove_genre(self, genre: str) -> None:
        """Удаляет жанр из базы данных"""
        o = self.get_genres()
        o.remove(genre)
        with self.connection:
            self.cursor.execute("UPDATE cache SET value = ? WHERE key = ?",
                                (json.dumps(o), 'genres_list'))

    def close(self):
        """Закрывает подключение к бд"""
        self.connection.close()
