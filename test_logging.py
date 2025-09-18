#!/usr/bin/env python3
"""
Test script to verify comprehensive HTTP request logging
"""

import network_handler
import logger

def test_logging():
    """Test the log_response function with a simple HTTP request"""
    try:
        # Test with a simple GET request
        import requests
        response = requests.get('https://httpbin.org/json')
        
        # Test our logging function
        network_handler.log_response(response, "Test JSON Request")
        
        logger.info("Logging test completed successfully!")
        logger.info("Check the latest log file in the logs/ directory to see the comprehensive request details")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_logging()