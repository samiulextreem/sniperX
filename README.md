# SniperX - Polymarket Orderbook Sniper

A Python tool to fetch Polymarket orderbook data on ping and track trading positions.

## Features

- Ping-triggered orderbook snapshots
- Automatic trade plan calculation based on available balance
- Position tracking with YAML ledger
- Human-readable snapshot format with best bids/asks

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure settings in `config.json`:
   - `tokens`: Array of token IDs and slugs to track
   - `investment`: Amount to invest per trade (e.g., 30)
   - `min_value`: Minimum order value filter (e.g., 20.0)
   - `sell_timeout`: Seconds to wait before auto-selling (default: 100)

3. Set initial balance in `balance.yaml` (default: $30)

4. Run the collector:
```bash
python main.py
```

## How It Works

1. Flask server runs on port 5000 waiting for pings
2. Send a ping from your Android app to trigger orderbook fetch
3. Script calculates trade plan based on available balance
4. Records buy transaction in `balance.yaml` ledger
5. Saves snapshot to `snapshots/` folder

## Ping the Server

From browser or app:
```
https://your-ngrok-url/ping?text=fetch
```

## Files

- `main.py` - Main script with ping-triggered orderbook collection
- `polymarket_client.py` - Orderbook fetch and snapshot functions
- `balance_manager.py` - Trading ledger (tracks balance and positions)
- `ping_server.py` - Flask server for receiving pings
- `config.py` - Configuration loader
- `config.json` - Token IDs, slugs, investment amount
- `balance.yaml` - Trading ledger (balance and positions)

## Output

- Snapshots: `snapshots/orderbook_{slug}_{timestamp}.txt`
- Ledger: `balance.yaml` (updated after each buy/sell)