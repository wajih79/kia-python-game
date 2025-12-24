# AI Prompt Challenge - Game Design Document

## Overview

**AI Prompt Challenge** is a new game mode that trains KIA professionals to write effective prompts for AI-assisted Python code generation. Players compete to craft the best prompts that result in working, high-quality Python code for real-world KIA business scenarios.

---

## Game Concept

### The Core Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📋 SCENARIO    →   ✍️ PROMPT    →   🤖 AI GENERATES   →   ⚡ EXECUTE   →   🏆 SCORE   │
│   (KIA Problem)      (Player)         (Python Code)         (Validate)      (Results)  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

1. **Scenario Presented**: A KIA-related business problem is displayed
2. **Prompt Writing**: Teams write a prompt to instruct an AI to generate Python code
3. **AI Generation**: The prompt is sent to Claude/GPT, which generates Python code
4. **Code Execution**: The generated code is executed in Pyodide
5. **Validation & Scoring**: Output is compared, and scores are calculated

---

## Game Modes

### Mode 1: Speed Challenge (Recommended for Training)
- **Time Limit**: 3 minutes per challenge
- **Objective**: Write a prompt that produces working code as quickly as possible
- **Scoring**: Correct output + time bonus + code quality bonus

### Mode 2: Efficiency Challenge
- **Time Limit**: 5 minutes per challenge
- **Objective**: Write the shortest/clearest prompt that produces working code
- **Scoring**: Correct output + prompt brevity bonus + clarity score

### Mode 3: Debug & Refine
- **Time Limit**: 7 minutes per challenge
- **Objective**: Iteratively improve prompts based on AI output
- **Attempts**: Up to 3 prompt submissions allowed
- **Scoring**: First attempt bonus, decreasing points per retry

---

## Scoring System

### Base Points
| Result | Points |
|--------|--------|
| Correct Output | 100 pts |
| Partial Match (80%+) | 60 pts |
| Code Runs (Wrong Output) | 20 pts |
| Code Fails to Run | 0 pts |

### Bonus Multipliers

**Time Bonus** (Speed Challenge):
- Under 1 minute: +50 pts
- Under 2 minutes: +30 pts
- Under 3 minutes: +10 pts

**Prompt Quality Bonus**:
- Clear structure (uses bullet points/numbered steps): +15 pts
- Includes input/output examples: +10 pts
- Specifies data types explicitly: +10 pts
- Under 100 words (concise): +15 pts

**Code Quality Bonus** (AI-generated code):
- Uses appropriate variable names: +5 pts
- Includes error handling: +10 pts
- Follows PEP 8 style: +5 pts
- Has comments/docstrings: +5 pts

---

## Round Structure

### Round 1: Basics - Variable & Calculation Prompts
**Theme**: Portfolio Calculations

| Challenge | Scenario | Difficulty |
|-----------|----------|------------|
| 1.1 | Calculate investment returns | Easy |
| 1.2 | Format currency output | Easy |
| 1.3 (Bonus) | Multi-currency conversion | Medium |

### Round 2: Data Handling Prompts
**Theme**: Asset Data Processing

| Challenge | Scenario | Difficulty |
|-----------|----------|------------|
| 2.1 | Parse and format stock data | Medium |
| 2.2 | Calculate portfolio weights | Medium |
| 2.3 (Bonus) | Generate investment report string | Medium |

### Round 3: List & Collection Prompts
**Theme**: Stock Portfolio Management

| Challenge | Scenario | Difficulty |
|-----------|----------|------------|
| 3.1 | Sort stocks by performance | Medium |
| 3.2 | Filter underperforming assets | Medium |
| 3.3 (Bonus) | Top N stocks by criteria | Hard |

### Round 4: Logic & Decision Prompts
**Theme**: Trading Decisions

| Challenge | Scenario | Difficulty |
|-----------|----------|------------|
| 4.1 | Buy/Sell/Hold recommendation | Hard |
| 4.2 | Risk assessment logic | Hard |
| 4.3 (Bonus) | Multi-factor decision tree | Hard |

### Round 5: Advanced - Function & Loop Prompts
**Theme**: Automated Analysis

