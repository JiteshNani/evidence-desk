import json
from pathlib import Path
from core import EvidenceDesk

def run():
    fixture=json.loads(Path('sample.json').read_text())
    desk=EvidenceDesk(fixture['documents'])
    results=[]
    for c in fixture['cases']:
        a=desk.answer(c['question'])
        correct=(a['status']=='abstained') if c['source'] is None else (a['status']=='answered' and a['citations'][0]['source']==c['source'])
        results.append({'question':c['question'],'expected_source':c['source'],'correct':correct,**a})
    ablation={}
    known=[c for c in fixture['cases'] if c['source']]
    for mode in ['tfidf','bm25','hybrid']:
        ablation[mode]=sum(bool(h:=desk.retrieve(c['question'],mode=mode)) and h[0]['source']==c['source'] for c in known)/len(known)
    report={'fixture':'six handcrafted cases; not a held-out real-world benchmark','case_count':len(results),'correct':sum(r['correct'] for r in results),'retrieval_top1':ablation,'cases':results}
    Path('evaluation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))

if __name__=='__main__':run()
