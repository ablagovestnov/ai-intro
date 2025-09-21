# 📁 Examples - Примеры реализации

Эта папка содержит примеры реализации различных приложений и решений.

## 🗂️ Структура

### `parse_pcap/` - Приложение для парсинга PCAP файлов
Полнофункциональное приложение на Python для:
- Парсинга PCAP файлов с использованием Scapy
- Сохранения данных в SQLite базу данных
- Экспорта данных в JSON формат с фильтрацией
- CLI интерфейса для удобного использования
- Подробной статистики трафика

**Основные файлы:**
- `traffic_parser_app.py` - Главное приложение с CLI
- `pcap_parser.py` - Парсер PCAP файлов
- `database.py` - Модели и обработчик SQLite
- `json_exporter.py` - Экспорт в JSON
- `config.py` - Конфигурация
- `requirements.txt` - Зависимости
- `README.md` - Подробная документация
- `QUICKSTART.md` - Быстрый старт
- `test_app.py` - Автоматические тесты
- `example_usage.py` - Пример использования

**Демонстрационные файлы:**
- `pcap_files/` - Директория с примером PCAP файла
- `create_sample_pcap.py` - Скрипт создания тестового PCAP
- `traffic_data.db` - Пример SQLite базы данных
- `traffic_export*.json` - Примеры JSON экспорта
- `DEMO_RESULTS.md` - Результаты демонстрации

**Документация по безопасности:**
- `SECURITY_REPORT.md` - Отчет о безопасности модулей
- `PROJECT_SUMMARY.md` - Резюме проекта

## 🚀 Быстрый старт

Для запуска примера парсинга PCAP:

```bash
cd examples/parse_pcap
pip install -r requirements.txt
python traffic_parser_app.py init
python traffic_parser_app.py parse --pcap-dir pcap_files
python traffic_parser_app.py export
```

## 📚 Документация

Каждый пример содержит подробную документацию:
- README.md - основная документация
- QUICKSTART.md - быстрый старт
- Примеры использования и тесты

---

*Примеры созданы для демонстрации различных подходов к решению задач программирования.*
