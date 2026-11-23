import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{ROOT / "eduai.db"}')
PRODUCTION = os.getenv('APP_ENV') == 'production'
JWT_SECRET = os.getenv('JWT_SECRET', '')
if len(JWT_SECRET) < 32:
    if PRODUCTION:
        raise RuntimeError('Production requires JWT_SECRET with at least 32 characters')
    path = ROOT / '.local-secret'
    if not path.exists():
        path.write_text(secrets.token_hex(32), encoding='utf-8')
    JWT_SECRET = path.read_text(encoding='utf-8').strip()
DEMO_PAYMENTS = not PRODUCTION and os.getenv('DEMO_PAYMENTS', 'true').lower() == 'true'
UPLOADS = ROOT / 'uploads'
FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://127.0.0.1:5173')
