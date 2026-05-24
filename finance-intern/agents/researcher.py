import json
from datetime import datetime
from state import ResearchState, Evidence, WorkingHypothesis
from utils import safe_parse


def researcher_agent(state: ResearchState, stock_data: dict, client) -> ResearchState:
    context = f"""
    Research Question: {state.question}
    Current Iteration: {state.iteration}

    Already Established (DO NOT repeat these):
    {state.established_results}

    Surveyor Guidance:
    {state.critiques[0] if state.critiques else "None"}

    Sanity Checks:
    {state.critiques[1] if len(state.critiques) > 1 else "None"}

    Your job: Investigate a NEW angle not already covered above.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": """You are a financial researcher.
                Each iteration you MUST investigate a completely different angle.
                Never repeat what is already in Established Results.

                Angles to explore (pick one not yet covered):
                - Valuation metrics (P/E, market cap)
                - Growth metrics (revenue, earnings growth)
                - Profitability (profit margins, ROE)
                - Risk factors (debt, market conditions)
                - Competitive position

                Always base your hypothesis on AT LEAST 3 specific metrics with actual numbers.
                Respond ONLY with valid JSON:
                {
                    "claim": "specific hypothesis with actual numbers",
                    "reasoning": "detailed reasoning citing specific metrics",
                    "confidence": "high/medium/low"
                }"""
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nStock Data: {json.dumps(stock_data)}"
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    evidence = Evidence(
        source="researcher",
        content=result["reasoning"],
        timestamp=str(datetime.now())
    )

    hypothesis = WorkingHypothesis(
        claim=result["claim"],
        evidence=[evidence],
        status="unverified"
    )

    state.hypotheses.append(hypothesis)
    state.iteration += 1
    state.save()

    return state
