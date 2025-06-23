from flask import Blueprint, jsonify, request, current_app as app
from app.api.iqoption import iq_api
from app.services.analysis import analyze_asset
from app.services.bank_management import calculate_entry_amount
from app.services.trading import execute_trades

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/connect', methods=['POST'])
def connect():
    """
    Connect to IQ Option API
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    success = iq_api.connect(email, password)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Connected to IQ Option'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to connect to IQ Option'}), 400

@api_bp.route('/balance', methods=['GET'])
def get_balance():
    """
    Get current balance
    """
    balance = iq_api.get_balance()
    
    if balance is not None:
        return jsonify({'status': 'success', 'balance': balance})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to get balance'}), 400

@api_bp.route('/assets', methods=['GET'])
def get_assets():
    """
    Get available assets
    """
    assets = iq_api.get_available_assets()
    
    if assets is not None:
        return jsonify({'status': 'success', 'assets': assets})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to get assets'}), 400

@api_bp.route('/candles/<asset>', methods=['GET'])
def get_candles(asset):
    """
    Get candles for a specific asset
    """
    timeframe = int(request.args.get('timeframe', 60))  # Default to 1 minute
    count = int(request.args.get('count', 100))
    
    candles = iq_api.get_candles(asset, timeframe, count)
    
    if candles is not None:
        return jsonify({'status': 'success', 'candles': candles})
    else:
        return jsonify({'status': 'error', 'message': f'Failed to get candles for {asset}'}), 400

@api_bp.route('/analyze/<asset>', methods=['GET'])
def analyze(asset):
    """
    Analyze a specific asset
    """
    timeframe = int(request.args.get('timeframe', 60))  # Default to 1 minute
    
    analysis = analyze_asset(asset, timeframe)
    
    if analysis is not None:
        return jsonify({'status': 'success', 'analysis': analysis})
    else:
        return jsonify({'status': 'error', 'message': f'Failed to analyze {asset}'}), 400

@api_bp.route('/trade', methods=['POST'])
def trade():
    """
    Execute trades based on analysis
    """
    data = request.get_json()
    assets = data.get('assets', app.config['DEFAULT_ASSETS'])
    
    results = execute_trades(assets)
    
    return jsonify({'status': 'success', 'results': results})

@api_bp.route('/positions', methods=['GET'])
def get_positions():
    """
    Get all open positions
    """
    positions = iq_api.get_all_open_positions()
    
    if positions is not None:
        return jsonify({'status': 'success', 'positions': positions})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to get positions'}), 400

@api_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Get or update settings
    """
    if request.method == 'GET':
        settings = {
            'expiration_time': app.config['EXPIRATION_TIME'],
            'max_bank_percentage': app.config['MAX_BANK_PERCENTAGE'],
            'daily_stop_loss': app.config['DAILY_STOP_LOSS'],
            'daily_stop_gain': app.config['DAILY_STOP_GAIN'],
            'default_assets': app.config['DEFAULT_ASSETS'],
            'rsi_period': app.config['RSI_PERIOD'],
            'rsi_overbought': app.config['RSI_OVERBOUGHT'],
            'rsi_oversold': app.config['RSI_OVERSOLD'],
            'macd_fast': app.config['MACD_FAST'],
            'macd_slow': app.config['MACD_SLOW'],
            'macd_signal': app.config['MACD_SIGNAL'],
            'balance_type': iq_api.balance_type
        }
        return jsonify({'status': 'success', 'settings': settings})
    else:
        data = request.get_json()
        
        # Update balance type if provided
        balance_type = data.get('balance_type')
        if balance_type:
            iq_api.set_balance_type(balance_type)
        
        return jsonify({'status': 'success', 'message': 'Settings updated'})

@api_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'success', 'message': 'API is running'})