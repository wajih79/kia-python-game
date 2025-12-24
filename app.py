"""
KIA Python Trading Challenge - Web-Based Team Competition
A real-time multiplayer game for teaching Python to financial professionals
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, join_room
import qrcode
import io
import base64
import os
import secrets
from datetime import datetime
import re
import socket
import anthropic


def get_local_ip():
    """Get the local network IP address"""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins="*")

# Game configuration
ROUND_TIME_LIMIT = 300  # 5 minutes per round

# Pre-game poll configuration
POLL_QUESTION = "What Takes Most of Your Time?"
POLL_OPTIONS = [
    "Manual data entry and Excel formatting",
    "Creating repetitive reports",
    "Calculating portfolio metrics",
    "Collecting data from multiple sources",
    "Updating dashboards"
]

# Game state stored in memory (use Redis for production scaling)
game_state = {
    'teams': {},  # team_id: {name, score, current_round, answers, joined_at}
    'current_round': 0,
    'round_start_time': None,
    'game_started': False,
    'game_paused': False,
    'trainer_connected': False,
    'poll_active': False,
    'poll_votes': {}  # team_id: [selected_options]
}

# Questions organized by rounds
# code_template = incomplete code for trainees to complete
# solution_code = correct solution (shown if wrong)
# expected_output = what the output should be
QUESTIONS = {
    1: {
        'title': 'Variables & Basic Math',
        'theme': 'Calculate Portfolio Returns',
        'questions': [
            {
                'id': '1.1',
                'question': 'KIA invested $500 million in a fund that returned 12%. Calculate the profit by multiplying investment by rate, then print it.',
                'code_template': '''initial_investment = 500000000
return_rate = 0.12

# Calculate the profit (multiply investment by rate)
profit = ???

print(f"Profit: ${profit}")''',
                'solution_code': '''initial_investment = 500000000
return_rate = 0.12

# Calculate the profit (multiply investment by rate)
profit = initial_investment * return_rate

print(f"Profit: ${profit}")''',
                'expected_output': 'Profit: $60000000.0',
                'points': 100
            },
            {
                'id': '1.2',
                'question': 'A $100 million investment grows at 8% annually for 5 years with compound interest. Use the formula: Final = Principal × (1 + rate) ^ years',
                'code_template': '''principal = 100000000
rate = 0.08
years = 5

# Apply the compound interest formula
# Hint: Use ** for exponent (power)
final_value = ???

print(f"Final Value: ${final_value:.2f}")''',
                'solution_code': '''principal = 100000000
rate = 0.08
years = 5

# Apply the compound interest formula
final_value = principal * (1 + rate) ** years

print(f"Final Value: ${final_value:.2f}")''',
                'expected_output': 'Final Value: $146932807.68',
                'points': 100
            },
            {
                'id': '1.3',
                'question': 'BONUS: Calculate 15% of 2 million. Hint: 15% = 0.15',
                'code_template': '''# Calculate 15% of 2 million
result = ???

print(result)''',
                'solution_code': '''# Calculate 15% of 2 million
result = 2000000 * 0.15

print(result)''',
                'expected_output': '300000.0',
                'points': 50
            }
        ]
    },
    2: {
        'title': 'Data Types & Strings',
        'theme': 'Format Investment Reports',
        'questions': [
            {
                'id': '2.1',
                'question': 'Format $750 billion with commas. In f-strings, use :, after the variable to add commas.',
                'code_template': '''aum = 750000000000

# Format with commas - add the formatting code after the colon
formatted = f"${aum:???}"

print(formatted)''',
                'solution_code': '''aum = 750000000000

# Format with commas
formatted = f"${aum:,}"

print(formatted)''',
                'expected_output': '$750,000,000,000',
                'points': 100
            },
            {
                'id': '2.2',
                'question': 'Convert $1,000,000 USD to KWD (exchange rate: 0.31). Multiply USD by the rate.',
                'code_template': '''usd_amount = 1000000
exchange_rate = 0.31

# Convert by multiplying
kwd_amount = ???

print(f"{kwd_amount:,.2f} KWD")''',
                'solution_code': '''usd_amount = 1000000
exchange_rate = 0.31

# Convert by multiplying
kwd_amount = usd_amount * exchange_rate

print(f"{kwd_amount:,.2f} KWD")''',
                'expected_output': '310,000.00 KWD',
                'points': 100
            },
            {
                'id': '2.3',
                'question': 'BONUS: Print the data type name of the number 3.14. Use type(x).__name__ to get just the name.',
                'code_template': '''x = 3.14

# Print just the type name (not the full <class ...>)
print(???)''',
                'solution_code': '''x = 3.14

# Print just the type name
print(type(x).__name__)''',
                'expected_output': 'float',
                'points': 50
            }
        ]
    },
    3: {
        'title': 'Lists',
        'theme': 'Manage Stock Portfolios',
        'questions': [
            {
                'id': '3.1',
                'question': 'Get the last stock from the list. Use negative indexing: list[-1] gets the last item.',
                'code_template': '''stocks = ["Apple", "Microsoft", "Google", "Amazon", "NVIDIA"]

# Get the last item using negative index
last_stock = stocks[???]

print(last_stock)''',
                'solution_code': '''stocks = ["Apple", "Microsoft", "Google", "Amazon", "NVIDIA"]

# Get the last item using negative index
last_stock = stocks[-1]

print(last_stock)''',
                'expected_output': 'NVIDIA',
                'points': 100
            },
            {
                'id': '3.2',
                'question': 'Calculate the total of all investments. Use the sum() function on the list.',
                'code_template': '''investments = [250, 180, 320, 150, 275]

# Calculate the total - what function adds all items?
total = ???

print(f"Total: ${total} million")''',
                'solution_code': '''investments = [250, 180, 320, 150, 275]

# Calculate the total using sum()
total = sum(investments)

print(f"Total: ${total} million")''',
                'expected_output': 'Total: $1175 million',
                'points': 100
            },
            {
                'id': '3.3',
                'question': 'BONUS: Print how many items are in the list. Use len() to get the length.',
                'code_template': '''numbers = [10, 20, 30, 40]

# Print the length of the list
print(???)''',
                'solution_code': '''numbers = [10, 20, 30, 40]

# Print the length of the list
print(len(numbers))''',
                'expected_output': '4',
                'points': 50
            }
        ]
    },
    4: {
        'title': 'Conditionals',
        'theme': 'Make Buy/Sell Decisions',
        'questions': [
            {
                'id': '4.1',
                'question': 'Complete the trading signal logic: "STRONG BUY" if return > 15%, "BUY" if > 5%, "HOLD" if > -5%, else "SELL".',
                'code_template': '''return_rate = 8.5

if return_rate > 15:
    signal = "STRONG BUY"
elif ???:
    signal = "BUY"
elif ???:
    signal = "HOLD"
else:
    signal = "SELL"

print(f"Signal: {signal}")''',
                'solution_code': '''return_rate = 8.5

if return_rate > 15:
    signal = "STRONG BUY"
elif return_rate > 5:
    signal = "BUY"
elif return_rate > -5:
    signal = "HOLD"
else:
    signal = "SELL"

print(f"Signal: {signal}")''',
                'expected_output': 'Signal: BUY',
                'points': 100
            },
            {
                'id': '4.2',
                'question': 'Determine risk: "MEDIUM-HIGH RISK" if volatility > 15 AND sector is "Tech". Use the "and" keyword.',
                'code_template': '''volatility = 22
sector = "Tech"

if volatility > 30:
    risk = "HIGH RISK"
elif volatility > 15 ??? sector == "Tech":
    risk = "MEDIUM-HIGH RISK"
elif volatility > 15:
    risk = "MEDIUM RISK"
else:
    risk = "LOW RISK"

print(risk)''',
                'solution_code': '''volatility = 22
sector = "Tech"

if volatility > 30:
    risk = "HIGH RISK"
elif volatility > 15 and sector == "Tech":
    risk = "MEDIUM-HIGH RISK"
elif volatility > 15:
    risk = "MEDIUM RISK"
else:
    risk = "LOW RISK"

print(risk)''',
                'expected_output': 'MEDIUM-HIGH RISK',
                'points': 100
            },
            {
                'id': '4.3',
                'question': 'BONUS: Approve if return > 0 AND risk is "LOW". Print "APPROVED" or "REJECTED".',
                'code_template': '''return_rate = 7
risk_level = "LOW"

# Check BOTH conditions using "and"
if ??? and ???:
    decision = "APPROVED"
else:
    decision = "REJECTED"

print(decision)''',
                'solution_code': '''return_rate = 7
risk_level = "LOW"

if return_rate > 0 and risk_level == "LOW":
    decision = "APPROVED"
else:
    decision = "REJECTED"

print(decision)''',
                'expected_output': 'APPROVED',
                'points': 50
            }
        ]
    },
    5: {
        'title': 'Loops & Functions',
        'theme': 'Analyze Multiple Assets',
        'questions': [
            {
                'id': '5.1',
                'question': 'Loop through stocks and print each one. Use: for item in list:',
                'code_template': '''stocks = ["Apple", "Google", "Amazon"]

# Complete the for loop
??? stock ??? stocks:
    print(stock)''',
                'solution_code': '''stocks = ["Apple", "Google", "Amazon"]

for stock in stocks:
    print(stock)''',
                'expected_output': 'Apple\nGoogle\nAmazon',
                'points': 100
            },
            {
                'id': '5.2',
                'question': 'Complete the function to calculate profit (principal × rate) and return the result.',
                'code_template': '''def calculate_profit(principal, rate):
    profit = ???
    return profit

# Test the function
result = calculate_profit(1000, 0.10)
print(f"Profit: ${result}")''',
                'solution_code': '''def calculate_profit(principal, rate):
    profit = principal * rate
    return profit

# Test the function
result = calculate_profit(1000, 0.10)
print(f"Profit: ${result}")''',
                'expected_output': 'Profit: $100.0',
                'points': 100
            },
            {
                'id': '5.3',
                'question': 'BOSS CHALLENGE: Loop through portfolio, calculate each profit, and add to total_profit.',
                'code_template': '''portfolio = [
    ("Oil Fund", 2000, 12.5),
    ("Tech Fund", 1500, 18.3),
    ("Real Estate", 800, 4.2),
    ("Bonds", 1200, -2.1)
]

total_profit = 0
for name, investment, rate in portfolio:
    # Calculate profit for this asset
    profit = ???
    # Add to total
    total_profit = ???

print(f"Total Profit: ${total_profit:.1f} million")''',
                'solution_code': '''portfolio = [
    ("Oil Fund", 2000, 12.5),
    ("Tech Fund", 1500, 18.3),
    ("Real Estate", 800, 4.2),
    ("Bonds", 1200, -2.1)
]

total_profit = 0
for name, investment, rate in portfolio:
    profit = investment * (rate / 100)
    total_profit = total_profit + profit

print(f"Total Profit: ${total_profit:.1f} million")''',
                'expected_output': 'Total Profit: $532.9 million',
                'points': 150
            }
        ]
    }
}

# AI Prompt Challenge - Questions for prompt-based code generation
PROMPT_CHALLENGES = {
    1: {
        'title': 'Variables & Calculations',
        'theme': 'Portfolio Returns',
        'time_limit': 180,  # 3 minutes
        'challenges': [
            {
                'id': 'P1.1',
                'title': 'Investment Return Calculator',
                'scenario': '''KIA invested $1,000,000 in a fund with an 8.5% annual return for 3 years (compound interest).

Calculate and display:
- Final value after 3 years
- Total profit made''',
                'given_data': '''initial_investment = 1000000
annual_rate = 0.085
years = 3''',
                'expected_output': '''Final Value: $1,277,289.13
Total Profit: $277,289.13''',
                'hints': [
                    'Use compound interest formula: final = principal * (1 + rate) ** years',
                    'Format output with 2 decimal places using :.2f',
                    'Calculate profit as final_value - initial_investment'
                ],
                'points': 100
            },
            {
                'id': 'P1.2',
                'title': 'Currency Converter',
                'scenario': '''Convert $5,000,000 USD to Kuwaiti Dinar (KWD).

Exchange rate: 1 USD = 0.31 KWD

Display both amounts with proper currency formatting.''',
                'given_data': '''amount_usd = 5000000
exchange_rate = 0.31''',
                'expected_output': '''USD: $5,000,000.00
KWD: KD 1,550,000.00''',
                'hints': [
                    'Multiply USD amount by exchange rate',
                    'Use :,.2f format for thousands separator and 2 decimals'
                ],
                'points': 100
            },
            {
                'id': 'P1.3',
                'title': 'Multi-Currency Portfolio',
                'scenario': '''Calculate total portfolio value in KWD.

Portfolio holdings and exchange rates to KWD are provided.
Display each currency's KWD value and the total.''',
                'given_data': '''portfolio = {"USD": 10000000, "EUR": 5000000, "GBP": 3000000}
rates_to_kwd = {"USD": 0.31, "EUR": 0.34, "GBP": 0.39}''',
                'expected_output': '''Portfolio Value in KWD:
USD: KD 3,100,000.00
EUR: KD 1,700,000.00
GBP: KD 1,170,000.00
Total: KD 5,970,000.00''',
                'hints': [
                    'Loop through the portfolio dictionary',
                    'Look up corresponding exchange rate for each currency',
                    'Keep a running total'
                ],
                'points': 150,
                'is_bonus': True
            }
        ]
    },
    2: {
        'title': 'Data Processing',
        'theme': 'Asset Data Handling',
        'time_limit': 180,
        'challenges': [
            {
                'id': 'P2.1',
                'title': 'Stock Data Parser',
                'scenario': '''Parse stock data string and format for reporting.

The data contains stock symbols and prices separated by colons and commas.
Display each stock's price and calculate the average.''',
                'given_data': '''data = "AAPL:178.50,MSFT:378.25,GOOGL:141.80,AMZN:178.35"''',
                'expected_output': '''AAPL: $178.50
MSFT: $378.25
GOOGL: $141.80
AMZN: $178.35
Average Price: $219.23''',
                'hints': [
                    'Split by comma first, then by colon',
                    'Convert price strings to floats',
                    'Calculate average = sum / count'
                ],
                'points': 100
            },
            {
                'id': 'P2.2',
                'title': 'Portfolio Weight Calculator',
                'scenario': '''Calculate the weight (percentage) of each investment in the portfolio.

Total portfolio value and individual investments are provided.''',
                'given_data': '''investments = {"Stocks": 450000000, "Bonds": 200000000, "Real Estate": 150000000, "Cash": 50000000}
total = 850000000''',
                'expected_output': '''Portfolio Weights:
Stocks: 52.94%
Bonds: 23.53%
Real Estate: 17.65%
Cash: 5.88%''',
                'hints': [
                    'Weight = (investment / total) * 100',
                    'Format percentage with 2 decimal places'
                ],
                'points': 100
            },
            {
                'id': 'P2.3',
                'title': 'Investment Report Generator',
                'scenario': '''Generate a formatted quarterly investment report.

Include fund name, current value, quarterly return, and status.''',
                'given_data': '''fund_name = "KIA Global Equity Fund"
current_value = 2500000000
quarterly_return = 4.7
benchmark_return = 3.2''',
                'expected_output': '''=== Quarterly Report ===
Fund: KIA Global Equity Fund
Value: $2,500,000,000.00
Return: 4.70%
Benchmark: 3.20%
Status: OUTPERFORMING (+1.50%)''',
                'hints': [
                    'Calculate performance vs benchmark',
                    'Use string formatting for alignment',
                    'Compare returns to determine status'
                ],
                'points': 150,
                'is_bonus': True
            }
        ]
    },
    3: {
        'title': 'Lists & Filtering',
        'theme': 'Portfolio Analysis',
        'time_limit': 180,
        'challenges': [
            {
                'id': 'P3.1',
                'title': 'Stock Performance Sorter',
                'scenario': '''Sort stocks by their annual return (highest to lowest).

Display the sorted list with rankings.''',
                'given_data': '''stocks = [
    {"symbol": "AAPL", "return": 12.5},
    {"symbol": "TSLA", "return": 45.8},
    {"symbol": "MSFT", "return": 15.2},
    {"symbol": "META", "return": -3.1},
    {"symbol": "NVDA", "return": 85.3}
]''',
                'expected_output': '''Stock Rankings by Return:
1. NVDA: 85.30%
2. TSLA: 45.80%
3. MSFT: 15.20%
4. AAPL: 12.50%
5. META: -3.10%''',
                'hints': [
                    'Use sorted() with key parameter',
                    'Sort in descending order with reverse=True',
                    'Use enumerate for ranking numbers'
                ],
                'points': 100
            },
            {
                'id': 'P3.2',
                'title': 'Underperforming Asset Filter',
                'scenario': '''Identify all underperforming assets (negative returns).

List them with their losses.''',
                'given_data': '''assets = [
    {"name": "Tech Fund", "return": 12.5},
    {"name": "Energy Fund", "return": -8.3},
    {"name": "Healthcare Fund", "return": 5.2},
    {"name": "Retail Fund", "return": -12.1},
    {"name": "Finance Fund", "return": 3.8}
]''',
                'expected_output': '''Underperforming Assets:
Energy Fund: -8.30%
Retail Fund: -12.10%
Total Underperformers: 2''',
                'hints': [
                    'Filter for assets where return < 0',
                    'Count the filtered results'
                ],
                'points': 100
            },
            {
                'id': 'P3.3',
                'title': 'Top N Stocks Selector',
                'scenario': '''Select the top 3 stocks by market value.

Display their details and combined value.''',
                'given_data': '''stocks = [
    {"symbol": "AAPL", "value": 2800000000000},
    {"symbol": "MSFT", "value": 2700000000000},
    {"symbol": "GOOGL", "value": 1800000000000},
    {"symbol": "AMZN", "value": 1700000000000},
    {"symbol": "NVDA", "value": 1200000000000}
]
n = 3''',
                'expected_output': '''Top 3 Stocks by Market Value:
1. AAPL: $2.80T
2. MSFT: $2.70T
3. GOOGL: $1.80T
Combined Value: $7.30T''',
                'hints': [
                    'Sort by value descending',
                    'Slice to get top n items',
                    'Format large numbers as trillions (divide by 1e12)'
                ],
                'points': 150,
                'is_bonus': True
            }
        ]
    },
    4: {
        'title': 'Logic & Decisions',
        'theme': 'Trading Strategies',
        'time_limit': 240,  # 4 minutes for more complex logic
        'challenges': [
            {
                'id': 'P4.1',
                'title': 'Trading Signal Generator',
                'scenario': '''Generate a trading recommendation based on price movement.

Rules:
- STRONG BUY if current > purchase * 1.20 (20% gain)
- BUY if current > purchase * 1.05
- HOLD if current > purchase * 0.95
- SELL if current <= purchase * 0.95''',
                'given_data': '''current_price = 156.00
purchase_price = 120.00
target_gain = 0.20
stop_loss = 0.05''',
                'expected_output': '''Current Position: +30.00%
Recommendation: STRONG BUY
Reason: Exceeded 20% target gain''',
                'hints': [
                    'Calculate percentage change: (current - purchase) / purchase * 100',
                    'Use if/elif/else for decision logic',
                    'Include the reason in output'
                ],
                'points': 100
            },
            {
                'id': 'P4.2',
                'title': 'Risk Assessment System',
                'scenario': '''Assess investment risk based on multiple factors.

Risk Levels:
- HIGH: volatility > 30 OR (sector is "Crypto" AND volatility > 15)
- MEDIUM-HIGH: volatility > 20 AND sector is "Tech"
- MEDIUM: volatility > 15
- LOW: volatility <= 15''',
                'given_data': '''volatility = 25
sector = "Tech"
market_cap = "Large"''',
                'expected_output': '''Risk Assessment:
Volatility: 25%
Sector: Tech
Risk Level: MEDIUM-HIGH
Recommendation: Suitable for moderate risk tolerance''',
                'hints': [
                    'Use compound conditions with and/or',
                    'Order conditions from most specific to least',
                    'Add contextual recommendation'
                ],
                'points': 100
            },
            {
                'id': 'P4.3',
                'title': 'Investment Approval System',
                'scenario': '''Multi-criteria investment approval logic.

Approval requires ALL of:
- Expected return > 5%
- Risk level is "LOW" or "MEDIUM"
- Investment amount <= available_budget

Provide detailed approval status.''',
                'given_data': '''expected_return = 8.5
risk_level = "MEDIUM"
investment_amount = 5000000
available_budget = 10000000''',
                'expected_output': '''Investment Proposal Review:
Expected Return: 8.50% [PASS]
Risk Level: MEDIUM [PASS]
Budget Check: $5M of $10M [PASS]
Status: APPROVED
Remaining Budget: $5,000,000.00''',
                'hints': [
                    'Check each criterion separately',
                    'Track pass/fail for each',
                    'All must pass for approval'
                ],
                'points': 150,
                'is_bonus': True
            }
        ]
    },
    5: {
        'title': 'Advanced Analysis',
        'theme': 'Automated Trading',
        'time_limit': 300,  # 5 minutes for boss challenge
        'challenges': [
            {
                'id': 'P5.1',
                'title': 'Portfolio Summary Function',
                'scenario': '''Create a function to summarize any portfolio.

The function should calculate total value, best performer, and average return.''',
                'given_data': '''portfolio = [
    {"name": "Tech Fund", "value": 500000, "return": 15.3},
    {"name": "Bond Fund", "value": 300000, "return": 4.2},
    {"name": "Real Estate", "value": 200000, "return": 8.7}
]''',
                'expected_output': '''Portfolio Summary:
Total Value: $1,000,000.00
Best Performer: Tech Fund (15.30%)
Average Return: 9.40%''',
                'hints': [
                    'Define a function that takes portfolio as parameter',
                    'Use max() with key to find best performer',
                    'Calculate average return from all funds'
                ],
                'points': 100
            },
            {
                'id': 'P5.2',
                'title': 'Batch Trade Processor',
                'scenario': '''Process multiple trades and generate a summary.

For each trade, calculate the total cost (shares * price) and running total.''',
                'given_data': '''trades = [
    {"symbol": "AAPL", "shares": 100, "price": 178.50, "action": "BUY"},
    {"symbol": "MSFT", "shares": 50, "price": 378.25, "action": "BUY"},
    {"symbol": "GOOGL", "shares": 30, "price": 141.80, "action": "SELL"}
]''',
                'expected_output': '''Trade Execution Report:
BUY 100 AAPL @ $178.50 = $17,850.00
BUY 50 MSFT @ $378.25 = $18,912.50
SELL 30 GOOGL @ $141.80 = $4,254.00
Net Cash Flow: -$32,508.50''',
                'hints': [
                    'Loop through each trade',
                    'Calculate cost for each trade',
                    'BUY is negative cash flow, SELL is positive'
                ],
                'points': 100
            },
            {
                'id': 'P5.3',
                'title': 'Complete Portfolio Analyzer',
                'scenario': '''BOSS CHALLENGE: Build a comprehensive portfolio analysis system.

Analyze the portfolio to provide:
1. Total portfolio value
2. Gain/Loss for each position
3. Best and worst performers
4. Overall portfolio return percentage
5. Risk classification based on sector diversity''',
                'given_data': '''portfolio = [
    {"symbol": "AAPL", "shares": 100, "purchase": 150, "current": 178, "sector": "Tech"},
    {"symbol": "MSFT", "shares": 50, "purchase": 350, "current": 378, "sector": "Tech"},
    {"symbol": "XOM", "shares": 200, "purchase": 95, "current": 105, "sector": "Energy"},
    {"symbol": "JNJ", "shares": 75, "purchase": 160, "current": 155, "sector": "Healthcare"}
]''',
                'expected_output': '''=== PORTFOLIO ANALYSIS ===

Holdings Summary:
AAPL: 100 shares @ $178.00 = $17,800.00 (+18.67%)
MSFT: 50 shares @ $378.00 = $18,900.00 (+8.00%)
XOM: 200 shares @ $105.00 = $21,000.00 (+10.53%)
JNJ: 75 shares @ $155.00 = $11,625.00 (-3.13%)

Portfolio Metrics:
Total Value: $69,325.00
Total Cost: $64,250.00
Overall Return: +7.90%

Performance:
Best: AAPL (+18.67%)
Worst: JNJ (-3.13%)

Risk Assessment:
Sectors: 3 (Tech, Energy, Healthcare)
Diversification: MODERATE''',
                'hints': [
                    'Calculate position value and return for each holding',
                    'Track total value and total cost',
                    'Find max and min returns',
                    'Count unique sectors for diversification'
                ],
                'points': 200,
                'is_boss': True
            }
        ]
    }
}

# Prompt game state (separate from regular game)
prompt_game_state = {
    'teams': {},  # team_id: {name, score, current_challenge, attempts, joined_at}
    'current_round': 0,
    'round_start_time': None,
    'game_started': False,
    'game_paused': False,
    'game_mode': 'speed',  # 'speed', 'efficiency', 'debug'
    'trainer_connected': False
}


def generate_qr_code(url):
    """Generate QR code as base64 image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode()


