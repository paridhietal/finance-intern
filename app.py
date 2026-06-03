import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from state import ResearchState
from utils import get_stock_data
from agents.surveyor import surveyor_agent
from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.reviewer import reviewer_agent
from agents.computer import computer_agent
from agents.orchestrator import orchestrator_agent
from agents.senior_critic import senior_critic_agent
from agents.adjudicator import adjudicator_agent
from agents.formatter import formatter_agent

load_dotenv()

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Finance Intern",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Finance Intern")
st.caption("Autonomous 9-agent financial research system")

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Stock Ticker", value="GOOGL").upper()
    max_iterations = st.slider("Max Iterations", 3, 8, 6)
    api_key = st.text_input("Groq API Key", type="password")
    run_button = st.button("Run Research", type="primary", use_container_width=True)

# ─── MAIN ────────────────────────────────────────────────────────────────────

if run_button:
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar")
        st.stop()

    client = Groq(api_key=api_key)

    # Stock data
    with st.spinner(f"Fetching stock data for {ticker}..."):
        stock_data = get_stock_data(ticker)

    st.subheader(f"📊 {ticker} Stock Data")
    cols = st.columns(5)
    cols[0].metric("Price", f"${stock_data['current_price']}")
    cols[1].metric("P/E Ratio", f"{round(stock_data['pe_ratio'], 2)}")
    cols[2].metric("Revenue Growth", f"{round(stock_data['revenue_growth']*100, 1)}%")
    cols[3].metric("Profit Margins", f"{round(stock_data['profit_margins']*100, 1)}%")
    cols[4].metric("ROE", f"{round(stock_data['return_on_equity']*100, 1)}%")

    st.divider()

    # Pre-loop agents
    col1, col2 = st.columns(2)

    with col1:
        with st.spinner("Surveyor mapping research landscape..."):
            survey = surveyor_agent(f"Is {ticker} a good buy right now?", client)
        with st.expander("🗺️ Surveyor Report"):
            st.write("**Key Techniques:**", survey['key_techniques'])
            st.write("**Known Pitfalls:**", survey['known_pitfalls'])
            st.write("**Guidance:**", survey['research_guidance'])

    with col2:
        with st.spinner("Planner creating research strategy..."):
            plan = planner_agent(f"Is {ticker} a good buy right now?", survey, client)
        with st.expander("📋 Research Plan"):
            st.write("**Strategy:**", plan['research_strategy'])
            st.write("**Investigation Steps:**")
            for step in plan['investigation_steps']:
                st.write(f"- {step}")
            st.write("**Sanity Checks:**")
            for check in plan['sanity_checks']:
                st.write(f"- {check}")

    st.divider()

    # Initialize state
    question = f"Is {ticker} a good buy right now?"
    state = ResearchState(question=question)
    state.critiques.append(f"SURVEYOR GUIDANCE: {survey['research_guidance']}")
    state.critiques.append(f"SANITY CHECKS: {plan['sanity_checks']}")
    state.critiques.append(f"RESEARCH STRATEGY: {plan['research_strategy']}")

    decision = {"decision": "CONTINUE", "next_focus": question}
    iteration_count = 0

    st.subheader("🔄 Research Loop")

    # Main loop
    for _ in range(max_iterations):
        iteration_count += 1

        with st.expander(f"Iteration {iteration_count}", expanded=iteration_count == 1):
            
            with st.spinner("Researcher forming hypothesis..."):
                state = researcher_agent(state, stock_data, client)
            latest = state.hypotheses[-1]
            st.info(f"**Hypothesis:** {latest.claim}")

            with st.spinner("Reviewer checking hypothesis..."):
                state = reviewer_agent(state, stock_data, client)
            status = state.hypotheses[-1].status
            if status == "VERIFIED":
                st.success(f"Reviewer: {status}")
            elif status == "REFUTED":
                st.error(f"Reviewer: {status}")
            else:
                st.warning(f"Reviewer: {status}")

            with st.spinner("Computer running numerical verification..."):
                state = computer_agent(state, stock_data, client)
            st.code(state.hypotheses[-1].evidence[0].content, language="text")

            with st.spinner("Orchestrator deciding next step..."):
                decision = orchestrator_agent(state, client)
            st.write(f"**Orchestrator:** {decision['decision']} — {decision['reason']}")

            if iteration_count % 3 == 0:
                with st.spinner("Senior Critic auditing research state..."):
                    state, critic_result = senior_critic_agent(state, client)
                st.warning(f"**Senior Critic:** {critic_result['assessment']} — {critic_result['reason']}")

                if critic_result.get("challenged_result"):
                    with st.spinner("Adjudicator arbitrating challenge..."):
                        state = adjudicator_agent(state, critic_result["challenged_result"], client)

        if decision["decision"] == "COMPLETE" and iteration_count >= 4:
            break

        state.question = decision["next_focus"]

    st.divider()

    # Final report
    st.subheader("📈 Final Investment Report")

    with st.spinner("Formatter producing final report..."):
        report = formatter_agent(state, survey, client)

    verdict_color = {"BUY": "green", "SELL": "red", "HOLD": "orange"}
    color = verdict_color.get(report['verdict'], "gray")

    st.markdown(f"## Verdict: :{color}[{report['verdict']}] ({report['confidence']} confidence)")
    st.write(report['summary'])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Key Findings")
        for f in report['key_findings']:
            st.write(f"✅ {f}")
    with col2:
        st.subheader("Risks")
        for r in report['risks']:
            st.write(f"⚠️ {r}")

    st.subheader("Recommendation")
    st.write(report['recommendation'])

    st.divider()
    st.subheader("Research Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Iterations", iteration_count)
    c2.metric("Established Results", len(state.established_results))
    c3.metric("Critiques Filed", len(state.critiques))

    if state.established_results:
        with st.expander("📌 All Established Results"):
            for r in state.established_results:
                st.write(f"- {r}")