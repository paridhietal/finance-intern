# Finance Intern

An autonomous multi-agent framework for financial research, inspired by [physics-intern](https://huggingface.co/spaces/huggingface/physics-intern).

Given a stock ticker, the system autonomously researches whether it is a good buy by breaking the problem into sub-questions, forming hypotheses, verifying them adversarially, and producing a structured investment report.

## Architecture

The system uses 7 specialized agents, each with a narrow role and its own context window:

| Agent | Role |
|---|---|
| Surveyor | Maps the research landscape before the loop begins |
| Researcher | Forms hypotheses based on real market data |
| Reviewer | Adversarially verifies or refutes each hypothesis |
| Orchestrator | Decides what to investigate next or declares completion |
| Senior Critic | Periodically audits the entire research state |
| Adjudicator | Independently arbitrates challenges to established results |
| Formatter | Produces the final investment report |

## Key Design Principles

- **Specialization** — each agent attempts one limited task with only the context it needs
- **Checks and balances** — every result gets adversarial review; no single agent can derail the process
- **Fresh context every call** — no conversation history carries over; a structured `ResearchState` persists instead, preventing error compounding

## Project Structure

```
finance-intern/
├── main.py              # entry point and main loop
├── state.py             # ResearchState, Evidence, WorkingHypothesis
├── utils.py             # safe_parse, get_stock_data
├── agents/
│   ├── surveyor.py
│   ├── researcher.py
│   ├── reviewer.py
│   ├── orchestrator.py
│   ├── senior_critic.py
│   ├── adjudicator.py
│   └── formatter.py
└── README.md
```

## Setup

```bash
pip install groq yfinance
export GROQ_API_KEY=your_key_here
python main.py
```

## Example Output

```
===== ITERATION 1 =====
VERIFIED — promoted to Established Result

===== ITERATION 3 =====
=== SENIOR CRITIC ===
Assessment: FLAWED
CHALLENGE FILED against: ...

=== ADJUDICATOR ===
Decision: KEEP

==================================================
FINAL INVESTMENT REPORT
==================================================
Verdict: BUY (high confidence)
Summary: ...
```

## Changing the Stock

Edit `main.py`:

```python
TICKER = "AAPL"   # change to any ticker
```
