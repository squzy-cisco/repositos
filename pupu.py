import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ------------------ КОНФИГУРАЦИЯ ------------------
API_KEY = "2f88e65db150871d7efc46f1"  # Замените на ваш реальный ключ
HISTORY_FILE = "C:/Users/student/PyCharmMiscProject/history.json"


# ------------------ РАБОТА С ИСТОРИЕЙ ------------------
def load_history():
    """Загружает историю из JSON-файла."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    """Сохраняет историю в JSON-файл."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def add_to_history(amount_from, currency_from, amount_to, currency_to, rate):
    """Добавляет запись в историю и сохраняет."""
    history = load_history()
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "amount_from": amount_from,
        "currency_from": currency_from,
        "amount_to": amount_to,
        "currency_to": currency_to,
        "rate": rate
    }
    history.append(record)
    save_history(history)
    return record


# ------------------ ПОЛУЧЕНИЕ КУРСА (исправленная версия) ------------------
def get_exchange_rate(from_currency, to_currency):
    """Запрашивает курс через API. Возвращает float или None при ошибке."""

    # Если валюты одинаковые
    if from_currency == to_currency:
        return 1.0

    # Правильный URL для API
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}"

    try:
        # Создаем запрос с User-Agent (некоторые API требуют)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        with urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())

        # Проверяем результат
        if data.get("result") == "success":
            rate = data.get("conversion_rate")
            if rate:
                return float(rate)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить курс валюты")
                return None
        else:
            error_msg = data.get("error-type", "Неизвестная ошибка")
            if error_msg == "invalid-api-key":
                messagebox.showerror("Ошибка API",
                                     "Неверный API-ключ!\nПолучите бесплатный ключ на exchangerate-api.com")
            elif error_msg == "unsupported-code":
                messagebox.showerror("Ошибка", f"Валюта {from_currency} или {to_currency} не поддерживается")
            else:
                messagebox.showerror("Ошибка API", f"Ошибка: {error_msg}")
            return None

    except HTTPError as e:
        if e.code == 403:
            messagebox.showerror("Ошибка доступа", "Неверный API-ключ. Проверьте ключ на сайте exchangerate-api.com")
        elif e.code == 404:
            messagebox.showerror("Ошибка", "API сервис не найден. Проверьте URL")
        else:
            messagebox.showerror("HTTP ошибка", f"Ошибка {e.code}: {e.reason}")
        return None

    except URLError as e:
        messagebox.showerror("Сетевая ошибка",
                             "Нет подключения к интернету!\n"
                             "Проверьте:\n"
                             "1. Подключение к интернету\n"
                             "2. Брандмауэр не блокирует Python\n"
                             "3. VPN/прокси (если используется)")
        return None

    except Exception as e:
        messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
        return None


