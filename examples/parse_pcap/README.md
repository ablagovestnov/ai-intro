# Traffic Parser Application

Приложение для парсинга PCAP файлов с сохранением данных в SQLite базу данных и экспортом в JSON формат.

## Возможности

- Парсинг PCAP файлов с использованием Scapy
- Сохранение данных в SQLite базу данных
- Экспорт данных в JSON формат
- Фильтрация данных по различным критериям
- Статистика по трафику
- CLI интерфейс для удобного использования

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте директорию для PCAP файлов:
```bash
mkdir pcap_files
```

## Использование

### Инициализация базы данных
```bash
python traffic_parser_app.py init
```

### Парсинг PCAP файлов
```bash
# Парсинг всех файлов из директории pcap_files
python traffic_parser_app.py parse

# Парсинг из конкретной директории
python traffic_parser_app.py parse --pcap-dir /path/to/pcap/files

# Парсинг с фильтрацией по протоколу
python traffic_parser_app.py parse --protocol TCP

# Парсинг с фильтрацией по IP адресу
python traffic_parser_app.py parse --ip 192.168.1.1

# Парсинг с фильтрацией по порту
python traffic_parser_app.py parse --port 80

# Парсинг с фильтрацией по размеру пакета
python traffic_parser_app.py parse --min-size 100 --max-size 1500
```

### Экспорт данных
```bash
# Экспорт всех данных
python traffic_parser_app.py export

# Экспорт с фильтрацией
python traffic_parser_app.py export --protocol UDP --ip 10.0.0.1
```

## Конфигурация

Настройки приложения можно изменить в файле `config.py`:

- `DATABASE_URL`: URL базы данных SQLite
- `PCAP_DIRECTORY`: Директория с PCAP файлами
- `OUTPUT_JSON_FILE`: Путь к выходному JSON файлу
- `LOG_LEVEL`: Уровень логирования
- `BATCH_SIZE`: Размер батча для записи в БД
- `MAX_PACKETS_PER_FILE`: Максимальное количество пакетов для обработки из одного файла

## Структура данных

### База данных
Таблица `traffic_packets` содержит следующие поля:
- `id`: Уникальный идентификатор
- `timestamp`: Временная метка пакета
- `source_ip`: IP адрес источника
- `destination_ip`: IP адрес назначения
- `source_port`: Порт источника
- `destination_port`: Порт назначения
- `protocol`: Протокол (TCP, UDP, ICMP, IPv6, etc.)
- `packet_size`: Размер пакета в байтах
- `packet_data`: Дополнительные данные пакета в JSON формате
- `file_name`: Имя исходного PCAP файла
- `created_at`: Время создания записи

### JSON экспорт
JSON файл содержит:
- `metadata`: Метаданные экспорта
- `packets`: Массив данных пакетов
- `statistics`: Статистика по трафику (если включена)

## Примеры использования

### Базовый парсинг
```bash
python traffic_parser_app.py parse --pcap-dir ./sample_pcaps
```

### Парсинг с фильтрацией
```bash
python traffic_parser_app.py parse --protocol TCP --port 443 --min-size 100
```

### Экспорт только HTTP трафика
```bash
python traffic_parser_app.py export --port 80 --port 8080
```

## Логирование

Приложение ведет подробные логи процесса парсинга. Уровень логирования можно настроить в `config.py`.

## Обработка ошибок

Приложение обрабатывает следующие типы ошибок:
- Отсутствие PCAP файлов
- Поврежденные PCAP файлы
- Ошибки базы данных
- Ошибки экспорта

## Производительность

- Обработка пакетов происходит батчами для оптимизации производительности
- Ограничение количества пакетов на файл предотвращает переполнение памяти
- Прогресс-бар показывает статус обработки

## Требования

- Python 3.7+
- Scapy 2.5.0+
- SQLAlchemy 2.0+
- Click для CLI интерфейса
- tqdm для прогресс-бара
