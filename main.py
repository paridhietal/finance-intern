from dotenv import load_dotenv
import os
load_dotenv()
from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

from state import ResearchState
from utils import get_stock_data
from agents.surveyor import surveyor_agent
from agents.researcher import researcher_agent
from agents.reviewer import reviewer_agent
from agents.orchestrator import orchestrator_agent
from agents.senior_critic import senior_critic_agent
from agents.adjudicator import adjudicator_agent
from agents.formatter import formatter_agent
from agents.computer import computer_agent
from agents.planner import planner_agent

# ─── CONFIG ──────────────────────────────────────────────────────────────────

TICKER = "GOOGL"
QUESTION = f"Is {TICKER} a good buy right now?"
MAX_ITERATIONS = 6

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print(f"Fetching stock data for {TICKER}...")
    stock_data = get_stock_data(TICKER)
    print("Stock data fetched:", stock_data)

    # Step 1 — Surveyor maps the landscape
    print("\n" + "="*50)
    survey = surveyor_agent(QUESTION, client)

    # Step 2 — Planner (NEW)
    plan = planner_agent(QUESTION, survey, client)

    # Step 3 — Initialize state with BOTH survey and plan
    state = ResearchState(question=QUESTION)
    state.critiques.append(f"SURVEYOR GUIDANCE: {survey['research_guidance']}")
    state.critiques.append(f"SANITY CHECKS: {plan['sanity_checks']}")
    state.critiques.append(f"RESEARCH STRATEGY: {plan['research_strategy']}")
    state.critiques.append(f"INVESTIGATION STEPS: {plan['investigation_steps']}")

    # Step 3 — Main research loop
    decision = {"decision": "CONTINUE", "next_focus": QUESTION}
    iteration_count = 0

    for _ in range(MAX_ITERATIONS):
        iteration_count += 1
        print(f"\n{'='*20} ITERATION {iteration_count} {'='*20}")

        state = researcher_agent(state, stock_data, client)
        state = reviewer_agent(state, stock_data, client)
        decision = orchestrator_agent(state, client)

        # Every 3rd iteration run Senior Critic
        if iteration_count % 3 == 0:
            state, critic_result = senior_critic_agent(state, client)
            if critic_result.get("challenged_result"):
                state = adjudicator_agent(state, critic_result["challenged_result"], client)

        if decision["decision"] == "COMPLETE" and iteration_count >= 4:
            print("\nOrchestrator declared COMPLETE")
            break
        
        if iteration_count % 2 == 0: #every 2nd iteration
            print("\n--- Running Computer Verification ---") 
            state = computer_agent(state, stock_data, client)
            state = reviewer_agent(state, stock_data, client)

        state.question = decision["next_focus"]

    # Step 4 — Format final report
    print("\n=== RESEARCH SUMMARY ===")
    print(f"Total Iterations: {state.iteration}")
    print(f"Established Results: {len(state.established_results)}")
    print(f"Critiques Filed: {len(state.critiques)}")

    formatter_agent(state, survey, client)
    
    

if __name__ == "__main__":
    main()
