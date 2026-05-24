from state import ResearchState
from utils import safe_parse


def senior_critic_agent(state: ResearchState, client):
    context = f"""
    Research Question: {state.question}
    Total Iterations: {state.iteration}
    All Hypotheses: {[{"claim": h.claim, "status": h.status} for h in state.hypotheses]}
    Established Results: {state.established_results}
    Critiques So Far: {state.critiques}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": """You are a senior research critic.
                Audit the ENTIRE research state.
                Ask: are we researching the right things? Are results coherent?

                Respond ONLY with valid JSON:
                {
                    "assessment": "SOUND/FLAWED",
                    "reason": "overall assessment",
                    "challenged_result": "exact text of established result you challenge, or null",
                    "recommendation": "what should change"
                }"""
            },
            {
                "role": "user",
                "content": f"Audit this research state: {context}"
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    print(f"\n=== SENIOR CRITIC ===")
    print(f"Assessment: {result['assessment']}")
    print(f"Reason: {result['reason']}")
    print(f"Recommendation: {result['recommendation']}")

    if result.get("challenged_result"):
        print(f"CHALLENGE FILED against: {result['challenged_result']}")
        state.critiques.append(f"SENIOR CRITIC CHALLENGE: {result['challenged_result']}")

    state.save()
    return state, result
