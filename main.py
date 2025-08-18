from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# Replace with your actual Gemini API key
API_KEY = "AIzaSyC6iwIZ4D7eODYEvsIlQFYHqNSebap7Jwo"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

TEMPLATE = """
You are an AI assistant helping to monitor a plant's health. Based on the following data, generate a unique, personalized response each time:

Plant Data:
- Location: {location}
- Plant Type: {plant_type}  
- Soil Moisture: {soil_moisture}
- Temperature: {temperature}°C
- Humidity: {humidity}%

Generate your response in this exact format:
MESSAGE: [encouraging message - max 16 chars]
MELODY: [note,duration,note,duration,note,duration]

Use musical notes C3-C6 and R for rests. Make each melody unique and reflect the plant's mood:
- Happy/healthy: Upbeat major scales
- Thirsty: Gentle, pleading tones  
- Perfect conditions: Peaceful melodies
- Issues: Attention-getting patterns

BE CREATIVE - generate a different melody each time, even for the same conditions!
"""

class ContextData(BaseModel):
    location: str
    plant_type: str  
    soil_moisture: float
    temperature: float
    humidity: float

@app.post("/consulta")
def consulta(data: ContextData):
    prompt = TEMPLATE.format(**data.dict())
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.9  # High creativity for unique melodies
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(ENDPOINT, headers=headers, json=payload)
        
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"respuesta": text}
        else:
            return {"error": f"API error: {r.status_code}"}
            
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

@app.get("/")
def root():
    return {"message": "Plant AI Melody Generator", "status": "running"}
