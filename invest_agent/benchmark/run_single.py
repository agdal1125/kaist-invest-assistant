import json
import os
from dotenv import load_dotenv
from invest_agent.agent import InvestAgent

load_dotenv()

NHAGENT_HOME = os.getenv("NHAGENT_HOME")
benchmark = f"{NHAGENT_HOME}/invest_agent/benchmark/all/functioncall_single.json"

# load benchmark data
with open(benchmark, "r") as f:
    benchmark_data = json.load(f)

# initialize agent
agent = InvestAgent(model="gpt-4.1-nano")

# evaluate multi turn test case
def evaluate_single(agent, data):
	agent.reset()
	correct = True
 
	prompt = data["initial_prompt"]
	target_tool_function = data["expected_response"]["function_call"]["name"]
	target_tool_arguments = data["expected_response"]["function_call"]["arguments"]
 
	response = agent.generate(prompt)
	tool_result = response["tool_result"]
 
	# print(tool_result)
	# print(target_tool_arguments)

	if tool_result is None:
		correct = False
	else:
		if tool_result["function"] != target_tool_function:
			correct = False
		else:
			for key, value in tool_result["arguments"].items():
				if key not in target_tool_arguments:
					correct = False
					break
				elif value != target_tool_arguments[key]:
					correct = False
					break
	
	return correct
 
corrects = []
for data in benchmark_data:
    agent.reset()
    print("Prompt: ", data["initial_prompt"])
    if not data["multi_turn"]:
        correct = evaluate_single(agent, data)
        print("Correct: ", correct)
        corrects.append(1 if correct else 0)

print(corrects)
print(sum(corrects) / len(corrects))
        