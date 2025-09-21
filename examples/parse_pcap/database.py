from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class TrafficPacket(Base):
    """Model for storing traffic packet data."""
    
    __tablename__ = 'traffic_packets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    source_ip = Column(String(45), nullable=True)  # IPv6 support
    destination_ip = Column(String(45), nullable=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)
    packet_size = Column(Integer, nullable=False)
    packet_data = Column(Text, nullable=True)  # JSON string for additional data
    file_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseHandler:
    """Handler for database operations."""
    
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
        
    def add_packet(self, session, packet_data):
        """Add a single packet to the database."""
        packet = TrafficPacket(**packet_data)
        session.add(packet)
        return packet
        
    def add_packets_batch(self, session, packets_data):
        """Add multiple packets to the database in batch."""
        packets = [TrafficPacket(**data) for data in packets_data]
        session.add_all(packets)
        return packets
        
    def get_all_packets(self, session):
        """Get all packets from the database."""
        return session.query(TrafficPacket).all()
        
    def get_packets_by_protocol(self, session, protocol):
        """Get packets filtered by protocol."""
        return session.query(TrafficPacket).filter(TrafficPacket.protocol == protocol).all()
        
    def get_packets_by_ip(self, session, ip_address):
        """Get packets filtered by IP address."""
        return session.query(TrafficPacket).filter(
            (TrafficPacket.source_ip == ip_address) | 
            (TrafficPacket.destination_ip == ip_address)
        ).all()
        
    def export_to_dict(self, packets):
        """Convert packets to dictionary format for JSON export."""
        result = []
        for packet in packets:
            packet_dict = {
                'id': packet.id,
                'timestamp': packet.timestamp.isoformat() if packet.timestamp else None,
                'source_ip': packet.source_ip,
                'destination_ip': packet.destination_ip,
                'source_port': packet.source_port,
                'destination_port': packet.destination_port,
                'protocol': packet.protocol,
                'packet_size': packet.packet_size,
                'packet_data': json.loads(packet.packet_data) if packet.packet_data else None,
                'file_name': packet.file_name,
                'created_at': packet.created_at.isoformat() if packet.created_at else None
            }
            result.append(packet_dict)
        return result
