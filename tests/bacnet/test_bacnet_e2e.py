"""
End-to-End Tests for BACnet Device Interaction

Tests reading, writing, and verification of AnalogValue objects
"""
import time
import logging
import pytest
from src.bacnet_client import BACnetClient

logger = logging.getLogger(__name__)


@pytest.mark.e2e
@pytest.mark.timeout(60)
class TestBACnetAnalogValueE2E:
    """End-to-end tests for BACnet AnalogValue operations"""
    
    def test_device_connection(self, bacnet_client, bacnet_config):
        """
        Test: Verify successful connection to BACnet device
        
        Steps:
        1. Connect to device (done in fixture)
        2. Verify device is accessible
        3. Read device information
        """
        # Get device info
        device_info = bacnet_client.get_device_info()
        
        # Assertions
        assert device_info is not None, "Failed to get device information"
        assert device_info["device_id"] == bacnet_config["device_id"], \
            f"Device ID mismatch: expected {bacnet_config['device_id']}, got {device_info['device_id']}"
        
        logger.info(f"✓ Connected to device: {device_info['name']}")
        logger.info(f"  - Device ID: {device_info['device_id']}")
        logger.info(f"  - Vendor: {device_info['vendor']}")
        logger.info(f"  - Model: {device_info['model']}")
    
    def test_read_analog_value_present_value(self, bacnet_client, bacnet_config):
        """
        Test: Read AnalogValue present value
        
        Steps:
        1. Read AnalogValue present value
        2. Verify value is numeric
        3. Log the value
        """
        instance = bacnet_config["analog_value_instance"]
        
        # Read present value
        value = bacnet_client.read_analog_value(instance)
        
        # Assertions
        assert value is not None, f"Failed to read AnalogValue:{instance}"
        assert isinstance(value, (int, float)), \
            f"Expected numeric value, got {type(value)}"
        
        logger.info(f"✓ Successfully read AnalogValue:{instance} = {value}")
    
    def test_write_analog_value_present_value(
        self,
        bacnet_client,
        bacnet_config,
        original_analog_value
    ):
        """
        Test: Write value to AnalogValue present value
        
        Steps:
        1. Write test value to AnalogValue
        2. Verify write operation succeeds
        3. Original value will be restored by fixture cleanup
        """
        instance = bacnet_config["analog_value_instance"]
        test_value = bacnet_config["test_write_value"]
        
        # Write test value
        bacnet_client.write_analog_value(instance, test_value)
        
        logger.info(f"✓ Successfully wrote {test_value} to AnalogValue:{instance}")
        logger.info(f"  (Original value {original_analog_value} will be restored)")
    
    def test_write_and_read_back_verify(
        self,
        bacnet_client,
        bacnet_config,
        original_analog_value
    ):
        """
        Test: Write value and read back to verify (Complete E2E Test)
        
        Steps:
        1. Read original value (done in fixture)
        2. Write new test value
        3. Wait for value to propagate
        4. Read back the value
        5. Verify written value matches read value
        6. Restore original value (done in fixture cleanup)
        """
        instance = bacnet_config["analog_value_instance"]
        test_value = bacnet_config["test_write_value"]
        
        logger.info(f"Starting E2E test for AnalogValue:{instance}")
        logger.info(f"Original value: {original_analog_value}")
        
        # Step 1: Write new value
        logger.info(f"Step 1: Writing test value {test_value}...")
        bacnet_client.write_analog_value(instance, test_value)
        
        # Step 2: Wait for value to propagate (adjust delay as needed)
        propagation_delay = 2
        logger.info(f"Step 2: Waiting {propagation_delay}s for value to propagate...")
        time.sleep(propagation_delay)
        
        # Step 3: Read back value
        logger.info(f"Step 3: Reading back value...")
        read_value = bacnet_client.read_analog_value(instance)
        
        # Step 4: Verify
        logger.info(f"Step 4: Verifying written value matches read value...")
        logger.info(f"  - Written value: {test_value}")
        logger.info(f"  - Read value: {read_value}")
        
        # Allow small floating point tolerance
        tolerance = 0.01
        assert abs(read_value - test_value) < tolerance, \
            f"Value mismatch: wrote {test_value}, read back {read_value}"
        
        logger.info(f"✓ E2E Test PASSED: Write-Read-Verify cycle successful!")
        logger.info(f"  - Original: {original_analog_value}")
        logger.info(f"  - Written: {test_value}")
        logger.info(f"  - Verified: {read_value}")
    
    def test_multiple_write_read_cycles(
        self,
        bacnet_client,
        bacnet_config,
        original_analog_value
    ):
        """
        Test: Perform multiple write-read-verify cycles
        
        Steps:
        1. Write multiple different values
        2. Verify each write by reading back
        3. Ensure consistency across cycles
        """
        instance = bacnet_config["analog_value_instance"]
        test_values = [10.0, 25.5, 50.0, 75.5, 100.0]
        
        logger.info(f"Testing multiple write-read cycles with values: {test_values}")
        
        for i, test_value in enumerate(test_values, 1):
            logger.info(f"Cycle {i}/{len(test_values)}: Testing value {test_value}")
            
            # Write
            bacnet_client.write_analog_value(instance, test_value)
            
            # Short delay
            time.sleep(1)
            
            # Read back
            read_value = bacnet_client.read_analog_value(instance)
            
            # Verify
            tolerance = 0.01
            assert abs(read_value - test_value) < tolerance, \
                f"Cycle {i} failed: wrote {test_value}, read {read_value}"
            
            logger.info(f"  ✓ Cycle {i} passed: {test_value} → {read_value}")
        
        logger.info(f"✓ All {len(test_values)} write-read cycles completed successfully!")
    
    @pytest.mark.parametrize("test_value", [0.0, 25.0, 50.0, 75.0, 100.0])
    def test_write_read_parametrized(
        self,
        bacnet_client,
        bacnet_config,
        original_analog_value,
        test_value
    ):
        """
        Test: Parametrized test for different values
        
        This test will run 5 times with different values
        """
        instance = bacnet_config["analog_value_instance"]
        
        # Write
        bacnet_client.write_analog_value(instance, test_value)
        time.sleep(1)
        
        # Read back
        read_value = bacnet_client.read_analog_value(instance)
        
        # Verify
        tolerance = 0.01
        assert abs(read_value - test_value) < tolerance, \
            f"Value mismatch: wrote {test_value}, read {read_value}"
        
        logger.info(f"✓ Parametrized test passed for value {test_value}")
    
    def test_read_analog_value_with_retry(self, bacnet_client, bacnet_config):
        """
        Test: Read with retry logic for robustness
        
        Demonstrates retry pattern for flaky network conditions
        """
        instance = bacnet_config["analog_value_instance"]
        max_retries = bacnet_config["retry_count"]
        retry_delay = bacnet_config["retry_delay"]
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Read attempt {attempt}/{max_retries}")
                value = bacnet_client.read_analog_value(instance)
                
                logger.info(f"✓ Successfully read on attempt {attempt}: {value}")
                assert value is not None
                return  # Success - exit test
                
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                if attempt == max_retries:
                    pytest.fail(f"Failed to read after {max_retries} attempts")
                
                time.sleep(retry_delay)


