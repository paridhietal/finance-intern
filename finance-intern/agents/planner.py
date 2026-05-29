from state import ResearchState
from utils import safe_parse


def planner_agent(question: str, survey: dict, client) -> dict:

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": """You are a research planner.
                Given a research question and surveyor findings,
                create a concrete research plan.

                Respond ONLY with valid JSON:
                {
                    "research_strategy": "overall approach in 2-3 sentences",
                    "investigation_steps": [
                        "step 1: what to investigate first",
                        "step 2: what to investigate second",
                        "step 3: what to investigate third"
                    ],
                    "sanity_checks": [
                        "check 1: specific pass/fail test",
                        "check 2: specific pass/fail test",
                        "check 3: specific pass/fail test"
                    ],
                    "success_criteria": "what a complete answer looks like"
                }"""
            },
            {
                "role": "user",
                "content": f"""
                Research Question: {question}
                
                Surveyor findings:
                - Key Techniques: {survey['key_techniques']}
                - Known Pitfalls: {survey['known_pitfalls']}
                - Sanity Checks: {survey['sanity_checks']}
                - Guidance: {survey['research_guidance']}
                
                Create a concrete research plan.
                """
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    print(f"\n=== PLANNER ===")
    print(f"Strategy: {result['research_strategy']}")
    print(f"\nInvestigation Steps:")
    for step in result['investigation_steps']:
        print(f"  - {step}")
    print(f"\nSanity Checks:")
    for check in result['sanity_checks']:
        print(f"  - {check}")
    print(f"\nSuccess Criteria: {result['success_criteria']}")

    return result