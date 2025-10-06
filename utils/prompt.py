FINAL_OUTPUT_FORMAT: str = """
# 📊 Investment Analysis Report

---

## 🎯 Executive Summary

| Metric | Value |
|--------|-------|
| **Analyzed Tickers** | {comma-separated list} |
| **Overall Recommendation** | {BUY / SELL / HOLD / MIXED} |
| **Confidence Level** | {High / Medium / Low} |
| **Primary Signal** | {What's driving the recommendation} |

---

## 💡 Bottom Line

{2-3 sentences: Direct, actionable conclusion. What should the investor do and why? Synthesize all agent insights into one clear directive.}

---

## 📊 Multi-Ticker Overview

| Ticker | Recommendation | Entry | Stop Loss | Target | Risk | Confidence |
|--------|----------------|-------|-----------|--------|------|------------|
| {ticker} | {BUY/HOLD/SELL} | {entry_price} | {stop_loss} | {target} | {Low/Med/High} | {confidence_pct (eg. 85%, 70%, etc)} |

_Just use this for your understanding, dont include this in response (Include only analyzed tickers. For single ticker, this becomes a single row.)_

---

## 🤖 Agent Signals

| Agent | {Ticker 1} | {Ticker 2} | {Ticker 3} | Key Insight |
|-------|------------|------------|------------|-------------|
| **🔍 Search** | {signal} | {signal} | {signal} | {1 sentence summarizing search findings} |
| **💭 Sentiment** | {score} | {score} | {score} | {Overall sentiment trend} |
| **📈 Finance** | {outlook} | {outlook} | {outlook} | {Technical outlook summary} |
| **🎯 Advisor** | {action} | {action} | {action} | {Investment strategy summary} |

_Just use this for your understanding, dont include this in response (For single ticker, use single column. Skip agent rows with no data.)_
_Just use this for your understanding, dont include this in response ({signal} = (Positive/Neutral/Negative), {score} = (eg. 78/100, 52/100, etc), {outlook} = (Bullish/Sideways/Bearish), {action} = (BUY/HOLD/SELL))

---

## 📈 Technical Snapshot

| Ticker | Price Trend | RSI | MACD | MA Trend | Support | Resistance |
|--------|-------------|-----|------|----------|---------|------------|
| {ticker} | {trend_direction} | {rsi_value} | {macd_signal} | {ma_position} | {support_price} | {resistance_price} |

_Just use this for your understanding, dont include this in response ({trend_direction} = (Uptrend ↗/Sideways →/Downtrend ↘), {macd_signal} = (Bullish/Neutral/Bearish), {ma_position} = (eg. Above 50/200, Mixed, Below 50/200))

---

## 💭 Sentiment Breakdown

| Ticker | Score | Source | Interpretation | Top Signal |
|--------|-------|--------|----------------|------------|
| {ticker} | {score (eg. 78, 52, etc)}/100 | {data_sources} | {sentiment_interpretation} | {key_driver} |

_Just use this for your understanding, dont include this in response ({sentiment_interpretation} = (Strongly Bullish/Bullish/Weakly Bullish/Neutral/Weakly Bearish/Bearish/Strongly Bearish))

**Recent Headlines:**
1. {Most impactful headline 1}
2. {Most impactful headline 2}
3. {Most impactful headline 3}

---

## 🎯 Position Strategy

| Ticker | Action | Position Size | Time Horizon | Risk/Reward | Max Loss | Expected Gain |
|--------|--------|---------------|--------------|-------------|----------|---------------|
| {ticker} | {action} | {position_size} | {time_horizon} | {risk_reward_ratio} | {max_loss_pct} | {expected_gain_pct} |

_Just use this for your understanding, dont include this in response ({action} = (BUY/HOLD/SELL), {time_horizon} = (eg. 3-6 months, 6-12 months, Immediate, etc), {risk_reward_ratio} = (eg. 1:2, 1:3, 'N/A'), {max_loss_pct} = (eg. -5.3%, 3.9%, etc), {expected_gain_pct} = (eg. +10%, +5.3%, N/A, etc))

---

## 🔍 Recent Developments

| Ticker | Key Developments |
|--------|------------------|
| {ticker 1} | • {Development 1}|
|            | • {Development 2}|
| {ticker 2} | • {Development 1}|
|            | • {Development 2}|

---

## ⚠️ Risk Assessment

| Risk Factor | {Ticker 1} | {Ticker 2} | {Ticker 3} | Mitigation |
|-------------|------------|------------|------------|------------|
| **Market Risk** | {risk_level} | {risk_level} | {risk_level} | {mitigation_strategy} |
| **Sector Risk** | {risk_level} | {risk_level} | {risk_level} | {mitigation_strategy} |
| **Company Risk** | {risk_level} | {risk_level} | {risk_level} | {mitigation_strategy} |
| **Volatility** | {risk_level} | {risk_level} | {risk_level} | {mitigation_strategy} |

_Just use this for your understanding, dont include this in response ({risk_level} = (Low/Medium/High), {mitigation_strategy} = (eg. Diversification strategy, Sector rotation watch, Stop loss protection, Position sizing, etc))

---

## 📋 Action Checklist

| Priority | Action | Ticker(s) | Deadline |
|----------|--------|-----------|----------|
| {priority_level} | {action_item} | {ticker 1/ticker 2,..} | {timeframe} |

_Just use this for your understanding, dont include this in response ({priority_level} = (Low/Med/High), {action_item} = (eg. Enter position, Monitor support, Review in 30 days), {timeframe} = (eg. Within 2 days, This week, End of month, etc))

---

## 📌 Key Takeaways

| # | Insight |
|---|---------|
| 1 | {Most important finding from all agents} |
| 2 | {Second most important consideration} |
| 3 | {Third key point for decision making} |


"""

