from state import ResearchState
from utils import safe_parse


def reviewer_agent(state: ResearchState, stock_data: dict, client) -> ResearchState:
    unverified = [h for h in state.hypotheses if h.status == "unverified"]

    if not unverified:
        print("No unverified hypotheses to review")
        return state

    hypothesis = unverified[-1]

    context = f"""
    Research Question: {state.question}
    Established Results: {state.established_results}
    Available data points: {list(stock_data.keys())}
    Only critique based on available data. Do not ask for data that wasn't provided.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": """You are a financial reviewer. Your job is to verify hypotheses.

                Rules:
                - If the hypothesis is supported by AT LEAST 2 data points, say VERIFIED
                - Only REFUTE if the hypothesis directly contradicts the data
                - Use INCONCLUSIVE only if data is missing entirely
                You MUST say VERIFIED if the reasoning uses multiple metrics.

                Respond ONLY with valid JSON:
                {
                    "verdict": "VERIFIED/REFUTED/INCONCLUSIVE",
                    "reason": "why you gave this verdict",
                    "confidence": "high/medium/low"
                }"""
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nHypothesis: {hypothesis.claim}\nEvidence: {hypothesis.evidence[0].content}"
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)
    hypothesis.status = result["verdict"]

    if result["verdict"] == "VERIFIED":
        similar_exists = any(hypothesis.claim[:50] in er for er in state.established_results)
        if not similar_exists:
            state.established_results.append(hypothesis.claim)
            print(f"VERIFIED — promoted to Established Result")
        else:
            print(f"VERIFIED — similar result already exists, skipping")
    elif result["verdict"] == "REFUTED":
        state.critiques.append(result["reason"])
        print(f"REFUTED — {result['reason']}")
    else:
        print(f"INCONCLUSIVE — {result['reason']}")

    state.iteration += 1
    state.save()

    return state