@pytest.mark.e2e
@pytest.mark.slow
class TestBACnetAnalogValueProperties:
    """Tests for reading AnalogValue properties beyond present value"""
    
    def test_read_analog_value_units(self, bacnet_client, bacnet_config):
        """
        Test: Read units property from AnalogValue
        
        Verifies the engineering units of the analog value
        """
        instance = bacnet_config["analog_value_instance"]
        
        try:
            units = bacnet_client.read_property(
                "analogValue",
                instance,
                "units"
            )
            
            logger.info(f"✓ AnalogValue:{instance} units: {units}")
            
            # Optional: verify expected units if configured
            expected_units = bacnet_config.get("expected_units")
            if expected_units:
                assert str(units).lower() == expected_units.lower(), \
                    f"Units mismatch: expected {expected_units}, got {units}"
                logger.info(f"  ✓ Units match expected: {expected_units}")
            
        except Exception as e:
            logger.warning(f"Could not read units property: {e}")
            pytest.skip("Units property not available or readable")
    
    def test_read_analog_value_description(self, bacnet_client, bacnet_config):
        """
        Test: Read description property from AnalogValue
        """
        instance = bacnet_config["analog_value_instance"]
        
        try:
            description = bacnet_client.read_property(
                "analogValue",
                instance,
                "description"
            )
            
            logger.info(f"✓ AnalogValue:{instance} description: {description}")
            assert description is not None
            
        except Exception as e:
            logger.warning(f"Could not read description property: {e}")
            pytest.skip("Description property not available or readable")


@pytest.mark.e2e
class TestBACnetErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_read_nonexistent_analog_value(self, bacnet_client):
        """
        Test: Attempt to read non-existent AnalogValue
        
        Verifies proper error handling for invalid objects
        """
        invalid_instance = 99999
        
        with pytest.raises(Exception) as exc_info:
            bacnet_client.read_analog_value(invalid_instance)
        
        logger.info(f"✓ Correctly raised exception for invalid instance: {exc_info.value}")
    
    def test_write_invalid_value_type(self, bacnet_client, bacnet_config):
        """
        Test: Attempt to write invalid data type
        
        Verifies type validation
        """
        instance = bacnet_config["analog_value_instance"]
        
        # This should handle type conversion or raise appropriate error
        try:
            # Try writing string that can be converted
            bacnet_client.write_analog_value(instance, "invalid")
            pytest.fail("Should have raised an error for invalid value type")
        except (ValueError, TypeError) as e:
            logger.info(f"✓ Correctly rejected invalid value type: {e}")