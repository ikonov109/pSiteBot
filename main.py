#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===================================================
     ПРОГРАММА ДЛЯ АВТОМАТИЧЕСКОГО ПОСЕЩЕНИЯ САЙТОВ
               (Версия с графическим интерфейсом)
===================================================

Данный скрипт предназначен ИСКЛЮЧИТЕЛЬНО для образовательных целей.
Автор не несёт ответственности за любое неправомерное использование,
в том числе за организацию DDoS-атак, нарушение условий обслуживания
веб-сайтов или любые другие противоправные действия.

Используя эту программу, вы принимаете на себя всю полноту ответственности
за её применение и обязуетесь соблюдать действующее законодательство.

Программа позволяет отправлять множественные HTTP-запросы к указанному URL
с возможностью использования прокси-серверов, подмены User-Agent,
задания задержек и многопоточности.
"""

import requests
import threading
import time
import random
import argparse
import sys
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ ====================
DISCLAIMER = """
=============================================================
|                    ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ              |
=============================================================
| Данная программа создана исключительно в образовательных  |
| целях для демонстрации работы с сетевыми запросами на     |
| языке Python. Любое использование программы для:          |
|   • нарушения штатной работы веб-сайтов (DDoS-атаки);     |
|   • несанкционированного сканирования ресурсов;           |
|   • накрутки счётчиков, голосований или рейтингов;        |
|   • иных действий, нарушающих законодательство или        |
|     условия использования конкретного сайта,              |
| является недопустимым и влечёт за собой ответственность   |
| исключительно пользователя.                                |
|                                                           |
| Автор программы не несёт никакой ответственности за       |
| последствия её применения. Используя данный скрипт, вы    |
| подтверждаете, что ознакомлены с этим предупреждением и   |
| согласны с ним.                                            |
=============================================================
"""
# ==============================================================


class WebsiteBot:
    """
    Класс для многопоточного выполнения HTTP-запросов к заданному URL.
    Поддерживает использование прокси, подмену User-Agent, задержки и повторные попытки.
    """

    def __init__(self, url, num_requests=1, num_threads=1, delay=0,
                 proxies_file=None, user_agents_file=None, timeout=10, retries=3,
                 stop_event=None, log_queue=None):
        """
        Инициализация бота.

        :param url: целевой URL
        :param num_requests: общее количество запросов
        :param num_threads: количество потоков
        :param delay: задержка между запросами (сек)
        :param proxies_file: файл со списком прокси (по одному на строку, формат: http://user:pass@host:port)
        :param user_agents_file: файл со списком User-Agent строк
        :param timeout: таймаут запроса (сек)
        :param retries: количество повторных попыток при ошибках
        :param stop_event: threading.Event для сигнала остановки
        :param log_queue: queue.Queue для передачи сообщений в GUI
        """
        self.url = url
        self.num_requests = num_requests
        self.num_threads = num_threads
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.stop_event = stop_event or threading.Event()
        self.log_queue = log_queue

        # Очередь задач (каждый элемент — номер запроса, можно добавить параметры)
        self.queue = queue.Queue()  # ПРАВИЛЬНО
        for i in range(num_requests):
            self.queue.put(i)

        # Загружаем прокси и user-agent'ы
        self.proxies = self._load_list_from_file(proxies_file) if proxies_file else []
        self.user_agents = self._load_list_from_file(user_agents_file) if user_agents_file else []

        # Статистика
        self.success_count = 0
        self.fail_count = 0
        self.start_time = None

    @staticmethod
    def _load_list_from_file(filename):
        """Загружает строки из файла, игнорируя пустые и комментарии (#)."""
        items = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        items.append(line)
        except Exception as e:
            print(f"[!] Ошибка загрузки файла {filename}: {e}")
        return items

    def _get_proxy(self):
        """Возвращает случайный прокси из списка или None."""
        if self.proxies:
            return random.choice(self.proxies)
        return None

    def _get_user_agent(self):
        """Возвращает случайный User-Agent или стандартный."""
        if self.user_agents:
            return random.choice(self.user_agents)
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def _make_request(self, session, proxy):
        """Выполняет один запрос с заданной сессией и прокси."""
        headers = {'User-Agent': self._get_user_agent()}
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        try:
            response = session.get(self.url, headers=headers, proxies=proxies,
                                   timeout=self.timeout, allow_redirects=True)
            status = response.status_code
            if status == 200:
                return True, status
            else:
                return False, status
        except Exception as e:
            return False, str(e)

    def _worker(self):
        """Функция, выполняемая в каждом потоке."""
        # Настраиваем сессию с повторными попытками
        session = requests.Session()
        retry_strategy = Retry(
            total=self.retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=0.5
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        while not self.queue.empty() and not self.stop_event.is_set():
            try:
                task = self.queue.get_nowait()
            except:
                break

            proxy = self._get_proxy()
            success, info = self._make_request(session, proxy)

            if success:
                self.success_count += 1
                msg = f"[+] Запрос #{task+1} выполнен успешно (статус: {info})"
            else:
                self.fail_count += 1
                msg = f"[-] Запрос #{task+1} провалился (ошибка: {info})"

            if self.log_queue:
                self.log_queue.put(msg)

            # Задержка между запросами
            if self.delay > 0 and not self.stop_event.is_set():
                # Дробим задержку на мелкие куски, чтобы можно было прервать
                for _ in range(int(self.delay * 10)):
                    if self.stop_event.is_set():
                        break
                    time.sleep(0.1)
                # остаток задержки
                remaining = self.delay - int(self.delay)
                if remaining > 0 and not self.stop_event.is_set():
                    time.sleep(remaining)

            self.queue.task_done()

    def run(self):
        """Запускает потоки и ожидает завершения."""
        self.start_time = time.time()
        threads = []

        start_msg = f"\n[+] Запуск {self.num_threads} потоков для {self.num_requests} запросов к {self.url}"
        if self.log_queue:
            self.log_queue.put(start_msg)
        if self.proxies:
            self.log_queue.put(f"[+] Используется {len(self.proxies)} прокси")
        if self.user_agents:
            self.log_queue.put(f"[+] Загружено {len(self.user_agents)} User-Agent'ов")
        self.log_queue.put("[+] Начало работы...\n")

        for _ in range(min(self.num_threads, self.num_requests)):
            t = threading.Thread(target=self._worker)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        elapsed = time.time() - self.start_time
        self.log_queue.put("\n[+] Работа завершена.")
        self.log_queue.put(f"[+] Успешно: {self.success_count}, Ошибок: {self.fail_count}")
        self.log_queue.put(f"[+] Время выполнения: {elapsed:.2f} сек.")


class BotGUI:
    """Графический интерфейс для управления WebsiteBot."""

    def __init__(self, root):
        self.root = root
        self.root.title("Бот для посещения сайтов (образовательный)")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Переменные для хранения значений полей
        self.url_var = tk.StringVar()
        self.requests_var = tk.IntVar(value=10)
        self.threads_var = tk.IntVar(value=2)
        self.delay_var = tk.DoubleVar(value=0.5)
        self.timeout_var = tk.IntVar(value=10)
        self.retries_var = tk.IntVar(value=3)
        self.proxies_file_var = tk.StringVar()
        self.useragents_file_var = tk.StringVar()

        # Флаг для остановки выполнения
        self.stop_event = threading.Event()
        self.bot_thread = None
        self.log_queue = queue.Queue()

        # Создание виджетов
        self.create_widgets()

        # Проверка очереди логов каждые 100 мс
        self.poll_log_queue()

        # Показать отказ от ответственности при запуске
        self.show_disclaimer()

    def show_disclaimer(self):
        """Показывает диалог с отказом от ответственности."""
        result = messagebox.askyesno("Отказ от ответственности", DISCLAIMER + "\n\nВы согласны с условиями?")
        if not result:
            self.root.quit()

    def create_widgets(self):
        """Создаёт элементы интерфейса."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Строка с URL
        ttk.Label(main_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=70)
        url_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W, pady=5, padx=(5,0))

        # Параметры запросов
        ttk.Label(main_frame, text="Количество запросов:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.requests_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Потоков:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20,0))
        ttk.Entry(main_frame, textvariable=self.threads_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Задержка (сек):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.delay_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Таймаут (сек):").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20,0))
        ttk.Entry(main_frame, textvariable=self.timeout_var, width=10).grid(row=2, column=3, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Повторные попытки:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.retries_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Файлы прокси и user-agent
        ttk.Label(main_frame, text="Файл с прокси:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.proxies_file_var, width=50).grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Обзор...", command=self.browse_proxies).grid(row=4, column=3, padx=5)

        ttk.Label(main_frame, text="Файл с User-Agent:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.useragents_file_var, width=50).grid(row=5, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Обзор...", command=self.browse_useragents).grid(row=5, column=3, padx=5)

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=4, pady=15)

        self.start_button = ttk.Button(button_frame, text="Запуск", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Стоп", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Очистить лог", command=self.clear_log).pack(side=tk.LEFT, padx=5)

        # Область лога
        ttk.Label(main_frame, text="Лог выполнения:").grid(row=7, column=0, sticky=tk.W, pady=(10,0))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=20, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.grid(row=8, column=0, columnspan=4, sticky=tk.NSEW, pady=5)

        # Настройка растяжения
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)

    def browse_proxies(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с прокси",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.proxies_file_var.set(filename)

    def browse_useragents(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с User-Agent",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.useragents_file_var.set(filename)

    def log(self, message):
        """Добавляет сообщение в лог (из основного потока)."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def poll_log_queue(self):
        """Периодически проверяет очередь сообщений от бота и выводит их в лог."""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log(msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.poll_log_queue)

    def start_bot(self):
        """Запускает бота в отдельном потоке."""
        # Проверка обязательного поля URL
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Не указан URL")
            return

        # Сбор параметров
        try:
            num_requests = self.requests_var.get()
            num_threads = self.threads_var.get()
            delay = self.delay_var.get()
            timeout = self.timeout_var.get()
            retries = self.retries_var.get()
        except tk.TclError:
            messagebox.showerror("Ошибка", "Проверьте правильность ввода числовых значений")
            return

        proxies_file = self.proxies_file_var.get().strip() or None
        useragents_file = self.useragents_file_var.get().strip() or None

        # Сброс события остановки
        self.stop_event.clear()

        # Создание бота
        self.bot = WebsiteBot(
            url=url,
            num_requests=num_requests,
            num_threads=num_threads,
            delay=delay,
            proxies_file=proxies_file,
            user_agents_file=useragents_file,
            timeout=timeout,
            retries=retries,
            stop_event=self.stop_event,
            log_queue=self.log_queue
        )

        # Запуск в отдельном потоке
        self.bot_thread = threading.Thread(target=self.bot.run)
        self.bot_thread.daemon = True
        self.bot_thread.start()

        # Обновление состояния кнопок
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Запуск мониторинга завершения потока
        self.monitor_bot()

    def monitor_bot(self):
        """Проверяет, завершился ли поток бота, и возвращает кнопки в исходное состояние."""
        if self.bot_thread and self.bot_thread.is_alive():
            self.root.after(500, self.monitor_bot)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log("[INFO] Поток бота завершён.")

    def stop_bot(self):
        """Устанавливает событие остановки для прерывания работы бота."""
        self.stop_event.set()
        self.log("[!] Получен сигнал остановки. Завершение работы...")


def main():
    # Если аргументов командной строки нет (только имя скрипта) — запускаем GUI
    if len(sys.argv) == 1:
        root = tk.Tk()
        app = BotGUI(root)
        root.mainloop()
    else:
        # Иначе работаем в режиме командной строки (как было ранее)
        parser = argparse.ArgumentParser(description="Бот для автоматических запросов к веб-сайту (только в образовательных целях).")
        parser.add_argument("--url", required=True, help="Целевой URL (обязательно)")
        parser.add_argument("--requests", type=int, default=1, help="Количество запросов (по умолчанию 1)")
        parser.add_argument("--threads", type=int, default=1, help="Количество потоков (по умолчанию 1)")
        parser.add_argument("--delay", type=float, default=0, help="Задержка между запросами в секундах (по умолчанию 0)")
        parser.add_argument("--proxies", help="Файл со списком прокси (по одному на строку)")
        parser.add_argument("--user-agents", dest="user_agents", help="Файл со списком User-Agent строк")
        parser.add_argument("--timeout", type=int, default=10, help="Таймаут запроса в секундах (по умолчанию 10)")
        parser.add_argument("--retries", type=int, default=3, help="Количество повторных попыток при ошибках (по умолчанию 3)")
        parser.add_argument("--no-confirm", action="store_true", help="Не запрашивать подтверждение отказа от ответственности (не рекомендуется)")
        args = parser.parse_args()

        if not args.no_confirm:
            print(DISCLAIMER)
            answer = input("Вы согласны с условиями и хотите продолжить? (y/N): ").strip().lower()
            if answer not in ('y', 'yes', 'д', 'да'):
                print("[!] Работа программы прервана пользователем.")
                sys.exit(0)

        bot = WebsiteBot(
            url=args.url,
            num_requests=args.requests,
            num_threads=args.threads,
            delay=args.delay,
            proxies_file=args.proxies,
            user_agents_file=args.user_agents,
            timeout=args.timeout,
            retries=args.retries
        )
        bot.run()


if __name__ == "__main__":
    main()