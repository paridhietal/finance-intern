# Finance Intern

> *What if you had a team of 9 analysts working around the clock on a single stock — each one checking the other's work, arguing over conclusions, running their own calculations, and refusing to sign off until the answer was actually good?*

That's finance-intern. A fully autonomous multi-agent financial research system that takes a stock ticker and produces a structured investment report — without a human in the loop.

---

## The Problem With Single-Agent AI

Most AI finance tools work like this:

```
You → "Is Apple a good buy?" → LLM → "Yes, Apple looks great!" → You
```

One agent. One pass. No checks. No pushback. The LLM confidently tells you what you want to hear.

finance-intern works differently. It's built on a simple idea: **no single agent should be trusted.**

---

## How It Works

Nine agents. Each one narrow, specialized, and skeptical of the others.

| Agent | Role |
|---|---|
| **Surveyor** | Maps the research landscape before anything begins — techniques, pitfalls, sanity checks |
| **Planner** | Lays out the investigation strategy and creates pass/fail sanity checks the answer must satisfy |
| **Researcher** | Forms hypotheses from real market data, exploring a new angle every iteration |
| **Reviewer** | Adversarially challenges every hypothesis — VERIFIED, REFUTED, or INCONCLUSIVE |
| **Computer** | Writes and executes real Python code to verify claims numerically |
| **Orchestrator** | Reads the full research state and decides what happens next — CONTINUE or COMPLETE |
| **Senior Critic** | Periodically audits whether the entire research direction makes sense |
| **Adjudicator** | Independently arbitrates when an Established Result gets challenged |
| **Formatter** | Produces the final report — or bounces back if the results are incomplete |

A hypothesis doesn't become an Established Result until it survives the Reviewer. An Established Result doesn't stay established if the Senior Critic challenges it — it goes to the Adjudicator for independent evaluation. The Formatter can't produce a report until the Orchestrator declares research complete.

**Claims can go backwards, not just forwards.**

---

## Three Design Principles

**1. Specialization**
Each LLM call attempts exactly one thing and receives only the context it needs. The Researcher never sees the Reviewer's reasoning. The Adjudicator never sees the Orchestrator's strategy. Narrow remit, isolated context.

**2. Checks and Balances**
Every result gets adversarial review. A Senior Critic audits the whole research direction every 3 iterations. An independent Adjudicator handles disputes between the Critic and Established Results. No single agent can derail the process.

**3. Fresh Context Every Call**
No conversation history carries over between agents. A structured `ResearchState` object persists instead — the accumulated results, hypotheses, critiques — and a carefully assembled context is built from it for each new call.

This prevents the single most common failure mode in multi-agent systems: **error compounding.** One wrong assumption in a long conversation becomes the foundation for every subsequent answer. Fresh context kills that problem at the root.

---

## The Research Loop

```
Before the loop:
  Surveyor  → maps techniques, pitfalls, sanity checks
  Planner   → builds investigation strategy + sanity checks

Main loop (repeats until Orchestrator says COMPLETE):
  Researcher   → forms a NEW hypothesis from real market data
  Reviewer     → VERIFIED / REFUTED / INCONCLUSIVE
  Computer     → writes + executes Python to verify numerically
  Orchestrator → CONTINUE or COMPLETE?

  Every 3rd iteration:
    Senior Critic → audits entire research state
    Adjudicator   → arbitrates if an Established Result is challenged

After the loop:
  Formatter → structured investment report
```

---

## The Computer Agent

This is the most interesting part. The Computer agent doesn't just reason — it **writes and runs its own Python code** to verify claims numerically.

Given real stock data, it generates code like this:

```python
# Generated autonomously by the Computer agent
pe_ratio = 29.23
earnings_growth = 0.82

peg_ratio = pe_ratio / earnings_growth
print('PEG ratio:', peg_ratio)  # → 35.65

intrinsic_value = (free_cashflow / 1e9) * 10
print('Intrinsic value estimate: $', intrinsic_value)  # → $279.21B

print('Is PEG below benchmark of 1?', peg_ratio < 1)   # → False
print('Are profit margins above 25%?', profit_margins > 0.25)  # → True
```

Then it executes that code in a sandboxed environment and feeds the numerical output back into the ResearchState as evidence. No hallucinated numbers — actual computed results.

---

## Example Output