def generate_team_id():
    """Generate a unique team ID"""
    return secrets.token_hex(4).upper()


def normalize_output(output):
    """Normalize output for comparison (strip whitespace, normalize newlines)"""
    if output is None:
        return ""
    # Strip whitespace, normalize line endings to spaces, lowercase
    text = str(output).strip()
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\s+', ' ', text)
    return text.lower()


def check_output_match(user_output, expected_output):
    """Check if user output matches expected output (flexible matching)"""
    if not user_output or not expected_output:
        return False

    user_norm = normalize_output(user_output)
    expected_norm = normalize_output(expected_output)

    # Exact match after normalization
    if user_norm == expected_norm:
        return True

    # Check if expected output is contained in user output (or vice versa)
    if expected_norm in user_norm or user_norm in expected_norm:
        return True

    # For multi-line outputs, check if all expected lines are present
    expected_lines = [line.strip().lower() for line in expected_output.strip().split('\n') if line.strip()]
    user_lines = [line.strip().lower() for line in user_output.strip().split('\n') if line.strip()]

    if expected_lines and user_lines:
        # Check if all expected lines match user lines
        if expected_lines == user_lines:
            return True
        # Check if expected content is in user output
        if all(exp_line in user_norm for exp_line in expected_lines):
            return True

    # Check if outputs contain the same key numbers
    user_numbers = re.findall(r'[\d,]+\.?\d*', user_output or '')
    expected_numbers = re.findall(r'[\d,]+\.?\d*', expected_output or '')

    if user_numbers and expected_numbers:
        try:
            user_val = float(user_numbers[-1].replace(',', '').rstrip('.'))
            expected_val = float(expected_numbers[-1].replace(',', '').rstrip('.'))
            if abs(user_val - expected_val) < 1:
                return True
        except:
            pass

    return False


