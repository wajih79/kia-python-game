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
    # Strip whitespace, normalize line endings
    return re.sub(r'\s+', ' ', str(output).strip()).lower()


def check_output_match(user_output, expected_output):
    """Check if user output matches expected output (flexible matching)"""
    user_norm = normalize_output(user_output)
    expected_norm = normalize_output(expected_output)

    # Exact match after normalization
    if user_norm == expected_norm:
        return True

    # Check if outputs contain the same key numbers
    user_numbers = re.findall(r'[\d,]+\.?\d*', user_output or '')
    expected_numbers = re.findall(r'[\d,]+\.?\d*', expected_output or '')

    if user_numbers and expected_numbers:
        # Compare all significant numbers
        try:
            # Get the main number (usually the last/largest one)
            user_val = float(user_numbers[-1].replace(',', '').rstrip('.'))
            expected_val = float(expected_numbers[-1].replace(',', '').rstrip('.'))
            if abs(user_val - expected_val) < 1:  # Allow small differences
                return True
        except:
            pass

    # Also try simple substring match for the key value
    # Extract just the number portion and compare
    user_clean = re.sub(r'[^\d.]', '', user_output or '')
    expected_clean = re.sub(r'[^\d.]', '', expected_output or '')

    if user_clean and expected_clean:
        try:
            if abs(float(user_clean) - float(expected_clean)) < 1:
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
