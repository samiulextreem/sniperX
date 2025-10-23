"""
Balance and position tracking for trading ledger
"""
import yaml
from pathlib import Path
from datetime import datetime

BALANCE_FILE = "balance.yaml"
TRADE_HISTORY_FILE = "trade_history.txt"

def load_balance():
    """Load balance and positions from YAML file"""
    if not Path(BALANCE_FILE).exists():
        return {"balance": 30.0, "positions": {}}
    
    with open(BALANCE_FILE, 'r') as f:
        data = yaml.safe_load(f)
        if data is None:
            return {"balance": 30.0, "positions": {}}
        return data

def save_balance(data):
    """Save balance and positions to YAML file"""
    with open(BALANCE_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def append_trade_history(trade_type, slug, shares, amount, price_per_share, balance_after, profit_loss=None):
    """Append trade to human-readable history file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(TRADE_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"{trade_type.upper()} - {timestamp}\n")
        f.write("=" * 70 + "\n")
        f.write(f"Token:          {slug}\n")
        f.write(f"Shares:         {shares:.2f}\n")
        f.write(f"Price/Share:    ${price_per_share:.3f}\n")
        
        if trade_type.lower() == "buy":
            f.write(f"Total Cost:     ${amount:.2f}\n")
        else:  # sell
            f.write(f"Total Proceeds: ${amount:.2f}\n")
            if profit_loss is not None:
                profit_emoji = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
                f.write(f"Profit/Loss:    {profit_emoji} ${profit_loss:+.2f}\n")
        
        f.write(f"Balance After:  ${balance_after:.2f}\n")
        f.write("=" * 70 + "\n\n")

def record_buy(slug, shares, total_cost):
    """Record a buy transaction"""
    data = load_balance()
    
    # Deduct from balance
    if data['balance'] < total_cost:
        print(f"WARNING: Insufficient balance (${data['balance']:.2f}) for purchase (${total_cost:.2f})")
        return False
    
    data['balance'] -= total_cost
    
    # Update position - ensure positions is a dict, not None
    if 'positions' not in data or data['positions'] is None:
        data['positions'] = {}
    
    if slug not in data['positions']:
        data['positions'][slug] = {
            'shares': 0.0,
            'avg_cost': 0.0,
            'total_invested': 0.0
        }
    
    position = data['positions'][slug]
    
    # Calculate new average cost
    old_shares = position['shares']
    old_invested = position['total_invested']
    new_shares = old_shares + shares
    new_invested = old_invested + total_cost
    
    position['shares'] = new_shares
    position['total_invested'] = new_invested
    position['avg_cost'] = new_invested / new_shares if new_shares > 0 else 0.0
    
    save_balance(data)
    
    # Append to trade history
    price_per_share = total_cost / shares if shares > 0 else 0.0
    append_trade_history("BUY", slug, shares, total_cost, price_per_share, data['balance'])
    
    return True

def record_sell(slug, shares, total_proceeds):
    """Record a sell transaction"""
    data = load_balance()
    
    if 'positions' not in data or data['positions'] is None:
        data['positions'] = {}
    
    if slug not in data['positions']:
        print(f"WARNING: No position found for {slug}")
        return False
    
    position = data['positions'][slug]
    
    if position['shares'] < shares:
        print(f"WARNING: Insufficient shares ({position['shares']:.2f}) to sell {shares:.2f}")
        return False
    
    # Calculate profit/loss before updating
    old_shares = position['shares']
    old_invested = position['total_invested']
    invested_in_sold = (shares / old_shares) * old_invested if old_shares > 0 else 0
    profit_loss = total_proceeds - invested_in_sold
    
    # Add proceeds to balance
    data['balance'] += total_proceeds
    
    # Update position
    position['shares'] -= shares
    position['total_invested'] -= invested_in_sold
    position['avg_cost'] = position['total_invested'] / position['shares'] if position['shares'] > 0 else 0.0
    
    save_balance(data)
    
    # Append to trade history
    price_per_share = total_proceeds / shares if shares > 0 else 0.0
    append_trade_history("SELL", slug, shares, total_proceeds, price_per_share, data['balance'], profit_loss)
    
    return True

def get_position(slug):
    """Get position info for a slug"""
    data = load_balance()
    if 'positions' not in data or data['positions'] is None:
        return None
    return data['positions'].get(slug)

def get_balance():
    """Get current balance"""
    data = load_balance()
    return data.get('balance', 0.0)

