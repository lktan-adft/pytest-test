"""
BACnet Client Wrapper for E2E Testing
Provides a clean interface for BACnet operations
"""
import logging
from typing import Optional, Any, Dict
import BAC0
from BAC0.core.devices.Points import NumericPoint

logger = logging.getLogger(__name__)


class BACnetClient:
    """Wrapper for BACnet operations using BAC0 library"""
    
    def __init__(
        self,
        local_ip: str,
        device_ip: str,
        device_id: int,
        bbmd_address: Optional[str] = None,
        bbmd_ttl: int = 900
    ):
        """
        Initialize BACnet client
        
        Args:
            local_ip: Local IP address for BACnet network
            device_ip: Target device IP address
            device_id: Target device ID
            bbmd_address: Optional BBMD address for foreign device registration
            bbmd_ttl: Time to live for BBMD registration
        """
        self.local_ip = local_ip
        self.device_ip = device_ip
        self.device_id = device_id
        self.bbmd_address = bbmd_address
        self.bbmd_ttl = bbmd_ttl
        
        self.bacnet = None
        self.device = None
        
    def connect(self) -> None:
        """Establish connection to BACnet network"""
        try:
            logger.info(f"Connecting to BACnet network on {self.local_ip}")
            
            # Initialize BAC0 with local IP
            if self.bbmd_address:
                logger.info(f"Registering as foreign device with BBMD: {self.bbmd_address}")
                self.bacnet = BAC0.connect(
                    ip=self.local_ip,
                    bbmdAddress=self.bbmd_address,
                    bbmdTTL=self.bbmd_ttl
                )
            else:
                self.bacnet = BAC0.lite(ip=self.local_ip)
            
            logger.info("BACnet network connection established")
            
            # Discover and connect to device
            logger.info(f"Discovering device at {self.device_ip} with ID {self.device_id}")
            device_address = f"{self.device_ip}:{self.device_id}"
            self.device = BAC0.device(device_address, self.device_id, self.bacnet)
            
            if self.device:
                logger.info(f"Successfully connected to device: {self.device.properties.name}")
            else:
                raise ConnectionError(f"Failed to connect to device {device_address}")
                
        except Exception as e:
            logger.error(f"Failed to connect to BACnet network: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from BACnet network"""
        try:
            if self.bacnet:
                logger.info("Disconnecting from BACnet network")
                self.bacnet.disconnect()
                self.bacnet = None
                self.device = None
                logger.info("Disconnected successfully")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            raise
    
    def read_analog_value(self, instance: int) -> float:
        """
        Read present value from an AnalogValue object
        
        Args:
            instance: Instance number of the AnalogValue object
            
        Returns:
            Current present value
        """
        try:
            logger.info(f"Reading AnalogValue:{instance}")
            
            # Read using BAC0
            point_name = f"analogValue:{instance}"
            value = self.device[point_name]
            
            logger.info(f"Read AnalogValue:{instance} = {value}")
            return float(value)
            
        except Exception as e:
            logger.error(f"Failed to read AnalogValue:{instance}: {e}")
            raise
    
    def write_analog_value(self, instance: int, value: float, priority: int = 8) -> None:
        """
        Write present value to an AnalogValue object
        
        Args:
            instance: Instance number of the AnalogValue object
            value: Value to write
            priority: Write priority (1-16, default 8)
        """
        try:
            logger.info(f"Writing {value} to AnalogValue:{instance} at priority {priority}")
            
            # Write using BAC0
            point_name = f"analogValue:{instance}"
            self.device[point_name] = value
            
            logger.info(f"Successfully wrote {value} to AnalogValue:{instance}")
            
        except Exception as e:
            logger.error(f"Failed to write to AnalogValue:{instance}: {e}")
            raise
    
    def read_property(
        self,
        object_type: str,
        instance: int,
        property_name: str
    ) -> Any:
        """
        Read a specific property from a BACnet object
        
        Args:
            object_type: Object type (e.g., 'analogValue', 'analogInput')
            instance: Instance number
            property_name: Property name (e.g., 'presentValue', 'units')
            
        Returns:
            Property value
        """
        try:
            logger.info(f"Reading {object_type}:{instance}.{property_name}")
            
            # Construct point name
            point_name = f"{object_type}:{instance}"
            
            # Get the point object
            point = self.device.find_point(point_name)
            
            if not point:
                raise ValueError(f"Point {point_name} not found")
            
            # Read property
            value = point.properties.__dict__.get(property_name)
            
            logger.info(f"Read {object_type}:{instance}.{property_name} = {value}")
            return value
            
        except Exception as e:
            logger.error(f"Failed to read property: {e}")
            raise
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get basic device information
        
        Returns:
            Dictionary with device properties
        """
        try:
            if not self.device:
                raise ConnectionError("Not connected to device")
            
            info = {
                "name": self.device.properties.name,
                "device_id": self.device.properties.device_id,
                "vendor": self.device.properties.vendor_name,
                "model": self.device.properties.model_name,
                "description": self.device.properties.description,
            }
            
            logger.info(f"Device info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()