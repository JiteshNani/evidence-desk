"""Local hybrid retrieval with source citations and conservative abstention."""
from dataclasses import dataclass, asdict
import math
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

STOP = frozenset('a an the is are of to for in on and what how does do can i'.split())

def tokens(text):
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if t not in STOP]

@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    text: str

class EvidenceDesk:
    def __init__(self, documents, chunk_words=90, overlap=15):
        if not 0 <= overlap < chunk_words:
            raise ValueError('overlap must be smaller than chunk_words')
        if not documents or len(documents) > 100:
            raise ValueError('provide 1 to 100 documents')
        self.chunks = []
        seen = set()
        for doc in documents:
            if doc['id'] in seen:
                raise ValueError('duplicate document id')
            seen.add(doc['id'])
            words = doc['text'].split()
            if not words or len(words) > 20000:
                raise ValueError('document must contain 1 to 20000 words')
            for start in range(0, len(words), chunk_words-overlap):
                self.chunks.append(Chunk(f"{doc['id']}:{start}", doc['id'], ' '.join(words[start:start+chunk_words])))
                if start+chunk_words >= len(words):
                    break
        self.vectorizer = TfidfVectorizer(tokenizer=tokens, token_pattern=None, lowercase=False)
        self.matrix = self.vectorizer.fit_transform(c.text for c in self.chunks)
        self.counts = [Counter(tokens(c.text)) for c in self.chunks]
        self.lengths = np.array([sum(c.values()) for c in self.counts])
        self.avg_length = float(self.lengths.mean()) or 1
        self.df = Counter(t for c in self.counts for t in c)

    def retrieve(self, question, k=3, mode='hybrid'):
        if not 1 <= k <= 10 or mode not in ('hybrid','tfidf','bm25'):
            raise ValueError('invalid retrieval settings')
        query_tokens = tokens(question)
        if not query_tokens:
            return []
        similarity = (self.matrix @ self.vectorizer.transform([question]).T).toarray().ravel()
        bm25 = np.zeros(len(self.chunks))
        for t in set(query_tokens):
            idf = math.log(1+(len(self.chunks)-self.df[t]+0.5)/(self.df[t]+0.5))
            for i,c in enumerate(self.counts):
                tf = c[t]
                denom = tf+1.2*(1-0.75+0.75*self.lengths[i]/self.avg_length)
                bm25[i] += idf*tf*2.2/denom if tf else 0
        scores = similarity if mode == 'tfidf' else bm25
        if mode == 'hybrid':
            scores = np.zeros(len(self.chunks))
            for raw in (similarity,bm25):
                for rank,idx in enumerate(np.argsort(-raw,kind='stable')):
                    if raw[idx] > 0:
                        scores[idx] += 1/(60+rank+1)
        order = np.argsort(-scores,kind='stable')
        return [{**asdict(self.chunks[i]), 'score':round(float(scores[i]),6),
                 'coverage':len(set(query_tokens)&set(self.counts[i]))/len(set(query_tokens))}
                for i in order[:k] if scores[i] > 0]

    def answer(self, question, k=3, min_coverage=0.5):
        hits = self.retrieve(question,k)
        if not hits or hits[0]['coverage'] < min_coverage:
            return {'status':'abstained','answer':'Insufficient evidence in the supplied documents.','citations':[]}
        # Extractive by design: no ungrounded model-generated sentences.
        best = hits[0]
        sentences = re.split(r'(?<=[.!?])\s+', best['text'])
        q = set(tokens(question))
        ranked = sorted(sentences,key=lambda s:len(q&set(tokens(s))),reverse=True)
        return {'status':'answered','answer':ranked[0],
                'citations':[{'source':best['source'],'chunk_id':best['id'],'quote':ranked[0]}]}
