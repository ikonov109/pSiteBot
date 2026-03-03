# pSiteBot — Образовательный бот для тестирования сайтов 🤖

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-Exe-orange)]()
[![Downloads](https://img.shields.io/github/downloads/ikonov109/pSiteBot/total)](https://github.com/ikonov109/pSiteBot/releases)
[![Stars](https://img.shields.io/github/stars/ikonov109/pSiteBot)](https://github.com/ikonov109/pSiteBot/stargazers)

> ⚠️ **ВАЖНО**: Программа создана **исключительно в образовательных целях**!  
> ⚠️ **ВАЖНО**: Автор **НЕ НЕСЁТ ОТВЕТСТВЕННОСТИ** за использование программы!  
> Не используйте для нарушения работы сайтов или DDoS-атак!

## 📋 О проекте
Программа для автоматической отправки HTTP-запросов с поддержкой:
- Многопоточности
- Прокси (HTTP/HTTPS/SOCKS)
- Смены User-Agent
- Задержек между запросами
- Графического интерфейса (tkinter)

## 🚀 Как использовать

### Вариант 1: Готовый .exe
1. Скачай `main.exe` из [релизов](https://github.com/ikonov109/pSiteBot/releases)
2. Запусти и пользуйся!

### Вариант 2: Из исходников
```bash
git clone https://github.com/ikonov109/pSiteBot.git
cd pSiteBot
pip install -r requirements.txt
python main.py
```

### Вариант 3: Сборка своего .exe (одним кликом)
Просто запусти один из файлов:
- **build.bat** — быстрая сборка
- **build.cmd** — подробная сборка с проверками

Они автоматически:
1. Проверят наличие PyInstaller
2. Установят все зависимости
3. Соберут программу в .exe
4. Покажут результат
