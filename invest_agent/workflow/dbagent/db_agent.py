import os
import json
import copy
import openai
from pathlib import Path
import httpx

from invest_agent.workflow.dbagent.prompt import STOCK_PROMPT, ETF_PROMPT
from invest_agent.workflow.stock_database.seach_algo import StockMatcher

# 프로젝트 루트 경로 자동 찾기
NH_HOME = os.getenv("NH_HOME")
if NH_HOME is None:
    # 현재 파일의 위치에서 프로젝트 루트를 찾습니다
    # db_agent.py -> dbagent -> workflow -> invest_agent -> project_root
    NH_HOME = str(Path(__file__).parent.parent.parent.parent)

TICKER_DB = json.load(open(f"{NH_HOME}/invest_agent/workflow/stock_database/stock_database.json", "r", encoding='utf-8'))

ETF_DB = json.load(open(f"{NH_HOME}/invest_agent/workflow/etf/etf_dict.json", "r", encoding='utf-8'))
ETF_NAME_DB = json.load(open(f"{NH_HOME}/invest_agent/workflow/etf/etf_name_database.json", "r", encoding='utf-8'))
ETF_STOCK_DB = json.load(open(f"{NH_HOME}/invest_agent/workflow/etf/etf_stock_database.json", "r", encoding='utf-8'))


class DBAgent:
    def __init__(self, model: str, debug: bool = False):
        self.model = model
        # SSL 검증 비활성화된 HTTP 클라이언트 생성
        http_client = httpx.Client(verify=False)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=http_client)
        self.messages = []
        self.stock_prompt = STOCK_PROMPT
        self.etf_prompt = ETF_PROMPT
        self.stock_matcher = StockMatcher(TICKER_DB)
        self.etf_name_matcher = StockMatcher(ETF_NAME_DB)
        self.etf_stock_matcher = StockMatcher(ETF_STOCK_DB)
        self.debug = debug
        
    def generate(self, sentence: str, mode: str = "stock"):
        """
        Extract stock-name related keywords from the sentence
        """
        if mode == "stock":
            prompt = self.stock_prompt.format(sentence=sentence)
        elif mode == "etf":
            prompt = self.etf_prompt.format(sentence=sentence)
        else:
            raise ValueError(f"Invalid mode: {mode}")
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(model=self.model, messages=self.messages)
        key_words = response.choices[0].message.content
        if self.debug:
            print("추출된 키워드: ", key_words)
        return key_words
    
    def query_stock(self, sentence: str):
        """
        Seach for stock
        """
        stock = self.generate(sentence, mode="stock")
        
        query_results = self.stock_matcher.search(stock)
        full_info = []
        ticker_list = []
        for query_result in query_results:
            if self.debug:
                full_info.append({"티커명": query_result[0], 
                            "유사도": query_result[1],
                            "query target": query_result[2]})
            else:
                full_info.append({"티커명": query_result[0], 
                            "유사도": query_result[1],})
            ticker_list.append(query_result[0])
        return {"full_info": full_info, "ticker_list": ticker_list}
    
    def query_etf_name(self, sentence: str, top_k: int = 3):
        """
        Seach for ETF name
        """
        etf = self.generate(sentence, mode="etf")
        query_results = self.etf_name_matcher.search(etf, top_k=top_k)
        etf_list = [query_result[0] for query_result in query_results]
        
        if self.debug:
            print("검색된 etf_list: ", etf_list)
            
        def _get_etf_infos(etf_name):
            results = [] # list of [etf_name, etf_code, composision_ratio]
            for etf_name_db, etf_info in ETF_DB.items():
                if etf_name == etf_name_db:
                    results.append([etf_name, etf_info["etf_code"], etf_info["ratio"]])
            return results
        
        results = []
        for etf_name in etf_list:
            etf_infos = _get_etf_infos(etf_name)
            if len(etf_infos) > 0:
                for etf_info in etf_infos:
                    results.append({"ETF코드": etf_info[1], "ETF명": etf_info[0], "구성 비중": etf_info[2]})
                    
        return results[:min(1, len(results))]
    
    def query_stock_etf(self, sentence: str, top_k: int = 3):
        stock = self.generate(sentence, mode="stock")
        query_results = self.etf_stock_matcher.search(stock, top_k=top_k)
        stock_list = [query_result[0] for query_result in query_results]
        
        if self.debug:
            print("검색된 stock_list: ", stock_list)
        
        def _get_etf_infos(stock_name):
            results = [] # list of [etf_name, etf_code, composision_ratio]
            for etf_name, etf_info in ETF_DB.items():
                if stock_name in etf_info["ratio"]:
                    composition_ratio = etf_info["ratio"][stock_name]
                    etf_code = etf_info["etf_code"]
                    results.append([etf_name, etf_code, composition_ratio])
            # conposition rate 기준으로 정렬
            results.sort(key=lambda x: x[2], reverse=True)
            return results[:min(5, len(results))]
        
        results = []
        for stock_name in stock_list:
            etf_infos = _get_etf_infos(stock_name)
            if len(etf_infos) > 0:
                for etf_info in etf_infos:
                    results.append({"ETF코드": etf_info[1], "관련 종목 명": stock_name, "ETF명": etf_info[0], "구성 비중": etf_info[2]})
                    
        results = results[:min(top_k * 5, len(results))]
        return results
    
if __name__ == "__main__":
    db_agent = DBAgent(model="gpt-4.1-mini", debug=True)
    
    # Stock 검색 예시
    stock_list = db_agent.query_stock("삼전 4주 구매해줘")
    print(stock_list["full_info"][:min(3, len(stock_list["full_info"]))])
    
    # ETF 검색 예시 (이름기반 검색)
    # etf_list = db_agent.query_etf_name("KODEX 증권 ETF의 정보를 알려줘")
    # print(etf_list)
    
    # ETF 검색 예시 (종목기반 검색)
    # etf_list = db_agent.query_stock_etf("POSCO홀딩스 관련 ETF의 코드를 알려줘")
    # print(etf_list)
    