@app.route('/')
def index():
    """Landing page with options"""
    return render_template('index.html')


@app.route('/trainer')
def trainer_dashboard():
    """Trainer dashboard to control the game and view all scores"""
    # Check if running on Render (production) or locally
    if os.environ.get('RENDER'):
        # Use the Render external URL
        render_url = os.environ.get('RENDER_EXTERNAL_URL', request.host_url.rstrip('/'))
        join_url = f"{render_url}/join"
    else:
        # Use local network IP so other devices can connect
        local_ip = get_local_ip()
        port = request.host.split(':')[-1] if ':' in request.host else '8080'
        join_url = f"http://{local_ip}:{port}/join"
    qr_code = generate_qr_code(join_url)

    return render_template('trainer.html',
                         qr_code=qr_code,
                         join_url=join_url,
                         teams=game_state['teams'],
                         current_round=game_state['current_round'],
                         total_rounds=len(QUESTIONS))


@app.route('/join', methods=['GET', 'POST'])
def join_game():
    """Team registration page"""
    if request.method == 'POST':
        team_name = request.form.get('team_name', '').strip()
        if team_name:
            team_id = generate_team_id()
            game_state['teams'][team_id] = {
                'name': team_name,
                'score': 0,
                'current_question': 0,
                'answers': {},
                'joined_at': datetime.now().isoformat()
            }
            session['team_id'] = team_id
            session['team_name'] = team_name

            # Notify trainer dashboard
            socketio.emit('team_joined', {
                'team_id': team_id,
                'team_name': team_name,
                'score': 0
            }, room='trainer')

            return redirect(url_for('team_game'))

    return render_template('join.html')


