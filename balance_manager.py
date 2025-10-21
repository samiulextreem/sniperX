"""
Balance and position tracking for trading ledger
"""
import yaml
from pathlib import Path

BALANCE_FILE = "balance.yaml"

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
    
    # Add proceeds to balance
    data['balance'] += total_proceeds
    
    # Update position
    old_shares = position['shares']
    old_invested = position['total_invested']
    
    # Proportionally reduce invested amount
    invested_in_sold = (shares / old_shares) * old_invested if old_shares > 0 else 0
    
    position['shares'] -= shares
    position['total_invested'] -= invested_in_sold
    position['avg_cost'] = position['total_invested'] / position['shares'] if position['shares'] > 0 else 0.0
    
    save_balance(data)
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

