from dotenv import load_dotenv
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[2] / "setup" / ".env"
load_dotenv(ENV_FILE)