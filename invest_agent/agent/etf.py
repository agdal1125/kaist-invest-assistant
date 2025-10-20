import os
import json
import time
from datetime import datetime
from openai import OpenAI
from bs4 import BeautifulSoup
import httpx

from invest_agent.workflow.dbagent.db_agent import DBAgent

from invest_agent.agent.prompt.etf.functions_trade_etf import STOCK_BUY, STOCK_SELL
from invest_agent.agent.prompt.etf.trade_time import KRX_TRADE_TIME, NXT_TRADE_TIME, SOR_TRADE_TIME, ORDER_CODE, NEED_PRICE, NO_NEED_PRICE
from invest_agent.agent.prompt.etf.prompt import (
    SYSTEM_PROMPT,
    INVALID_TRADE_PROMPT,
    INITIAL_GUIDE_FORMAT, 
    ETF_INFO_AUGMENTATION_PROMPT
    )


class ETFAgent:
    def __init__(self, model: str):
        self.model = model
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.curr_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # SSL 검증 비활성화된 HTTP 클라이언트 생성
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=http_client)
        
        self.db_agent = DBAgent(model="gpt-4.1-mini")
        
        self.last_etf_info = ""
        
        from invest_agent.agent.prompt.etf.prompt import SYSTEM_PROMPT
        from invest_agent.agent.prompt.etf.prompt import INVALID_TRADE_PROMPT
        self.system_prompt = SYSTEM_PROMPT
        self.invalid_trade_prompt = INVALID_TRADE_PROMPT
        self.functions = [STOCK_BUY, STOCK_SELL]
        
        # Initialize messages
        self.messages = []
        self.reset()
    
    def generate(self, prompt: str, curr_datetime: str = ""):
        # DB 검색
        etf_info = self.db_agent.query_stock_etf(prompt)
        
        print(etf_info)
        
        etf_info_str = ETF_INFO_AUGMENTATION_PROMPT.format(
            etf_info=etf_info,
            last_etf_info=self.last_etf_info
        )
        
        if len(etf_info) > 0:
            self.last_etf_info = etf_info
        
        prompt = prompt + etf_info_str
        print(prompt)
        
        # 시간 설정
        if curr_datetime == "":
            if self.curr_datetime is None or self.curr_datetime == "":
                self.curr_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            curr_datetime = self.curr_datetime
        self.curr_date = curr_datetime.split(" ")[0]
        self.curr_time = curr_datetime.split(" ")[1]
        
        # 메시지 추가
        self.messages.append({"role": "user", "content": prompt})
        
        self.curr_datetime = curr_datetime
        self.set_time(curr_datetime)
        
        # 응답 생성
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.functions
        )
        self.messages.append(completion.choices[0].message)
        
        content = completion.choices[0].message.content
        tool_calls = completion.choices[0].message.tool_calls
        tool_result_str = ""
        
        # 함수 호출
        if tool_calls:
            for tool_call in tool_calls:
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "command executed"
                })
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                arguments["exchange"] = self.get_valid_exchange(arguments["order_code"])[0]
                
                tool_result_str += self.parse_tool_calls(tool_call)
                tool_result_str += f"exchange: {arguments['exchange']}"
                
                tool_result = {
                    "function": function_name,
                    "arguments": arguments
                }
        else:
            tool_calls = None
            tool_result = None
        
        # 응답 반환
        print({
            "content": content,
            "tool_result": tool_result,
            "tool_result_str": tool_result_str,
        })
            
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
        date, time = datetime.split(" ")
        system_prompt = self.messages[0]["content"]
        soup = BeautifulSoup(system_prompt, "html.parser")
        soup.find("date").string = date
        soup.find("time").string = time
        self.messages[0]["content"] = str(soup)
        self.curr_datetime = datetime
        
    def check_valid_trade(self, tool_result):
        exchange = tool_result["arguments"]["exchange"]
        order_code = tool_result["arguments"]["order_code"]
        
        trade_time = KRX_TRADE_TIME if exchange == "KRX" else NXT_TRADE_TIME if exchange == "NXT" else SOR_TRADE_TIME
        
        for timetable in trade_time.values():
            if self.curr_time >= timetable["time"][0] and self.curr_time <= timetable["time"][1]:
                if order_code in timetable["order_code"]:
                    return True
        return False
    
    def get_valid_order_code(self):
        """
        현재 시간을 기반으로 가능한 주문방법들을 안내
        """
        if self.curr_datetime is None or self.curr_datetime == "":
            self.curr_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dt = datetime.strptime(self.curr_datetime, "%Y-%m-%d %H:%M:%S")
        now = dt.time()

        available_codes = set()

        # 세 개의 거래소 모두 확인
        for exchange, trade_time_dict in {
            "KRX": KRX_TRADE_TIME,
            "NXT": NXT_TRADE_TIME,
            "SOR": SOR_TRADE_TIME
        }.items():
            for market, info in trade_time_dict.items():
                start = datetime.strptime(info["time"][0], "%H:%M").time()
                end   = datetime.strptime(info["time"][1], "%H:%M").time()

                if start <= now <= end:
                    available_codes.update(info["order_code"])

        return sorted(available_codes)
    
    def get_initial_guide(self):
        """
        현재 시간을 기반으로 가능한 주문방법들을 안내
        """
        valid_order_code = self.get_valid_order_code()
        valid_order_code = list(valid_order_code)
        
        need_price_name = []
        no_need_price_name = []
        for code in valid_order_code:
            if code in NEED_PRICE:
                need_price_name.append(ORDER_CODE[code])
            else:
                no_need_price_name.append(ORDER_CODE[code])
        
        if len(need_price_name) > 0:
            need_price_str = " | ".join(need_price_name)
        else:
            need_price_str = "가능한 주문이 존재하지 않습니다."
        if len(no_need_price_name) > 0:
            no_need_price_str = " | ".join(no_need_price_name)
        else:
            no_need_price_str = "가능한 주문이 존재하지 않습니다."
        
        return INITIAL_GUIDE_FORMAT.format(curr_time=self.curr_datetime, need_price=need_price_str, no_need_price=no_need_price_str)
        
    def get_valid_exchange(self, order_code):
        """
        주어진 주문 코드에 대해 거래 가능한 거래소를 반환
        """
        if self.curr_datetime is None or self.curr_datetime == "":
            self.curr_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dt = datetime.strptime(self.curr_datetime, "%Y-%m-%d %H:%M:%S")
        now = dt.time()

        available_exchanges = []

        # 세 개의 거래소 모두 확인
        for exchange, trade_time_dict in {
            "KRX": KRX_TRADE_TIME,
            "NXT": NXT_TRADE_TIME,
            "SOR": SOR_TRADE_TIME
        }.items():
            for market, info in trade_time_dict.items():
                start = datetime.strptime(info["time"][0], "%H:%M").time()
                end   = datetime.strptime(info["time"][1], "%H:%M").time()

                if start <= now <= end and order_code in info["order_code"]:
                    available_exchanges.append(exchange)
                    break  # 해당 거래소에서 주문코드가 가능하면 다음 거래소로

        return available_exchanges

if __name__ == "__main__":
    agent = ETFAgent(model="gpt-4.1-nano")
    agent.reset()
    response = agent.generate("지금 몇시야?", "2025-07-31 10:14")
    print(response)