from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import Dict, List
import json
from datetime import datetime

from services.llm_service import LLMService
from services.prospect_service import ProspectService
from models.prospect import ProspectProfile, ChannelMessages, ChannelMessage, Language

app = FastAPI(title="Offline LLM Cold Outreach Engine")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
llm_service = LLMService()
prospect_service = ProspectService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main demo page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze-prospect")
async def analyze_prospect(
    linkedin_url: str = Form(...), 
    variations: int = Form(2),
    language: str = Form("english")
):
    """Analyze prospect and generate messages with A/B variations in specified language"""
    try:
        # Convert language string to enum
        try:
            selected_language = Language(language.lower())
        except ValueError:
            selected_language = Language.ENGLISH
        
        # Get prospect profile (mock data for demo)
        prospect = prospect_service.get_prospect_by_url(linkedin_url)
        
        if not prospect:
            return {"error": "Prospect not found. Please use one of our demo URLs."}
        
        # Get semantic tone analysis for the prospect
        tone_analysis = llm_service._get_tone_aware_instructions(prospect)
        
        # Generate multiple variations
        all_variations = []
        for i in range(min(variations, 3)):  # Max 3 variations
            print(f"\n🔄 [VARIATION {i+1}] Starting generation...")
            messages = await llm_service.generate_messages(prospect, selected_language)
            all_variations.append({
                "variation_id": i + 1,
                "messages": messages.dict()
            })
        
        return {
            "success": True,
            "prospect": prospect.dict(),
            "tone_analysis": {
                "primary_tone": tone_analysis['primary_tone'],
                "confidence": tone_analysis['confidence'],
                "all_tones": tone_analysis['all_tones'],
                "analysis_summary": tone_analysis['analysis_summary'],
                "recommendations": tone_analysis['recommendations']
            },
            "variations": all_variations,
            "total_variations": len(all_variations),
            "language": selected_language.value,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {"error": f"Failed to generate messages: {str(e)}"}

@app.post("/export-messages")
async def export_messages(request: Request):
    """Export generated messages as JSON/CSV"""
    try:
        data = await request.json()
        
        # Create export data
        export_data = {
            "prospect": data.get("prospect", {}),
            "variations": data.get("variations", []),
            "exported_at": datetime.now().isoformat(),
            "export_type": "offline_llm_outreach_messages"
        }
        
        return {
            "success": True,
            "download_data": export_data,
            "filename": f"outreach_messages_{data.get('prospect', {}).get('name', 'prospect').replace(' ', '_')}.json"
        }
    
    except Exception as e:
        return {"error": f"Failed to export: {str(e)}"}

@app.post("/simulate-reply")
async def simulate_reply(request: Request):
    """Simulate a prospect's reply to a message"""
    try:
        print("🔄 [SIMULATE-REPLY] API endpoint called")
        data = await request.json()
        print(f"📝 [SIMULATE-REPLY] Received data keys: {list(data.keys())}")
        
        # Extract message and prospect data
        message_data = data.get("message", {})
        prospect_data = data.get("prospect", {})
        
        print(f"📧 [SIMULATE-REPLY] Message channel: {message_data.get('channel', 'unknown')}")
        print(f"👤 [SIMULATE-REPLY] Prospect: {prospect_data.get('name', 'unknown')}")
        
        # Reconstruct objects
        message = ChannelMessage(**message_data)
        prospect = ProspectProfile(**prospect_data)
        
        print("🤖 [SIMULATE-REPLY] Calling LLM service...")
        # Generate simulated reply
        reply = await llm_service.simulate_reply(message, prospect)
        
        print(f"✅ [SIMULATE-REPLY] Generated reply: {reply[:50]}...")
        
        return {
            "success": True,
            "reply": reply,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ [SIMULATE-REPLY] Error: {str(e)}")
        return {"error": f"Failed to simulate reply: {str(e)}"}

@app.get("/demo-prospects")
async def get_demo_prospects():
    """Get available demo prospect URLs"""
    return prospect_service.get_demo_prospects()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    llm_status = llm_service.health_check()
    return {
        "status": "healthy",
        "llm_available": llm_status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)