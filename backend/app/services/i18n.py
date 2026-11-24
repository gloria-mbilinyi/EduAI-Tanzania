import json
from pathlib import Path
SW=json.loads(Path(__file__).with_name('sw.json').read_text(encoding='utf-8'))
def translate(value,language):return SW.get(value,value) if language.startswith('sw') else value
