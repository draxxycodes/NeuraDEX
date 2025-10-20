from hyperon import MeTTa
import os
import json # Using json for pretty printing the output

# Get the directory of the current script to build the correct path
script_dir = os.path.dirname(os.path.realpath(__file__))
risk_rules_path = os.path.join(script_dir, "metta", "rules", "risk_rules.metta")

# Initialize the MeTTa interpreter
metta = MeTTa()

print(f"--- Loading rules from: {risk_rules_path} ---")

# Load the standard library and our risk rules
metta.run("!(import! &self std)")
with open(risk_rules_path, "r") as f:
    metta.run(f.read())

print("\n--- Running Failing Test Case (High Volatility) ---")

# This is the exact data structure from the failing test
metta_input = "((Asset SHIB (alloc 0.3) (value 3000)) (Asset BTC (alloc 0.7) (value 7000)))"
metta_assertion = f"!(assess-portfolio (AssetList {metta_input}))"

# This list will be populated by the interpreter with the execution trace
trace = []

print(f"\n--- EXECUTING WITH TRACE: {metta_assertion} ---\n")
result = metta.run(metta_assertion, trace)

print("\n\n--- EXECUTION TRACE ---")
# Use json.dumps for a readable, indented view of the trace
print(json.dumps(trace, indent=4))


print(f"\n\n--- FINAL RESULT ---")
print(result)