@app.route('/game')
def team_game():
    """Main game interface for teams"""
    team_id = session.get('team_id')
    if not team_id or team_id not in game_state['teams']:
        return redirect(url_for('join_game'))

    team = game_state['teams'][team_id]
    return render_template('game.html',
                         team_id=team_id,
                         team_name=team['name'],
                         score=team['score'],
                         questions=QUESTIONS,
                         current_round=game_state['current_round'],
                         game_started=game_state['game_started'])


@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Handle answer submission from teams - now compares code output"""
    team_id = session.get('team_id')
    if not team_id or team_id not in game_state['teams']:
        return jsonify({'error': 'Not registered'}), 401

    data = request.json
    question_id = data.get('question_id')
    user_code = data.get('code', '')
    user_output = data.get('output', '')

    # Find the question
    round_num = int(question_id.split('.')[0])
    if round_num not in QUESTIONS:
        return jsonify({'error': 'Invalid question'}), 400

    question = None
    for q in QUESTIONS[round_num]['questions']:
        if q['id'] == question_id:
            question = q
            break

    if not question:
        return jsonify({'error': 'Question not found'}), 400

    # Check if already answered correctly
    existing_answer = game_state['teams'][team_id]['answers'].get(question_id)
    if existing_answer and existing_answer.get('correct'):
        return jsonify({
            'error': 'Already answered correctly',
            'correct': True,
            'points_earned': 0,
            'total_score': game_state['teams'][team_id]['score']
        }), 200

    # Compare output
    expected_output = question.get('expected_output', '')
    is_correct = check_output_match(user_output, expected_output)

    points_earned = 0
    if is_correct:
        points_earned = question['points']
        game_state['teams'][team_id]['score'] += points_earned

    # Record answer
    game_state['teams'][team_id]['answers'][question_id] = {
        'code': user_code,
        'output': user_output,
        'correct': is_correct,
        'points': points_earned,
        'timestamp': datetime.now().isoformat()
    }

    # Notify trainer
    team = game_state['teams'][team_id]
    socketio.emit('score_update', {
        'team_id': team_id,
        'team_name': team['name'],
        'score': team['score'],
        'question_id': question_id,
        'correct': is_correct,
        'points': points_earned
    }, room='trainer')

    return jsonify({
        'correct': is_correct,
        'points_earned': points_earned,
        'total_score': game_state['teams'][team_id]['score'],
        'expected_output': expected_output if not is_correct else None,
        'solution_code': question.get('solution_code', '') if not is_correct else None
    })


@app.route('/api/game_state')
def get_game_state():
    """Get current game state for teams"""
    team_id = session.get('team_id')
    team_score = 0
    team_answers = {}

    if team_id and team_id in game_state['teams']:
        team_score = game_state['teams'][team_id]['score']
        team_answers = game_state['teams'][team_id]['answers']

    # Calculate remaining time
    time_remaining = ROUND_TIME_LIMIT
    if game_state['round_start_time'] and game_state['game_started']:
        elapsed = (datetime.now() - game_state['round_start_time']).seconds
        time_remaining = max(0, ROUND_TIME_LIMIT - elapsed)

    return jsonify({
        'current_round': game_state['current_round'],
        'game_started': game_state['game_started'],
        'game_paused': game_state['game_paused'],
        'poll_active': game_state['poll_active'],
        'your_score': team_score,
        'your_answers': team_answers,
        'time_remaining': time_remaining
    })


@app.route('/api/trainer/start_round', methods=['POST'])
def start_round():
    """Trainer starts a new round"""
    round_num = request.json.get('round', 1)
    game_state['current_round'] = round_num
    game_state['game_started'] = True
    game_state['game_paused'] = False
    game_state['round_start_time'] = datetime.now()

    socketio.emit('round_started', {
        'round': round_num,
        'title': QUESTIONS[round_num]['title'],
        'theme': QUESTIONS[round_num]['theme'],
        'time_limit': ROUND_TIME_LIMIT
    })

    return jsonify({'success': True, 'round': round_num})


@app.route('/api/trainer/pause_game', methods=['POST'])
def pause_game():
    """Trainer pauses the game"""
    game_state['game_paused'] = not game_state['game_paused']

    socketio.emit('game_paused', {
        'paused': game_state['game_paused']
    })

    return jsonify({'success': True, 'paused': game_state['game_paused']})


@app.route('/api/trainer/reset_game', methods=['POST'])
def reset_game():
    """Trainer resets the entire game"""
    game_state['teams'] = {}
    game_state['current_round'] = 0
    game_state['game_started'] = False
    game_state['game_paused'] = False
    game_state['round_start_time'] = None

    socketio.emit('game_reset', {})

    return jsonify({'success': True})


@app.route('/api/trainer/teams')
def get_teams():
    """Get all teams and scores for trainer"""
    teams_list = []
    for team_id, team_data in game_state['teams'].items():
        teams_list.append({
            'id': team_id,
            'name': team_data['name'],
            'score': team_data['score'],
            'answers': team_data['answers']
        })

    # Sort by score descending
    teams_list.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({
        'teams': teams_list,
        'current_round': game_state['current_round'],
        'game_started': game_state['game_started']
    })


# Poll endpoints
@app.route('/api/poll/start', methods=['POST'])
def start_poll():
    """Trainer starts the poll"""
    game_state['poll_active'] = True
    game_state['poll_votes'] = {}

    socketio.emit('poll_started', {
        'question': POLL_QUESTION,
        'options': POLL_OPTIONS
    })

    return jsonify({'success': True})


@app.route('/api/poll/stop', methods=['POST'])
def stop_poll():
    """Trainer stops the poll"""
    game_state['poll_active'] = False

    socketio.emit('poll_stopped', {})

    return jsonify({'success': True})


@app.route('/api/poll/vote', methods=['POST'])
def submit_vote():
    """Team submits their vote"""
    team_id = session.get('team_id')
    if not team_id or team_id not in game_state['teams']:
        return jsonify({'error': 'Not registered'}), 401

    if not game_state['poll_active']:
        return jsonify({'error': 'Poll not active'}), 400

    data = request.json
    selected_options = data.get('options', [])

    game_state['poll_votes'][team_id] = selected_options

    # Calculate results and send to trainer
    results = calculate_poll_results()
    socketio.emit('poll_update', {
        'results': results,
        'total_votes': len(game_state['poll_votes'])
    }, room='trainer')

    return jsonify({'success': True})


@app.route('/api/poll/results')
def get_poll_results():
    """Get current poll results"""
    results = calculate_poll_results()
    return jsonify({
        'question': POLL_QUESTION,
        'options': POLL_OPTIONS,
        'results': results,
        'total_votes': len(game_state['poll_votes']),
        'active': game_state['poll_active']
    })


def calculate_poll_results():
    """Calculate poll results as percentages"""
    results = {option: 0 for option in POLL_OPTIONS}
    total_votes = len(game_state['poll_votes'])

    for team_votes in game_state['poll_votes'].values():
        for option in team_votes:
            if option in results:
                results[option] += 1

    # Convert to percentages
    if total_votes > 0:
        results = {k: round((v / total_votes) * 100) for k, v in results.items()}

    return results


# ============ AI PROMPT CHALLENGE FUNCTIONS ============

def generate_code_from_prompt(prompt: str, challenge_context: str, given_data: str) -> dict:
    """Generate Python code from user prompt using Claude API"""
    try:
        client = anthropic.Anthropic()

        system_prompt = """You are a Python code generator for KIA (Kuwait Investment Authority) training exercises.
