import os
import logging
from typing import List, Dict, Any, Optional
from tqdm import tqdm
import click

from config import Config
from database import DatabaseHandler
from pcap_parser import PCAPParser
from json_exporter import JSONExporter

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrafficParserApp:
    """Main application class for traffic parsing."""
    
    def __init__(self):
        self.config = Config()
        self.db_handler = DatabaseHandler(self.config.DATABASE_URL)
        self.parser = PCAPParser(self.config.MAX_PACKETS_PER_FILE)
        self.exporter = JSONExporter(self.config.OUTPUT_JSON_FILE)
        
    def initialize_database(self):
        """Initialize the database and create tables."""
        try:
            self.db_handler.create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def parse_pcap_files(self, directory_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse PCAP files from the specified directory.
        
        Args:
            directory_path: Path to directory with PCAP files
            
        Returns:
            List of parsed packet data
        """
        if not directory_path:
            directory_path = self.config.PCAP_DIRECTORY
            
        if not os.path.exists(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return []
        
        logger.info(f"Starting to parse PCAP files from: {directory_path}")
        
        # Parse all PCAP files
        all_packets = self.parser.parse_directory(directory_path)
        
        logger.info(f"Parsed {len(all_packets)} packets from PCAP files")
        return all_packets
    
    def save_to_database(self, packets_data: List[Dict[str, Any]], 
                        batch_size: Optional[int] = None) -> bool:
        """
        Save parsed packets to the database.
        
        Args:
            packets_data: List of packet data dictionaries
            batch_size: Size of batches for database insertion
            
        Returns:
            True if successful, False otherwise
        """
        if not packets_data:
            logger.warning("No packet data to save")
            return True
        
        batch_size = batch_size or self.config.BATCH_SIZE
        session = self.db_handler.get_session()
        
        try:
            logger.info(f"Saving {len(packets_data)} packets to database")
            
            # Process packets in batches
            for i in tqdm(range(0, len(packets_data), batch_size), 
                         desc="Saving packets to database"):
                batch = packets_data[i:i + batch_size]
                self.db_handler.add_packets_batch(session, batch)
                session.commit()
            
            logger.info("Successfully saved all packets to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def export_to_json(self, include_statistics: bool = True, 
                      filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Export database data to JSON file.
        
        Args:
            include_statistics: Whether to include statistics
            filters: Optional filters to apply
            
        Returns:
            True if successful, False otherwise
        """
        session = self.db_handler.get_session()
        
        try:
            logger.info("Exporting data from database to JSON")
            
            # Get all packets from database
            packets = self.db_handler.get_all_packets(session)
            
            if not packets:
                logger.warning("No packets found in database")
                return False
            
            # Convert to dictionary format
            packets_data = self.db_handler.export_to_dict(packets)
            
            # Export to JSON
            if filters:
                success = self.exporter.export_filtered_packets(packets_data, filters)
            else:
                success = self.exporter.export_packets(packets_data)
            
            # Export statistics if requested
            if include_statistics and success:
                self.exporter.export_statistics(packets_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
        finally:
            session.close()
    
    def run_full_pipeline(self, pcap_directory: Optional[str] = None, 
                         export_filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Run the complete pipeline: parse PCAP files, save to database, export to JSON.
        
        Args:
            pcap_directory: Directory with PCAP files
            export_filters: Optional filters for JSON export
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting full traffic parsing pipeline")
            
            # Initialize database
            self.initialize_database()
            
            # Parse PCAP files
            packets_data = self.parse_pcap_files(pcap_directory)
            
            if not packets_data:
                logger.error("No packets were parsed from PCAP files")
                return False
            
            # Save to database
            if not self.save_to_database(packets_data):
                logger.error("Failed to save packets to database")
                return False
            
            # Export to JSON
            if not self.export_to_json(filters=export_filters):
                logger.error("Failed to export data to JSON")
                return False
            
            logger.info("Pipeline completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return False

# CLI Interface
@click.group()
def cli():
    """Traffic Parser CLI - Parse PCAP files and export to JSON."""
    pass

@cli.command()
@click.option('--pcap-dir', default=None, help='Directory containing PCAP files')
@click.option('--output', default=None, help='Output JSON file path')
@click.option('--protocol', default=None, help='Filter by protocol (TCP, UDP, ICMP, etc.)')
@click.option('--ip', default=None, help='Filter by IP address')
@click.option('--port', default=None, type=int, help='Filter by port number')
@click.option('--min-size', default=None, type=int, help='Minimum packet size')
@click.option('--max-size', default=None, type=int, help='Maximum packet size')
@click.option('--no-stats', is_flag=True, help='Skip statistics export')
def parse(pcap_dir, output, protocol, ip, port, min_size, max_size, no_stats):
    """Parse PCAP files and export to JSON."""
    app = TrafficParserApp()
    
    # Override config if CLI options provided
    if pcap_dir:
        app.config.PCAP_DIRECTORY = pcap_dir
    if output:
        app.exporter = JSONExporter(output)
    
    # Prepare filters
    filters = {}
    if protocol:
        filters['protocol'] = protocol
    if ip:
        filters['ip_address'] = ip
    if port:
        filters['port'] = port
    if min_size:
        filters['min_size'] = min_size
    if max_size:
        filters['max_size'] = max_size
    
    # Run pipeline
    success = app.run_full_pipeline(
        pcap_directory=pcap_dir,
        export_filters=filters if filters else None
    )
    
    if success:
        click.echo("✅ Traffic parsing completed successfully!")
    else:
        click.echo("❌ Traffic parsing failed!")
        exit(1)

@cli.command()
@click.option('--output', default=None, help='Output JSON file path')
@click.option('--protocol', default=None, help='Filter by protocol')
@click.option('--ip', default=None, help='Filter by IP address')
def export(output, protocol, ip):
    """Export existing database data to JSON."""
    app = TrafficParserApp()
    
    if output:
        app.exporter = JSONExporter(output)
    
    filters = {}
    if protocol:
        filters['protocol'] = protocol
    if ip:
        filters['ip_address'] = ip
    
    success = app.export_to_json(filters=filters if filters else None)
    
    if success:
        click.echo("✅ Export completed successfully!")
    else:
        click.echo("❌ Export failed!")
        exit(1)

@cli.command()
def init():
    """Initialize the database."""
    app = TrafficParserApp()
    app.initialize_database()
    click.echo("✅ Database initialized successfully!")

if __name__ == "__main__":
    cli()
