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


def format_time(seconds):
	"""Convert seconds to MM:SS format"""
	minutes = int(seconds // 60)
	secs = int(seconds % 60)
	return f"{minutes:02d}:{secs:02d}"

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
	
	# Print startup info
	print("\n" + "="*70)
	print("🎯 SNIPERX STARTED")
	print("="*70)
	print(f"📊 Tracking: {len(tokens)} token(s)")
	print(f"💰 Investment per trade: ${investment:.2f}")
	print(f"⏱️  Auto-sell timeout: {format_time(sell_timeout)}")
	print(f"🌐 Ping server running on: http://0.0.0.0:5000/ping")
	print("="*70 + "\n")
	print("⏳ Waiting for ping signal...\n")
	
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
								sys.stdout.write("\r" + " " * 100 + "\r")  # Clear countdown line
								sys.stdout.flush()
								sell_timers[slug] = datetime.now()
								print(f"\n{'─'*70}")
								print(f"🔄 TIMER RESET - {slug.upper()}")
								print(f"⏱️  Auto-sell in: {format_time(sell_timeout)}")
								print(f"{'─'*70}\n")
							else:
								# Position exists but no timer (maybe from restart) - don't start timer
								print(f"\n{'─'*70}")
								print(f"📌 POSITION DETECTED - {slug.upper()}")
								print(f"💡 Waiting for next ping to start timer")
								print(f"{'─'*70}\n")
						else:
							# No position - try to buy
							available_balance = get_balance()
							investment_amount = min(investment, available_balance)
							
							# Save snapshot (quiet) and include trade plan using available balance
							_, trade_info = save_orderbook_snapshot(orderbook_data, token_id, min_value=min_value, slug=slug, investment=investment_amount, trade_type="BUY")
							
							# Minimal console: show each fill individually and record transaction
							if trade_info and 'fills' in trade_info:
								fills = trade_info['fills']
								total_shares = trade_info['shares']
								total_spent = trade_info['spend']
								
								# Record the buy transaction in ledger
								if record_buy(slug, total_shares, total_spent):
									new_balance = get_balance()
									position = get_position(slug)
									
									print(f"\n{'═'*70}")
									print(f"✅ BUY ORDER EXECUTED - {slug.upper()}")
									print(f"{'═'*70}")
									for f in fills:
										print(f"  📈 Buy {f['shares']:.2f} shares @ ${f['price']:.3f} = ${f['cost']:.2f}")
									print(f"  ───────────────────────────────────")
									print(f"  💰 Total Spent:     ${total_spent:.2f}")
									print(f"  📊 Total Shares:    {total_shares:.2f}")
									print(f"  💵 Avg Cost:        ${position['avg_cost']:.3f}")
									print(f"  💼 Balance:         ${new_balance:.2f}")
									print(f"{'═'*70}")
									
									# Start sell timer ONLY after buy
									sell_timers[slug] = datetime.now()
									print(f"⏱️  AUTO-SELL TIMER STARTED: {format_time(sell_timeout)}")
									print(f"{'═'*70}\n")
								else:
									print(f"\n⚠️  {slug.upper()}: Insufficient balance\n")
							else:
								print(f"\n⚠️  {slug.upper()}: No liquidity available\n")
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
						time_str = format_time(time_remaining)
						# Create a nice progress bar
						progress_percent = (time_elapsed / sell_timeout) * 100
						bar_length = 30
						filled_length = int(bar_length * progress_percent / 100)
						bar = '█' * filled_length + '░' * (bar_length - filled_length)
						
						sys.stdout.write(f"\r⏱️  [{bar}] {slug.upper()}: {time_str} remaining   ")
						sys.stdout.flush()
					
					if time_elapsed >= sell_timeout:
						# Timer expired - sell the position
						position = get_position(slug)
						if position and position['shares'] > 0:
							# Clear the countdown line before printing results
							sys.stdout.write("\r" + " " * 100 + "\r")
							sys.stdout.flush()
							
							print(f"\n{'═'*70}")
							print(f"⏰ TIMER EXPIRED - AUTO-SELLING {slug.upper()}")
							print(f"{'═'*70}")
							
							# Fetch current orderbook to get best bid prices
							orderbook_data = fetch_orderbook(token_id)
							if orderbook_data:
								# Save snapshot before selling
								save_orderbook_snapshot(orderbook_data, token_id, min_value=min_value, slug=slug, investment=0, trade_type="SELL")
								
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
									profit_emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
									
									print(f"💼 SELL ORDER EXECUTED")
									print(f"{'─'*70}")
									for f in sell_fills:
										print(f"  📉 Sell {f['shares']:.2f} shares @ ${f['price']:.3f} = ${f['proceeds']:.2f}")
									print(f"  ───────────────────────────────────")
									print(f"  💵 Total Proceeds:  ${total_proceeds:.2f}")
									print(f"  📊 Shares Sold:     {position['shares']:.2f}")
									print(f"  {profit_emoji} Profit/Loss:    ${profit:+.2f}")
									print(f"  💼 New Balance:     ${new_balance:.2f}")
									print(f"{'═'*70}\n")
									
									# Remove timer
									del sell_timers[slug]
								else:
									print(f"❌ Failed to record sell for {slug}")
									print(f"{'═'*70}\n")
									del sell_timers[slug]
							else:
								print(f"❌ Failed to fetch orderbook for selling")
								print(f"{'═'*70}\n")
								del sell_timers[slug]
			
			# Small sleep to avoid busy-waiting
			time.sleep(0.2)
			
	except KeyboardInterrupt:
		print("\n\n" + "="*70)
		print("🛑 SNIPERX STOPPED")
		print("="*70)
		print("👋 Goodbye!\n")

if __name__ == "__main__":
	main()
