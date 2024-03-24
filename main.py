"""Библиотека, позволяющая отрисовывать интерфейс"""
import dearpygui.dearpygui as dpg

from sqlite import SQLite

class LibraryApp:
    """Класс для созданного приложения, содержащий в себе функции для рендера
     и взаимодействия с кнопками"""

    def __init__(self, width: int, height: int, title: str):
        self.width = width
        self.height = height
        self.title = title
        self.db = SQLite("database.db")
        self.setup_gui()

    def setup_gui(self) -> None:
        """Пререндер интерфейса"""
        dpg.create_context()
        with dpg.window(pos=[0, 0], no_resize=True, no_close=True, no_move=True, no_title_bar=True,
                        width=self.width, height=self.height):
            dpg.add_text(self.title, pos=[360, 20], color=(30, 215, 96, 255))

            dpg.add_text("Genres list:", pos=[40, 70])
            dpg.add_listbox(self.db.get_genres(), width=150, pos=[40, 90], tag="listbox_genre",
                            callback=self.change_selected_genre)

            dpg.add_button(label="Delete genre", callback=self.delete_genre, pos=[200, 90],
                           height=20, width=100)
            dpg.add_button(label="Add genre", pos=[200, 120], height=20, width=100)

            with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True,
                           tag="modal_add_genre"):
                dpg.add_text("Input genre name here:")
                dpg.add_text("(Press enter to add genre)")
                dpg.add_input_text(default_value="genre name", readonly=False, tag="genre_title",
                                   on_enter=True, callback=self.add_genre)


            dpg.add_checkbox(label="Display all books", pos=[40, 190], tag="checkbox_display_books",
                             default_value=True, callback=self.change_status_display_books)
            dpg.add_text("Books list:", pos=[40, 210])
            dpg.add_listbox(self.format_books(self.db.get_all_books()), width=150,
                            pos=[40, 230], tag="listbox_books")

            dpg.add_button(label="Delete book", callback=self.delete_book, pos=[200, 230],
                           height=20, width=100)
            dpg.add_button(label="Add book", pos=[200, 260], height=20, width=100)

            with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True,
                           tag="modal_add_book"):
                dpg.add_text("Input genre name here:")
                dpg.add_input_text(default_value="Book author", width=300, readonly=False,
                                   tag="book_author")
                dpg.add_input_text(default_value="Book title", width=300, readonly=False,
                                   tag="book_title")
                dpg.add_input_text(default_value="Description", readonly=False,
                                   tag="book_description", height=200, width=300,
                                   multiline=True)

                dpg.add_checkbox(label="Custom genre", default_value=False,
                                 callback=self.change_genre_input, tag="checkbox_custom_genre")

                dpg.add_input_text(default_value="Genre", width=300, readonly=False,
                                   tag="book_genre_text", show=False)
                dpg.add_listbox(self.db.get_genres(), width=300, tag="book_genre_listbox")

                dpg.add_button(label="Add book", callback=self.add_book)

            dpg.add_text("Search for book", pos=[410, 70])
            dpg.add_input_text(default_value="Keyword...", width=300, readonly=False,
                               callback=self.search_for_book, tag="search_book", pos=[410, 90])
            dpg.add_listbox(self.format_books(self.db.get_all_books(), True), pos=[410, 120],
                            width=300, tag="search_values", callback=self.display_book)
            dpg.add_input_text(default_value="", readonly=True, tag="book_displayer",
                               pos=[410, 195], height=175, width=300, multiline=True)

            dpg.create_viewport(width=self.width, height=self.height, resizable=False,
                                title=self.title, always_on_top=False)
            dpg.set_viewport_max_width(self.width)
            dpg.set_viewport_max_height(self.height)

    @staticmethod
    def show_gui() -> None:
        """Отображение интерфейса"""
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    @staticmethod
    def format_books(books: list[list], format_for_search: bool = False) -> list:
        """
        Возвращает отформатированный список книг по заданным параметрам

        :param books: Список данных о книгах (автор, название, описание, жанр)
        :param format_for_search: Доп. параметр для ренедера списка под всех книг / меню поиска книг
        :return:
        """
        selected_genre = dpg.get_value('listbox_genre') # Выбранный жанр в левой части меню

        display_status_books = dpg.get_value("checkbox_display_books") # Статус чекбокса,
        # который отображает весь список книг в левой части, либо только по выбранному жанру
        return [' - '.join(args[:2]) for args in books if args[3] == selected_genre or
                display_status_books or format_for_search]

    @staticmethod
    def change_genre_input(sender, appdata) -> None:
        """В зависимости от статуса чекбокса отображает пользователю окно
         для выбора жанра добавляемой книги"""
        dpg.configure_item('book_genre_text', show=appdata)
        dpg.configure_item('book_genre_listbox', show=not appdata)

    def change_selected_genre(self) -> None:
        """В левой части меню отображает список книг по выбранному жанру"""
        dpg.configure_item("listbox_books", items=self.format_books(self.db.get_all_books()))

    def add_genre(self, sender, appdata) -> None:
        """Добавляет новый жанр в бд, обновляет информацию в интерфейсе пользователя"""
        self.db.add_new_genre(appdata)
        dpg.configure_item('modal_add_genre', show=False)
        dpg.configure_item("listbox_genre", items=self.db.get_genres())
        dpg.configure_item("book_genre_listbox", items=self.db.get_genres())

    def delete_genre(self) -> None:
        """Удаляет выбранный жанр из бд, обновляет информацию в интерфейсе пользователя"""
        self.db.remove_genre(dpg.get_value('listbox_genre'))
        dpg.configure_item("listbox_genre", items=self.db.get_genres())
        dpg.configure_item("book_genre_listbox", items=self.db.get_genres())

    def add_book(self) -> None:
        """Добавляет новую книгу в бд, обновляет информацию в интерфейсе пользователя"""
        author = dpg.get_value("book_author")
        title = dpg.get_value("book_title")

        # Проверка на существование книги с таким же автором и названием
        if bool(self.db.fetch_book(author, title)):
            dpg.configure_item('modal_add_book', show=False)
            return

        if dpg.get_value("checkbox_custom_genre"):
            genre = dpg.get_value("book_genre_text")
            if genre not in self.db.get_genres():
                self.db.add_new_genre(genre)
        else: genre = dpg.get_value("book_genre_listbox")

        description = dpg.get_value("book_description")
        self.db.add_new_book(author, title, description, genre)
        dpg.configure_item('modal_add_book', show=False)
        dpg.configure_item("listbox_genre", items=self.db.get_genres())
        dpg.configure_item("book_genre_listbox", items=self.db.get_genres())
        dpg.configure_item("listbox_books", items=self.format_books(self.db.get_all_books()))
        dpg.configure_item('search_values', items=self.format_books(self.db.get_all_books(), True))

    def delete_book(self) -> None:
        """Удаляет книгу из бд, обновляет информацию в интерфейсе пользователя"""
        self.db.remove_book(*dpg.get_value('listbox_books').split(' - '))
        dpg.configure_item("listbox_books", items=self.format_books(self.db.get_all_books()))
        dpg.configure_item('search_values', items=self.format_books(self.db.get_all_books(), True))

    def change_status_display_books(self) -> None:
        """Переключает статус чекбокса, который отображает весь
         список книг в левой части, либо только по выбранному жанру"""
        dpg.configure_item("listbox_books", items=self.format_books(self.db.get_all_books()))

    def display_book(self, sender, appdata) -> None:
        """Отображает в большом поле справа информацию о выбранной книге из поиска"""
        author, title = appdata.split(" - ")
        book_data = self.db.fetch_book(author, title)
        dpg.configure_item("book_displayer",
                           default_value=f"{author} - {title} ({book_data[3]})\n\n{book_data[2]}")

    def search_for_book(self) -> None:
        """Ищет книги по ключевому слову и обновляет информацию в интерфейсе пользователя"""
        request = dpg.get_value("search_book")
        books = self.db.get_all_books()
        books = [x for x in books if request in x[0] or request in x[1]]
        dpg.configure_item('search_values', items=self.format_books(books, True))


if __name__ == "__main__":
    app = LibraryApp(800, 500, "LibraryApp")
    app.show_gui()