| Challenge | Scenario | Difficulty |
|-----------|----------|------------|
| 5.1 | Portfolio summary function | Hard |
| 5.2 | Batch process multiple assets | Hard |
| 5.3 (Boss) | Full trading algorithm | Expert |

---

## KIA-Specific Challenge Scenarios

### Challenge Example 1.1: Investment Return Calculator

**Scenario Display**:
```
📊 PORTFOLIO RETURNS CALCULATOR

You need to calculate the profit from an investment.

Given Data:
- Initial Investment: $1,000,000
- Annual Return Rate: 8.5%
- Investment Period: 3 years (compound annually)

Required Output:
- Final value after 3 years
- Total profit made

Write a prompt that instructs an AI to generate Python code
that calculates and prints these values.
```

**Expected Output**:
```
Final Value: $1,277,289.13
Total Profit: $277,289.13
```

**Ideal Prompt Example**:
```
Write Python code that:
1. Starts with initial_investment = 1000000, rate = 0.085, years = 3
2. Calculates compound interest: final = initial * (1 + rate)^years
3. Calculates profit = final - initial
4. Prints "Final Value: $X" and "Total Profit: $X" with 2 decimal places
```

---

### Challenge Example 2.1: Stock Data Parser

**Scenario Display**:
```
📈 STOCK DATA FORMATTER

KIA receives daily stock data that needs formatting for reports.

Given Data (as string):
"AAPL:178.50,MSFT:378.25,GOOGL:141.80,AMZN:178.35"

Required Output:
- Parse the string into stock symbols and prices
- Print each stock on a new line as: "SYMBOL: $PRICE"
- Calculate and print the average price

Write a prompt to generate Python code for this task.
```

**Expected Output**:
```
AAPL: $178.50
MSFT: $378.25
GOOGL: $141.80
AMZN: $178.35
Average Price: $219.23
```

---

### Challenge Example 3.2: Portfolio Filter

**Scenario Display**:
```
📉 UNDERPERFORMING ASSET FILTER

KIA needs to identify assets that are underperforming.

Given Data:
stocks = [
    {"symbol": "AAPL", "return": 12.5},
    {"symbol": "TSLA", "return": -8.3},
    {"symbol": "MSFT", "return": 15.2},
    {"symbol": "META", "return": -3.1},
    {"symbol": "NVDA", "return": 45.8}
]

Criteria: An asset is "underperforming" if return < 0

Required Output:
- List all underperforming assets
- Show their symbols and returns

Write a prompt for AI to generate filtering code.
```

**Expected Output**:
```
Underperforming Assets:
TSLA: -8.3%
META: -3.1%
```

---

### Challenge Example 4.1: Trading Decision

**Scenario Display**:
```
💹 BUY/SELL/HOLD ADVISOR

Create logic for an automated trading recommendation.

Given Data:
current_price = 150.00
purchase_price = 120.00
target_gain = 0.20  # 20%
stop_loss = 0.10    # 10%

Rules:
- If current price >= purchase price * (1 + target_gain): SELL
- If current price <= purchase price * (1 - stop_loss): SELL (stop loss)
- Otherwise: HOLD

Required Output:
- Current gain/loss percentage
- Recommendation: BUY, SELL, or HOLD
- Reason for recommendation

Write a prompt for AI to implement this decision logic.
```

**Expected Output**:
```
Current Position: +25.00%
Recommendation: SELL
Reason: Target gain of 20% achieved
```

---

### Challenge Example 5.3 (Boss): Full Trading Algorithm

**Scenario Display**:
```
🏆 BOSS CHALLENGE: AUTOMATED PORTFOLIO ANALYZER

Create a complete portfolio analysis function.

Given Data:
portfolio = [
    {"symbol": "AAPL", "shares": 100, "purchase_price": 150, "current_price": 178},
    {"symbol": "MSFT", "shares": 50, "purchase_price": 350, "current_price": 378},
    {"symbol": "TSLA", "shares": 30, "purchase_price": 250, "current_price": 180},
    {"symbol": "NVDA", "shares": 25, "purchase_price": 400, "current_price": 875}
]

Requirements:
1. Calculate total portfolio value
2. Calculate total gain/loss for each position
3. Identify best and worst performers
4. Calculate overall portfolio return %
5. Generate a formatted summary report

Write a comprehensive prompt for this analysis.
```

