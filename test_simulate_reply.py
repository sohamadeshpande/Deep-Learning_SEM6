#!/usr/bin/env python3
"""
Test script for the simulate reply feature
"""
import requests
import json

# Test data
test_message = {
    "channel": "email",
    "subject": "AI-powered solution for tech professionals",
    "content": "Hi Sarah! I noticed your recent post about AI in hiring and thought you might be interested in our local AI outreach solution. Would love to connect and discuss how it could help TechFlow AI streamline your recruitment outreach.",
    "word_count": 35,
    "personalization_elements": ["Name (Sarah)", "Company (TechFlow AI)", "Recent activity reference"],
    "language": "english"
}

test_prospect = {
    "id": "sarah-chen-cto",
    "name": "Sarah Chen",
    "company": "TechFlow AI",
    "role": "Chief Technology Officer",
    "industry": "Technology",
    "location": "San Francisco, CA",
    "linkedin_url": "https://linkedin.com/in/sarah-chen-cto",
    "interests": ["AI/ML", "Team Building", "Tech Innovation"],
    "recent_activity": [
        {
            "type": "post",
            "content": "Excited about the potential of AI in transforming our hiring process. Looking for innovative solutions that can help us identify top talent more efficiently.",
            "date": "2024-01-15",
            "engagement": 45
        }
    ],
    "communication_style": {
        "formality_level": "professional",
        "language_type": "technical",
        "tone_preference": "direct",
        "confidence_score": 0.85,
        "analysis_summary": "Professional technical communicator with direct approach"
    },
    "about_section": "CTO at TechFlow AI, passionate about building scalable systems and leading high-performing engineering teams.",
    "created_at": "2024-01-01T00:00:00"
}

def test_simulate_reply():
    """Test the simulate reply endpoint"""
    url = "http://localhost:8000/simulate-reply"
    
    payload = {
        "message": test_message,
        "prospect": test_prospect
    }
    
    print("🧪 Testing simulate reply endpoint...")
    print(f"📡 URL: {url}")
    print(f"📝 Payload keys: {list(payload.keys())}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success', False)}")
            
            if data.get('success'):
                reply = data.get('reply', '')
                print(f"💬 Generated Reply: {reply}")
                print(f"⏰ Timestamp: {data.get('timestamp', 'N/A')}")
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🚫 Request failed: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    test_simulate_reply()