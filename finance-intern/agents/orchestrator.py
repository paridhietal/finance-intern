from state import ResearchState
from utils import safe_parse


def orchestrator_agent(state: ResearchState, client) -> dict:
    context = f"""
    Research Question: {state.question}
    Iteration: {state.iteration}
    Hypotheses: {[{"claim": h.claim, "status": h.status} for h in state.hypotheses]}
    Established Results: {state.established_results}
    Critiques: {state.critiques}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": """You are a research orchestrator.
                Rules:
                - If Established Results is empty, you MUST say CONTINUE
                - If all hypotheses are REFUTED, you MUST say CONTINUE
                - Only say COMPLETE if at least 1 Established Result exists

                Respond ONLY with valid JSON:
                {
                    "decision": "CONTINUE/COMPLETE",
                    "reason": "why",
                    "next_focus": "what the researcher should investigate next"
                }"""
            },
            {
                "role": "user",
                "content": f"Research state: {context}"
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    print(f"Orchestrator decision: {result['decision']}")
    print(f"Reason: {result['reason']}")
    print(f"Next focus: {result['next_focus']}")

    return result
