from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from inference import classify_text, extract_entities

app = FastAPI()


class TextRequest(BaseModel):
    text: str


@app.post("/predict/")
async def predict(request: TextRequest):
    try:
        result = classify_text(request.text)
        return {
            "result": result,
            "error": False,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/extract/")
async def extract(request: TextRequest):
    try:
        entities = extract_entities(request.text)
        return {
            "results": entities,
            "error": False,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
