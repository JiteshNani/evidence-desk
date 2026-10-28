"""Development-selected coverage gate; separately reported regression queries.

Handcrafted fixtures test software behavior, not real-world generalization.
The query split is not an independently curated or blinded benchmark.
"""
import json
import math
from pathlib import Path
from time import perf_counter
import numpy as np
from core import EvidenceDesk

ROOT = Path(__file__).resolve().parent


def retrieval_metrics(ranked_sources, relevant, k=3):
    """Document-level binary relevance; repeated chunks count once."""
    ranked = list(dict.fromkeys(ranked_sources))[:k]
    relevant = set(relevant)
    if not relevant:
        return None
    hits = [int(s in relevant) for s in ranked]
    recall = sum(hits) / len(relevant)
    mrr = next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0)
    dcg = sum(hit / math.log2(i + 2) for i, hit in enumerate(hits))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return {'recall_at_3': recall, 'mrr_at_3': mrr, 'ndcg_at_3': dcg / ideal}


def evaluate(desk, cases, threshold):
    rows = []
    for case in cases:
        started = perf_counter()
        answer = desk.answer(case['question'], min_coverage=threshold)
        elapsed = (perf_counter() - started) * 1000
        expected = case['sources']
        predicted = [c['source'] for c in answer['citations']]
        correct = (answer['status'] == 'abstained') if not expected else (
            answer['status'] == 'answered' and predicted[0] in expected)
        row = {**case, 'status': answer['status'], 'predicted_sources': predicted,
               'correct': correct, 'latency_ms': round(elapsed, 3), 'retrieval': {}}
        for mode in ('tfidf', 'bm25', 'hybrid'):
            hits = desk.retrieve(case['question'], k=10, mode=mode)
            row['retrieval'][mode] = retrieval_metrics([h['source'] for h in hits], expected)
        rows.append(row)
    return rows


def summarize(rows):
    answerable = [r for r in rows if r['sources']]
    unknown = [r for r in rows if not r['sources']]
    summary = {'case_count': len(rows), 'correct_source_or_abstention': sum(r['correct'] for r in rows),
               'answerable_count': len(answerable), 'unanswerable_count': len(unknown),
               'false_abstentions': sum(r['status'] == 'abstained' for r in answerable),
               'false_acceptances': sum(r['status'] == 'answered' for r in unknown),
               'latency_ms': {'p50': float(np.percentile([r['latency_ms'] for r in rows], 50)),
                              'p95': float(np.percentile([r['latency_ms'] for r in rows], 95))},
               'retrieval': {}}
    for mode in ('tfidf', 'bm25', 'hybrid'):
        summary['retrieval'][mode] = {key: float(np.mean([r['retrieval'][mode][key] for r in answerable]))
                                     for key in ('recall_at_3', 'mrr_at_3', 'ndcg_at_3')}
    summary['by_challenge'] = {tag: {'count': len(group), 'correct': sum(r['correct'] for r in group)}
        for tag in sorted({r['challenge'] for r in rows})
        if (group := [r for r in rows if r['challenge'] == tag])}
    return summary


def run():
    fixture = json.loads((ROOT / 'evaluation_suite.json').read_text(encoding='utf-8'))
    dev, test = fixture['development'], fixture['test']
    if set(c['question'].strip().lower() for c in dev) & set(c['question'].strip().lower() for c in test):
        raise ValueError('duplicate query across development and test')
    desk = EvidenceDesk(fixture['documents'])
    candidates = []
    for threshold in (0.25, 0.5, 0.75, 1.0):
        summary = summarize(evaluate(desk, dev, threshold))
        candidates.append({'threshold': threshold, **summary})
    # Most correct dev decisions; ties favor fewer false accepts, then stricter gate.
    chosen = max(candidates, key=lambda r: (r['correct_source_or_abstention'], -r['false_acceptances'], r['threshold']))
    rows = evaluate(desk, test, chosen['threshold'])
    report = {'scope': 'AI-assisted handcrafted regression fixture; not a blinded or real-world benchmark',
              'selection': 'Coverage threshold chosen using development queries only; no test-based tuning',
              'metric_boundary': 'Correct source/abstention is not semantic answer correctness or contradiction detection',
              'latency_boundary': 'Warm local answer path only; excludes index construction, network and LLM inference',
              'selected_threshold': chosen['threshold'], 'development_candidates': candidates,
              'test_summary': summarize(rows), 'test_cases': rows}
    (ROOT / 'evaluation_suite_results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'selected_threshold': chosen['threshold'], **report['test_summary']}, indent=2))
    return report


if __name__ == '__main__':
    run()
