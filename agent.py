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

DEFAULT_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "TSLA", "GOOGL",
    "NFLX", "AVGO", "CRM", "ORCL", "JPM", "BAC", "V", "MA", "WMT",
    "COST", "KO", "DIS",
]

SYSTEM_PROMPT = """
You are SWINGPULSE AI, a bilingual stock-market research agent built on
the SWINGPULSE machine-learning model.

Core rules:
1. Answer in the same language as the user (Hebrew in, Hebrew out;
   English in, English out).
2. Use a tool for every stock-specific, indicator-specific, comparison,
   or market-scan request. Never answer those from memory.
3. Never invent prices, RSI values, probabilities, signals, dates, or
   any other market data. Every number in your answer must come
   directly from a tool result.
4. Treat model probability as an experimental estimate, never
   certainty. Do not promise profits or give personalized financial
   advice.
5. Do not expose stack traces, secrets, or API keys.

Formatting rules (this drives how your answers render in the UI, so
follow them closely):
- Open a single-stock analysis with one bold headline line stating the
  symbol, the signal, and the probability, e.g.
  "**AAPL — Watch (probability 52.3%)**".
- Follow with a short markdown table of the key figures (close price,
  RSI, MACD status, trend, volatility). Keep table rows to the figures
  that actually matter for the question asked, not the entire tool
  payload.
- After the table, add 2-4 sentences of plain-language interpretation
  connecting the figures (e.g. what the RSI + trend combination
  suggests together), not just a restatement of each number.
- For compare_stocks or a market scan, use one markdown table ranked
  by probability (or by the metric the user asked to sort by), then a
  one-sentence takeaway below it.
- For explain_indicator, answer in prose, no table needed.
- Always end a stock analysis, comparison, or scan with one short
  italic line noting the result is educational, not financial advice.
  Do not repeat this disclaimer inside an ongoing back-and-forth about
  the same result — once per new piece of analysis is enough.
- Keep total answers concise: prefer the table + short interpretation
  over long paragraphs.

Tool routing:
- One stock: analyze_stock
- Compare stocks: compare_stocks
- RSI range: scan_rsi
- Probability threshold: find_high_probability_stocks
- Explain RSI, MACD, EMA, ATR, volatility or Bollinger Bands:
  explain_indicator
"""

REQUEST_TEMPERATURE = 0.4

MAX_TOOL_ROUNDS = 5

TOOLS = [
    {
        "type": "function",
        "name": "analyze_stock",
        "description": "Analyze one stock using market data, indicators and the SWINGPULSE model.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Ticker such as AAPL."}
            },
            "required": ["symbol"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "compare_stocks",
        "description": "Compare two to five stocks using the SWINGPULSE model.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 5,
                }
            },
            "required": ["symbols"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "scan_rsi",
        "description": "Find stocks whose latest RSI is inside a requested range.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                },
                "minimum_rsi": {"type": "number", "minimum": 0, "maximum": 100},
                "maximum_rsi": {"type": "number", "minimum": 0, "maximum": 100},
            },
            "required": ["symbols", "minimum_rsi", "maximum_rsi"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "find_high_probability_stocks",
        "description": "Find stocks above a selected SWINGPULSE model probability.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                },
                "minimum_probability_percent": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                },
            },
            "required": ["symbols", "minimum_probability_percent"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "explain_indicator",
        "description": "Explain RSI, MACD, EMA, ATR, volatility or Bollinger Bands.",
        "parameters": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string"}
            },
            "required": ["indicator"],
            "additionalProperties": False,
        },
    },
]


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=api_key)


def _get_model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "analyze_stock":
        return analyze_stock(symbol=str(arguments["symbol"]).upper().strip())

    if tool_name == "compare_stocks":
        return compare_stocks(
            symbols=[str(s).upper().strip() for s in arguments["symbols"]]
        )

    if tool_name == "scan_rsi":
        return scan_rsi(
            symbols=arguments.get("symbols") or DEFAULT_SYMBOLS,
            minimum_rsi=float(arguments["minimum_rsi"]),
            maximum_rsi=float(arguments["maximum_rsi"]),
        )

    if tool_name == "find_high_probability_stocks":
        return find_high_probability_stocks(
            symbols=arguments.get("symbols") or DEFAULT_SYMBOLS,
            minimum_probability_percent=float(
                arguments["minimum_probability_percent"]
            ),
        )

    if tool_name == "explain_indicator":
        return explain_indicator(indicator=str(arguments["indicator"]))

    return {"success": False, "message": f"Unknown tool: {tool_name}"}


