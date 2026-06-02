import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from train import predict_bte, load_production_model
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Loading ML model and scaler during startup...")
    try:
        model, scaler = load_production_model()
        ml_models["model"] = model
        ml_models["scaler"] = scaler
        logging.info("ML model and scaler loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load model on startup: {e}")
    yield
    ml_models.clear()

app = FastAPI(title="Brake Thermal Efficiency Predictor", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/status")
async def status_check():
    logging.info("✅ Status check hit.")
    return {"message": "✅ App is running and ready to serve predictions.", "status": "ok"}

class PredictionRequest(BaseModel):
    engine_load: float
    fuel_blend_percentage: float
    nanoparticle_concentration: float
    injection_pressure: float
    engine_speed: float

@app.post("/predict")
async def predict(data: PredictionRequest):
    try:
        if "model" not in ml_models or "scaler" not in ml_models:
            raise ValueError("Model is not loaded. Ensure a model is trained and available.")
            
        input_data = data.model_dump()
        logging.info(f"Received input: {input_data}")

        prediction = predict_bte(ml_models["model"], ml_models["scaler"], input_data)
        return {"predicted_BTE": round(prediction, 3)}

    except ValueError as ve:
        logging.error(f"ValueError during prediction: {ve}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(ve)})
    except Exception as e:
        logging.error(f"Unexpected error during prediction: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "An unexpected error occurred. Please try again later."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000)