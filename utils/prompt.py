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
| Ticker | Current Price | Amount | Shares | Why |
|--------|---------------|--------|--------|-----|
| {ticker} | ${current_price} | ${X} ({X}%) | {N} shares | {Brief reason based on backtest} |
| Cash | - | ${X} ({X}%) | - | Safety buffer |

## Action Steps
1. **Execute Trade**: Based on the recommended strategy, the following action is advised:
   - **Ticker**: {ticker}
   - **Current Market Price**: ${current_price} (CRITICAL: This is the ACTUAL price right now)
   - **Action**: {BUY/SELL}
   - **Entry Price Range**: ${lower_range} - ${upper_range} (should be close to current price)
   - **Recommended Shares**: {N} shares
   - **Position Size**: ${total_investment}
   - **Stop-Loss**: ${stop_loss_price} (exit if drops below this)
   - **Take-Profit Target 1**: ${take_profit_price_1} (first exit target)
   - **Take-Profit Target 2**: ${take_profit_price_2} (second exit target)
2. **Timeline**: This recommendation is for a {short/medium/long term} holding period.
3. **Monitor**: Keep an eye on {key metric or event to watch}.

## Conclusion:
_Give the overall advisory outlook in 1-2 sentences, combining all indicators together and giving a summary to the user._
_Note: Backtesting period: {period}. Broker: {broker}. Market: {market}. If any tool failed or returned no data, clearly state which one and provide basic recommendation based on risk profile only._
"""

TEAM_CONVERSATIONAL_OUTPUT = """
# PersonaQuant Analysis for {ticker_or_query}

## Executive Summary
_{A 2-3 sentence summary synthesizing the findings from all agents. It should balance the different perspectives and give a high-level conclusion. Example: "While technical indicators for NVDA suggest a short-term buying opportunity, negative sentiment from recent news warrants a cautious approach. The recommended strategy is to wait for a clear trend."}_

## Overall Recommendation
**Decision:** {BUY | SELL | HOLD}
**Confidence:** {High | Medium | Low}
**Reasoning:** _{A brief explanation for the recommendation, highlighting the most critical factors. Example: "Confidence is medium because the bullish technical signals are in conflict with bearish news sentiment."}_

## Agent Findings
| Agent | Signal/Strategy | Key Finding |
|---|---|---|
| **Search** | _{Positive/Negative/Neutral}_ | _{Brief summary of key news}_ |
| **Sentiment** | _{Bullish/Bearish/Neutral}_ | _{Overall market mood and score}_ |
| **Finance** | _{BUY/SELL/HOLD}_ | _{Summary of technical indicators}_ |
| **Advisory** | _{Recommended Strategy}_ | _{Backtest winner with expected returns}_ |

## Recommended Action Plan
_Give a concise action plan based on the overall information from all the agents. Write them properly in sections, steps, or in bullet points._


## Risks & Caveats
- _{List any conflicting signals, e.g., "Technicals are bullish, but news sentiment is negative due to recent regulatory concerns."}_
- _{Mention any other risks, e.g., "High volatility expected around the upcoming earnings report."}_
- _{Note if any agent failed or data was missing.}_
"""
