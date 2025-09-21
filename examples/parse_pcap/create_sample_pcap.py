#!/usr/bin/env python3
"""
Скрипт для создания примера PCAP файла с различными типами трафика
"""

import os
from scapy.all import Ether, IP, TCP, UDP, ICMP, Raw, wrpcap
from datetime import datetime

def create_sample_pcap():
    """Создает пример PCAP файла с различными типами трафика."""
    
    print("🔧 Создание примера PCAP файла...")
    
    # Создаем список пакетов
    packets = []
    
    # 1. HTTP запрос (GET)
    http_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=12345, dport=80) / Raw(b"GET /index.html HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0\r\n\r\n")
    packets.append(http_packet)
    
    # 2. HTTP ответ
    http_response = Ether() / IP(src="192.168.1.1", dst="192.168.1.100") / TCP(sport=80, dport=12345) / Raw(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 1234\r\n\r\n<html><body>Hello World</body></html>")
    packets.append(http_response)
    
    # 3. HTTPS запрос (TLS handshake simulation)
    https_packet = Ether() / IP(src="192.168.1.100", dst="8.8.8.8") / TCP(sport=12346, dport=443) / Raw(b"CONNECT example.com:443 HTTP/1.1\r\nHost: example.com\r\n\r\n")
    packets.append(https_packet)
    
    # 4. DNS запрос
    dns_query = Ether() / IP(src="192.168.1.100", dst="8.8.8.8") / UDP(sport=12347, dport=53) / Raw(b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01")
    packets.append(dns_query)
    
    # 5. DNS ответ
    dns_response = Ether() / IP(src="8.8.8.8", dst="192.168.1.100") / UDP(sport=53, dport=12347) / Raw(b"\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\x5d\xb8\xd8\x22")
    packets.append(dns_response)
    
    # 6. ICMP ping запрос
    icmp_ping = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / ICMP(type=8, code=0) / Raw(b"Hello, this is a ping packet!")
    packets.append(icmp_ping)
    
    # 7. ICMP ping ответ
    icmp_pong = Ether() / IP(src="192.168.1.1", dst="192.168.1.100") / ICMP(type=0, code=0) / Raw(b"Hello, this is a ping packet!")
    packets.append(icmp_pong)
    
    # 8. SSH соединение
    ssh_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.50") / TCP(sport=12348, dport=22) / Raw(b"SSH-2.0-OpenSSH_8.0\r\n")
    packets.append(ssh_packet)
    
    # 9. FTP команда
    ftp_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.200") / TCP(sport=12349, dport=21) / Raw(b"USER anonymous\r\n")
    packets.append(ftp_packet)
    
    # 10. SMTP команда
    smtp_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=12350, dport=25) / Raw(b"HELO example.com\r\n")
    packets.append(smtp_packet)
    
    # 11. Большой пакет (для тестирования размера)
    large_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=12351, dport=8080) / Raw(b"X" * 1000)  # 1000 байт данных
    packets.append(large_packet)
    
    # 12. Маленький пакет
    small_packet = Ether() / IP(src="192.168.1.200", dst="192.168.1.1") / TCP(sport=12352, dport=8080) / Raw(b"A")
    packets.append(small_packet)
    
    # 13. UDP пакет с данными
    udp_data = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / UDP(sport=12353, dport=1234) / Raw(b"This is UDP data packet")
    packets.append(udp_data)
    
    # 14. IPv6 пакет
    ipv6_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1") / TCP(sport=12354, dport=80) / Raw(b"IPv6 test packet")
    packets.append(ipv6_packet)
    
    # 15. Пакет с фрагментацией (симуляция)
    fragmented_packet = Ether() / IP(src="192.168.1.100", dst="192.168.1.1", flags=1) / TCP(sport=12355, dport=80) / Raw(b"Fragmented packet data")
    packets.append(fragmented_packet)
    
    return packets

def main():
    """Основная функция для создания примера PCAP файла."""
    
    print("🚀 Создание примера PCAP файла для Traffic Parser Application")
    print("=" * 60)
    
    # Создаем директорию если не существует
    pcap_dir = "pcap_files"
    if not os.path.exists(pcap_dir):
        os.makedirs(pcap_dir)
        print(f"📁 Создана директория: {pcap_dir}")
    
    # Создаем пакеты
    packets = create_sample_pcap()
    
    # Сохраняем в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sample_traffic_{timestamp}.pcap"
    filepath = os.path.join(pcap_dir, filename)
    
    try:
        wrpcap(filepath, packets)
        print(f"✅ PCAP файл создан: {filepath}")
        print(f"📊 Количество пакетов: {len(packets)}")
        
        # Показываем статистику
        protocols = {}
        total_size = 0
        
        for packet in packets:
            # Определяем протокол
            if packet.haslayer(TCP):
                protocol = "TCP"
            elif packet.haslayer(UDP):
                protocol = "UDP"
            elif packet.haslayer(ICMP):
                protocol = "ICMP"
            else:
                protocol = "Other"
            
            protocols[protocol] = protocols.get(protocol, 0) + 1
            total_size += len(packet)
        
        print("\n📈 Статистика пакетов:")
        for protocol, count in sorted(protocols.items(), key=lambda x: x[1], reverse=True):
            print(f"   {protocol}: {count} пакетов")
        
        print(f"\n📦 Общий размер: {total_size} байт")
        print(f"📄 Размер файла: {os.path.getsize(filepath)} байт")
        
        print(f"\n🎯 Теперь можно протестировать приложение:")
        print(f"   python traffic_parser_app.py parse --pcap-dir {pcap_dir}")
        print(f"   python traffic_parser_app.py export")
        
    except Exception as e:
        print(f"❌ Ошибка создания PCAP файла: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
