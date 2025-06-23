import time
import logging
from fx_iqoption import IQOption
from flask import current_app as app

logger = logging.getLogger(__name__)

class IQOptionAPI:
    """
    Wrapper for IQ Option API
    """
    def __init__(self):
        self.api = None
        self.connected = False
        self.balance_type = 'PRACTICE'  # or 'REAL'
        
    def connect(self, email=None, password=None):
        """
        Connect to IQ Option API
        """
        try:
            email = email or app.config['IQOPTION_EMAIL']
            password = password or app.config['IQOPTION_PASSWORD']
            
            if not email or not password:
                logger.error("IQ Option credentials not provided")
                return False
                
            self.api = IQOption(email, password)
            self.connected = self.api.connect()
            
            if self.connected:
                logger.info("Successfully connected to IQ Option")
                self.api.change_balance(self.balance_type)
                return True
            else:
                logger.error("Failed to connect to IQ Option")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to IQ Option: {str(e)}")
            return False
    
    def get_balance(self):
        """
        Get current balance
        """
        if not self.connected or not self.api:
            logger.error("Not connected to IQ Option")
            return None
            
        return self.api.get_balance()
    
    def get_candles(self, asset, timeframe, count, endtime=None):
        """
        Get candles for a specific asset
        """
        if not self.connected or not self.api:
            logger.error("Not connected to IQ Option")
            return None
            
        endtime = endtime or time.time()
        return self.api.get_candles(asset, timeframe, count, endtime)
    
    def place_binary_order(self, asset, amount, direction, expiration):
        """
        Place a binary option order
        """
        if not self.connected or not self.api:
            logger.error("Not connected to IQ Option")
            return None
            
        if direction.upper() not in ['CALL', 'PUT']:
            logger.error(f"Invalid direction: {direction}")
            return None
            
        try:
            result = self.api.buy(amount, asset, direction.lower(), expiration)
            return result
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def get_all_open_positions(self):
        """
        Get all open positions
        """
        if not self.connected or not self.api:
            logger.error("Not connected to IQ Option")
            return None
            
        return self.api.get_all_open_positions()
    
    def get_available_assets(self):
        """
        Get all available assets for binary options
        """
        if not self.connected or not self.api:
            logger.error("Not connected to IQ Option")
            return None
            
        return self.api.get_all_open_time()
    
    def set_balance_type(self, balance_type):
        """
        Set balance type (PRACTICE or REAL)
        """
        if balance_type not in ['PRACTICE', 'REAL']:
            logger.error(f"Invalid balance type: {balance_type}")
            return False
            
        self.balance_type = balance_type
        
        if self.connected and self.api:
            self.api.change_balance(balance_type)
            return True
            
        return False

# Create a singleton instance
iq_api = IQOptionAPI()