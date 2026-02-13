#!/usr/bin/env python3
"""
Minimal test script to verify BAC0 event loop fix
Run this to test if the event loop issue is resolved
"""

import sys
import logging
from dotenv import load_dotenv
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

def test_eventloop_client():
    """Test the EventLoopBACnetClient"""
    logger.info("=" * 60)
    logger.info("Testing EventLoopBACnetClient")
    logger.info("=" * 60)
    
    try:
        from src.eventloop_bacnet_client import EventLoopBACnetClient
        
        # Get config from .env
        local_ip = os.getenv("BACNET_LOCAL_IP")
        device_ip = os.getenv("BACNET_DEVICE_IP")
        device_id = int(os.getenv("BACNET_DEVICE_ID", "0"))
        instance = int(os.getenv("ANALOG_VALUE_INSTANCE", "1"))
        
        if not all([local_ip, device_ip, device_id]):
            logger.error("Missing configuration in .env file")
            logger.error("Required: BACNET_LOCAL_IP, BACNET_DEVICE_IP, BACNET_DEVICE_ID")
            return False
        
        logger.info(f"Configuration:")
        logger.info(f"  Local IP: {local_ip}")
        logger.info(f"  Device IP: {device_ip}")
        logger.info(f"  Device ID: {device_id}")
        logger.info(f"  AnalogValue Instance: {instance}")
        logger.info("")
        
        # Create client
        logger.info("Step 1: Creating BACnet client...")
        client = EventLoopBACnetClient(
            local_ip=local_ip,
            device_ip=device_ip,
            device_id=device_id
        )
        logger.info("✓ Client created successfully")
        logger.info("")
        
        # Connect
        logger.info("Step 2: Connecting to BACnet network...")
        client.connect()
        logger.info("✓ Connected successfully")
        logger.info("")
        
        # Read value
        logger.info(f"Step 3: Reading AnalogValue:{instance}...")
        value = client.read_analog_value(instance)
        logger.info(f"✓ Read successful: {value}")
        logger.info("")
        
        # Get device info
        logger.info("Step 4: Reading device information...")
        info = client.get_device_info()
        logger.info(f"✓ Device Name: {info['name']}")
        logger.info(f"  Device ID: {info['device_id']}")
        logger.info(f"  Vendor: {info['vendor']}")
        logger.info(f"  Model: {info['model']}")
        logger.info("")
        
        # Disconnect
        logger.info("Step 5: Disconnecting...")
        client.disconnect()
        logger.info("✓ Disconnected successfully")
        logger.info("")
        
        logger.info("=" * 60)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"✗ TEST FAILED: {e}")
        logger.error("=" * 60)
        import traceback
        traceback.print_exc()
        return False


def test_simple_client():
    """Test the SimpleBACnetClient (may fail with event loop error)"""
    logger.info("=" * 60)
    logger.info("Testing SimpleBACnetClient (for comparison)")
    logger.info("=" * 60)
    
    try:
        from src.simple_bacnet_client import SimpleBACnetClient
        
        # Get config from .env
        local_ip = os.getenv("BACNET_LOCAL_IP")
        device_ip = os.getenv("BACNET_DEVICE_IP")
        device_id = int(os.getenv("BACNET_DEVICE_ID", "0"))
        instance = int(os.getenv("ANALOG_VALUE_INSTANCE", "1"))
        
        logger.info("Creating and connecting SimpleBACnetClient...")
        client = SimpleBACnetClient(
            local_ip=local_ip,
            device_ip=device_ip,
            device_id=device_id
        )
        
        client.connect()
        logger.info("✓ SimpleBACnetClient works!")
        
        client.disconnect()
        return True
        
    except RuntimeError as e:
        if "event loop" in str(e).lower():
            logger.warning("✗ SimpleBACnetClient has event loop issue (expected)")
            logger.warning("  Use EventLoopBACnetClient instead")
        else:
            logger.error(f"✗ SimpleBACnetClient error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ SimpleBACnetClient error: {e}")
        return False


if __name__ == "__main__":
    logger.info("")
    logger.info("BACnet Event Loop Test")
    logger.info("")
    
    # Test EventLoopBACnetClient (should work)
    result1 = test_eventloop_client()
    
    logger.info("")
    logger.info("-" * 60)
    logger.info("")
    
    # Test SimpleBACnetClient (may fail)
    result2 = test_simple_client()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY:")
    logger.info(f"  EventLoopBACnetClient: {'PASS ✓' if result1 else 'FAIL ✗'}")
    logger.info(f"  SimpleBACnetClient: {'PASS ✓' if result2 else 'FAIL ✗'}")
    logger.info("=" * 60)
    logger.info("")
    
    if result1:
        logger.info("✓ Event loop issue is RESOLVED!")
        logger.info("  Use EventLoopBACnetClient for all tests")
        sys.exit(0)
    else:
        logger.error("✗ Event loop issue persists")
        logger.error("  Check TROUBLESHOOTING.md for more solutions")
        sys.exit(1)