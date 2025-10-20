import ssl
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL 검증 비활성화
ssl._create_default_https_context = ssl._create_unverified_context

from .all import AllAgent
from .stock import StockAgent
from .etf import ETFAgent
from .human import Human

__all__ = [
    "AllAgent",
    "StockAgent",
    "ETFAgent",
    "Human",
]