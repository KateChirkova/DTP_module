from fastapi import FastAPI
app = FastAPI(title="🚗 Модуль ДТП ЦОДД")

@app.get("/")
def root():
    return {"status": "Готов!", "module": "dtp-detection"}

@app.get("/health")
def health():
    return {"db": "soon", "yolo": "soon"}