#!/usr/bin/env python3
"""
Demo runner for Offline LLM Cold Outreach Engine
Run this script to start the demo server
"""

import uvicorn
import sys
import os

def main():
    print("🚀 Starting Offline LLM Cold Outreach Engine Demo...")
    print("=" * 60)
    print("📍 Demo will be available at: http://localhost:8000")
    print("🔒 Privacy-First: All processing happens locally")
    print("🤖 AI-Powered: Hyper-personalized message generation")
    print("📱 Multi-Channel: Email, LinkedIn, WhatsApp, SMS, Instagram")
    print("=" * 60)
    
    try:
        # Run the FastAPI app
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thanks for trying our solution!")
    except Exception as e:
        print(f"❌ Error starting demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()