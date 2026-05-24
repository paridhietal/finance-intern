from state import ResearchState
from utils import safe_parse


def adjudicator_agent(state: ResearchState, challenged_result: str, client) -> ResearchState:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": """You are an independent adjudicator.
                Evaluate whether a challenged result should stay or be removed.
                Be fair and objective.

                Respond ONLY with valid JSON:
                {
                    "decision": "KEEP/DEMOTE",
                    "reason": "why"
                }"""
            },
            {
                "role": "user",
                "content": f"""
                Established Result being challenged: {challenged_result}
                All evidence so far: {[h.evidence[0].content for h in state.hypotheses]}
                Should this result stay or be removed?"""
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    print(f"\n=== ADJUDICATOR ===")
    print(f"Decision: {result['decision']}")
    print(f"Reason: {result['reason']}")

    if result["decision"] == "DEMOTE":
        if challenged_result in state.established_results:
            state.established_results.remove(challenged_result)
            print(f"Result DEMOTED and removed")
    else:
        print(f"Result KEPT in Established Results")

    state.save()
    return state
