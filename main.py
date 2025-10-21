#!/usr/bin/env python3
"""
Simple Polymarket orderbook data collection
"""

import time
import threading
import sys
from datetime import datetime, timedelta
from config import load_config
from polymarket_client import fetch_orderbook, save_orderbook_snapshot
from ping_server import start_ping_server, ping_data
from balance_manager import record_buy, record_sell, get_balance, get_position


def main():
	"""Main function - simple orderbook collection every second"""
	
	# Start ping server in background
	ping_thread = threading.Thread(target=start_ping_server, daemon=True)
	ping_thread.start()
	
	# Load configuration
	config = load_config()
	tokens = config.get('tokens', [])
	investment = float(config.get('investment', 0))
	min_value = float(config.get('min_value', 20.0))
	sell_timeout = int(config.get('sell_timeout', 100))  # seconds
	
	# Quiet mode: no startup console prints
	
	# Track sell timers for each token
	sell_timers = {}  # {slug: datetime when timer started}
	
	try:
		last_seen_count = 0
		while True:
			# Only act when a new ping arrives
			current_count = ping_data.get('count', 0)
			if current_count > last_seen_count:
				# New ping received; fetch and save snapshots once per ping
				for t in tokens:
					token_id = t['id']
					slug = t.get('slug')
					orderbook_data = fetch_orderbook(token_id)
					if orderbook_data:
						# Check if we have an existing position
						position = get_position(slug)
						
						if position and position['shares'] > 0:
							# We have a position - check if timer exists
							if slug in sell_timers:
								# Timer already running - reset it
								sys.stdout.write("\r" + " " * 80 + "\r")  # Clear countdown line
								sys.stdout.flush()
								sell_timers[slug] = datetime.now()
								print(f"\n{slug}: Timer reset ({sell_timeout}s to auto-sell)")
							else:
								# Position exists but no timer (maybe from restart) - don't start timer
								print(f"\n{slug}: Position exists, waiting for next ping to start timer")
						else:
							# No position - try to buy
							available_balance = get_balance()
							investment_amount = min(investment, available_balance)
							
							# Save snapshot (quiet) and include trade plan using available balance
							_, trade_info = save_orderbook_snapshot(orderbook_data, token_id, min_value=min_value, slug=slug, investment=investment_amount)
							
							# Minimal console: show each fill individually and record transaction
							if trade_info and 'fills' in trade_info:
								fills = trade_info['fills']
								total_shares = trade_info['shares']
								total_spent = trade_info['spend']
								
								# Record the buy transaction in ledger
								if record_buy(slug, total_shares, total_spent):
									new_balance = get_balance()
									position = get_position(slug)
									
									print(f"\n{(slug or token_id[:10]+'...')}: saved")
									for f in fills:
										print(f"  Buy {f['shares']:.2f} @ ${f['price']:.3f} = ${f['cost']:.2f}")
									print(f"  Total: {total_shares:.2f} shares for ${total_spent:.2f}")
									print(f"  Balance: ${new_balance:.2f} | Position: {position['shares']:.2f} shares @ ${position['avg_cost']:.3f} avg")
									
									# Start sell timer ONLY after buy
									sell_timers[slug] = datetime.now()
									print(f"  ⏱️  Sell timer started ({sell_timeout}s)")
								else:
									print(f"{(slug or token_id[:10]+'...')}: saved, insufficient balance")
							else:
								print(f"{(slug or token_id[:10]+'...')}: saved, no asks available")
				last_seen_count = current_count
			
			# Check sell timers and display countdown
			for t in tokens:
				slug = t.get('slug')
				token_id = t['id']
				
				if slug in sell_timers:
					time_elapsed = (datetime.now() - sell_timers[slug]).total_seconds()
					time_remaining = int(sell_timeout - time_elapsed)
					
					# Display countdown (update in place)
					if time_remaining > 0:
						sys.stdout.write(f"\r⏱️  {slug}: {time_remaining}s remaining")
						sys.stdout.flush()
					
					if time_elapsed >= sell_timeout:
						# Timer expired - sell the position
						position = get_position(slug)
						if position and position['shares'] > 0:
							print(f"\n⏰ Timer expired for {slug} - Auto-selling position...")
							
							# Fetch current orderbook to get best bid prices
							orderbook_data = fetch_orderbook(token_id)
							if orderbook_data:
								bids = orderbook_data.get('bids', [])
								
								# Sort bids by price (high to low) to sell at best prices
								sorted_bids = sorted(bids, key=lambda x: float(x['price']), reverse=True)
								
								# Calculate sell proceeds by filling across bid levels
								shares_to_sell = position['shares']
								total_proceeds = 0.0
								sell_fills = []
								
								for bid in sorted_bids:
									if shares_to_sell <= 0:
										break
									
									price = float(bid['price'])
									available_size = float(bid['size'])
									
									shares_at_price = min(available_size, shares_to_sell)
									proceeds = shares_at_price * price
									
									sell_fills.append({'price': price, 'shares': shares_at_price, 'proceeds': proceeds})
									total_proceeds += proceeds
									shares_to_sell -= shares_at_price
								
								# Record the sell
								if record_sell(slug, position['shares'], total_proceeds):
									new_balance = get_balance()
									profit = total_proceeds - position['total_invested']
									
									# Clear the countdown line before printing results
									sys.stdout.write("\r" + " " * 80 + "\r")
									sys.stdout.flush()
									
									print(f"  Sold {position['shares']:.2f} shares:")
									for f in sell_fills:
										print(f"    Sell {f['shares']:.2f} @ ${f['price']:.3f} = ${f['proceeds']:.2f}")
									print(f"  Total proceeds: ${total_proceeds:.2f}")
									print(f"  Profit/Loss: ${profit:+.2f}")
									print(f"  New balance: ${new_balance:.2f}")
									
									# Remove timer
									del sell_timers[slug]
								else:
									print(f"  Failed to record sell for {slug}")
									del sell_timers[slug]
							else:
								print(f"  Failed to fetch orderbook for selling {slug}")
								del sell_timers[slug]
			
			# Small sleep to avoid busy-waiting
			time.sleep(0.2)
			
	except KeyboardInterrupt:
		print("\nStopping collection...")

if __name__ == "__main__":
	main()
