import json
import os
from dotenv import load_dotenv
from invest_agent.agent.agent import InvestAgent
from invest_agent.agent.human import Human

load_dotenv()

NHAGENT_HOME = os.getenv("NHAGENT_HOME")
MAX_TURN = 3
benchmark = f"{NHAGENT_HOME}/invest_agent/benchmark/trade_irrational/trade_multi.json"

# load benchmark data
with open(benchmark, "r") as f:
    benchmark_data = json.load(f)

# initialize agent
agent = InvestAgent(model="gpt-4.1-mini", mode="trade")
human = Human(model="gpt-4.1-mini")

# evaluate multi turn test case
def evaluate_multi(agent, human, data):
	agent.reset()
	correct = True
 
	prompt = data["initial_prompt"]
	target_tool_function = data["expected_response"]["function_call"]["name"]
	target_tool_arguments = data["expected_response"]["function_call"]["arguments"]
	additional_information = data["additional_information"]
 
	response = agent.generate(prompt, curr_datetime=data["current_time"])
	tool_result = response["tool_result"]
 
	# print(tool_result)
	# print(target_tool_arguments)
 
	conversation = []
	conversation.append({"role": "user", "content": prompt})

	for i in range(MAX_TURN):
		response = agent.generate(prompt)
  
		print("Agent: ", response["content"])
  
		tool_result = response["tool_result"]
		if tool_result is not None:
			break
		conversation.append({"role": "assistant", "content": response["content"]})
		
		human_response = human.generate(conversation, additional_information)
  
		print("Human: ", human_response)
  
		conversation.append({"role": "user", "content": human_response})

		prompt = human_response
  
	print("Tool result: ", response["tool_result_str"])
  

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
    if data["multi_turn"]:
        correct = evaluate_multi(agent, human, data)
        print("Correct: ", correct)
        corrects.append(1 if correct else 0)
    print("-"*100)

print(corrects)
print(sum(corrects) / len(corrects))
        