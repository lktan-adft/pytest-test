"""
BACnet Client with Proper Event Loop Management
Handles asyncio event loop for BAC0 library
"""
import logging
import time
import asyncio
import threading
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

try:
    import BAC0
except ImportError as e:
    logger.error(f"Failed to import BAC0: {e}")
    raise


class EventLoopBACnetClient:
    """BACnet client that manages its own event loop in a separate thread"""
    
    def __init__(
        self,
        local_ip: str,
        device_ip: str,
        device_id: int,
        bbmd_address: Optional[str] = None,
        bbmd_ttl: int = 900
    ):
        """
        Initialize BACnet client with event loop management
        
        Args:
            local_ip: Local IP address for BACnet network
            device_ip: Target device IP address
            device_id: Target device ID
            bbmd_address: Optional BBMD address
            bbmd_ttl: Time to live for BBMD registration
        """
        self.local_ip = local_ip
        self.device_ip = device_ip
        self.device_id = device_id
        self.bbmd_address = bbmd_address
        self.bbmd_ttl = bbmd_ttl
        
        self.bacnet = None
        self.device_address = f"{self.device_ip}:{self.device_id}"
        
        # Event loop management
        self.loop = None
        self.loop_thread = None
        self._stop_event = threading.Event()
        
    def _run_event_loop(self):
        """Run event loop in separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        logger.info("Event loop started in separate thread")
        
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
            logger.info("Event loop closed")
    
    def _start_event_loop(self):
        """Start event loop in background thread"""
        if self.loop_thread is None or not self.loop_thread.is_alive():
            self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
            self.loop_thread.start()
            
            # Wait for loop to be ready
            timeout = 5
            start_time = time.time()
            while self.loop is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.loop is None:
                raise RuntimeError("Failed to start event loop")
            
            logger.info("Event loop thread started successfully")
    
    def _stop_event_loop(self):
        """Stop the event loop"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            
            if self.loop_thread:
                self.loop_thread.join(timeout=5)
    
    def connect(self) -> None:
        """Establish connection to BACnet network"""
        try:
            # Start event loop first
            self._start_event_loop()
            
            logger.info(f"Connecting to BACnet network on {self.local_ip}")
            
            # Create BAC0 instance in the event loop
            future = asyncio.run_coroutine_threadsafe(
                self._async_connect(),
                self.loop
            )
            
            # Wait for connection with timeout
            self.bacnet = future.result(timeout=10)
            
            # Give network time to initialize
            time.sleep(2)
            
            logger.info("BACnet network connection established")
            logger.info(f"Device address: {self.device_address}")
            
        except Exception as e:
            logger.error(f"Failed to connect to BACnet network: {e}")
            self._stop_event_loop()
            raise
    
    async def _async_connect(self):
        """Async connection method"""
        if self.bbmd_address:
            logger.info(f"Connecting with BBMD: {self.bbmd_address}")
            bacnet = BAC0.connect(
                ip=self.local_ip,
                bbmdAddress=self.bbmd_address,
                bbmdTTL=self.bbmd_ttl
            )
        else:
            bacnet = BAC0.lite(ip=self.local_ip)
        
        return bacnet
    
    def disconnect(self) -> None:
        """Disconnect from BACnet network"""
        try:
            if self.bacnet:
                logger.info("Disconnecting from BACnet network")
                
                # Disconnect BAC0
                self.bacnet.disconnect()
                time.sleep(1)  # Wait for port to release
                self.bacnet = None
                
                logger.info("Disconnected from BACnet")
            
            # Stop event loop
            self._stop_event_loop()
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def read_analog_value(self, instance: int) -> float:
        """
        Read present value from an AnalogValue object
        
        Args:
            instance: Instance number of the AnalogValue object
            
        Returns:
            Current present value
        """
        try:
            if not self.bacnet:
                raise ConnectionError("Not connected to BACnet network")
            
            logger.info(f"Reading AnalogValue:{instance} from {self.device_address}")
            
            # Use BAC0 read method
            request = f"{self.device_address} analogValue {instance} presentValue"
            
            value = self.bacnet.read(request)
            
            if value is None:
                raise ValueError(f"Failed to read AnalogValue:{instance} - got None response")
            
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
            if not self.bacnet:
                raise ConnectionError("Not connected to BACnet network")
            
            logger.info(f"Writing {value} to AnalogValue:{instance} at priority {priority}")
            
            # Use BAC0 write method
            request = f"{self.device_address} analogValue {instance} presentValue {value} - {priority}"
            
            result = self.bacnet.write(request)
            
            logger.info(f"Write result: {result}")
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
            if not self.bacnet:
                raise ConnectionError("Not connected to BACnet network")
            
            logger.info(f"Reading {object_type}:{instance}.{property_name}")
            
            request = f"{self.device_address} {object_type} {instance} {property_name}"
            
            value = self.bacnet.read(request)
            
            logger.info(f"Read {object_type}:{instance}.{property_name} = {value}")
            return value
            
        except Exception as e:
            logger.error(f"Failed to read property: {e}")
            raise
    
    def whois(self) -> list:
        """
        Perform Who-Is to discover devices on network
        
        Returns:
            List of discovered devices
        """
        try:
            if not self.bacnet:
                raise ConnectionError("Not connected to BACnet network")
            
            logger.info("Performing Who-Is discovery...")
            self.bacnet.whois()
            
            # Wait for I-Am responses
            time.sleep(3)
            
            devices = self.bacnet.devices
            logger.info(f"Discovered {len(devices)} devices")
            
            return devices
            
        except Exception as e:
            logger.error(f"Who-Is failed: {e}")
            raise
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get basic device information
        
        Returns:
            Dictionary with device properties
        """
        try:
            if not self.bacnet:
                raise ConnectionError("Not connected to BACnet network")
            
            logger.info(f"Reading device information for {self.device_address}")
            
            device_request = f"{self.device_address} device {self.device_id}"
            
            info = {
                "device_id": self.device_id,
                "device_address": self.device_address,
            }
            
            # Try to read common properties
            try:
                info["name"] = self.bacnet.read(f"{device_request} objectName")
            except:
                info["name"] = "Unknown"
            
            try:
                info["vendor"] = self.bacnet.read(f"{device_request} vendorName")
            except:
                info["vendor"] = "Unknown"
            
            try:
                info["model"] = self.bacnet.read(f"{device_request} modelName")
            except:
                info["model"] = "Unknown"
            
            try:
                info["description"] = self.bacnet.read(f"{device_request} description")
            except:
                info["description"] = "Unknown"
            
            logger.info(f"Device info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {
                "device_id": self.device_id,
                "device_address": self.device_address,
                "name": "Unknown",
                "vendor": "Unknown",
                "model": "Unknown",
                "description": "Unknown"
            }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()