# ------------------ GUI ПРИЛОЖЕНИЯ ------------------
class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Список популярных валют
        self.currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "CHF", "AUD", "CNY", "RUB", "TRY", "INR", "BRL", "MXN",
                           "KRW"]

        # Переменные
        self.amount_var = tk.StringVar()
        self.from_currency = tk.StringVar(value="USD")
        self.to_currency = tk.StringVar(value="EUR")
        self.history = load_history()

        # Построение интерфейса
        self.create_widgets()
        self.update_history_table()

        # Проверка API при запуске
        self.check_api_key()

    def check_api_key(self):
        """Проверяет работоспособность API-ключа"""
        if API_KEY == "YOUR_API_KEY_HERE":
            messagebox.showwarning("Внимание!",
                                   "Не установлен API-ключ!\n\n"
                                   "1. Зайдите на exchangerate-api.com\n"
                                   "2. Получите бесплатный ключ\n"
                                   "3. Вставьте его в 11-ю строку кода\n\n"
                                   "Пока конвертация не будет работать!")
            return

        # Тестовый запрос к API
        try:
            url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/USD/EUR"
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get("result") == "success":
                    self.result_label.config(text="✅ API подключен успешно!", foreground="green")
                    self.root.after(3000, lambda: self.result_label.config(text="", foreground="black"))
                else:
                    self.result_label.config(text="❌ Ошибка API ключа!", foreground="red")
        except:
            pass  # Ошибка обработается при первой конвертации

    def create_widgets(self):
        # Рамка ввода
        input_frame = ttk.LabelFrame(self.root, text="Конвертация", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.amount_var, width=15, font=("Arial", 10)).grid(row=0, column=1, padx=5,
                                                                                                pady=5)

        ttk.Label(input_frame, text="Из валюты:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        from_combo = ttk.Combobox(input_frame, textvariable=self.from_currency, values=self.currencies, width=10,
                                  font=("Arial", 10))
        from_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="В валюту:", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        to_combo = ttk.Combobox(input_frame, textvariable=self.to_currency, values=self.currencies, width=10,
                                font=("Arial", 10))
        to_combo.grid(row=0, column=5, padx=5, pady=5)

        convert_btn = ttk.Button(input_frame, text="Конвертировать", command=self.convert, width=15)
        convert_btn.grid(row=0, column=6, padx=10, pady=5)

        # Рамка результата
        result_frame = ttk.LabelFrame(self.root, text="Результат", padding=10)
        result_frame.pack(fill="x", padx=10, pady=5)

        self.result_label = ttk.Label(result_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.pack()

        # Таблица истории
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создаем фрейм для таблицы и скролла
        tree_frame = ttk.Frame(history_frame)
        tree_frame.pack(fill="both", expand=True)

        columns = ("timestamp", "amount_from", "currency_from", "amount_to", "currency_to", "rate")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        self.tree.heading("timestamp", text="Дата/время")
        self.tree.heading("amount_from", text="Сумма (из)")
        self.tree.heading("currency_from", text="Из")
        self.tree.heading("amount_to", text="Сумма (в)")
        self.tree.heading("currency_to", text="В")
        self.tree.heading("rate", text="Курс")

        self.tree.column("timestamp", width=140)
        self.tree.column("amount_from", width=90)
        self.tree.column("currency_from", width=60)
        self.tree.column("amount_to", width=90)
        self.tree.column("currency_to", width=60)
        self.tree.column("rate", width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(side="bottom", fill="x", pady=5)

        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить курс", command=self.refresh_rate).pack(side="left", padx=5)

    def convert(self):
        """Выполняет конвертацию."""
        # Проверка API ключа
        if API_KEY == ("demo"):
            messagebox.showerror("Ошибка",
                                 "API ключ не настроен!\n\n"
                                 "Как получить ключ:\n"
                                 "1. Перейдите на exchangerate-api.com\n"
                                 "2. Введите email\n"
                                 "3. Скопируйте ключ\n"
                                 "4. Вставьте его в 11-ю строку кода")
            return

        # Проверка корректности суммы
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
            return

        from_cur = self.from_currency.get().upper()
        to_cur = self.to_currency.get().upper()

        # Показываем процесс загрузки
        self.result_label.config(text="Загрузка курса...", foreground="blue")
        self.root.update()

        if from_cur == to_cur:
            result_amount = amount
            rate = 1.0
            self.result_label.config(text=f"{amount:.2f} {from_cur} = {result_amount:.2f} {to_cur}", foreground="green")
        else:
            rate = get_exchange_rate(from_cur, to_cur)
            if rate is None:
                self.result_label.config(text="Ошибка получения курса", foreground="red")
                return
            result_amount = amount * rate
            # Отображение результата
            self.result_label.config(text=f"{amount:.2f} {from_cur} = {result_amount:.4f} {to_cur}  (курс: {rate:.6f})",
                                     foreground="green")

        # Добавляем в историю
        add_to_history(amount, from_cur, result_amount, to_cur, rate)
        self.update_history_table()

    def refresh_rate(self):
        """Показывает текущий курс без конвертации."""
        from_cur = self.from_currency.get().upper()
        to_cur = self.to_currency.get().upper()

        if from_cur == to_cur:
            messagebox.showinfo("Курс", f"Курс {from_cur} к {to_cur}: 1.0000")
        else:
            self.result_label.config(text="Загрузка курса...", foreground="blue")
            self.root.update()

            rate = get_exchange_rate(from_cur, to_cur)
            if rate:
                messagebox.showinfo("Текущий курс", f"1 {from_cur} = {rate:.6f} {to_cur}")
                self.result_label.config(text=f"1 {from_cur} = {rate:.6f} {to_cur}", foreground="green")
                self.root.after(3000, lambda: self.result_label.config(text=""))
            else:
                self.result_label.config(text="Ошибка получения курса", foreground="red")

    def update_history_table(self):
        """Обновляет таблицу истории из текущего списка."""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Загружаем актуальную историю
        self.history = load_history()
        for rec in reversed(self.history):  # Показываем последние сверху
            self.tree.insert("", "end", values=(
                rec["timestamp"],
                f"{rec['amount_from']:.4f}",
                rec["currency_from"],
                f"{rec['amount_to']:.4f}",
                rec["currency_to"],
                f"{rec['rate']:.6f}"
            ))

    def clear_history(self):
        """Очищает историю после подтверждения."""
        if messagebox.askyesno("Подтверждение", "Удалить всю историю конвертаций?"):
            save_history([])
            self.update_history_table()
            self.result_label.config(text="История очищена", foreground="blue")
            self.root.after(2000, lambda: self.result_label.config(text=""))


# ------------------ ЗАПУСК ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()