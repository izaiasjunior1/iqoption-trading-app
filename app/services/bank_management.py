import logging
from datetime import datetime, date
from flask import current_app as app
from app.api.iqoption import iq_api

logger = logging.getLogger(__name__)

# Store daily trading statistics
daily_stats = {
    'date': date.today(),
    'initial_balance': 0,
    'current_balance': 0,
    'profit_loss': 0,
    'trades': [],
    'assets': {}
}

def initialize_daily_stats():
    """
    Initialize daily trading statistics
    """
    global daily_stats
    
    today = date.today()
    
    # Reset stats if it's a new day
    if daily_stats['date'] != today:
        balance = iq_api.get_balance()
        
        if balance is not None:
            daily_stats = {
                'date': today,
                'initial_balance': balance,
                'current_balance': balance,
                'profit_loss': 0,
                'trades': [],
                'assets': {}
            }
            logger.info(f"Initialized daily stats with balance: {balance}")
        else:
            logger.error("Failed to get balance for daily stats initialization")
    
    return daily_stats

def update_balance():
    """
    Update current balance in daily stats
    """
    global daily_stats
    
    balance = iq_api.get_balance()
    
    if balance is not None:
        daily_stats['current_balance'] = balance
        daily_stats['profit_loss'] = balance - daily_stats['initial_balance']
        
        logger.info(f"Updated balance: {balance}, P/L: {daily_stats['profit_loss']}")
    else:
        logger.error("Failed to update balance")
    
    return daily_stats

def check_stop_conditions():
    """
    Check if stop loss or stop gain conditions are met
    """
    global daily_stats
    
    # Initialize if needed
    if daily_stats['initial_balance'] == 0:
        initialize_daily_stats()
    
    # Update balance
    update_balance()
    
    # Calculate profit/loss percentage
    if daily_stats['initial_balance'] > 0:
        pl_percentage = (daily_stats['profit_loss'] / daily_stats['initial_balance']) * 100
    else:
        pl_percentage = 0
    
    # Check stop conditions
    stop_loss_pct = app.config['DAILY_STOP_LOSS'] * 100
    stop_gain_pct = app.config['DAILY_STOP_GAIN'] * 100
    
    if pl_percentage <= -stop_loss_pct:
        logger.warning(f"STOP LOSS triggered: {pl_percentage:.2f}% loss")
        return {
            'stop_triggered': True,
            'reason': 'STOP_LOSS',
            'percentage': pl_percentage
        }
    elif pl_percentage >= stop_gain_pct:
        logger.info(f"STOP GAIN triggered: {pl_percentage:.2f}% gain")
        return {
            'stop_triggered': True,
            'reason': 'STOP_GAIN',
            'percentage': pl_percentage
        }
    else:
        return {
            'stop_triggered': False,
            'percentage': pl_percentage
        }

def calculate_entry_amount(assets):
    """
    Calculate entry amount for each asset based on bank management rules
    
    Args:
        assets (list): List of assets to trade
        
    Returns:
        dict: Dictionary with entry amounts for each asset
    """
    # Initialize if needed
    if daily_stats['initial_balance'] == 0:
        initialize_daily_stats()
    
    # Update balance
    update_balance()
    
    # Calculate total amount to risk
    max_bank_percentage = app.config['MAX_BANK_PERCENTAGE']
    total_risk_amount = daily_stats['current_balance'] * max_bank_percentage
    
    # Divide among assets
    num_assets = len(assets)
    if num_assets == 0:
        return {}
    
    per_asset_amount = total_risk_amount / num_assets
    
    # Round to appropriate value (minimum trade amount is usually $1)
    per_asset_amount = max(1, round(per_asset_amount, 2))
    
    # Create result dictionary
    result = {asset: per_asset_amount for asset in assets}
    
    logger.info(f"Calculated entry amounts: {result}")
    return result

def record_trade(asset, amount, direction, result=None, profit_loss=None):
    """
    Record a trade in daily statistics
    
    Args:
        asset (str): Asset traded
        amount (float): Trade amount
        direction (str): 'CALL' or 'PUT'
        result (str, optional): 'WIN', 'LOSS', or None if pending
        profit_loss (float, optional): Profit or loss amount
    """
    global daily_stats
    
    # Initialize asset stats if not exists
    if asset not in daily_stats['assets']:
        daily_stats['assets'][asset] = {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'profit_loss': 0
        }
    
    # Create trade record
    trade = {
        'timestamp': datetime.now().isoformat(),
        'asset': asset,
        'amount': amount,
        'direction': direction,
        'result': result,
        'profit_loss': profit_loss
    }
    
    # Add to trades list
    daily_stats['trades'].append(trade)
    
    # Update asset stats if result is known
    if result:
        daily_stats['assets'][asset]['trades'] += 1
        
        if result == 'WIN':
            daily_stats['assets'][asset]['wins'] += 1
        elif result == 'LOSS':
            daily_stats['assets'][asset]['losses'] += 1
            
        if profit_loss:
            daily_stats['assets'][asset]['profit_loss'] += profit_loss
    
    logger.info(f"Recorded trade: {trade}")
    return trade

def get_daily_stats():
    """
    Get current daily statistics
    """
    # Initialize if needed
    if daily_stats['initial_balance'] == 0:
        initialize_daily_stats()
    else:
        update_balance()
    
    return daily_stats