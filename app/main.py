from fastapi import FastAPI

app = FastAPI(title="AutoResearcher", version="0.1.0")

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "name": "AutoResearcher",
        "message": "Hello from the Self-Initiated Research Agent!",
        "next": "POST /plan with a JSON body: {\"goal\": \"...\"} (stub for now)"
    }
