#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Traffic Parser Application
"""

import os
import sys
import tempfile
import shutil
from scapy.all import Ether, IP, TCP, Raw, wrpcap

def create_sample_pcap():
    """Создает тестовый PCAP файл с несколькими пакетами."""
    
    # Создаем несколько тестовых пакетов
    packets = []
    
    # HTTP запрос
    http_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=12345, dport=80) / Raw(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
    packets.append(http_packet)
    
    # HTTPS запрос
    https_packet = Ether() / IP(src="192.168.1.100", dst="8.8.8.8") / TCP(sport=12346, dport=443) / Raw(b"CONNECT example.com:443 HTTP/1.1\r\n\r\n")
    packets.append(https_packet)
    
    # DNS запрос
    dns_packet = Ether() / IP(src="192.168.1.100", dst="8.8.8.8") / TCP(sport=12347, dport=53) / Raw(b"DNS query data")
    packets.append(dns_packet)
    
    # UDP пакет
    udp_packet = Ether() / IP(src="192.168.1.200", dst="192.168.1.1") / TCP(sport=12348, dport=8080) / Raw(b"UDP data")
    packets.append(udp_packet)
    
    # ICMP пакет
    icmp_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=12349, dport=0) / Raw(b"ICMP ping")
    packets.append(icmp_packet)
    
    return packets

def main():
    """Основная функция тестирования."""
    
    print("🧪 Тестирование Traffic Parser Application")
    print("=" * 50)
    
    # Создаем временную директорию для тестов
    temp_dir = tempfile.mkdtemp()
    test_pcap_dir = os.path.join(temp_dir, "test_pcaps")
    os.makedirs(test_pcap_dir)
    
    try:
        # Создаем тестовые PCAP файлы
        print("\n1. Создание тестовых PCAP файлов...")
        packets = create_sample_pcap()
        
        # Сохраняем в несколько файлов
        test_files = []
        for i, packet in enumerate(packets):
            filename = f"test_packet_{i+1}.pcap"
            filepath = os.path.join(test_pcap_dir, filename)
            wrpcap(filepath, [packet])
            test_files.append(filename)
            print(f"   ✅ Создан {filename}")
        
        print(f"   📁 Создано {len(test_files)} тестовых PCAP файлов в {test_pcap_dir}")
        
        # Импортируем и тестируем приложение
        print("\n2. Тестирование парсера...")
        
        try:
            from pcap_parser import PCAPParser
            
            parser = PCAPParser()
            parsed_packets = parser.parse_directory(test_pcap_dir)
            
            print(f"   ✅ Парсер обработал {len(parsed_packets)} пакетов")
            
            # Показываем статистику
            protocols = {}
            for packet in parsed_packets:
                protocol = packet.get('protocol', 'Unknown')
                protocols[protocol] = protocols.get(protocol, 0) + 1
            
            print("   📊 Статистика по протоколам:")
            for protocol, count in protocols.items():
                print(f"      {protocol}: {count} пакетов")
                
        except ImportError as e:
            print(f"   ❌ Ошибка импорта: {e}")
            print("   Убедитесь, что установлены все зависимости: pip install -r requirements.txt")
            return
        except Exception as e:
            print(f"   ❌ Ошибка парсинга: {e}")
            return
        
        # Тестируем базу данных
        print("\n3. Тестирование базы данных...")
        
        try:
            from database import DatabaseHandler
            
            # Создаем временную БД
            test_db_path = os.path.join(temp_dir, "test.db")
            db_handler = DatabaseHandler(f"sqlite:///{test_db_path}")
            db_handler.create_tables()
            
            # Сохраняем пакеты
            session = db_handler.get_session()
            db_handler.add_packets_batch(session, parsed_packets)
            session.commit()
            
            # Проверяем сохранение
            all_packets = db_handler.get_all_packets(session)
            print(f"   ✅ В базу данных сохранено {len(all_packets)} пакетов")
            
            session.close()
            
        except Exception as e:
            print(f"   ❌ Ошибка работы с БД: {e}")
            return
        
        # Тестируем JSON экспорт
        print("\n4. Тестирование JSON экспорта...")
        
        try:
            from json_exporter import JSONExporter
            
            test_json_path = os.path.join(temp_dir, "test_export.json")
            exporter = JSONExporter(test_json_path)
            
            # Конвертируем данные для экспорта
            packets_data = db_handler.export_to_dict(all_packets)
            success = exporter.export_packets(packets_data)
            
            if success:
                print(f"   ✅ Данные экспортированы в {test_json_path}")
                
                # Проверяем размер файла
                file_size = os.path.getsize(test_json_path)
                print(f"   📄 Размер JSON файла: {file_size} байт")
            else:
                print("   ❌ Ошибка экспорта в JSON")
                
        except Exception as e:
            print(f"   ❌ Ошибка JSON экспорта: {e}")
            return
        
        print("\n🎉 Все тесты прошли успешно!")
        print("\n📋 Созданные файлы:")
        print(f"   - Тестовые PCAP файлы: {test_pcap_dir}")
        print(f"   - Тестовая БД: {test_db_path}")
        print(f"   - JSON экспорт: {test_json_path}")
        
        print("\n🚀 Приложение готово к использованию!")
        print("Для работы с реальными PCAP файлами:")
        print("1. Поместите PCAP файлы в директорию pcap_files/")
        print("2. Запустите: python traffic_parser_app.py parse")
        print("3. Экспортируйте данные: python traffic_parser_app.py export")
        
    finally:
        # Очищаем временные файлы
        print(f"\n🧹 Очистка временных файлов...")
        shutil.rmtree(temp_dir)
        print("   ✅ Временные файлы удалены")

if __name__ == "__main__":
    main()
