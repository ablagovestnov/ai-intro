# 🚀 Быстрый старт - Traffic Parser Application

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
python traffic_parser_app.py init
```

### 3. Подготовка PCAP файлов
Поместите ваши PCAP файлы в директорию `pcap_files/`:
```bash
# Создайте директорию (уже создана)
mkdir -p pcap_files

# Скопируйте ваши PCAP файлы
cp /path/to/your/*.pcap pcap_files/
```

### 4. Парсинг и экспорт
```bash
# Парсинг всех PCAP файлов
python traffic_parser_app.py parse

# Парсинг с фильтрацией по протоколу
python traffic_parser_app.py parse --protocol TCP

# Парсинг с фильтрацией по IP
python traffic_parser_app.py parse --ip 192.168.1.1

# Парсинг с фильтрацией по порту
python traffic_parser_app.py parse --port 80
```

### 5. Экспорт данных
```bash
# Экспорт всех данных
python traffic_parser_app.py export

# Экспорт с фильтрацией
python traffic_parser_app.py export --protocol UDP
```

## Результаты

После выполнения команды `parse` вы получите:
- ✅ База данных SQLite: `traffic_data.db`
- ✅ JSON файл с данными: `traffic_export.json`
- ✅ JSON файл со статистикой: `traffic_export_statistics.json`

## Тестирование

Для проверки работы приложения:
```bash
python test_app.py
```

## Структура проекта

```
devTalkPres/
├── traffic_parser_app.py    # Основное приложение с CLI
├── pcap_parser.py          # Парсер PCAP файлов
├── database.py             # Модели и обработчик БД
├── json_exporter.py        # Экспорт в JSON
├── config.py               # Конфигурация
├── test_app.py             # Тестовый скрипт
├── example_usage.py        # Пример использования
├── requirements.txt        # Зависимости
├── README.md               # Подробная документация
├── QUICKSTART.md           # Этот файл
└── pcap_files/             # Директория для PCAP файлов
```

## Примеры команд

```bash
# Полный цикл обработки
python traffic_parser_app.py parse --pcap-dir ./pcap_files --output ./results.json

# Фильтрация HTTP трафика
python traffic_parser_app.py parse --protocol TCP --port 80

# Фильтрация по размеру пакетов
python traffic_parser_app.py parse --min-size 100 --max-size 1500

# Экспорт только UDP трафика
python traffic_parser_app.py export --protocol UDP
```

## Поддержка

При возникновении проблем:
1. Проверьте, что все зависимости установлены
2. Убедитесь, что PCAP файлы находятся в правильной директории
3. Проверьте логи приложения
4. Запустите тест: `python test_app.py`
