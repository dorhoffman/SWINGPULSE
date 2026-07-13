from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from tools import (
    analyze_stock,
    compare_stocks,
    explain_indicator,
    find_high_probability_stocks,
    scan_rsi,
)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# רשימה ראשונית לסריקות כאשר המשתמש לא מציין מניות מסוימות.
DEFAULT_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "META",
    "AMZN",
    "TSLA",
    "GOOGL",
    "NFLX",
    "AVGO",
    "CRM",
    "ORCL",
    "JPM",
    "BAC",
    "V",
    "MA",
    "WMT",
    "COST",
    "KO",
    "DIS",
]


SYSTEM_PROMPT = """
You are SWINGPULSE AI, an AI swing-trading research assistant.

Your responsibilities:
1. Understand natural-language questions in English or Hebrew.
2. Use the available tools for live stock analysis.
3. Never invent prices, RSI values, probabilities, signals or market data.
4. Base every stock-specific answer on tool output.
5. Clearly distinguish model probability from certainty.
6. Do not give guaranteed profit claims or personalized financial advice.
7. Answer in the same language as the user.
8. Keep explanations clear and practical.

When the user asks:
- To analyze one stock: use analyze_stock.
- To compare stocks: use compare_stocks.
- For stocks around RSI 30: use scan_rsi.
- For high model probability: use find_high_probability_stocks.
- About RSI, MACD, EMA, ATR, volatility or Bollinger Bands:
  use explain_indicator.

When a market scan does not include a list of symbols,
use the default symbols supplied by the application.

Always mention that the result is educational and not financial advice.
"""


TOOLS = [
    {
        "type": "function",
        "name": "analyze_stock",
        "description": (
            "Analyze one stock using live market data, technical indicators "
            "and the trained SWINGPULSE machine-learning model."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker, for example AAPL or NVDA.",
                }
            },
            "required": ["symbol"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "compare_stocks",
        "description": (
            "Compare between two and five stocks and rank them "
            "by SWINGPULSE model probability."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "A list containing between two and five stock tickers."
                    ),
                }
            },
            "required": ["symbols"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "scan_rsi",
        "description": (
            "Scan stocks and find those whose latest RSI is inside "
            "a requested range. Use this for questions such as "
            "'find stocks close to RSI 30'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": (
                        "Stock symbols to scan. Use null when the user "
                        "does not provide a list."
                    ),
                },
                "minimum_rsi": {
                    "type": "number",
                    "description": "Minimum RSI value, from 0 to 100.",
                },
                "maximum_rsi": {
                    "type": "number",
                    "description": "Maximum RSI value, from 0 to 100.",
                },
            },
            "required": [
                "symbols",
                "minimum_rsi",
                "maximum_rsi",
            ],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "find_high_probability_stocks",
        "description": (
            "Find stocks whose SWINGPULSE model probability is above "
            "a selected percentage."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": (
                        "Stock symbols to scan. Use null when the user "
                        "does not provide a list."
                    ),
                },
                "minimum_probability_percent": {
                    "type": "number",
                    "description": (
                        "Minimum model probability as a percentage, "
                        "for example 45."
                    ),
                },
            },
            "required": [
                "symbols",
                "minimum_probability_percent",
            ],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "explain_indicator",
        "description": (
            "Explain a technical indicator such as RSI, MACD, EMA, "
            "ATR, volatility or Bollinger Bands."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "indicator": {
                    "type": "string",
                    "description": "The technical indicator to explain.",
                }
            },
            "required": ["indicator"],
            "additionalProperties": False,
        },
    },
]


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute the local SWINGPULSE tool selected by OpenAI.
    """

    if tool_name == "analyze_stock":
        return analyze_stock(
            symbol=arguments["symbol"]
        )

    if tool_name == "compare_stocks":
        return compare_stocks(
            symbols=arguments["symbols"]
        )

    if tool_name == "scan_rsi":
        symbols = arguments.get("symbols")

        if not symbols:
            symbols = DEFAULT_SYMBOLS

        return scan_rsi(
            symbols=symbols,
            minimum_rsi=float(
                arguments["minimum_rsi"]
            ),
            maximum_rsi=float(
                arguments["maximum_rsi"]
            ),
        )

    if tool_name == "find_high_probability_stocks":
        symbols = arguments.get("symbols")

        if not symbols:
            symbols = DEFAULT_SYMBOLS

        return find_high_probability_stocks(
            symbols=symbols,
            minimum_probability_percent=float(
                arguments[
                    "minimum_probability_percent"
                ]
            ),
        )

    if tool_name == "explain_indicator":
        return explain_indicator(
            indicator=arguments["indicator"]
        )

    return {
        "success": False,
        "message": f"Unknown tool: {tool_name}",
    }


def ask_agent(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """
    Send a user message to SWINGPULSE AI.

    The model may select one or more tools.
    Tool results are returned to the model so it can prepare
    the final natural-language response.
    """

    if not os.getenv("OPENAI_API_KEY"):
        return (
            "OPENAI_API_KEY is not configured in Render."
        )

    user_message = str(user_message).strip()

    if not user_message:
        return "Please enter a question."

    input_items: list[Any] = []

    if conversation_history:
        for message in conversation_history[-8:]:
            role = message.get("role")
            content = message.get("content")

            if role in {"user", "assistant"} and content:
                input_items.append({
                    "role": role,
                    "content": content,
                })

    input_items.append({
        "role": "user",
        "content": user_message,
    })

    try:
        response = client.responses.create(
            model="gpt-5.6",
            instructions=SYSTEM_PROMPT,
            input=input_items,
            tools=TOOLS,
        )

        # ייתכן שהמודל יבקש מספר כלים ברצף.
        for _ in range(5):
            function_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                return response.output_text

            # מוסיפים את פלט המודל לרצף השיחה.
            input_items.extend(response.output)

            for function_call in function_calls:
                try:
                    arguments = json.loads(
                        function_call.arguments
                    )

                    tool_result = execute_tool(
                        tool_name=function_call.name,
                        arguments=arguments,
                    )

                except Exception as error:
                    tool_result = {
                        "success": False,
                        "message": str(error),
                    }

                input_items.append({
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                        default=str,
                    ),
                })

            response = client.responses.create(
                model="gpt-4.1-mini"
                instructions=SYSTEM_PROMPT,
                input=input_items,
                tools=TOOLS,
            )

        return (
            "The agent reached the maximum number of tool calls. "
            "Please try a more focused question."
        )

    except Exception as error:
        return (
            "SWINGPULSE AI could not complete the request. "
            f"Error: {error}"
        )