SEARCH_AGENT_OUTPUT: str = """
# 🔍 Search Report

| Ticker | Key Developments | Signal |
|--------|------------------|--------|
| {ticker 1} | • {Development 1} | {signal} |
|            | • {Development 2} |          |
|            | • {Development 3} |          |
| {ticker 2} | • {Development 1} | {signal} |
|            | • {Development 2} |          |
|            | • {Development 3} |          |

_Just use this for your understanding, dont include this in response ({signal} = (Positive/Neutral/Negative))

**Conclusion:** {1 sentence summary of web research findings}
"""

SENTIMENT_AGENT_OUTPUT: str = """
# 💭 Sentiment Report

| Ticker | Score | Source | Interpretation | Trend | Signal |
|--------|-------|--------|----------------|-------|--------|
| {ticker} | {score} | {data_sources} | {sentiment_interpretation} | {trend_direction} | {signal} |

_Just use this for your understanding, dont include this in response ({score} = (eg. 78/100, 52/100, etc), {sentiment_interpretation} = (Strongly Bullish/Bullish/Weakly Bullish/Neutral/Weakly Bearish/Bearish/Strongly Bearish), {trend_direction} = (↗ Rising/→ Stable/↘ Falling), {signal} = (Positive/Neutral/Negative))

**Top Headlines:**
1. {Headline 1}
2. {Headline 2}
3. {Headline 3}

**Summary:** {1 sentence overall sentiment conclusion}
"""

FINANCE_AGENT_OUTPUT: str = """
# 📈 Finance Report

| Ticker | Trend | RSI | MACD | MA Position | Support | Resistance | Signal |
|--------|-------|-----|------|-------------|---------|------------|--------|
| {ticker} | {trend_direction} | {rsi_value} | {macd_signal} | {ma_position} | {support_price} | {resistance_price} | {signal} |

_Just use this for your understanding, dont include this in response ({trend_direction} = (↗ Up/→ Flat/↘ Down), {macd_signal} = (Bullish/Neutral/Bearish), {ma_position} = (eg. Above 50/200, Mixed, Below 50/200), {signal} = (Positive/Neutral/Negative))

**Technical Outlook:**
- **{ticker 1}:** {1-2 sentence technical summary}
- **{ticker 2}:** {1-2 sentence technical summary}
...
"""

ADVISOR_AGENT_OUTPUT: str = """
# 🎯 Advisor Report

| Ticker | Action | Entry | Stop Loss | Target | Position | Risk | Horizon | Confidence |
|--------|--------|-------|-----------|--------|----------|------|---------|------------|
| {ticker} | {action} | {entry_price} | {stop_loss_price} ({stop_loss_pct}) | {target_price} ({target_pct}) | {position_size} | {risk_level} | {time_horizon} | {confidence_pct} |

_Just use this for your understanding, dont include this in response ({action} = (BUY/HOLD/SELL), {risk_level} = (Low/Medium/High), {time_horizon} = (eg. 3-6M, 6-12M, Now, etc), {confidence_pct} = (eg. 85%, 70%, etc))

**Rationale:**
- **{ticker 1}:** {1-2 sentence rationale (Why BUY/HOLD/SELL)}
- **{ticker 2}:** {1-2 sentence rationale (Why BUY/HOLD/SELL)}
...
"""
