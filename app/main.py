from fastapi import FastAPI, HTTPException
from app.schemas import PlanRequest, PlanResponse, Subtopic
from app.planner import make_plan


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

@app.post("/plan", response_model=PlanResponse)
def plan(req: PlanRequest):
    goal = req.goal.strip()
    if len(goal) < 8:
        raise HTTPException(status_code=400, detail="Goal is too short.")
    plan_dict = make_plan(goal)
    # Pydantic v2 will coerce dicts to response model automatically
    return plan_dict