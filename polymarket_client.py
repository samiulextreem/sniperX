import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


def fetch_orderbook(token_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch orderbook data from Polymarket API for a given token ID
    
    Args:
        token_id (str): The token ID to fetch orderbook for
        
    Returns:
        Dict containing orderbook data or None if request fails
    """
    url = "https://clob.polymarket.com/book"
    params = {'token_id': token_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None


def save_orderbook_snapshot(orderbook_data: Dict[str, Any], token_id: str, min_value: float = 20.0, slug: Optional[str] = None, investment: float = 0.0, trade_type: str = "BUY") -> tuple[str, Optional[Dict[str, float]]]:
    """
    Save orderbook data to a readable text file with timestamp, filtering out orders with value < min_value
    The file will be saved under: snapshots/<slug_or_idprefix>/<timestamp>/
    
    Args:
        orderbook_data (Dict): The orderbook data to save
        token_id (str): The token ID for filename
        min_value (float): Minimum value threshold (price * size)
        slug (str, optional): Human-friendly name used for folder and filename
        trade_type (str): "BUY" or "SELL" to label the snapshot
        
    Returns:
        str: The filename where the snapshot was saved
    """
    # Simple directory structure: just snapshots/
    base_dir = 'snapshots'
    os.makedirs(base_dir, exist_ok=True)
    
    # Human-readable timestamp format: oct19_12_45_21 (month-day_hour_minutes_seconds)
    now = datetime.now()
    month_abbr = now.strftime("%b").lower()  # oct, nov, dec, etc.
    day = now.strftime("%d")  # 19, 20, etc.
    hour = now.strftime("%H")  # 12, 22, etc.
    minute = now.strftime("%M")  # 45, 42, etc.
    second = now.strftime("%S")  # 21, 34, etc.
    
    timestamp_str = f"{month_abbr}{day}_{hour}_{minute}_{second}"
    slug_or_prefix = (slug or (token_id[:10]))
    trade_label = trade_type.upper()
    
    filename = os.path.join(
        base_dir,
        f"{trade_label}_{slug_or_prefix}_{timestamp_str}.txt"
    )
    
    # Filter bids and asks based on minimum value
    filtered_bids = []
    filtered_asks = []
    
    # Filter bids (include all, no filtering)
    if 'bids' in orderbook_data:
        for bid in orderbook_data['bids']:
            price = float(bid['price'])
            size = float(bid['size'])
            value = price * size
            filtered_bids.append({
                'price': price,
                'size': size,
                'total_value': round(value, 2)
            })
    
    # Filter asks (include all, NO FILTERING)
    if 'asks' in orderbook_data:
        for ask in orderbook_data['asks']:
            try:
                price = float(ask.get('price', 0))
                size = float(ask.get('size', 0))
                if price > 0 and size > 0:
                    value = price * size
                    filtered_asks.append({
                        'price': price,
                        'size': size,
                        'total_value': round(value, 2)
                    })
            except (ValueError, TypeError, AttributeError):
                continue
    
    print(f"DEBUG: Total bids: {len(filtered_bids)}, Total asks: {len(filtered_asks)}")
    if filtered_asks:
        ask_prices = [a['price'] for a in filtered_asks]
        print(f"DEBUG: Ask prices range: {min(ask_prices):.3f} to {max(ask_prices):.3f}")
    
    # Sort: bids high->low (best bids are highest), asks low->high (best asks are lowest)
    filtered_bids.sort(key=lambda x: x['price'], reverse=True)
    filtered_asks.sort(key=lambda x: x['price'])  # LOW to HIGH for asks

    # Prepare simple table formatting
    def format_table(rows, title):
        if not rows:
            return f"No {title.lower()} found"
        
        lines = []
        for row in rows:
            price_str = f"{row['price']:.3f}".ljust(10)
            size_str = f"{row['size']:.2f}".ljust(10)
            value_str = f"{row['total_value']:.2f}".ljust(10)
            lines.append(f"{price_str} | {size_str} | {value_str}              |     {title}")
        
        return "\n".join(lines)

    # Top 5: best bids (highest prices) and best asks (lowest prices)
    top_bids = filtered_bids[:5]
    top_asks = filtered_asks[:5]

    # Compute realistic trade plan by filling orders across the orderbook
    trade_line = ""
    trade_info = None
    
    if trade_type == "SELL":
        # For SELL snapshots, show best bid prices available
        if filtered_bids:
            trade_line = f"Market snapshot for SELL - Best bid: ${filtered_bids[0]['price']:.3f}"
        else:
            trade_line = "Market snapshot for SELL - No bids available"
    elif filtered_asks and investment > 0:
        # BUY: Sort asks by price (low to high) to fill from best prices first
        sorted_asks = sorted(filtered_asks, key=lambda x: x['price'])
        
        remaining_investment = investment
        total_shares = 0.0
        total_spent = 0.0
        fills = []
        
        # Fill orders from lowest ask price upward until investment is exhausted
        for ask in sorted_asks:
            if remaining_investment <= 0:
                break
            
            price = float(ask['price'])
            available_size = float(ask['size'])
            
            # How many shares can we buy at this price level?
            max_shares_at_price = remaining_investment / price
            shares_to_buy = min(available_size, max_shares_at_price)
            cost = shares_to_buy * price
            
            if shares_to_buy > 0:
                fills.append({'price': price, 'shares': shares_to_buy, 'cost': cost})
                total_shares += shares_to_buy
                total_spent += cost
                remaining_investment -= cost
        
        if fills:
            # Format trade plan showing each individual fill
            if len(fills) == 1:
                # Single price level
                fill_detail = f"{fills[0]['shares']:.2f} @ ${fills[0]['price']:.3f} = ${fills[0]['cost']:.2f}"
                trade_line = f"Trade plan: {fill_detail}"
            else:
                # Multiple price levels - show each one
                fill_lines = []
                for f in fills:
                    fill_lines.append(f"{f['shares']:.2f} @ ${f['price']:.3f} = ${f['cost']:.2f}")
                trade_line = "Trade plan:\n  " + "\n  ".join(fill_lines) + f"\n  Total: {total_shares:.2f} shares for ${total_spent:.2f}"
            
            trade_info = {
                'shares': total_shares,
                'spend': total_spent,
                'fills': fills
            }
            
            print(f"DEBUG: Filled {len(fills)} price levels for total ${total_spent:.2f}")
        else:
            trade_line = "Trade plan: no valid fills available"
    else:
        trade_line = "Trade plan: no asks available or no investment"

    # Write readable text file
    with open(filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write(f"POLYMARKET ORDERBOOK SNAPSHOT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Token ID: {token_id}\n")
        if slug:
            f.write(f"Slug: {slug}\n")
        # Put spread at the top
        if filtered_bids and filtered_asks:
            top_bid_price = filtered_bids[0]['price']
            top_ask_price = filtered_asks[0]['price']
            spread_top = top_ask_price - top_bid_price
            f.write(f"Spread: ${spread_top:.4f}\n")
        f.write(trade_line + "\n")
        f.write("=" * 60 + "\n\n")
        
        # Write asks section (display high->low, so reverse the list)
        display_asks = list(reversed(top_asks))
        f.write(format_table(display_asks, "ASKS") + "\n")
        
        # Add spread line between asks and bids
        if top_asks and top_bids:
            best_ask_price = top_asks[0]['price']  # lowest ask (first in sorted list)
            best_bid_price = top_bids[0]['price']  # highest bid (first in sorted list)
            spread = best_ask_price - best_bid_price
            f.write("---------------------------------------------     spread {:.4f}\n".format(spread))
        else:
            f.write("---------------------------------------------\n")
        
        # Write bids section (already sorted high->low)
        f.write(format_table(top_bids, "BIDS") + "\n\n")
        
        # Write summary
        f.write("SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Bids (>= ${min_value}): {len(filtered_bids)}\n")
        f.write(f"Total Asks (>= ${min_value}): {len(filtered_asks)}\n")
        
        if top_bids and top_asks:
            best_bid_price = top_bids[0]['price']
            best_ask_price = top_asks[0]['price']
            spread = best_ask_price - best_bid_price
            f.write(f"Best Bid: ${best_bid_price:.3f}\n")
            f.write(f"Best Ask: ${best_ask_price:.3f}\n")
            f.write(f"Spread: ${spread:.4f}\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    return filename, trade_info
