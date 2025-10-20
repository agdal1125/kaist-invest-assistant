import os
import json
import time
from openai import OpenAI
from bs4 import BeautifulSoup
import httpx
from invest_agent.agent.prompt.all import SYSTEM_PROMPT, FUNCTIONS_ALL


class AllAgent:
    def __init__(self, model: str):
        self.model = model
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.curr_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # SSL 검증 비활성화된 HTTP 클라이언트 생성
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=http_client)
        
        self.system_prompt = SYSTEM_PROMPT
        self.functions = FUNCTIONS_ALL
    
    def generate(self, prompt: str, curr_datetime: str = ""):
        if curr_datetime == "":
            curr_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        self.curr_datetime = curr_datetime
        self.curr_date = curr_datetime.split(" ")[0]
        self.curr_time = curr_datetime.split(" ")[1]
        
        self.set_time(curr_datetime)
        self.messages.append({"role": "user", "content": prompt})
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.functions
        )
        self.messages.append(completion.choices[0].message)
        
        content = completion.choices[0].message.content
        tool_calls = completion.choices[0].message.tool_calls
        tool_result_str = ""
        
        if tool_calls:
            for tool_call in tool_calls:
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "command executed"
                })
                tool_result_str += self.parse_tool_calls(tool_call) + "\n"
                tool_result = {
                    "function": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                }
        else:
            tool_calls = None
            tool_result = None
            
        if tool_result and (tool_result["function"] in ["stock_buy", "stock_sell"]):
            valid = self.check_valid_trade(tool_result)
            valid_exchange = self.get_valid_exchange(tool_result["arguments"]["order_code"])
            valid_order_code = self.get_valid_order_code(tool_result["arguments"]["exchange"])
            print(valid, valid_exchange, valid_order_code)
            if not valid:
                content = self.invalid_trade_prompt.format(curr_time=self.curr_time, 
                                                           order_code=tool_result["arguments"]["order_code"],
                                                           valid_exchange=valid_exchange, 
                                                           valid_order_code=valid_order_code)
                self.messages.append({"role": "user", "content": content})
                
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.functions
                )
                self.messages.append(completion.choices[0].message)
                
                content = completion.choices[0].message.content
                tool_calls = completion.choices[0].message.tool_calls
                tool_result_str = ""
                
                if tool_calls:
                    for tool_call in tool_calls:
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "command executed"
                        })
                        tool_result_str += self.parse_tool_calls(tool_call) + "\n"
                        tool_result = {
                            "function": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments)
                        }
                else:
                    tool_calls = None
                    tool_result = None
                
                return {
                    "content": content,
                    "tool_result": tool_result,
                    "tool_result_str": tool_result_str,
                }
                
            
        return {
            "content": content,
            "tool_result": tool_result,
            "tool_result_str": tool_result_str,
        }
    
    def reset(self):
        system_prompt = self.system_prompt.replace("{{today}}", self.today)
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
    
    def parse_tool_calls(self, tool_call):
        if tool_call is None:
            return ""
        result_str = f"다음 함수를 실행합니다: {tool_call.function.name}\n"
        
        args = json.loads(tool_call.function.arguments)
        for key, value in args.items():
            result_str += f"{key}: {value}\n"
        return result_str
    
    def set_time(self, datetime: str):
        date, curr_time = datetime.split(" ")
        system_prompt = self.messages[0]["content"]
        soup = BeautifulSoup(system_prompt, "html.parser")
        time_tag = soup.find("time")
        if time_tag:
            time_tag.string = curr_time
        self.messages[0]["content"] = str(soup)
        
    def get_initial_guide(self):
        return "안녕하세요! 통합 투자 에이전트입니다.\n\n환전, 시장 정보 조회 등 모든 기능을 사용하실 수 있습니다.\n무엇을 도와드릴까요?"
        
if __name__ == "__main__":
    agent = AllAgent(model="gpt-4.1-nano")
    agent.reset()
    response = agent.generate("지금 몇시야?", "2025-07-31 10:14")
    print(response)