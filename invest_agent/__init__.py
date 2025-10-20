import ssl
import urllib3
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL 검증 비활성화
ssl._create_default_https_context = ssl._create_unverified_context

