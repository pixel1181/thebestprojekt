import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from github_api import GitHubAPI


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Загрузка избранных пользователей
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Инициализация API
        self.api = GitHubAPI()

        # Создание интерфейса
        self.setup_ui()

    def setup_ui(self):
        # Стили
        style = ttk.Style()
        style.theme_use('clam')

        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Поле поиска
        search_frame = ttk.LabelFrame(main_frame, text="Поиск пользователя", padding="10")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(search_frame, text="Введите имя пользователя GitHub:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.grid(row=1, column=0, padx=(0, 10), pady=(5, 0))
        self.search_entry.bind('<Return>', lambda e: self.search_user())

        self.search_button = ttk.Button(search_frame, text="Найти", command=self.search_user)
        self.search_button.grid(row=1, column=1, pady=(5, 0))

        # Результаты поиска
        results_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Создание Treeview для отображения результатов
        columns = ("Логин", "ID", "Тип", "Избранное")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)

        self.results_tree.column("Логин", width=150)
        self.results_tree.column("Тип", width=100)
        self.results_tree.column("Избранное", width=100)

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Двойной клик для просмотра профиля
        self.results_tree.bind('<Double-Button-1>', self.show_user_profile)

        # Избранные пользователи
        favorites_frame = ttk.LabelFrame(main_frame, text="Избранные пользователи", padding="10")
        favorites_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        columns_fav = ("Логин", "ID", "Дата добавления")
        self.favorites_tree = ttk.Treeview(favorites_frame, columns=columns_fav, show="headings", height=15)

        for col in columns_fav:
            self.favorites_tree.heading(col, text=col)
            self.favorites_tree.column(col, width=120)

        self.favorites_tree.column("Логин", width=150)

        scrollbar_fav = ttk.Scrollbar(favorites_frame, orient=tk.VERTICAL, command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=scrollbar_fav.set)

        self.favorites_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_fav.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Контекстное меню для избранных
        self.favorites_tree.bind('<Button-3>', self.show_context_menu)
        self.favorites_tree.bind('<Double-Button-1>', self.show_favorite_profile)

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.remove_fav_button = ttk.Button(button_frame, text="Удалить из избранного",
                                            command=self.remove_from_favorites)
        self.remove_fav_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(button_frame, text="Обновить список", command=self.refresh_favorites)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        favorites_frame.columnconfigure(0, weight=1)
        favorites_frame.rowconfigure(0, weight=1)

        # Загрузка избранных при старте
        self.refresh_favorites()

    def search_user(self):
        username = self.search_entry.get().strip()

        # Проверка корректности ввода
        if not username:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            return

        # Очистка предыдущих результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Поиск пользователя
        result = self.api.search_user(username)

        if result["success"]:
            users = result["data"]
            for user in users:
                is_favorite = "Да" if user["login"] in self.favorites else "Нет"
                self.results_tree.insert("", tk.END, values=(
                    user["login"],
                    user["id"],
                    user["type"],
                    is_favorite
                ), tags=(user["login"],))
        else:
            messagebox.showerror("Ошибка", result["error"])

    def add_to_favorites(self, username):
        if username in self.favorites:
            messagebox.showinfo("Информация", f"Пользователь {username} уже в избранном!")
            return

        # Получение информации о пользователе
        result = self.api.get_user_info(username)

        if result["success"]:
            user_info = result["data"]
            self.favorites[username] = {
                "id": user_info["id"],
                "login": user_info["login"],
                "avatar_url": user_info["avatar_url"],
                "html_url": user_info["html_url"],
                "date_added": self.get_current_date()
            }
            self.save_favorites()
            self.refresh_favorites()
            messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")
        else:
            messagebox.showerror("Ошибка", result["error"])

    def remove_from_favorites(self):
        selected = self.favorites_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return

        username = self.favorites_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", f"Удалить {username} из избранного?"):
            del self.favorites[username]
            self.save_favorites()
            self.refresh_favorites()
            self.search_user()  # Обновление результатов поиска

    def show_user_profile(self, event):
        selected = self.results_tree.selection()
        if selected:
            username = self.results_tree.item(selected[0])['values'][0]
            self.show_profile_dialog(username)

    def show_favorite_profile(self, event):
        selected = self.favorites_tree.selection()
        if selected:
            username = self.favorites_tree.item(selected[0])['values'][0]
            self.show_profile_dialog(username)

    def show_profile_dialog(self, username):
        result = self.api.get_user_info(username)

        if result["success"]:
            user = result["data"]
            # Создание диалогового окна с информацией о пользователе
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Профиль: {username}")
            dialog.geometry("400x300")
            dialog.resizable(False, False)

            info_text = f"""
            Информация о пользователе:

            Логин: {user.get('login', 'Н/Д')}
            ID: {user.get('id', 'Н/Д')}
            Имя: {user.get('name', 'Н/Д')}
            Компания: {user.get('company', 'Н/Д')}
            Местоположение: {user.get('location', 'Н/Д')}
            Email: {user.get('email', 'Н/Д')}
            Публичные репозитории: {user.get('public_repos', 0)}
            Подписчики: {user.get('followers', 0)}
            Профиль: {user.get('html_url', 'Н/Д')}
            """

            text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(fill=tk.BOTH, expand=True)

            # Кнопка добавления в избранное
            if username not in self.favorites:
                fav_button = ttk.Button(dialog, text="Добавить в избранное",
                                        command=lambda: self.add_to_favorites(username))
                fav_button.pack(pady=10)
        else:
            messagebox.showerror("Ошибка", result["error"])

    def show_context_menu(self, event):
        selected = self.favorites_tree.selection()
        if selected:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Удалить из избранного", command=self.remove_from_favorites)
            menu.add_command(label="Показать профиль", command=lambda: self.show_favorite_profile(None))
            menu.post(event.x_root, event.y_root)

    def refresh_favorites(self):
        # Очистка списка избранных
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)

        # Обновление списка
        for username, info in self.favorites.items():
            self.favorites_tree.insert("", tk.END, values=(
                username,
                info["id"],
                info["date_added"]
            ))

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def get_current_date(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()