import os
import json
import re
import unicodedata
from collections import defaultdict
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

NH_HOME = os.getenv("NH_HOME")

# -------- 1) 정규화 --------
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    s = re.sub(r"[^0-9a-z가-힣]+", " ", s)     # 한/영/숫자만
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" 플랫폼 스", " 플랫폼스").replace(" 플랫폼 즈", " 플랫폼즈")
    s = s.replace(" 주식 회사", " ").replace(" 회사", " ").replace(" 사", " ")
    return s.replace(" ", "")  # 최종적으로 공백 제거(검색용)

# -------- 2) 인덱싱 --------
class StockMatcher:
    def __init__(self, ticker_to_aliases: dict):
        self.ticker_to_aliases = {}
        self.alias_records = []      # [(norm_alias, raw_alias, ticker), ...]
        self.exact_map = defaultdict(set)

        # 별칭 확장 + 정규화
        for ticker, aliases in ticker_to_aliases.items():
            pool = set(aliases) | {ticker}
            normed = []
            for a in pool:
                na = norm(a)
                if na:
                    normed.append((na, a))
                    self.exact_map[na].add(ticker)
            self.ticker_to_aliases[ticker] = [a for _, a in normed]
            for na, ra in normed:
                self.alias_records.append((na, ra, ticker))

        # TF-IDF(문자 n-gram)
        self.corpus = [r[0] for r in self.alias_records]
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2,4))
        self.tfidf = self.vectorizer.fit_transform(self.corpus)

    # -------- 3) 검색 --------
    def search(self, query: str, top_k=5):
        qn = norm(query)
        if not qn:
            return []

        # A) 정확/프리픽스 힌트
        exact_tickers = self.exact_map.get(qn, set())
        prefix_hits = [i for i,(na,_,_) in enumerate(self.alias_records) if na.startswith(qn) or qn in na]

        # B) TF-IDF 후보(코사인)
        qv = self.vectorizer.transform([qn])
        cos = cosine_similarity(qv, self.tfidf).ravel()
        tfidf_top_idx = cos.argsort()[::-1][:200]

        # C) 퍼지매칭 후보
        candidates = set(prefix_hits) | set(tfidf_top_idx)
        fuzzy_scores = np.zeros(len(self.alias_records))
        for i in candidates:
            na = self.alias_records[i][0]
            fuzzy_scores[i] = fuzz.partial_ratio(qn, na) / 100.0

        # 최종 별칭 스코어 결합
        scores = 0.9*cos + 0.7*fuzzy_scores
        for i in prefix_hits: scores[i] += 0.6
        for i,(na,_,_) in enumerate(self.alias_records):
            if na == qn: scores[i] += 1.0  # exact boost

        # 티커 단위 집계(최고 스코어 사용)
        ticker_best = defaultdict(float)
        ticker_alias = {}
        for i, s in enumerate(scores):
            if s <= 0: continue
            _, raw, ticker = self.alias_records[i]
            if s > ticker_best[ticker]:
                ticker_best[ticker] = s
                ticker_alias[ticker] = raw

        # 랭킹 및 임계값 필터
        ranked = sorted(ticker_best.items(), key=lambda x: x[1], reverse=True)[:top_k]
        ranked = [(t, sc, ticker_alias[t]) for t, sc in ranked if sc >= 0.05]
        return ranked

if __name__ == "__main__":
    
    DB_PATH = f"{NH_HOME}/invest_agent/workflow/stock_database/stock_database.json"
    with open(DB_PATH, "r") as f:
        ticker_db = json.load(f)
    
    matcher = StockMatcher(ticker_db)

    print(matcher.search("마소"))
    print(matcher.search("엔비"))
    print(matcher.search("팔란"))
