# IQ Option Trading App

A binary options trading application for IQ Option with multiple assets, technical analysis, and mobile web interface.

## Features

- **Platform**: IQ Option
- **Operation Type**: Multiple simultaneous assets
- **Expiration**: 1 Minute
- **Bank Management**:
  - Maximum 20% of bank per total lot
  - Automatic entry division by asset
  - Daily Stop Loss: 40% of bank
  - Daily Stop Gain: 100% (double the bank)
- **Entry Conditions**:
  - Price Action
  - News
  - Fundamental Analysis
  - Volume
  - RSI+MACD
  - M1 Signals
  - Candle Patterns
- **Interface**: Mobile browser access (Safari, Chrome)
- **Backend**: Python + Flask

## Project Structure

```
iqoption-trading-app/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── iqoption.py
│   │   └── routes.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── trading.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis.py
│   │   ├── bank_management.py
│   │   └── trading.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/
│       ├── index.html
│       ├── dashboard.html
│       └── settings.html
├── config.py
├── requirements.txt
└── run.py
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/izaiasjunior1/iqoption-trading-app.git
cd iqoption-trading-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your IQ Option credentials in config.py

5. Run the application:
```bash
python run.py
```

## Technical Indicators

The application uses several technical indicators for analysis:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Volume Analysis
- Candlestick Patterns

## Bank Management

The system automatically manages your bank according to the following rules:
- Maximum exposure: 20% of total bank per lot
- Daily Stop Loss: 40% of bank
- Daily Stop Gain: 100% (double the bank)
- Automatic entry division by asset

## Mobile Interface

The web interface is optimized for mobile browsers (Safari, Chrome) and provides:
- Real-time trading dashboard
- Asset selection
- Technical analysis charts
- Entry/exit management
- Bank statistics