from pathlib import Path
import json,sys
from sqlalchemy.schema import CreateTable,CreateIndex
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.main import app
from app.core.database import Base,engine
out=ROOT/'docs/api';out.mkdir(parents=True,exist_ok=True)
schema=app.openapi();(out/'openapi.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
lines=['# API route catalogue','','Generated from the actual FastAPI OpenAPI contract. Bearer JWT is required unless marked public.','','| Method | Path | Access |','| --- | --- | --- |']
for path,ops in sorted(schema['paths'].items()):
 for method,op in ops.items():
  if method in {'get','post','patch','put','delete'}:lines.append(f'| {method.upper()} | `{path}` | {"Bearer JWT" if op.get("security") else "Public"} |')
(out/'ROUTES.md').write_text('\n'.join(lines)+'\n')
ddl=['-- Schema only, not a dump of demonstration or personal records.','-- Generated for the exercised SQLite dialect. Production PostgreSQL is not integration-tested.']
for t in Base.metadata.sorted_tables:
 ddl.append(str(CreateTable(t).compile(engine)).strip()+';')
 ddl.extend(str(CreateIndex(i).compile(engine))+';' for i in t.indexes)
(ROOT/'docs/architecture/SCHEMA.sql').write_text('\n'.join(line.rstrip() for line in '\n\n'.join(ddl).splitlines())+'\n')
print(json.dumps({'paths':len(schema['paths']),'operations':len(lines)-5,'tables':len(Base.metadata.tables)}))
