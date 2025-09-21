import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class JSONExporter:
    """Exporter for converting database data to JSON format."""
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        
    def export_packets(self, packets_data: List[Dict[str, Any]], 
                      include_metadata: bool = True) -> bool:
        """
        Export packets data to JSON file.
        
        Args:
            packets_data: List of packet dictionaries
            include_metadata: Whether to include export metadata
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'total_packets': len(packets_data),
                    'export_version': '1.0'
                } if include_metadata else None,
                'packets': packets_data
            }
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Write to JSON file with pretty formatting
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Successfully exported {len(packets_data)} packets to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    def export_filtered_packets(self, packets_data: List[Dict[str, Any]], 
                              filters: Dict[str, Any] = None) -> bool:
        """
        Export filtered packets data to JSON file.
        
        Args:
            packets_data: List of packet dictionaries
            filters: Dictionary with filter criteria
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            filtered_packets = self._apply_filters(packets_data, filters or {})
            
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'total_packets': len(filtered_packets),
                    'filters_applied': filters,
                    'export_version': '1.0'
                },
                'packets': filtered_packets
            }
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Write to JSON file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Successfully exported {len(filtered_packets)} filtered packets to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting filtered data to JSON: {e}")
            return False
    
    def _apply_filters(self, packets_data: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filters to packets data.
        
        Args:
            packets_data: List of packet dictionaries
            filters: Dictionary with filter criteria
            
        Returns:
            Filtered list of packets
        """
        filtered_packets = packets_data.copy()
        
        # Filter by protocol
        if 'protocol' in filters and filters['protocol']:
            filtered_packets = [p for p in filtered_packets 
                              if p.get('protocol') == filters['protocol']]
        
        # Filter by IP address
        if 'ip_address' in filters and filters['ip_address']:
            ip = filters['ip_address']
            filtered_packets = [p for p in filtered_packets 
                              if p.get('source_ip') == ip or p.get('destination_ip') == ip]
        
        # Filter by port
        if 'port' in filters and filters['port']:
            port = filters['port']
            filtered_packets = [p for p in filtered_packets 
                              if p.get('source_port') == port or p.get('destination_port') == port]
        
        # Filter by packet size range
        if 'min_size' in filters and filters['min_size']:
            filtered_packets = [p for p in filtered_packets 
                              if p.get('packet_size', 0) >= filters['min_size']]
        
        if 'max_size' in filters and filters['max_size']:
            filtered_packets = [p for p in filtered_packets 
                              if p.get('packet_size', 0) <= filters['max_size']]
        
        # Filter by time range
        if 'start_time' in filters and filters['start_time']:
            start_time = datetime.fromisoformat(filters['start_time'])
            filtered_packets = [p for p in filtered_packets 
                              if datetime.fromisoformat(p.get('timestamp', '')) >= start_time]
        
        if 'end_time' in filters and filters['end_time']:
            end_time = datetime.fromisoformat(filters['end_time'])
            filtered_packets = [p for p in filtered_packets 
                              if datetime.fromisoformat(p.get('timestamp', '')) <= end_time]
        
        return filtered_packets
    
    def export_statistics(self, packets_data: List[Dict[str, Any]]) -> bool:
        """
        Export packet statistics to JSON file.
        
        Args:
            packets_data: List of packet dictionaries
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            stats = self._calculate_statistics(packets_data)
            
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'total_packets': len(packets_data),
                    'export_version': '1.0'
                },
                'statistics': stats
            }
            
            # Create statistics file name
            stats_file = self.output_file.replace('.json', '_statistics.json')
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(stats_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Write to JSON file
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Successfully exported statistics to {stats_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting statistics: {e}")
            return False
    
    def _calculate_statistics(self, packets_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics from packets data.
        
        Args:
            packets_data: List of packet dictionaries
            
        Returns:
            Dictionary with calculated statistics
        """
        if not packets_data:
            return {}
        
        # Protocol distribution
        protocols = {}
        for packet in packets_data:
            protocol = packet.get('protocol', 'Unknown')
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        # IP address distribution
        source_ips = {}
        dest_ips = {}
        for packet in packets_data:
            if packet.get('source_ip'):
                source_ips[packet['source_ip']] = source_ips.get(packet['source_ip'], 0) + 1
            if packet.get('destination_ip'):
                dest_ips[packet['destination_ip']] = dest_ips.get(packet['destination_ip'], 0) + 1
        
        # Port distribution
        source_ports = {}
        dest_ports = {}
        for packet in packets_data:
            if packet.get('source_port'):
                source_ports[packet['source_port']] = source_ports.get(packet['source_port'], 0) + 1
            if packet.get('destination_port'):
                dest_ports[packet['destination_port']] = dest_ports.get(packet['destination_port'], 0) + 1
        
        # Packet size statistics
        packet_sizes = [packet.get('packet_size', 0) for packet in packets_data]
        
        return {
            'total_packets': len(packets_data),
            'protocol_distribution': protocols,
            'top_source_ips': dict(sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_destination_ips': dict(sorted(dest_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_source_ports': dict(sorted(source_ports.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_destination_ports': dict(sorted(dest_ports.items(), key=lambda x: x[1], reverse=True)[:10]),
            'packet_size_stats': {
                'min': min(packet_sizes) if packet_sizes else 0,
                'max': max(packet_sizes) if packet_sizes else 0,
                'average': sum(packet_sizes) / len(packet_sizes) if packet_sizes else 0,
                'total_bytes': sum(packet_sizes)
            }
        }