Your task is to generate ONLY executable Python code based on the user's prompt.

IMPORTANT RULES:
1. Output ONLY the Python code - no explanations, no markdown, no code blocks
2. The code must be self-contained and print its output
3. Start with the given data variables exactly as provided
4. Follow the user's instructions precisely
5. Use proper formatting for currency (commas, 2 decimal places)
6. The code should run without any imports (basic Python only)

Generate clean, working Python code that produces the expected output format."""

        user_message = f"""Challenge Context:
{challenge_context}

Given Data (use these exact variable names and values):
{given_data}

User's Prompt:
{prompt}

Generate the Python code:"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extract the code from the response
        code = message.content[0].text.strip()

        # Clean up any markdown code blocks if present
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]

        return {
            'success': True,
            'code': code.strip(),
            'error': None
        }

    except anthropic.APIError as e:
        return {
            'success': False,
            'code': None,
            'error': f"API Error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'code': None,
            'error': f"Error: {str(e)}"
        }


def evaluate_prompt_quality(prompt: str) -> dict:
    """Evaluate the quality of a prompt and return bonus points"""
    score = 0
    feedback = []

    # Check for clarity - uses numbered steps or bullet points
    if any(marker in prompt for marker in ['1.', '2.', '3.', '-', '*', '•']):
        score += 15
        feedback.append("Clear structure (+15)")

    # Check for specificity - mentions data types or format
    if any(word in prompt.lower() for word in ['float', 'int', 'string', 'decimal', 'format', ':.2f', 'comma']):
        score += 10
        feedback.append("Specifies formatting (+10)")

    # Check for examples in prompt
    if any(phrase in prompt.lower() for phrase in ['for example', 'e.g.', 'like this:', 'output:', 'such as']):
        score += 10
        feedback.append("Includes examples (+10)")

    # Check for conciseness (under 150 words is good)
    word_count = len(prompt.split())
    if word_count < 50:
        score += 15
        feedback.append("Very concise (+15)")
    elif word_count < 100:
        score += 10
        feedback.append("Concise (+10)")
    elif word_count < 150:
        score += 5
        feedback.append("Reasonably concise (+5)")

    return {
        'bonus_points': score,
        'feedback': feedback,
        'word_count': word_count
    }