---

## Prompt Quality Evaluation Criteria

### What Makes an Effective Prompt?

**1. Clarity (25%)**
- Clear statement of the goal
- Unambiguous instructions
- No room for misinterpretation

**2. Specificity (25%)**
- Exact variable names if needed
- Precise output format requirements
- Data types specified

**3. Structure (20%)**
- Logical order of steps
- Numbered or bulleted points
- Separation of input/processing/output

**4. Context (15%)**
- Relevant constraints mentioned
- Edge cases considered
- Domain context provided

**5. Conciseness (15%)**
- No unnecessary words
- Direct instructions
- Focused on essentials

---

## Prompt Tips Display (In-Game Help)

### Effective Prompt Strategies

```
┌────────────────────────────────────────────────────────────┐
│  💡 PROMPT WRITING TIPS                                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ✅ DO:                                                    │
│  • Start with "Write Python code that..."                  │
│  • Use numbered steps for multi-part tasks                 │
│  • Specify exact output format with examples               │
│  • Mention data types (int, float, list, dict)             │
│  • Include edge cases if relevant                          │
│                                                            │
│  ❌ DON'T:                                                 │
│  • Be vague: "make it work somehow"                        │
│  • Forget output format: "just print the result"           │
│  • Over-explain obvious things                             │
│  • Use ambiguous terms without definition                  │
│                                                            │
│  📝 EXAMPLE STRUCTURE:                                     │
│  "Write Python code that:                                  │
│   1. Takes [input description]                             │
│   2. Processes it by [specific operation]                  │
│   3. Prints output as: [exact format with example]"        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Technical Implementation

### New Components Required

```
app.py additions:
├── /api/ai/generate          # Send prompt to Claude API
├── /api/ai/validate          # Validate generated code
├── AI_CHALLENGES dictionary  # New challenge definitions
└── prompt_scoring()          # Evaluate prompt quality

templates/
├── prompt_game.html          # New game interface for prompts
└── prompt_trainer.html       # Trainer view for prompt game

config/
└── ai_config.py              # Claude API configuration
```

### API Flow

```
Team submits prompt
        ↓
POST /api/ai/generate
        ↓
Claude API generates Python code
        ↓
Code returned to client
        ↓
Pyodide executes code in browser
        ↓
Output compared to expected
        ↓
POST /api/submit_prompt_answer
        ↓
Score calculated & broadcasted
```

### Claude API Integration

```python
import anthropic

