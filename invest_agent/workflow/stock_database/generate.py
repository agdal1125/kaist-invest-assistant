import os
import json
import time
import random
from xml.etree import ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple

from tqdm.auto import tqdm
from openai import OpenAI
from db_prompt import DB_PROMPT

NH_HOME = os.getenv("NH_HOME")

SOURCE_PATH = f"{NH_HOME}/stock_database/stock_data.json"
TARGET_PATH = f"{NH_HOME}/stock_database/stock_korean_name.json"

def parse_stock_korean_fields(s: str) -> Dict[str, Any]:
    wrapped = f"<root>{s}</root>"
    root = ET.fromstring(wrapped)
    name = (root.findtext("Name") or "").strip()
    nickname_raw = (root.findtext("Nickname") or "").strip()
    nicknames = [n.strip() for n in nickname_raw.split(",") if n.strip()] if nickname_raw else []
    return {"name": name, "nicknames": nicknames}

def call_model_with_retry(symbol: str, eng_name: str, max_retries: int = 3, timeout_sec: int = 60) -> Tuple[str, List[str]]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    base_prompt = DB_PROMPT.format(symbol=symbol, name=eng_name)
    xml_hint = """
<Name>정확한 한국어 정식명</Name>
<Nickname>쉼표(,)로 구분된 한국어 별칭들</Nickname>
"""
    retry_hint = "이전 응답이 잘못되었습니다. 위 XML 형식만 출력하세요."

    for attempt in range(1, max_retries + 1):
        prompt = base_prompt + "\n\n" + (xml_hint if attempt == 1 else retry_hint)
        try:
            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout_sec,
            )
            content = resp.choices[0].message.content
            parsed = parse_stock_korean_fields(content)
            if parsed["name"]:
                return parsed["name"], parsed["nicknames"]
            raise ValueError("Empty name")
        except Exception:
            if attempt < max_retries:
                time.sleep((2 ** (attempt - 1)) + random.uniform(0, 0.5))
            else:
                return eng_name, []

def process_one(item: Dict[str, Any]) -> Dict[str, Any]:
    symbol = item.get("symbol", "")
    eng_name = item.get("name", "")
    name_ko, nicknames = call_model_with_retry(symbol, eng_name)
    out = dict(item)
    out["name"] = name_ko
    out["nicknames"] = nicknames
    return out

def main(max_workers: int = None):
    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    results: List[Dict[str, Any]] = [None] * len(data)

    if max_workers is None:
        max_workers = min(8, os.cpu_count() or 4)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one, item): idx for idx, item in enumerate(data)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing", unit="stock"):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = data[idx]

            # 매번 파일 업데이트
            with open(TARGET_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    [r if r is not None else d for r, d in zip(results, data)],
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

if __name__ == "__main__":
    main()
