import pytest
from evaluate_suite import retrieval_metrics, summarize


def test_duplicate_chunks_do_not_inflate_recall():
    r = retrieval_metrics(['a', 'a', 'b'], ['a', 'b'])
    assert r['recall_at_3'] == 1
    assert r['ndcg_at_3'] == 1


def test_missing_relevant_document():
    r = retrieval_metrics(['x', 'y'], ['a'])
    assert r == {'recall_at_3': 0, 'mrr_at_3': 0, 'ndcg_at_3': 0}


def test_reciprocal_rank_and_cutoff():
    assert retrieval_metrics(['x', 'a'], ['a'])['mrr_at_3'] == 0.5
    assert retrieval_metrics(['x', 'y', 'z', 'a'], ['a'])['recall_at_3'] == 0


def test_no_retrieval_score_for_unanswerable():
    assert retrieval_metrics(['x'], []) is None


def test_ndcg_penalizes_lower_rank():
    assert retrieval_metrics(['x', 'a'], ['a'])['ndcg_at_3'] == pytest.approx(1 / 1.584962500721156)
