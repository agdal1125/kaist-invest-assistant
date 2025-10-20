import os
import json
import time
from openai import OpenAI
import httpx
from invest_agent.agent.prompt.human import SYSTEM_PROMPT_HUMAN, USER_PROMPT_HUMAN

class Human:
    def __init__(self, model: str):
        self.model = model
        # SSL 검증 비활성화된 HTTP 클라이언트 생성
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=http_client)
        self.messages = []
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.system_prompt = SYSTEM_PROMPT_HUMAN
        self.user_prompt = USER_PROMPT_HUMAN
        
    def generate(self, conversation: list, additional_information: dict):
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        additional_information = json.dumps(additional_information, ensure_ascii=False)
        
        prompt = self.user_prompt.format(conversation=conversation, additional_information=additional_information)
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt}, {"role": "user", "content": prompt}],
        )
        
        return completion.choices[0].message.content
    
if __name__ == "__main__":
    human = Human(model="gpt-4.1-nano")
    conversation = [
        {"role": "user", "content": "오늘 날짜는 뭐야?"},
        {"role": "assistant", "content": "오늘 날짜는 2025-07-02 입니다. 구매하고싶은 주식이 있으신가요?"}
    ]
    additional_information = {"stock": "된장블루베리개구리를 10주 사고싶어."}
    response = human.generate(conversation, additional_information)
    print(response)