```
=== SURVEYOR REPORT ===
Key Techniques: Fundamental Analysis, Technical Analysis, Quantitative Modeling...
Known Pitfalls: Confirmation Bias, Overreliance on Historical Data...

=== PLANNER ===
Strategy: Multi-faceted approach combining fundamental and quantitative analysis
Investigation Steps:
  - Step 1: Analyze profitability metrics — ROE, profit margins, free cash flow
  - Step 2: Evaluate valuation metrics — P/E ratio, PEG ratio, market cap
  - Step 3: Assess risk factors — debt-to-equity, earnings growth sustainability
Sanity Checks:
  - Verify P/E against industry average
  - Check PEG ratio relative to growth rate
  - Confirm free cash flow supports valuation

==================== ITERATION 1 ====================
Hypothesis: GOOGL is a good buy based on ROE of 38.88%, profit margins
            of 37.91%, and free cash flow of $27.92B
VERIFIED — promoted to Established Result

==================== ITERATION 2 ====================
Hypothesis: GOOGL valuation metrics suggest overvaluation at current price
REFUTED — hypothesis relies on data points not available

--- Running Computer Verification ---
=== COMPUTER AGENT ===
Generated Code:
  peg_ratio = pe_ratio / earnings_growth      # → 35.65
  intrinsic_value = (free_cashflow / 1e9) * 10 # → $279.21B

Output:
  PEG ratio: 35.65 — above typical benchmark of 1
  Intrinsic value estimate below current price
  PE ratio above benchmark | Profit margins above benchmark
  Return on equity above benchmark | Free cash flow above benchmark

=== SENIOR CRITIC === (iteration 3)
Assessment: FLAWED
Reason: Over-reliance on profitability metrics without considering
        macro environment or competitive threats
Challenge filed against: "GOOGL is a good buy based on ROE of 38.88%..."

=== ADJUDICATOR ===
Decision: KEEP
Reason: Multiple independent metrics support the claim despite the challenge

==================================================
FINAL INVESTMENT REPORT
==================================================
Verdict: HOLD (medium confidence)

Summary: GOOGL's strong profitability metrics are offset by a PEG ratio
of 35.65 and an intrinsic value estimate below current price, suggesting
limited upside at current levels...

Key Findings:
  ✅ ROE of 38.88% significantly above 20% benchmark
  ✅ Profit margins of 37.91% indicate strong operational efficiency
  ✅ Free cash flow of $27.92B supports long-term investment capacity

Risks:
  ⚠️ PEG ratio of 35.65 suggests potential overvaluation
  ⚠️ Intrinsic value estimate below current market price
==================================================
```

---

## Project Structure

```
finance-intern/
├── main.py                  ← entry point, main research loop (CLI)
├── app.py                   ← Streamlit web UI
├── state.py                 ← ResearchState, Evidence, WorkingHypothesis
├── utils.py                 ← safe_parse, get_stock_data
├── requirements.txt
├── agents/
│   ├── surveyor.py          ← maps research landscape
│   ├── planner.py           ← builds investigation strategy
│   ├── researcher.py        ← forms hypotheses
│   ├── reviewer.py          ← adversarial verification
│   ├── computer.py          ← writes + executes Python
│   ├── orchestrator.py      ← controls the loop
│   ├── senior_critic.py     ← periodic audit
│   ├── adjudicator.py       ← dispute resolution
│   └── formatter.py         ← final report
└── README.md
```

---

## Setup

```bash
git clone https://github.com/paridhietal/finance-intern
cd finance-intern
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

**Run via CLI:**
```bash
python main.py
```

**Run via Web UI:**
```bash
streamlit run app.py
```

Change the stock in `main.py`:
```python
TICKER = "AAPL"   # or TSLA, MSFT, AMZN...
```

---

## Why This Architecture

The design is inspired by [physics-intern](https://huggingface.co/spaces/huggingface/physics-intern), which applies the same multi-agent orchestration pattern to theoretical physics problems.

The core insight: **research is adversarial by nature.** Good science doesn't produce conclusions — it tries to destroy them. finance-intern encodes that into the architecture itself.

The **Senior Critic + Adjudicator** pattern solves a real problem. Without it, a reviewer that's too strict would block all progress. A reviewer that's too lenient would verify everything. The Adjudicator breaks that deadlock — a third party who sees both the original evidence and the critique, and makes a final independent call.

The **Computer agent** solves a different problem — LLMs hallucinate numbers. By forcing numerical claims to be verified through actual code execution, the system catches errors that pure reasoning would miss. A PEG ratio of 35.65 means something very different from 1.2, and no amount of careful prompting catches that as reliably as running the math.

---

## Built With

- [Groq](https://console.groq.com) — free LLM inference (Llama 3.3 70B)
- [yfinance](https://github.com/ranaroussi/yfinance) — real market data
- [Streamlit](https://streamlit.io) — web UI
- Python — everything else

---

*Built as a portfolio project exploring multi-agent orchestration, adversarial review patterns, and structured state management in LLM systems.*
