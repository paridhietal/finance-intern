from state import ResearchState
from utils import safe_parse


def formatter_agent(state: ResearchState, survey: dict, client) -> dict:
    context = f"""
    Original Question: {state.question}
    Established Results: {state.established_results}
    Critiques Filed: {state.critiques}
    Sanity Checks from Surveyor: {survey['sanity_checks']}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": """You are a financial report formatter.
                Take the research results and produce a clean professional investment report.
                Be honest about the research process.
                If critiques were filed or results were demoted, mention that in risks.
                Do not overstate confidence if research had contradictions.

                Respond ONLY with valid JSON:
                {
                    "verdict": "BUY/SELL/HOLD",
                    "confidence": "high/medium/low",
                    "summary": "2-3 sentence executive summary",
                    "key_findings": ["finding1", "finding2", "finding3"],
                    "risks": ["risk1", "risk2"],
                    "recommendation": "final recommendation paragraph"
                }"""
            },
            {
                "role": "user",
                "content": f"Produce a final report from this research: {context}"
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    print(f"\n{'='*50}")
    print(f"FINAL INVESTMENT REPORT")
    print(f"{'='*50}")
    print(f"Verdict: {result['verdict']} ({result['confidence']} confidence)")
    print(f"\nSummary: {result['summary']}")
    print(f"\nKey Findings:")
    for f in result['key_findings']:
        print(f"  - {f}")
    print(f"\nRisks:")
    for r in result['risks']:
        print(f"  - {r}")
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"{'='*50}")

    return result
