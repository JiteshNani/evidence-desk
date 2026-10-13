from fastapi import FastAPI
from pydantic import BaseModel, Field
from core import EvidenceDesk

app = FastAPI(title='Evidence Desk',version='1.0.0')
class Document(BaseModel):
    id: str = Field(min_length=1,max_length=100)
    text: str = Field(min_length=1,max_length=100000)
class Query(BaseModel):
    question: str = Field(min_length=1,max_length=1000)
    documents: list[Document] = Field(min_length=1,max_length=30)
    k: int = Field(default=3,ge=1,le=10)

@app.get('/health')
def health():
    return {'status':'ok','version':'1.0.0'}

@app.post('/answer')
def answer(q:Query):
    from fastapi import HTTPException
    try:
        return EvidenceDesk([d.model_dump() for d in q.documents]).answer(q.question,q.k)
    except ValueError as e:
        raise HTTPException(422,str(e)) from e

@app.get('/',include_in_schema=False)
def demo_page():
    from fastapi.responses import FileResponse
    from pathlib import Path
    return FileResponse(Path(__file__).with_name('index.html'))
