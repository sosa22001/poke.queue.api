import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"version": "0.0.1"}

@app.get("/project")
def project():
    return {"project": "poke queue"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)