# ============ AI PROMPT CHALLENGE ROUTES ============

@app.route('/prompt-trainer')
def prompt_trainer_dashboard():
    """Trainer dashboard for the AI Prompt Challenge"""
    if os.environ.get('RENDER'):
        render_url = os.environ.get('RENDER_EXTERNAL_URL', request.host_url.rstrip('/'))
        join_url = f"{render_url}/prompt-join"
    else:
        local_ip = get_local_ip()
        port = request.host.split(':')[-1] if ':' in request.host else '8080'
        join_url = f"http://{local_ip}:{port}/prompt-join"

    qr_code = generate_qr_code(join_url)

    return render_template('prompt_trainer.html',
                          qr_code=qr_code,
                          join_url=join_url,
                          teams=prompt_game_state['teams'],
                          current_round=prompt_game_state['current_round'],
                          total_rounds=len(PROMPT_CHALLENGES),
                          challenges=PROMPT_CHALLENGES)


@app.route('/prompt-join', methods=['GET', 'POST'])
def prompt_join_game():
    """Team registration for AI Prompt Challenge"""
    if request.method == 'POST':
        team_name = request.form.get('team_name', '').strip()
        if team_name:
            team_id = generate_team_id()
            prompt_game_state['teams'][team_id] = {
                'name': team_name,
                'score': 0,
                'attempts': {},  # challenge_id: {attempts, best_score}
                'joined_at': datetime.now().isoformat()
            }
            session['prompt_team_id'] = team_id
            session['prompt_team_name'] = team_name

            # Notify trainer dashboard
            socketio.emit('prompt_team_joined', {
                'team_id': team_id,
                'team_name': team_name,
                'score': 0
            }, room='prompt_trainer')

            return redirect(url_for('prompt_play'))

    return render_template('prompt_join.html')


