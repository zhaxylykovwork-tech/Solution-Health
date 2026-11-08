"""Submission checks. Requires PyYAML, jsonschema and openapi-spec-validator."""
from pathlib import Path
import copy
import re
import xml.etree.ElementTree as ET
import yaml
from jsonschema import Draft4Validator, FormatChecker, RefResolver
from openapi_spec_validator import validate

ROOT=Path(__file__).resolve().parents[1]
documents=[]
for path in sorted((ROOT/'Task3.3').glob('*.yaml')):
    doc=yaml.safe_load(path.read_text(encoding='utf-8-sig'))
    validate(doc)
    assert doc['security']==[{'bearerAuth':[]}]
    op=doc['paths']['/appointments']['get']
    assert {p['name'] for p in op['parameters']}=={'status','limit','offset'}
    for code,res in op['responses'].items():
        media=res['content']['application/json']
        Draft4Validator(media['schema'],resolver=RefResolver.from_schema(doc),format_checker=FormatChecker()).validate(media['example'])
    documents.append(doc)
    print(path.relative_to(ROOT),': schema + response examples PASS')
left,right=map(copy.deepcopy,documents)
assert {left.pop('openapi'),right.pop('openapi')}=={'3.0.3','3.2.0'}
assert left==right
print('Same business API in both OpenAPI versions: PASS')

links=0
for md in ROOT.rglob('*.md'):
    if '.tools' in md.parts:continue
    for raw in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',md.read_text(encoding='utf-8-sig')):
        if '://' in raw or raw.startswith('#'):continue
        target=raw.split('#')[0]
        assert (md.parent/target).exists(),(md.relative_to(ROOT),target)
        links+=1
for directory in ['Task1','Task2','Task3.1','Task3.2','Task3.3','Task4.1','Task4.2','Task4.3']:
    assert (ROOT/directory/'README.md').is_file()
for drawio in ROOT.glob('Task*/*.drawio'):
    xml=ET.parse(drawio);model=xml.find('.//mxGraphModel')
    width,height=float(model.get('pageWidth')),float(model.get('pageHeight'))
    ids=[c.get('id') for c in xml.findall('.//mxCell')]
    assert len(ids)==len(set(ids)),drawio
    for geom in xml.findall('.//mxCell[@vertex="1"]/mxGeometry'):
        x,y,w,h=[float(geom.get(k,'0')) for k in ['x','y','width','height']]
        assert x>=0 and y>=0 and x+w<=width and y+h<=height,(drawio,x,y,w,h)
    ET.parse(drawio.with_suffix('.svg'))
    for ext in ['.pdf','.png','.svg']:
        assert drawio.with_suffix(ext).stat().st_size>1000
print(f'Local links: {links} PASS; 8 task directories PASS; 5 editable diagrams + exports PASS')
assert len(list(ROOT.glob('Task*/*.drawio')))==5
print('All automated submission checks PASS')
