#!/usr/bin/env python3
"""
Пример использования Traffic Parser Application
"""

import os
from traffic_parser_app import TrafficParserApp

def main():
    """Пример использования приложения."""
    
    # Создаем экземпляр приложения
    app = TrafficParserApp()
    
    print("🚀 Traffic Parser Application - Пример использования")
    print("=" * 50)
    
    # 1. Инициализация базы данных
    print("\n1. Инициализация базы данных...")
    try:
        app.initialize_database()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # 2. Проверяем наличие PCAP файлов
    pcap_dir = app.config.PCAP_DIRECTORY
    print(f"\n2. Проверка директории с PCAP файлами: {pcap_dir}")
    
    if not os.path.exists(pcap_dir):
        print(f"⚠️  Директория {pcap_dir} не существует")
        print("Создайте директорию и поместите туда PCAP файлы")
        return
    
    pcap_files = [f for f in os.listdir(pcap_dir) if f.lower().endswith(('.pcap', '.pcapng'))]
    
    if not pcap_files:
        print(f"⚠️  В директории {pcap_dir} не найдено PCAP файлов")
        print("Поместите PCAP файлы в эту директорию для парсинга")
        return
    
    print(f"✅ Найдено {len(pcap_files)} PCAP файлов:")
    for file in pcap_files[:5]:  # Показываем первые 5 файлов
        print(f"   - {file}")
    if len(pcap_files) > 5:
        print(f"   ... и еще {len(pcap_files) - 5} файлов")
    
    # 3. Парсинг PCAP файлов
    print(f"\n3. Парсинг PCAP файлов...")
    try:
        packets_data = app.parse_pcap_files()
        
        if not packets_data:
            print("⚠️  Не удалось распарсить пакеты из PCAP файлов")
            return
        
        print(f"✅ Распарсено {len(packets_data)} пакетов")
        
        # Показываем статистику по протоколам
        protocols = {}
        for packet in packets_data:
            protocol = packet.get('protocol', 'Unknown')
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        print("\n📊 Статистика по протоколам:")
        for protocol, count in sorted(protocols.items(), key=lambda x: x[1], reverse=True):
            print(f"   {protocol}: {count} пакетов")
            
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return
    
    # 4. Сохранение в базу данных
    print(f"\n4. Сохранение в базу данных...")
    try:
        success = app.save_to_database(packets_data)
        if success:
            print("✅ Данные сохранены в базу данных")
        else:
            print("❌ Ошибка сохранения в БД")
            return
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return
    
    # 5. Экспорт в JSON
    print(f"\n5. Экспорт в JSON...")
    try:
        success = app.export_to_json(include_statistics=True)
        if success:
            print(f"✅ Данные экспортированы в {app.config.OUTPUT_JSON_FILE}")
            print(f"✅ Статистика экспортирована в {app.config.OUTPUT_JSON_FILE.replace('.json', '_statistics.json')}")
        else:
            print("❌ Ошибка экспорта в JSON")
            return
    except Exception as e:
        print(f"❌ Ошибка экспорта: {e}")
        return
    
    # 6. Демонстрация фильтрации
    print(f"\n6. Демонстрация фильтрации...")
    
    # Фильтр по TCP трафику
    tcp_filters = {'protocol': 'TCP'}
    print("   Фильтрация TCP трафика...")
    try:
        success = app.export_to_json(filters=tcp_filters)
        if success:
            tcp_output = app.config.OUTPUT_JSON_FILE.replace('.json', '_tcp_filtered.json')
            print(f"✅ TCP трафик экспортирован в {tcp_output}")
    except Exception as e:
        print(f"❌ Ошибка фильтрации TCP: {e}")
    
    print("\n🎉 Пример использования завершен!")
    print("\nДля более детального использования см. README.md")
    print("Или используйте CLI команды:")
    print("  python traffic_parser_app.py parse --help")
    print("  python traffic_parser_app.py export --help")

if __name__ == "__main__":
    main()
