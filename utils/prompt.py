FINAL_OUTPUT_FORMAT: str = """
# Executive Summary:
---
Tickers: list if more = []
Recommendation: str
Note: str

# Agent Summary (if only 1 then give that one only):

Sentiment Agent Name: str
---
Recommendation: str
Sentiment Score (if applicable)
- Score
- Source
- Reason
- Top 5 Headlines combined
    - Headline 1
    - Headline 2
    - Headline 3
    ....

Finance Agent Name: str
---
Recommendation: str
Important Techinals (if applicable)
- Technical 1
- Technical 2
- Technical 3
....

Advisor Agent Name: str
---
Recommendation: str
Personalized Information:
- Position
- Error Margin
- Capital Allocation
- Stop Loss/Profit
....

# Final Conclusion:
---
2-3 lines conclusion of entire thing.
"""

SENTIMENT_AGENT_OUTPUT: str = """
Sentiment Agent Name: str
---
Recommendation: str
Sentiment Score (if applicable)
    - Score
    - Source
    - Reason
    - Top 5 Headlines combined
        - Headline 1
        - Headline 2
        - Headline 3
        ....
Conclusion: str
"""

FINANCE_AGENT_OUTPUT: str = """
Finance Agent Name: str
---
Recommendation: str
Important Techinals (if applicable)
    - Technical 1
    - Technical 2
    - Technical 3
    ....
Conclusion: str
"""

ADVISOR_AGENT_OUTPUT: str = """
Advisor Agent Name: str
---
Recommendation: str
Personalized Information:
    - Position
    - Error Margin
    - Capital Allocation
    - Stop Loss/Profit
    ....
Conclusion: str
"""
