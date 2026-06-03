import json
import sys
import io
import traceback
from state import ResearchState, Evidence, WorkingHypothesis
from utils import safe_parse
from datetime import datetime


def execute_code(code: str) -> dict:
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    result = {"output": "", "error": None, "success": False}

    try:
        safe_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "float": float,
                "int": int,
                "str": str,
                "list": list,
                "dict": dict,
                "zip": zip,
                "enumerate": enumerate,
            }
        }
        exec(code, safe_globals)
        result["output"] = buffer.getvalue()
        result["success"] = True
    except Exception as e:
        result["error"] = traceback.format_exc()
        result["success"] = False
    finally:
        sys.stdout = old_stdout

    return result


def computer_agent(state: ResearchState, stock_data: dict, client) -> ResearchState:

    context = f"""
    Research Question: {state.question}
    Stock Data Available: {json.dumps(stock_data)}
    Established Results: {state.established_results}
    Latest Hypothesis: {state.hypotheses[-1].claim if state.hypotheses else "None"}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": """You are a financial computing agent.
                Write Python code to numerically verify financial claims.

                Rules:
                - Only use basic Python, no imports
                - Use stock_data values directly as numbers in your code
                - Always print results clearly
                - Keep code simple and short

                Respond ONLY with valid JSON:
                {
                    "code": "your python code here",
                    "what_it_tests": "what this code verifies"
                }"""
            },
            {
                "role": "user",
                "content": f"""Write code to numerically verify claims about this stock: {context}"
                 - current_price = {stock_data['current_price']}
                - pe_ratio = {stock_data['pe_ratio']}
                - revenue_growth = {stock_data['revenue_growth']}
                - profit_margins = {stock_data['profit_margins']}
                - return_on_equity = {stock_data['return_on_equity']}
                - earnings_growth = {stock_data['earnings_growth']}
                - free_cashflow = {stock_data['free_cashflow']}
                
                Calculate and print: PEG ratio, intrinsic value estimate, 
                and whether each metric is above or below typical benchmarks."""
            }
        ]
    )

    #Get raw code directly - no JSON parsing needed
    code = response.choices[0].message.content.strip()
    
    #Strip markdown if present
    if code.startswith("```"):
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[6:]
        elif code.startswith("json"):
            code = code[4:]
    code = code.strip()
    
    #If model returned JSON instead of raw code, extract the code field
    if code.startswith("{"):
        try:
            parsed = json.loads(code.replace('\n', '\\n'))
            code = parsed.get("code", code).replace('\\n', '\n')
        except:
            #Try extracting code between quotes manually
            import re
            match = re.search(r'"code":\s*"(.*?)"(?:,|\s*})', code, re.DOTALL)
            if match:
                code = match.group(1).replace('\\n', '\n')
            
    print(f"\n=== COMPUTER AGENT ===")
    print(f"Generate Code:\n{code}\n")
    
    #Step 2 - Execute it
    execution = execute_code(code)

    if execution["success"]:
        print(f"Output: {execution['output']}")
        numerical_evidence = execution["output"]
    else:
        print(f"Execution failed: {execution['error']}")
        numerical_evidence = f"Code execution failed: {execution['error'][:100]}"

    evidence = Evidence(
        source="computer",
        content=f"Numerical verification: {numerical_evidence}",
        timestamp=str(datetime.now())
    )

    hypothesis = WorkingHypothesis(
        claim=f"Numerical analysis: {numerical_evidence[:100]}",
        evidence=[evidence],
        status="unverified"
    )

    state.hypotheses.append(hypothesis)
    state.iteration += 1
    state.save()

    return state