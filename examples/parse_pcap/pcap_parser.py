import os
import json
from datetime import datetime
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, IPv6
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PCAPParser:
    """Parser for PCAP files using Scapy."""
    
    def __init__(self, max_packets_per_file: int = 10000):
        self.max_packets_per_file = max_packets_per_file
        
    def parse_pcap_file(self, file_path: str) -> List[Dict]:
        """
        Parse a PCAP file and extract packet information.
        
        Args:
            file_path: Path to the PCAP file
            
        Returns:
            List of dictionaries containing packet data
        """
        packets_data = []
        
        try:
            logger.info(f"Parsing PCAP file: {file_path}")
            
            # Read PCAP file
            packets = rdpcap(file_path)
            
            # Limit number of packets if specified
            if self.max_packets_per_file and len(packets) > self.max_packets_per_file:
                packets = packets[:self.max_packets_per_file]
                logger.warning(f"Limited to {self.max_packets_per_file} packets from {file_path}")
            
            file_name = os.path.basename(file_path)
            
            for i, packet in enumerate(packets):
                try:
                    packet_data = self._extract_packet_info(packet, file_name)
                    if packet_data:
                        packets_data.append(packet_data)
                except Exception as e:
                    logger.error(f"Error parsing packet {i} from {file_path}: {e}")
                    continue
                    
            logger.info(f"Successfully parsed {len(packets_data)} packets from {file_path}")
            
        except Exception as e:
            logger.error(f"Error reading PCAP file {file_path}: {e}")
            
        return packets_data
    
    def _extract_packet_info(self, packet, file_name: str) -> Optional[Dict]:
        """
        Extract relevant information from a single packet.
        
        Args:
            packet: Scapy packet object
            file_name: Name of the source file
            
        Returns:
            Dictionary with packet information or None if extraction fails
        """
        try:
            packet_data = {
                'timestamp': datetime.fromtimestamp(float(packet.time)),
                'packet_size': len(packet),
                'file_name': file_name,
                'packet_data': None
            }
            
            # Extract IP information
            if packet.haslayer(IP):
                ip_layer = packet[IP]
                packet_data.update({
                    'source_ip': ip_layer.src,
                    'destination_ip': ip_layer.dst,
                    'protocol': 'IP'
                })
                
                # Extract transport layer information
                if packet.haslayer(TCP):
                    tcp_layer = packet[TCP]
                    packet_data.update({
                        'source_port': tcp_layer.sport,
                        'destination_port': tcp_layer.dport,
                        'protocol': 'TCP'
                    })
                    packet_data['packet_data'] = json.dumps({
                        'tcp_flags': str(tcp_layer.flags),
                        'tcp_seq': tcp_layer.seq,
                        'tcp_ack': tcp_layer.ack,
                        'tcp_window': tcp_layer.window
                    })
                    
                elif packet.haslayer(UDP):
                    udp_layer = packet[UDP]
                    packet_data.update({
                        'source_port': udp_layer.sport,
                        'destination_port': udp_layer.dport,
                        'protocol': 'UDP'
                    })
                    packet_data['packet_data'] = json.dumps({
                        'udp_length': udp_layer.len,
                        'udp_checksum': udp_layer.chksum
                    })
                    
                elif packet.haslayer(ICMP):
                    icmp_layer = packet[ICMP]
                    packet_data.update({
                        'protocol': 'ICMP'
                    })
                    packet_data['packet_data'] = json.dumps({
                        'icmp_type': icmp_layer.type,
                        'icmp_code': icmp_layer.code
                    })
                    
            elif packet.haslayer(IPv6):
                ipv6_layer = packet[IPv6]
                packet_data.update({
                    'source_ip': ipv6_layer.src,
                    'destination_ip': ipv6_layer.dst,
                    'protocol': 'IPv6'
                })
                
                # Check for transport layer protocols in IPv6
                if packet.haslayer(TCP):
                    tcp_layer = packet[TCP]
                    packet_data.update({
                        'source_port': tcp_layer.sport,
                        'destination_port': tcp_layer.dport,
                        'protocol': 'TCPv6'
                    })
                elif packet.haslayer(UDP):
                    udp_layer = packet[UDP]
                    packet_data.update({
                        'source_port': udp_layer.sport,
                        'destination_port': udp_layer.dport,
                        'protocol': 'UDPv6'
                    })
            else:
                # Non-IP packet
                packet_data.update({
                    'protocol': 'Other',
                    'packet_data': json.dumps({
                        'packet_summary': packet.summary(),
                        'packet_layers': [layer.name for layer in packet.layers()]
                    })
                })
            
            return packet_data
            
        except Exception as e:
            logger.error(f"Error extracting packet info: {e}")
            return None
    
    def parse_directory(self, directory_path: str) -> List[Dict]:
        """
        Parse all PCAP files in a directory.
        
        Args:
            directory_path: Path to directory containing PCAP files
            
        Returns:
            List of all packet data from all files
        """
        all_packets = []
        
        if not os.path.exists(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return all_packets
            
        pcap_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.pcap', '.pcapng'))]
        
        if not pcap_files:
            logger.warning(f"No PCAP files found in directory: {directory_path}")
            return all_packets
            
        logger.info(f"Found {len(pcap_files)} PCAP files in {directory_path}")
        
        for pcap_file in pcap_files:
            file_path = os.path.join(directory_path, pcap_file)
            packets_data = self.parse_pcap_file(file_path)
            all_packets.extend(packets_data)
            
        logger.info(f"Total packets parsed: {len(all_packets)}")
        return all_packets
