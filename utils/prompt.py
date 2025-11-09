SEARCH_AGENT_OUTPUT: str = """
# News Analysis Report: {ticker}

**Headline:** {A 1-sentence summary of the single most critical recent news item.}

**Key Developments:**
* **[{timeframe}]:** {News item 1 and its immediate context.}
* **[{timeframe}]:** {News item 2 and its immediate context.}
* **[{timeframe}]:** {News item 3, if relevant.}

**Analytical Insight:**
{A 1-2 sentence analysis of *what this news means* for the stock. Is it a short-term catalyst? Does it change the long-term thesis? Does it confirm or contradict the technicals? This is the "so what?"}

_Note: If search results are limited, state that. Searched using company name + keywords._
"""

SENTIMENT_AGENT_OUTPUT: str = """
# Sentiment Analysis: {ticker}

**Overall Sentiment:** {Bullish | Bearish | Neutral}

**Sentiment Drivers:**
* **Social Media (Reddit/X):** {General theme, e.g., "High volume of discussion, primarily positive around {feature}." or "Fear/uncertainty dominates threads."}
* **News Headlines:** {General theme, e.g., "Recent press coverage is predominantly negative, focusing on {topic}."}

**Analytical Insight:**
{1-2 sentences on what this sentiment implies. e.g., "The high social media hype suggests a potential for a short-term, volatile rally, even as news sentiment remains cautious." or "The overwhelming bearishness indicates high fear, which could be a contrarian 'buy' signal if fundamentals are strong."}

_Note: If data for a source is unavailable (e.g., limited Reddit coverage for Indian stocks), state it._
"""

FINANCE_AGENT_OUTPUT: str = """
# Technical Analysis: {ticker}

**Current Price:** {currency_symbol}{price}
**Technical Outlook:** {Bullish | Bearish | Neutral / Consolidating}

**Key Indicator Summary:**
* **Trend:** {Price is currently trading {above/below} the {50/200}-day moving average, indicating a {long-term/short-term} {uptrend/downtrend}.}
* **Momentum:** {RSI is at {value}, suggesting {oversold/overbought/neutral} conditions. MACD is {bullishly/bearishly} crossed.}
* **Key Levels to Watch:**
    * **Support (Floor):** {currency_symbol}{support1}, {currency_symbol}{support2}
    * **Resistance (Ceiling):** {currency_symbol}{resistance1}, {currency_symbol}{resistance2}

**Analytical Insight:**
{1-2 sentences combining the indicators. e.g., "The stock is in a clear uptrend but is currently overbought (RSI > 70), suggesting a short-term pullback to support at {currency_symbol}{support1} is possible before continuing higher."}

_Note: If any indicator data is missing, state which one._
"""

ADVISOR_AGENT_OUTPUT: str = """
# Strategy & Trade Plan: {ticker}

**Recommended Strategy:** {Strategy Name, e.g., "SMA Crossover" or "Buy & Hold"}
**Strategy Rationale:** {This strategy was selected based on {backtest performance / user risk profile}, showing a {X}% annual return with a max loss of {X}% during the {period} backtest.}

**Proposed Trade Parameters:**
* **Action:** {BUY | SELL | WAIT}
* **Timeline:** {Short-term (weeks) | Medium-term (months) | Long-term (years)}
* **Entry Range:** {currency_symbol}{lower_range} - {currency_symbol}{upper_range}
* **Stop-Loss Target:** {currency_symbol}{stop_loss_price} (e.g., ~{X}% below entry)
* **Profit Target 1:** {currency_symbol}{take_profit_price_1}
* **Position Size:** {Recommend {N} shares, totaling {currency_symbol}{total_investment} ({X}% of portfolio)}

**Analytical Insight:**
{1-2 sentences on *why* this trade makes sense *now*. e.g., "This trade plan aims to capture the new uptrend identified by the technical agent, while the stop-loss protects against a failure at the {currency_symbol}{resistance} level."}

_Note: All parameters are based on backtesting and current market conditions. They are not guaranteed._
"""

TEAM_CONVERSATIONAL_OUTPUT: str = """
# {Reflect the user's question, e.g., "Analysis of {Ticker}" or "Strategy for {Query}"}

## The Verdict: **{Decision: BUY | SELL | HOLD}**

**Current Stance:**
{1-2 concise, non-robotic sentences that *directly* address the user's question, synthesizing the key findings. Example: "While {Ticker} shows strong technical momentum, recent negative news and bearish market sentiment suggest a high-risk entry. We recommend holding for now." or "This appears to be a solid buying opportunity, as the technicals are bullish, and recent news provides a clear positive catalyst."}

---

## Core Rationale (The Agents' Consensus)

| Factor | Signal | Key Finding |
|---|---|---|
| **Technical Analysis** | {Technical Outlook: Bullish/Bearish} | {1-sentence summary from Finance Agent, e.g., "Price is overbought, nearing major resistance at {currency_symbol}{X}."} |
| **Market Sentiment** | {Overall Sentiment: Bullish/Bearish} | {1-sentence summary from Sentiment Agent, e.g., "Social media hype is high, but news remains cautious."} |
| **News & Catalysts** | {Impact: Positive/Negative/Neutral} | {1-sentence summary from Search Agent, e.g., "Upcoming {event} is a major catalyst."} |
| **Strategy Backtest** | {Strategy: {Strategy Name}} | {1-sentence summary from Advisor Agent, e.g., "Backtest favors a mean-reversion strategy."} |

---

## Recommended Action Plan

{This section provides the clear, "leads to somewhere" advice.}

**If the Verdict is BUY or SELL:**
* **Action:** {BUY/SELL} {Ticker}
* **Entry Range:** {e.g., Wait for a dip to {currency_symbol}{X} or buy at market price.}
* **Stop-Loss:** {Set a stop-loss at {currency_symbol}{stop_loss_price} to manage risk.}
* **Profit Target:** {Look to take initial profits near {currency_symbol}{take_profit_price_1}.}
* **Timeline:** {Short-term / Medium-term}

**If the Verdict is HOLD:**
* **Monitor:** Keep a close watch on the **{currency_symbol}{key_level}** support/resistance level.
* **Trigger:** {A {break above/drop below} this level would be a new {buy/sell} signal.}
* **Next Catalyst:** {Pay attention to the {event} on {date}.}

---

## Key Risks & Conflicting Signals
* **Primary Conflict:** {Identify the main conflict, e.g., "Technicals are bullish, but fundamentals from recent news are weak."}
* **Market Context:** {e.g., "The overall market is in a 'fear' state (VIX: {value}), so all long positions have elevated risk."}
* _{Any other critical risk or missing data point from an agent.}_
"""
