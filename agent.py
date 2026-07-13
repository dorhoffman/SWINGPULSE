from openai import OpenAI
import os

from tools import (
    analyze_stock,
    compare_stocks,
    scan_rsi,
    explain_indicator,
    find_high_probability_stocks,
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


SYSTEM_PROMPT = """
You are SWINGPULSE AI.

You are an AI swing trading assistant.

Always use the available tools whenever the user asks about:

- stocks
- RSI
- MACD
- EMA
- comparisons
- market analysis
- probabilities
- technical indicators

Never invent stock prices.

Never invent probabilities.

Always rely on tool outputs.

After receiving the tool output,
explain it clearly in simple English.
"""
def ask_agent(user_message: str):

    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
    )

    return response.output_text
