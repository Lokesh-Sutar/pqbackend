FINAL_OUTPUT_FORMAT: str = """
# 📊 Investment Analysis Report

**Tickers:** {list all}  
**Recommendation:** BUY / SELL / HOLD / MIXED  
**Confidence:** {High/Medium/Low}

---

## 🎯 Bottom Line
{2-3 sentences: Direct actionable conclusion synthesizing all agent insights. State what to do and why.}

---

## 📋 Quick Overview

| Agent | Key Finding | Signal |
|-------|-------------|--------|
| 🔍 Search | {1-2 sentence summary} | ✅/⚠️/❌ |
| 💭 Sentiment | {Trend & summary} | ✅/⚠️/❌ |
| 📈 Finance | {Technical outlook} | ✅/⚠️/❌ |
| 🎯 Advisor | {Recommendation} | ✅/⚠️/❌ |

_(Skip rows for agents with no data)_

---

## 📊 Key Metrics

**{Ticker}:**
- **Price Action:** {trend direction}
- **Sentiment Score:** {0-100} [{source}]
- **Technical Signal:** {Bullish/Bearish/Neutral}
- **Entry/Exit:** ${entry} / SL: ${stop} / TP: ${target}

_(Repeat for each ticker if multiple)_

---

## Investment Strategy
**{Ticker}:** 
- Position: {size} | Risk: {level} | Horizon: {timeframe}
- Entry: ${X} | Stop: ${Y} (-Z%) | Target: ${A} (+B%)

---

## ⚠️ Risk Factors
- {Key risk 1}
- {Key risk 2}
- {Key risk 3}

---

## 🎯 Action Items
1. {Specific action based on recommendation}
2. {Monitoring points}
3. {Exit conditions}

---

"""

SEARCH_AGENT_OUTPUT: str = """
# 🔍 Search Report

**{Ticker/Company}:**
- {Key insight 1}
- {Key insight 2}
- {Key insight 3}

_(Repeat for multiple tickers)_

**Conclusion:** {1 sentence}
"""

SENTIMENT_AGENT_OUTPUT: str = """
# 💭 Sentiment Report

**{Ticker}:**
- **Score:** {0-100} [{Source}]
- **Signal:** {Bullish/Bearish/Neutral}
- **Trend:** {Improving/Declining/Stable}

**Top Headlines:**
1. {Headline 1}
2. {Headline 2}
3. {Headline 3}

_(Repeat for multiple tickers)_
"""

FINANCE_AGENT_OUTPUT: str = """
# 📈 Finance Report

**{Ticker}:**

**Signal:** {Bullish/Bearish/Neutral}

**Technicals:**
- RSI: {value} ({overbought/oversold/neutral})
- MACD: {bullish/bearish}
- Trend: {up/down/sideways}
- Support: ${X} | Resistance: ${Y}

**Outlook:** {1-2 sentence conclusion}

_(Repeat for multiple tickers)_
"""

ADVISOR_AGENT_OUTPUT: str = """
# 🎯 Advisor Report

**{Ticker} - {BUY/SELL/HOLD}**

**Setup:**
- Entry: ${X}
- Stop Loss: ${Y} (-Z%)
- Target: ${A} (+B%)
- Position: {size}
- Risk: {Low/Med/High}

**Rationale:** {2 sentences why this trade makes sense}

_(Repeat for multiple tickers)_
"""
