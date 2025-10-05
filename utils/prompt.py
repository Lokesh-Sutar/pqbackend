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
| {AAPL} | {BUY} | ${150} | ${142} | ${165} | {Med} | {85%} |
| {MSFT} | {HOLD} | ${380} | ${365} | ${400} | {Low} | {70%} |
| {GOOGL} | {SELL} | ${140} | ${145} | ${130} | {High} | {75%} |

_(Include only analyzed tickers. For single ticker, this becomes a single row.)_

---

## 🤖 Agent Signals

| Agent | {Ticker 1} | {Ticker 2} | {Ticker 3} | Key Insight |
|-------|------------|------------|------------|-------------|
| **🔍 Search** | ✅ Positive | ⚠️ Neutral | ❌ Negative | {1 sentence summarizing search findings} |
| **💭 Sentiment** | 78/100 ✅ | 52/100 ⚠️ | 35/100 ❌ | {Overall sentiment trend} |
| **📈 Finance** | Bullish ✅ | Sideways ⚠️ | Bearish ❌ | {Technical outlook summary} |
| **🎯 Advisor** | BUY ✅ | HOLD ⚠️ | SELL ❌ | {Investment strategy summary} |

_(For single ticker, use single column. Skip agent rows with no data.)_

---

## 📈 Technical Snapshot

| Ticker | Price Trend | RSI | MACD | MA Trend | Support | Resistance |
|--------|-------------|-----|------|----------|---------|------------|
| {AAPL} | {Uptrend ↗} | {65} | {Bullish ✅} | {Above 50/200} | ${145} | ${160} |
| {MSFT} | {Sideways →} | {48} | {Neutral ⚠️} | {Mixed} | ${375} | ${390} |
| {GOOGL} | {Downtrend ↘} | {32} | {Bearish ❌} | {Below 50/200} | ${130} | ${145} |

---

## 💭 Sentiment Breakdown

| Ticker | Score | Source | Interpretation | Top Signal |
|--------|-------|--------|----------------|------------|
| {AAPL} | 78/100 | {Reddit/YFinance} | {Strongly Bullish} | {Product launch hype} |
| {MSFT} | 52/100 | {Twitter/Finhub} | {Neutral} | {Mixed earnings reaction} |
| {GOOGL} | 35/100 | {News/Reddit} | {Bearish} | {Regulatory concerns} |

**Recent Headlines:**
1. {Most impactful headline 1}
2. {Most impactful headline 2}
3. {Most impactful headline 3}

---

## 🎯 Position Strategy

| Ticker | Action | Position Size | Time Horizon | Risk/Reward | Max Loss | Expected Gain |
|--------|--------|---------------|--------------|-------------|----------|---------------|
| {AAPL} | {BUY} | {5% / $5,000} | {3-6 months} | {1:2} | {-5.3%} | {+10%} |
| {MSFT} | {HOLD} | {Current} | {6-12 months} | {1:1.5} | {-3.9%} | {+5.3%} |
| {GOOGL} | {SELL} | {Exit} | {Immediate} | {N/A} | {Cut at -3.6%} | {N/A} |

---

## 🔍 Recent Developments

| Ticker | Key Developments |
|--------|------------------|
| {AAPL} | • {Development 1}|
|        | • {Development 2}|
| {MSFT} | • {Development 1}|
|        | • {Development 2}|

---

## ⚠️ Risk Assessment

| Risk Factor | {Ticker 1} | {Ticker 2} | {Ticker 3} | Mitigation |
|-------------|------------|------------|------------|------------|
| **Market Risk** | {Medium} | {Low} | {High} | {Diversification strategy} |
| **Sector Risk** | {Low} | {Medium} | {High} | {Sector rotation watch} |
| **Company Risk** | {Low} | {Low} | {Medium} | {Stop loss protection} |
| **Volatility** | {Moderate} | {Low} | {High} | {Position sizing} |

---

## 📋 Action Checklist

| Priority | Action | Ticker(s) | Deadline |
|----------|--------|-----------|----------|
| 🔴 High | {Action 1 - e.g., Enter position} | {AAPL} | {Within 2 days} |
| 🟡 Med | {Action 2 - e.g., Monitor support} | {MSFT} | {This week} |
| 🟢 Low | {Action 3 - e.g., Review in 30 days} | {GOOGL} | {End of month} |

---

## 📌 Key Takeaways

| # | Insight |
|---|---------|
| 1️⃣ | {Most important finding from all agents} |
| 2️⃣ | {Second most important consideration} |
| 3️⃣ | {Third key point for decision making} |


"""

SEARCH_AGENT_OUTPUT: str = """
# 🔍 Search Report

| Ticker | Key Developments | Signal |
|--------|------------------|--------|
| {AAPL} | • {Development 1} | ✅/⚠️/❌ |
|        | • {Development 2} |          |
|        | • {Development 3} |          |
| {AAPL} | • {Development 1} | ✅/⚠️/❌ |
|        | • {Development 2} |          |
|        | • {Development 3} |          |


**Conclusion:** {1 sentence summary of web research findings}
"""

SENTIMENT_AGENT_OUTPUT: str = """
# 💭 Sentiment Report

| Ticker | Score | Source | Interpretation | Trend | Signal |
|--------|-------|--------|----------------|-------|--------|
| {AAPL} | 78/100 | {Reddit/YFinance} | {Strongly Bullish} | ↗ Rising | ✅ |
| {MSFT} | 52/100 | {Twitter} | {Neutral} | → Stable | ⚠️ |
| {GOOGL} | 35/100 | {Finhub} | {Bearish} | ↘ Falling | ❌ |

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
| {AAPL} | ↗ Up | 65 | Bullish ✅ | Above 50/200 | $145 | $160 | ✅ |
| {MSFT} | → Flat | 48 | Neutral ⚠️ | Mixed | $375 | $390 | ⚠️ |
| {GOOGL} | ↘ Down | 32 | Bearish ❌ | Below 50/200 | $130 | $145 | ❌ |

**Technical Outlook:**
- **{AAPL}:** {1-2 sentence technical summary}
- **{MSFT}:** {1-2 sentence technical summary}
- **{GOOGL}:** {1-2 sentence technical summary}
"""

ADVISOR_AGENT_OUTPUT: str = """
# 🎯 Advisor Report

| Ticker | Action | Entry | Stop Loss | Target | Position | Risk | Horizon | Confidence |
|--------|--------|-------|-----------|--------|----------|------|---------|------------|
| {AAPL} | BUY ✅ | $150 | $142 (-5.3%) | $165 (+10%) | 5% / $5K | Medium | 3-6M | 85% |
| {MSFT} | HOLD ⚠️ | $380 | $365 (-3.9%) | $400 (+5.3%) | Current | Low | 6-12M | 70% |
| {GOOGL} | SELL ❌ | $140 | $145 (-3.6%) | $130 (-7%) | Exit | High | Now | 75% |

**Rationale:**
- **{AAPL}:** {1-2 sentence why BUY}
- **{MSFT}:** {1-2 sentence why HOLD}
- **{GOOGL}:** {1-2 sentence why SELL}
"""