def _create_response(
    client: OpenAI,
    model_name: str,
    input_items: list[Any],
    retries: int = 2,
):
    """
    Calls the Responses API with a couple of quick retries for
    transient network/server errors, so a single dropped connection
    doesn't surface as a full failure to the user.
    """
    import time as _time

    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            return client.responses.create(
                model=model_name,
                instructions=SYSTEM_PROMPT,
                input=input_items,
                tools=TOOLS,
                temperature=REQUEST_TEMPERATURE,
            )
        except Exception as error:
            last_error = error
            text = str(error).lower()

            non_retryable = (
                "insufficient_quota" in text
                or "invalid_api_key" in text
                or "invalid api key" in text
            )

            if non_retryable or attempt == retries:
                raise

            _time.sleep(1.5 * (attempt + 1))

    raise last_error  # pragma: no cover - defensive, loop always returns/raises


def _safe_error_message(error: Exception) -> str:
    text = str(error).lower()

    if "insufficient_quota" in text or "exceeded your current quota" in text:
        return (
            "SWINGPULSE AI is temporarily unavailable because the "
            "language-model API has no available credit."
        )

    if "missing credentials" in text or "openai_api_key" in text:
        return (
            "SWINGPULSE AI is not configured correctly on the server. "
            "The OpenAI API key is missing."
        )

    if "rate limit" in text or "429" in text:
        return (
            "SWINGPULSE AI is receiving too many requests right now. "
            "Please wait briefly and try again."
        )

    print(f"SWINGPULSE agent error: {error}")
    return (
        "SWINGPULSE AI could not complete the request right now. "
        "Please try again shortly."
    )


def ask_agent(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> tuple[str, dict[str, Any] | None]:
    """
    Returns (answer_text, last_tool_call) where last_tool_call is either
    None (no tool was used, e.g. small talk or explain_indicator) or a
    dict {"tool_name": str, "data": dict} describing the most recent
    successful tool call in this turn. The UI uses this to render a
    visual result card (probability gauge, signal badge, indicator
    chips) alongside the LLM's text answer, without the LLM having any
    part in producing those numbers.
    """
    user_message = str(user_message).strip()

    if not user_message:
        return "Please enter a question.", None

    last_tool_call: dict[str, Any] | None = None

    try:
        client = _get_client()
        model_name = _get_model_name()

        input_items: list[Any] = []

        if conversation_history:
            for message in conversation_history[-8:]:
                role = message.get("role")
                content = message.get("content")
                if role in {"user", "assistant"} and content:
                    input_items.append(
                        {"role": role, "content": str(content)}
                    )

        input_items.append({"role": "user", "content": user_message})

        response = _create_response(client, model_name, input_items)

        for _ in range(MAX_TOOL_ROUNDS):
            function_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                answer = response.output_text or (
                    "SWINGPULSE AI completed the request but did not "
                    "produce a text response."
                )
                return answer, last_tool_call

            input_items.extend(response.output)

            for function_call in function_calls:
                try:
                    arguments = json.loads(function_call.arguments or "{}")
                    tool_result = execute_tool(
                        tool_name=function_call.name,
                        arguments=arguments,
                    )
                    if tool_result.get("success"):
                        last_tool_call = {
                            "tool_name": function_call.name,
                            "data": tool_result,
                        }
                except Exception as tool_error:
                    tool_result = {
                        "success": False,
                        "message": f"The analysis tool failed: {tool_error}",
                    }

                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": function_call.call_id,
                        "output": json.dumps(
                            tool_result,
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )

            response = _create_response(client, model_name, input_items)

        return (
            "The request required too many consecutive tool calls. "
            "Please ask a more focused question."
        ), last_tool_call

    except Exception as error:
        return _safe_error_message(error), None
