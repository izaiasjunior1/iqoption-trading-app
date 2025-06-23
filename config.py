import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # IQ Option credentials
    IQOPTION_EMAIL = os.environ.get('IQOPTION_EMAIL')
    IQOPTION_PASSWORD = os.environ.get('IQOPTION_PASSWORD')
    
    # Trading parameters
    EXPIRATION_TIME = 1  # 1 minute
    MAX_BANK_PERCENTAGE = 0.20  # 20% of bank per total lot
    DAILY_STOP_LOSS = 0.40  # 40% of bank
    DAILY_STOP_GAIN = 1.00  # 100% of bank (double)
    
    # Assets to trade (can be configured in the UI)
    DEFAULT_ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'EURJPY']
    
    # Technical indicators parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # Flask configuration
    DEBUG = os.environ.get('DEBUG') or True
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}