def generate_code_from_prompt(prompt: str, challenge_context: str) -> str:
    client = anthropic.Anthropic()

    system_prompt = """You are a Python code generator for KIA training.
    Generate ONLY executable Python code based on the user's prompt.
    Do not include explanations, just the code.
    The code should be self-contained and print its output."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Context: {challenge_context}\n\nPrompt: {prompt}"}
        ]
    )

    return extract_python_code(message.content)
```

---

## UI/UX Design

### Prompt Input Interface

```
┌─────────────────────────────────────────────────────────────┐
│  CHALLENGE 2.1: Stock Data Parser                    ⏱️ 4:32 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 SCENARIO                                                │
│  ─────────────────────────────────────────────────────────  │
│  KIA receives daily stock data: "AAPL:178.50,MSFT:378.25"   │
│  Parse and format it for the daily report.                  │
│                                                             │
│  📥 GIVEN DATA                                              │
│  data = "AAPL:178.50,MSFT:378.25,GOOGL:141.80"              │
│                                                             │
│  📤 EXPECTED OUTPUT                                         │
│  AAPL: $178.50                                              │
│  MSFT: $378.25                                              │
│  ...                                                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ✍️ YOUR PROMPT                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Write Python code that:                                 ││
│  │ 1. Parses the stock string by splitting on commas       ││
│  │ 2. For each stock, splits on ":" to get symbol & price  ││
│  │ 3. Prints each as "SYMBOL: $PRICE"                      ││
│  │ 4. Calculates and prints average price                  ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  [ 💡 Tips ]  [ 🚀 Generate Code ]  [ 📊 View Examples ]    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  🤖 AI GENERATED CODE                  [ ▶️ Run Code ]      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ data = "AAPL:178.50,MSFT:378.25,GOOGL:141.80"           ││
│  │ stocks = data.split(",")                                ││
│  │ total = 0                                               ││
│  │ for stock in stocks:                                    ││
│  │     symbol, price = stock.split(":")                    ││
│  │     price = float(price)                                ││
│  │     print(f"{symbol}: ${price:.2f}")                    ││
│  │     total += price                                      ││
│  │ print(f"Average: ${total/len(stocks):.2f}")             ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  📤 OUTPUT                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ AAPL: $178.50                                           ││
│  │ MSFT: $378.25                                           ││
│  │ GOOGL: $141.80                                          ││
│  │ Average: $232.85                                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  [ ✅ Submit Answer ]                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Gamification Elements

### Achievements

| Achievement | Criteria | Badge |
|-------------|----------|-------|
| First Try! | Correct on first prompt attempt | 🎯 |
| Speed Demon | Complete in under 1 minute | ⚡ |
| Wordsmith | Prompt under 50 words, correct result | ✨ |
| Perfect Round | All challenges correct in a round | 🏆 |
| Prompt Master | 5 challenges with quality bonus | 👑 |

### Leaderboard Display

```
┌─────────────────────────────────────────┐
│  🏆 LEADERBOARD                         │
├─────────────────────────────────────────┤
│  1. 🥇 Team Alpha       │ 485 pts       │
│  2. 🥈 Team Beta        │ 420 pts       │
│  3. 🥉 Team Gamma       │ 380 pts       │
│  4.    Team Delta       │ 290 pts       │
│  5.    Team Epsilon     │ 245 pts       │
└─────────────────────────────────────────┘
```

---

## Learning Outcomes

After completing the AI Prompt Challenge, participants will be able to:

1. **Write Clear Instructions**: Structure prompts that AI can understand and execute correctly
2. **Specify Requirements**: Include necessary details like data types, formats, and edge cases
3. **Iterate Effectively**: Refine prompts based on AI output to achieve desired results
4. **Understand AI Limitations**: Recognize when prompts are too vague or ambiguous
5. **Apply to Real Work**: Use prompt skills for actual KIA coding tasks with AI assistants

---

## Future Enhancements

### Phase 2 Features
- **Prompt History**: View and learn from past attempts
- **Peer Comparison**: See how others prompted for the same challenge
- **Custom Challenges**: Trainer can create new scenarios
- **Difficulty Scaling**: Adaptive difficulty based on team performance

### Phase 3 Features
- **Multi-Language**: Support for prompting in Arabic
- **Code Review Mode**: AI critiques the generated code
- **Collaborative Prompting**: Teams work together on complex prompts
- **Real API Integration**: Connect to actual KIA data systems

---

## Appendix: Full Challenge Set

### Round 1 Challenges (Complete)

**Challenge 1.1: Investment Return Calculator**
```python
# Context
initial_investment = 1000000
annual_rate = 0.085
years = 3

# Expected calculations
final_value = initial_investment * (1 + annual_rate) ** years
profit = final_value - initial_investment

# Expected output
# Final Value: $1,277,289.13
# Total Profit: $277,289.13
```

**Challenge 1.2: Currency Formatter**
```python
# Context
amount_usd = 5000000
exchange_rate_kwd = 0.31

# Expected calculations
amount_kwd = amount_usd * exchange_rate_kwd

# Expected output
# USD: $5,000,000.00
# KWD: KD 1,550,000.00
```

**Challenge 1.3 (Bonus): Multi-Currency Portfolio**
```python
# Context
portfolio = {
    "USD": 10000000,
    "EUR": 5000000,
    "GBP": 3000000
}
rates_to_kwd = {"USD": 0.31, "EUR": 0.34, "GBP": 0.39}

# Expected output
# Portfolio Value in KWD:
# USD: KD 3,100,000.00
# EUR: KD 1,700,000.00
# GBP: KD 1,170,000.00
# Total: KD 5,970,000.00
```

[Additional challenges defined in similar format...]

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Author: KIA Training Team*
