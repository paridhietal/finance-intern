from utils import safe_parse


def surveyor_agent(question: str, client) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": """You are a research surveyor.
                Before any research begins, map the landscape.
                Identify what techniques exist, what pitfalls to watch for,
                and what a good answer should look like.

                Respond ONLY with valid JSON:
                {
                    "key_techniques": ["technique1", "technique2", "technique3"],
                    "known_pitfalls": ["pitfall1", "pitfall2", "pitfall3"],
                    "sanity_checks": ["check1", "check2", "check3"],
                    "research_guidance": "overall guidance for the research"
                }"""
            },
            {
                "role": "user",
                "content": f"Map the research landscape for this question: {question}"
            }
        ]
    )

    result = safe_parse(response.choices[0].message.content)

    print(f"\n=== SURVEYOR REPORT ===")
    print(f"Key Techniques: {result['key_techniques']}")
    print(f"Common Pitfalls: {result['known_pitfalls']}")
    print(f"Sanity Checks: {result['sanity_checks']}")
    print(f"Guidance: {result['research_guidance']}")

    return result