@app.route('/prompt-play')
def prompt_play():
    """Main game interface for AI Prompt Challenge"""
    team_id = session.get('prompt_team_id')
    if not team_id or team_id not in prompt_game_state['teams']:
        return redirect(url_for('prompt_join_game'))

    team = prompt_game_state['teams'][team_id]
    return render_template('prompt_game.html',
                          team_id=team_id,
                          team_name=team['name'],
                          score=team['score'],
                          challenges=PROMPT_CHALLENGES,
                          current_round=prompt_game_state['current_round'],
                          game_started=prompt_game_state['game_started'])


@app.route('/api/prompt/generate', methods=['POST'])
def api_generate_code():
    """Generate code from user prompt using Claude API"""
    team_id = session.get('prompt_team_id')
    if not team_id or team_id not in prompt_game_state['teams']:
        return jsonify({'error': 'Not registered'}), 401

    data = request.json
    prompt = data.get('prompt', '')
    challenge_id = data.get('challenge_id', '')

    if not prompt or not challenge_id:
        return jsonify({'error': 'Missing prompt or challenge_id'}), 400

    # Find the challenge
    round_num = int(challenge_id[1])  # P1.1 -> 1
    challenge = None
    for c in PROMPT_CHALLENGES.get(round_num, {}).get('challenges', []):
        if c['id'] == challenge_id:
            challenge = c
            break

    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404

    # Generate code using Claude
    result = generate_code_from_prompt(
        prompt=prompt,
        challenge_context=challenge['scenario'],
        given_data=challenge['given_data']
    )

    if result['success']:
        # Evaluate prompt quality
        quality = evaluate_prompt_quality(prompt)
        result['prompt_quality'] = quality

    return jsonify(result)


