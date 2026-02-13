"""
Pytest configuration and shared fixtures for BACnet E2E tests
"""
import os
import logging
import pytest
from dotenv import load_dotenv
# from src.bacnet_client import BACnetClient
from src.eventloop_bacnet_client import EventLoopBACnetClient as BACnetClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(scope="session")
def bacnet_config():
    """
    Load BACnet configuration from environment variables
    
    Returns:
        Dictionary with configuration values
    """
    config = {
        "device_ip": os.getenv("BACNET_DEVICE_IP"),
        "device_id": int(os.getenv("BACNET_DEVICE_ID", "0")),
        "device_port": int(os.getenv("BACNET_DEVICE_PORT", "47808")),
        "local_ip": os.getenv("BACNET_LOCAL_IP"),
        "bbmd_address": os.getenv("BACNET_BBMD_ADDRESS", ""),
        "bbmd_ttl": int(os.getenv("BACNET_BBMD_TTL", "900")),
        "analog_value_instance": int(os.getenv("ANALOG_VALUE_INSTANCE", "1")),
        "test_write_value": float(os.getenv("ANALOG_VALUE_TEST_WRITE_VALUE", "75.5")),
        "expected_units": os.getenv("ANALOG_VALUE_EXPECTED_UNITS", ""),
        "test_timeout": int(os.getenv("TEST_TIMEOUT", "30")),
        "retry_count": int(os.getenv("TEST_RETRY_COUNT", "3")),
        "retry_delay": int(os.getenv("TEST_RETRY_DELAY", "2")),
    }
    
    # Validate required configuration
    required_fields = ["device_ip", "device_id", "local_ip"]
    missing_fields = [field for field in required_fields if not config[field]]
    
    if missing_fields:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing_fields)}. "
            "Please check your .env file."
        )
    
    return config


@pytest.fixture(scope="session")
def bacnet_client(bacnet_config):
    """
    Create and connect a BACnet client for testing
    
    Yields:
        Connected BACnetClient instance
    """
    client = BACnetClient(
        local_ip=bacnet_config["local_ip"],
        device_ip=bacnet_config["device_ip"],
        device_id=bacnet_config["device_id"],
        bbmd_address=bacnet_config["bbmd_address"] if bacnet_config["bbmd_address"] else None,
        bbmd_ttl=bacnet_config["bbmd_ttl"]
    )
    
    # Connect to BACnet network
    client.connect()
    
    yield client
    
    # Cleanup: disconnect after test
    client.disconnect()


@pytest.fixture(scope="function")
def original_analog_value(bacnet_client, bacnet_config):
    """
    Read and store the original value of AnalogValue before test
    
    This fixture ensures we can restore the original value after testing
    
    Returns:
        Original present value
    """
    instance = bacnet_config["analog_value_instance"]
    original_value = bacnet_client.read_analog_value(instance)
    logging.info(f"Stored original AnalogValue:{instance} = {original_value}")
    
    yield original_value
    
    # Cleanup: restore original value after test
    try:
        bacnet_client.write_analog_value(instance, original_value)
        logging.info(f"Restored AnalogValue:{instance} to {original_value}")
    except Exception as e:
        logging.error(f"Failed to restore original value: {e}")


def pytest_configure(config):
    """Add custom markers"""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )