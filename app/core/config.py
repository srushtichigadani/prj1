from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CAPTCHA_VIDEO_DIR = BASE_DIR / "videos"
CAPTCHA_VIDEO_DIR.mkdir(exist_ok=True)

