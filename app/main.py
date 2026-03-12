from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.captcha import router as captcha_router

app = FastAPI(title="Captcha API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


app.include_router(captcha_router)


