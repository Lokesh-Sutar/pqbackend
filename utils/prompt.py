FINAL_OUTPUT_FORMAT = ''


SEARCH_AGENT_OUTPUT: str = """
# Recent News & Developments

## Latest Updates
| Ticker | Recent News | Impact | When |
|--------|-------------|--------|------|
| {ticker} | {Development 1} | {Positive/Negative/Neutral} | {timeframe if available} |
|          | {Development 2} | {Positive/Negative/Neutral} | {timeframe} |
|          | {Development 3} | {Positive/Negative/Neutral} | {timeframe} |

**Key Takeaway:** {1 sentence on what matters most from the news - focus on catalysts that could move the stock}

## Conclusion:
_Give the overall search outlook in 1-2 sentences and giving a summary to the user._

_Note: If web search returns limited results, state that. For better results, searched using company name + relevant keywords (not just ticker)._
"""

SENTIMENT_AGENT_OUTPUT: str = """
# Market Sentiment Report

## Sentiment Score
| Ticker | Overall Score | Sources Used | Market Mood | Signal |
|--------|---------------|--------------|-------------|--------|
| {ticker} | {score}/100 | {Reddit/News/YFinance} | {Bullish/Bearish/Neutral} | {BUY/SELL/HOLD} |

**What People Are Saying:**
{2-3 bullet points of actual headlines or sentiment drivers - keep it factual}
- {Headline/theme 1}
- {Headline/theme 2}
- {Headline/theme 3}

**Overall Trend:** (Hype/Fear/Neutral) - {1 sentence explaining the broader market sentiment context}

## Conclusion:
_Give the overall sentiment outlook in 1-2 sentences, combining all indicators together and giving a summary to the user._

_Note: For Indian stocks, primarily using news sources as Reddit/social media may have limited coverage. If no sentiment data available for a source, explicitly state which source had no data._
"""

FINANCE_AGENT_OUTPUT: str = """
# Technical Analysis Report

## Signal Summary
| Ticker | Price | Trend | RSI | MACD | Moving Averages | Signal |
|--------|-------|-------|-----|------|-----------------|--------|
| {ticker} | ${price} | {↗/→/↘} | {value} ({condition}) | {Bullish/Bearish/Neutral} | {Above/Below/Mixed} | {BUY/SELL/HOLD} |

**What This Means:**
- **{ticker}**: {Plain English explanation: "Price is trending up with strong momentum" or "Oversold conditions suggest potential bounce" - max 1 sentence per ticker}

**Key Levels to Watch:**
| Ticker | Support (Floor) | Resistance (Ceiling) | Current Price |
|--------|-----------------|----------------------|---------------|
| {ticker} | ${support} | ${resistance} | ${current} |

**Market Fear Gauge (VIX):** {value} - {Low/Moderate/High} fear means {explanation in simple terms}

## Conclusion:
_Give the overall technical outlook in 1-2 sentences, combining all indicators together and giving a summary to the user._

_Note: If any indicator data is missing, state which one and provide analysis with available data only._
"""

ADVISOR_AGENT_OUTPUT: str = """
# Strategy & Portfolio Recommendation

## Tested Strategies
| Strategy | Annual Return | Risk Score | Max Loss | Winner |
|----------|---------------|------------|----------|--------|
| Buy & Hold | {X}% | {Sharpe} | -{X}% | {✓ if best} |
| Dollar Cost Averaging | {X}% | {Sharpe} | -{X}% | {✓ if best} |
| SMA Crossover | {X}% | {Sharpe} | -{X}% | {✓ if best} |
| RSI Mean Reversion | {X}% | {Sharpe} | -{X}% | {✓ if best} |

**Recommended Approach:** {strategy_name}  
**Why:** {1 sentence explaining why it won - e.g., "Best balance of returns and stability for conservative investors" or "Highest returns with acceptable risk"}

**What to Expect:**
- Potential annual return: {X}%
- Worst case loss: -{X}%
- Trading fees: ${X}
- Estimated tax: ${X}

## Your Portfolio Split
| Ticker | Amount | Why |
|--------|--------|-----|
| {ticker} | ${X} ({X}%) | {Brief reason based on backtest} |
| Cash | ${X} ({X}%) | Safety buffer |

## Action Steps
1. **{ticker}**: {Specific action - e.g., "Invest $500 monthly using Dollar Cost Averaging" or "Buy at $145-150, set stop-loss at $135"}
2. **Timeline**: {short/medium/long term}
3. **Monitor**: {What to watch for}

## Conclusion:
_Give the overall advisory outlook in 1-2 sentences, combining all indicators together and giving a summary to the user._
_Note: Backtesting period: {period}. Broker: {broker}. Market: {market}. If any tool failed or returned no data, clearly state which one and provide basic recommendation based on risk profile only._
"""