@app.route('/api/prompt/submit', methods=['POST'])
def api_submit_prompt_answer():
    """Submit and score a prompt challenge answer"""
    team_id = session.get('prompt_team_id')
    if not team_id or team_id not in prompt_game_state['teams']:
        return jsonify({'error': 'Not registered'}), 401

    data = request.json
    challenge_id = data.get('challenge_id', '')
    prompt = data.get('prompt', '')
    generated_code = data.get('generated_code', '')
    user_output = data.get('output', '')

    # Find the challenge
    round_num = int(challenge_id[1])
    challenge = None
    for c in PROMPT_CHALLENGES.get(round_num, {}).get('challenges', []):
        if c['id'] == challenge_id:
            challenge = c
            break

    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404

    # Check if already answered correctly
    team = prompt_game_state['teams'][team_id]
    existing = team['attempts'].get(challenge_id, {})
    if existing.get('correct'):
        return jsonify({
            'error': 'Already solved',
            'correct': True,
            'points_earned': 0,
            'total_score': team['score']
        })

    # Compare output
    is_correct = check_output_match(user_output, challenge['expected_output'])

    # Calculate points
    points_earned = 0
    prompt_bonus = 0

    if is_correct:
        base_points = challenge['points']

        # Evaluate prompt quality for bonus
        quality = evaluate_prompt_quality(prompt)
        prompt_bonus = quality['bonus_points']

        # Apply attempt penalty (if not first attempt)
        attempt_num = existing.get('attempts', 0) + 1
        if attempt_num == 1:
            points_earned = base_points + prompt_bonus
        elif attempt_num == 2:
            points_earned = int((base_points + prompt_bonus) * 0.75)
        else:
            points_earned = int((base_points + prompt_bonus) * 0.5)

        team['score'] += points_earned

    # Record attempt
    team['attempts'][challenge_id] = {
        'attempts': existing.get('attempts', 0) + 1,
        'correct': is_correct,
        'prompt': prompt,
        'code': generated_code,
        'output': user_output,
        'points': points_earned,
        'prompt_bonus': prompt_bonus,
        'timestamp': datetime.now().isoformat()
    }

    # Notify trainer
    socketio.emit('prompt_score_update', {
        'team_id': team_id,
        'team_name': team['name'],
        'score': team['score'],
        'challenge_id': challenge_id,
        'correct': is_correct,
        'points': points_earned
    }, room='prompt_trainer')

    return jsonify({
        'correct': is_correct,
        'points_earned': points_earned,
        'prompt_bonus': prompt_bonus,
        'total_score': team['score'],
        'expected_output': challenge['expected_output'] if not is_correct else None,
        'attempt_number': team['attempts'][challenge_id]['attempts']
    })


@app.route('/api/prompt/game_state')
def get_prompt_game_state():
    """Get current prompt game state"""
    team_id = session.get('prompt_team_id')
    team_score = 0
    team_attempts = {}

    if team_id and team_id in prompt_game_state['teams']:
        team_score = prompt_game_state['teams'][team_id]['score']
        team_attempts = prompt_game_state['teams'][team_id]['attempts']

    # Calculate remaining time
    time_remaining = 180  # Default 3 minutes
    if prompt_game_state['current_round'] in PROMPT_CHALLENGES:
        time_limit = PROMPT_CHALLENGES[prompt_game_state['current_round']].get('time_limit', 180)
        if prompt_game_state['round_start_time'] and prompt_game_state['game_started']:
            elapsed = (datetime.now() - prompt_game_state['round_start_time']).seconds
            time_remaining = max(0, time_limit - elapsed)
        else:
            time_remaining = time_limit

    return jsonify({
        'current_round': prompt_game_state['current_round'],
        'game_started': prompt_game_state['game_started'],
        'game_paused': prompt_game_state['game_paused'],
        'game_mode': prompt_game_state['game_mode'],
        'your_score': team_score,
        'your_attempts': team_attempts,
        'time_remaining': time_remaining
    })


@app.route('/api/prompt/trainer/start_round', methods=['POST'])
def prompt_start_round():
    """Trainer starts a new round in prompt challenge"""
    round_num = request.json.get('round', 1)
    prompt_game_state['current_round'] = round_num
    prompt_game_state['game_started'] = True
    prompt_game_state['game_paused'] = False
    prompt_game_state['round_start_time'] = datetime.now()

    round_data = PROMPT_CHALLENGES.get(round_num, {})

    socketio.emit('prompt_round_started', {
        'round': round_num,
        'title': round_data.get('title', ''),
        'theme': round_data.get('theme', ''),
        'time_limit': round_data.get('time_limit', 180)
    })

    return jsonify({'success': True, 'round': round_num})


@app.route('/api/prompt/trainer/pause', methods=['POST'])
def prompt_pause_game():
    """Trainer pauses/resumes the prompt game"""
    prompt_game_state['game_paused'] = not prompt_game_state['game_paused']

    socketio.emit('prompt_game_paused', {
        'paused': prompt_game_state['game_paused']
    })

    return jsonify({'success': True, 'paused': prompt_game_state['game_paused']})


@app.route('/api/prompt/trainer/reset', methods=['POST'])
def prompt_reset_game():
    """Trainer resets the prompt game"""
    prompt_game_state['teams'] = {}
    prompt_game_state['current_round'] = 0
    prompt_game_state['game_started'] = False
    prompt_game_state['game_paused'] = False
    prompt_game_state['round_start_time'] = None

    socketio.emit('prompt_game_reset', {})

    return jsonify({'success': True})


@app.route('/api/prompt/trainer/teams')
def get_prompt_teams():
    """Get all teams and scores for prompt game trainer"""
    teams_list = []
    for team_id, team_data in prompt_game_state['teams'].items():
        teams_list.append({
            'id': team_id,
            'name': team_data['name'],
            'score': team_data['score'],
            'attempts': team_data['attempts']
        })

    teams_list.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({
        'teams': teams_list,
        'current_round': prompt_game_state['current_round'],
        'game_started': prompt_game_state['game_started']
    })


# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    pass


@socketio.on('join_trainer')
def handle_trainer_join():
    """Trainer joins their room for updates"""
    join_room('trainer')
    game_state['trainer_connected'] = True
    emit('connected', {'status': 'Trainer connected'})


@socketio.on('join_team_room')
def handle_team_join(data):
    """Team joins their room for updates"""
    team_id = data.get('team_id')
    if team_id:
        join_room(f'team_{team_id}')
        emit('connected', {'status': 'Team connected'})


@socketio.on('join_prompt_trainer')
def handle_prompt_trainer_join():
    """Prompt game trainer joins their room"""
    join_room('prompt_trainer')
    prompt_game_state['trainer_connected'] = True
    emit('connected', {'status': 'Prompt trainer connected'})


@socketio.on('join_prompt_team')
def handle_prompt_team_join(data):
    """Prompt game team joins their room"""
    team_id = data.get('team_id')
    if team_id:
        join_room(f'prompt_team_{team_id}')
        emit('connected', {'status': 'Prompt team connected'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
