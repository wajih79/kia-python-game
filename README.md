# KIA Python Trading Challenge

A web-based interactive game for teaching Python to financial professionals at Kuwait Investment Authority.

## Features

- **QR Code Registration**: Teams scan to join instantly
- **Real-time Scoring**: Live score updates via WebSocket
- **Trainer Dashboard**: Control game flow, view all team scores
- **Team Interface**: Answer Python challenges, see only your score
- **5 Rounds**: Progressive difficulty covering Python fundamentals

## Quick Deploy to Render

1. Push this folder to a GitHub repository
2. Go to [render.com](https://render.com) and sign up
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Render will auto-detect the configuration
6. Click "Create Web Service"

Your game will be live at `https://your-app-name.onrender.com`

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open http://localhost:5000
```

## How to Use

### As Trainer:
1. Open `/trainer` on your device
2. Display the QR code on projector
3. Wait for teams to join
4. Click round buttons to start each round
5. Watch live scores update

### As Team:
1. Scan QR code or visit the join URL
2. Enter team name
3. Wait for trainer to start the game
4. Answer questions as fast as possible
5. See your score update in real-time

## Game Structure

| Round | Topic | Theme |
|-------|-------|-------|
| 1 | Variables & Math | Portfolio Returns |
| 2 | Data Types & Strings | Investment Reports |
| 3 | Lists | Stock Portfolios |
| 4 | Conditionals | Buy/Sell Decisions |
| 5 | Loops & Functions | Asset Analysis |

## Scoring

- Correct answer: 100 points
- Bonus questions: 50 points
- Boss challenge: 150 points
