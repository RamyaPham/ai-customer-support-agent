import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
REFUND_WINDOW_DAYS = int(os.getenv("REFUND_WINDOW_DAYS", "30"))
ESCALATION_THRESHOLD = float(os.getenv("ESCALATION_THRESHOLD", "500"))
