from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Get API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

TEMPLATE = """
You are an AI assistant helping to monitor a plant's health. Based on the following data, generate a unique, personalized response each time:

Plant Data:
- Location: {location}
- Plant Type: {plant_type}  
- Soil Moisture Level: {soil_moisture}
- Temperature: {temperature}°C
- Humidity: {humidity}%

Generate your response in this exact format:
MESSAGE: [encouraging message - max 16 chars]
MELODY: [note,duration,note,duration,note,duration]

Use musical notes C3-C6 and R for rests. Duration in seconds (like 0.5, 1.0).
Make each melody unique and reflect the plant's mood:
- Happy/healthy: Upbeat major scales, cheerful rhythms
- Thirsty/stressed: Gentle, pleading tones, slower tempo
- Perfect conditions: Peaceful, flowing melodies
- Problems: Attention-getting patterns, urgent rhythms

BE CREATIVE - generate a completely different melody each time, even for the same conditions!
Add variety in rhythm, note patterns, and musical phrases.
"""

class ContextData(BaseModel):
    location: str
    plant_type: str  
    soil_moisture: float
    temperature: float
    humidity: float

@app.post("/consulta")
def consulta(data: ContextData):
    try:
        prompt = TEMPLATE.format(**data.dict())
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.9,  # High creativity for unique melodies
                "topP": 0.8,
                "topK": 40
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return {"respuesta": text}
            else:
                return {"error": "No response generated from AI"}
        else:
            return {"error": f"API error: {response.status_code}", "details": response.text}
            
    except requests.exceptions.Timeout:
        return {"error": "Request timeout - AI service took too long"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@app.get("/")
def root():
    return {
        "message": "Plant AI Melody Generator API", 
        "status": "running",
        "api_key_configured": bool(API_KEY)
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "plant-melody-api"}
