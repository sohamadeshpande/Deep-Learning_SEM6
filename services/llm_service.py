import time
import requests
import json
from typing import Dict, List
from models.prospect import ProspectProfile, ChannelMessages, ChannelMessage, Language
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from services.embedding_service import EmbeddingService

class LLMService:
    """Service for LLM-powered message generation using Ollama"""
    
    def __init__(self):
        self.model_loaded = False
        self.model_name = "llama3:latest"
        self.ollama_url = "http://localhost:11434"
        self.session = self._create_session_with_retries()
        self.embedding_service = None  # Lazy-load embedding service
        self.tone_analysis_cache = {}  # Cache tone analyses for performance
        self._initialize_model()
    
    def _create_session_with_retries(self):
        """Create requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _initialize_model(self):
        """Initialize connection to Ollama"""
        try:
            print("🔍 Checking Ollama connection...")
            # Test Ollama connection with longer timeout
            response = self.session.get(f"{self.ollama_url}/api/tags", timeout=15)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if any(model['name'] == self.model_name for model in models):
                    self.model_loaded = True
                    print(f"✅ Connected to Ollama with {self.model_name}")
                else:
                    print(f"❌ Model {self.model_name} not found in Ollama")
                    print(f"📦 Available models: {[m.get('name', 'unknown') for m in models]}")
            else:
                print("❌ Ollama not responding")
        except requests.exceptions.Timeout:
            print(f"❌ Ollama connection timeout (15s exceeded)")
            print("💡 Make sure Ollama is running: ollama serve")
            print("📝 Using mock responses for demo")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
            print("💡 Make sure Ollama is running on port 11434")
            print("📝 Using mock responses for demo")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("📝 Using mock responses for demo")
    
    def _call_ollama(self, prompt: str, max_tokens: int = 500, language: Language = Language.ENGLISH) -> tuple[str, bool]:
        """Call Ollama API for text generation with language-specific settings"""
        if not self.model_loaded:
            print("🔄 Using fallback generation (Ollama not available)")
            return self._fallback_generation(prompt), False
        
        try:
            print(f"🤖 [OLLAMA] Generating with LLaMA 3... (max {max_tokens} tokens)")
            start_time = time.time()
            
            # Add language-specific system message
            if language == Language.HINDI:
                system_msg = "आप हिंदी में व्यावसायिक संदेश लिखने के विशेषज्ञ हैं। केवल हिंदी का उपयोग करें।"
            elif language == Language.MARATHI:
                system_msg = "तुम्ही मराठीत व्यावसायिक संदेश लिहिण्यात तज्ञ आहात। फक्त मराठी वापरा।"
            else:
                system_msg = "You are a professional business communication expert. Write only the requested content without explanations."
            
            # Combine system message with user prompt
            full_prompt = f"System: {system_msg}\n\nUser: {prompt}"
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Better balance for creativity and consistency
                    "max_tokens": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "seed": None
                }
            }
            
            response = self.session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120  # Increased to 2 minutes for LLaMA 3 processing
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                generation_time = time.time() - start_time
                print(f"✅ [OLLAMA] Generated {len(generated_text)} chars in {generation_time:.1f}s")
                print(f"📝 [PREVIEW] {generated_text[:100]}{'...' if len(generated_text) > 100 else ''}")
                return generated_text, True
            else:
                print(f"❌ [OLLAMA] API error: {response.status_code}")
                return self._fallback_generation(prompt), False
                
        except requests.exceptions.Timeout:
            print(f"❌ [OLLAMA] Timeout after 120s - model is taking too long")
            print("💡 Tips: Model may be loading. First generation is slower.")
            print("💡 Increase available RAM or use a smaller model (mistral, neural-chat)")
            return self._fallback_generation(prompt), False
        except requests.exceptions.ConnectionError:
            print(f"❌ [OLLAMA] Connection error - Ollama may have crashed")
            print("💡 Restart Ollama: ollama serve")
            return self._fallback_generation(prompt), False
        except Exception as e:
            print(f"❌ [OLLAMA] Error: {e}")
            return self._fallback_generation(prompt), False
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback to mock generation if Ollama fails"""
        print("⚠️  Using FALLBACK generation (not Ollama)")
        
        # Check if this is a Hindi prompt
        if any(hindi_word in prompt for hindi_word in ["हिंदी", "मैसेज", "ईमेल", "भेजना"]):
            # Return proper Hindi fallback
            if "Subject:" in prompt or "ईमेल" in prompt:
                return """Subject: आपके व्यापार के लिए AI समाधान

नमस्ते,

मैंने आपकी कंपनी के बारे में पढ़ा है और मुझे लगता है कि हमारा AI आउटरीच समाधान आपके लिए उपयोगी हो सकता है। यह पूरी तरह से स्थानीय रूप से काम करता है और आपकी डेटा सुरक्षा को बनाए रखता है।

क्या आप इस बारे में बात करना चाहेंगे?

धन्यवाद"""
            elif "LinkedIn" in prompt or "मैसेज" in prompt:
                return """नमस्ते! मैंने आपकी प्रोफाइल देखी है और आपके काम से प्रभावित हूं। हमारे पास एक AI समाधान है जो आपकी कंपनी के लिए उपयोगी हो सकता है। क्या आप इस बारे में चर्चा करना चाहेंगे? 🚀"""
            else:
                return """नमस्ते! आपकी कंपनी के लिए हमारे पास एक बेहतरीन AI समाधान है। क्या आप इसके बारे में जानना चाहेंगे? 😊"""
        
        # Extract key info from prompt for smart English fallback
        if "email" in prompt.lower() and "subject" in prompt.lower():
            return "Subject: Quick question about your recent insights\n\nHi there! I noticed your recent post and thought you might be interested in our solution..."
        return "Hi! I saw your profile and thought our solution might interest you. Would love to connect!"
    
    async def generate_messages(self, prospect: ProspectProfile, language: Language = Language.ENGLISH) -> ChannelMessages:
        """Generate personalized messages for all channels"""
        start_time = time.time()
        
        if not self.model_loaded:
            raise Exception("LLM model not loaded")
        
        print(f"\n🎯 [GENERATION] Starting for {prospect.name} ({prospect.role} at {prospect.company})")
        print(f"📊 [PROFILE] Style: {prospect.communication_style.formality_level.value}, Recent activity: {len(prospect.recent_activity)} items")
        print(f"🌍 [LANGUAGE] Generating in: {language.value.title()}")
        
        # Simulate LLM processing time
        await self._simulate_processing()
        
        # Generate messages based on prospect profile
        print(f"📧 [EMAIL] Generating...")
        email = self._generate_email(prospect, language)
        
        print(f"💼 [LINKEDIN] Generating...")
        linkedin_dm = self._generate_linkedin_dm(prospect, language)
        
        print(f"📱 [WHATSAPP] Generating...")
        whatsapp = self._generate_whatsapp(prospect, language)
        
        print(f"📲 [SMS] Generating...")
        sms = self._generate_sms(prospect, language)
        
        print(f"📸 [INSTAGRAM] Generating...")
        instagram_dm = self._generate_instagram_dm(prospect, language)
        
        total_time = time.time() - start_time
        print(f"🎉 [COMPLETE] All 5 channels generated in {total_time:.1f}s")
        
        # Log generated messages
        print(f"\n📧 [OUTPUT PREVIEW]:")
        print(f"   Email: {email.content[:80]}...")
        print(f"   LinkedIn: {linkedin_dm.content[:80]}...")
        print(f"   WhatsApp: {whatsapp.content[:80]}...")
        print(f"   SMS: {sms.content[:60]}...")
        print(f"   Instagram: {instagram_dm.content[:80]}...")
        
        messages = ChannelMessages(
            prospect_id=prospect.id,
            email=email,
            linkedin_dm=linkedin_dm,
            whatsapp=whatsapp,
            sms=sms,
            instagram_dm=instagram_dm,
            generated_at=datetime.now(),
            generation_time_seconds=total_time
        )
        
        return messages
    
    async def _simulate_processing(self):
        """Simulate LLM processing time"""
        import asyncio
        await asyncio.sleep(2)  # Simulate 2 seconds of processing
    
    def _get_language_instructions(self, language: Language) -> dict:
        """Get language-specific instructions and examples"""
        instructions = {
            Language.ENGLISH: {
                "instruction": "Write in professional English",
                "greeting": "Hi",
                "closing": "Best regards",
                "cta_examples": ["Would love to connect", "Let's schedule a call", "Interested in learning more?"]
            },
            Language.HINDI: {
                "instruction": "केवल शुद्ध हिंदी में देवनागरी लिपि का उपयोग करके लिखें। व्यक्तिगत नाम अंग्रेजी में रखें।",
                "greeting": "नमस्ते",
                "closing": "धन्यवाद",
                "cta_examples": ["आपसे जुड़ना चाहूंगा", "एक बैठक का समय निर्धारित करें", "अधिक जानकारी चाहिए"]
            },
            Language.MARATHI: {
                "instruction": "फक्त शुद्ध मराठीत देवनागरी लिपी वापरून लिहा। व्यक्तिगत नावे इंग्रजीत ठेवा।",
                "greeting": "नमस्कार",
                "closing": "धन्यवाद",
                "cta_examples": ["तुमच्याशी संपर्क साधू इच्छितो", "एक बैठक ठरवूया", "अधिक माहिती हवी"]
            }
        }
        return instructions.get(language, instructions[Language.ENGLISH])
    
    def _get_tone_aware_instructions(self, prospect: ProspectProfile) -> Dict:
        """
        Get tone-aware generation instructions using semantic embeddings
        
        Returns:
            Dict with tone analysis and LLM prompt instructions
        """
        # Lazy-load embedding service on first use
        if self.embedding_service is None:
            print("🤖 [EMBEDDINGS] Initializing semantic analysis model (first time)...")
            self.embedding_service = EmbeddingService()
        
        # Check cache first
        if prospect.id in self.tone_analysis_cache:
            return self.tone_analysis_cache[prospect.id]
        
        # Analyze communication style using embeddings
        analysis = self.embedding_service.analyze_communication_style(prospect)
        
        # Get tone-specific prompt instructions
        primary_tone = analysis['primary_tone']
        tone_instructions = self.embedding_service.get_prompt_instructions_for_tone(primary_tone)
        
        # Get recommendations for this tone
        recommendations = self.embedding_service._get_tone_recommendations(primary_tone)
        
        result = {
            "primary_tone": primary_tone,
            "confidence": analysis['primary_tone_confidence'],
            "all_tones": analysis['all_tone_scores'],
            "prompt_instructions": tone_instructions,
            "recommendations": recommendations,
            "analysis_summary": analysis['analysis_summary']
        }
        
        # Cache the result
        self.tone_analysis_cache[prospect.id] = result
        return result
    
    def _generate_email(self, prospect: ProspectProfile, language: Language = Language.ENGLISH) -> ChannelMessage:
        """Generate personalized email using Ollama"""
        
        # Get tone-aware instructions using embeddings
        tone_analysis = self._get_tone_aware_instructions(prospect)
        primary_tone = tone_analysis['primary_tone']
        tone_instructions = tone_analysis['prompt_instructions']
        
        # Get recent activity for personalization
        recent_post = prospect.recent_activity[0] if prospect.recent_activity else None
        lang_instructions = self._get_language_instructions(language)
        
        # Create detailed prompt for Ollama with language support and tone awareness
        if language == Language.ENGLISH:
            prompt = f"""Write a professional email to {prospect.name}, {prospect.role} at {prospect.company}.

TONE GUIDANCE: {tone_instructions}
Detected Communication Style: {primary_tone.upper()} (Confidence: {tone_analysis['confidence']:.0%})

Start with "Subject:" then write the email.
Mention our AI outreach solution that works locally.
Reference their recent activity if relevant.
Keep it 150-200 words.

Subject:"""

        elif language == Language.HINDI:
            prompt = f"""हिंदी में एक व्यावसायिक ईमेल लिखें।

{prospect.name} को ईमेल भेजना है। वे {prospect.company} में {prospect.role} हैं।

Subject: से शुरू करें, फिर हिंदी ईमेल लिखें।
केवल हिंदी का उपयोग करें। नाम अंग्रेजी में रखें।
AI समाधान के बारे में बताएं।

Subject:"""

        else:  # Marathi
            prompt = f"""एक व्यावसायिक कोल्ड आउटरीच ईमेल लिहा।

व्यक्ती: {prospect.name}, {prospect.role} at {prospect.company}
शैली: औपचारिक व्यापारिक
आवडी: {', '.join(prospect.interests[:3])}"""

            if recent_post:
                prompt += f"""
अलीकडील पोस्ट: "{recent_post.content[:100]}..."
या पोस्टचा संदर्भ द्या।"""

            prompt += f"""

आवश्यकता:
- "Subject: " पासून सुरुवात करा मग मराठी विषय लिहा
- मग ईमेलचा मुख्य भाग लिहा
- एकूण 120-200 मराठी शब्द ठेवा
- त्यांची भूमिका/कंपनीचा उल्लेख करा
- स्थानिक AI आउटरीच समाधानाचा उल्लेख करा
- स्पष्ट कॉल-टू-एक्शनसह समाप्त करा
- फक्त मराठीत लिहा, व्यक्तिगत नावे इंग्रजीत ठेवा

Subject:"""

        # Call Ollama with logging
        response, is_ollama = self._call_ollama(prompt, max_tokens=400, language=language)
        
        # Parse response
        if "Subject:" in response:
            parts = response.split("Subject:", 1)[1].strip()
            if "\n\n" in parts:
                subject = parts.split("\n\n")[0].strip()
                content = parts.split("\n\n", 1)[1].strip()
            else:
                lines = parts.split("\n")
                subject = lines[0].strip()
                content = "\n".join(lines[1:]).strip()
        else:
            subject = f"AI-powered solution for {prospect.industry.lower()} professionals"
            content = response
        
        # Identify personalization elements
        personalization = []
        if prospect.name.lower() in content.lower():
            personalization.append(f"Name ({prospect.name})")
        if prospect.company.lower() in content.lower():
            personalization.append(f"Company ({prospect.company})")
        if prospect.role.lower() in content.lower():
            personalization.append(f"Role ({prospect.role})")
        if recent_post and any(word in content.lower() for word in recent_post.content.lower().split()[:5]):
            personalization.append("Recent activity reference")
        
        # Add generation source indicator
        if is_ollama:
            personalization.append("🤖 Generated by LLaMA 3")
        else:
            personalization.append("⚠️ Fallback generation")
        
        message = ChannelMessage(
            channel="email",
            subject=subject,
            content=content,
            word_count=len(content.split()),
            personalization_elements=personalization,
            language=language
        )
        
        # Add success scoring
        success_data = self._calculate_success_score(message, prospect)
        message.success_score = success_data["score"]
        message.response_probability = success_data["response_probability"]
        message.prob_color = success_data["prob_color"]
        message.scoring_factors = success_data["scoring_factors"]
        message.optimization_suggestions = success_data["optimization_suggestions"]
        
        return message
    
    def _generate_linkedin_dm(self, prospect: ProspectProfile, language: Language = Language.ENGLISH) -> ChannelMessage:
        """Generate LinkedIn DM using Ollama"""
        
        # Get tone-aware instructions
        tone_analysis = self._get_tone_aware_instructions(prospect)
        tone_instructions = tone_analysis['prompt_instructions']
        
        recent_post = prospect.recent_activity[0] if prospect.recent_activity else None
        lang_instructions = self._get_language_instructions(language)
        
        if language == Language.ENGLISH:
            prompt = f"""Write a LinkedIn message to {prospect.name}, {prospect.role} at {prospect.company}.

TONE GUIDANCE: {tone_instructions}
Detected Style: {tone_analysis['primary_tone'].upper()}

Make it professional and conversational. Mention their work and our AI outreach solution.
Keep it 80-120 words.

LinkedIn message:"""

        elif language == Language.HINDI:
            prompt = f"""{prospect.name} को LinkedIn मैसेज भेजना है।

वे {prospect.company} में {prospect.role} हैं।
केवल हिंदी में लिखें। नाम अंग्रेजी में रखें।
AI समाधान के बारे में बताएं।
80 शब्दों में लिखें।

मैसेज:"""

        else:  # Marathi
            prompt = f"""एक LinkedIn डायरेक्ट मेसेज लिहा।

प्राप्तकर्ता: {prospect.name}, {prospect.role} at {prospect.company}
शैली: {prospect.communication_style.formality_level.value}"""

            if recent_post:
                prompt += f"""
त्यांची अलीकडील पोस्ट: "{recent_post.content[:80]}..."
या पोस्टचा संदर्भ द्या।"""

            prompt += f"""

आवश्यकता:
- जास्तीत जास्त 80-120 मराठी शब्द
- त्यांची भूमिका/कंपनीचा उल्लेख करा
- AI आउटरीच समाधानाचा उल्लेख करा
- कॉल-टू-एक्शन समाविष्ट करा
- LinkedIn साठी योग्य टोन
- फक्त मराठीत लिहा, व्यक्तिगत नावे इंग्रजीत ठेवा

LinkedIn DM लिहा:"""

        content, is_ollama = self._call_ollama(prompt, max_tokens=200, language=language)
        
        # Identify personalization
        personalization = []
        if prospect.name.lower() in content.lower():
            personalization.append(f"Name reference")
        if recent_post and any(word in content.lower() for word in recent_post.content.lower().split()[:3]):
            personalization.append("Recent post reference")
        if prospect.company.lower() in content.lower():
            personalization.append(f"Company mention")
        
        # Add generation source
        if is_ollama:
            personalization.append("🤖 Generated by LLaMA 3")
        else:
            personalization.append("⚠️ Fallback generation")
        
        message = ChannelMessage(
            channel="linkedin_dm",
            content=content,
            word_count=len(content.split()),
            personalization_elements=personalization,
            language=language
        )
        
        # Add success scoring
        success_data = self._calculate_success_score(message, prospect)
        message.success_score = success_data["score"]
        message.response_probability = success_data["response_probability"]
        message.prob_color = success_data["prob_color"]
        message.scoring_factors = success_data["scoring_factors"]
        message.optimization_suggestions = success_data["optimization_suggestions"]
        
        return message
    
    def _generate_whatsapp(self, prospect: ProspectProfile, language: Language = Language.ENGLISH) -> ChannelMessage:
        """Generate WhatsApp message using Ollama"""
        
        # Get tone-aware instructions
        tone_analysis = self._get_tone_aware_instructions(prospect)
        tone_instructions = tone_analysis['prompt_instructions']
        
        recent_post = prospect.recent_activity[0] if prospect.recent_activity else None
        lang_instructions = self._get_language_instructions(language)
        
        if language == Language.ENGLISH:
            prompt = f"""Write a WhatsApp message to {prospect.name}.

TONE GUIDANCE: {tone_instructions}
Style: {tone_analysis['primary_tone'].upper()}

Make it casual and friendly. Mention our AI solution.
Use 1-2 emojis. Keep it 40-60 words.

WhatsApp:"""

        elif language == Language.HINDI:
            prompt = f"""{prospect.name} को WhatsApp मैसेज भेजना है।

केवल हिंदी में लिखें। नाम अंग्रेजी में रखें।
AI समाधान के बारे में बताएं।
50 शब्दों में लिखें।
1 इमोजी का उपयोग करें।

मैसेज:"""

        else:  # Marathi
            prompt = f"""एक WhatsApp मेसेज लिहा।

प्राप्तकर्ता: {prospect.name} ({prospect.role} at {prospect.company})"""

            if recent_post:
                prompt += f"""
संदर्भ: त्यांची पोस्ट "{recent_post.content[:50]}..." बद्दल"""

            prompt += f"""

आवश्यकता:
- जास्तीत जास्त 40-70 मराठी शब्द
- WhatsApp साठी अनौपचारिक टोन
- 1-2 योग्य इमोजी वापरा
- त्यांची भूमिका/कंपनीचा उल्लेख करा
- AI समाधानाचा संक्षिप्त उल्लेख करा
- प्रश्न/कॉल-टू-एक्शनसह समाप्त करा
- फक्त मराठीत लिहा, व्यक्तिगत नावे इंग्रजीत ठेवा

WhatsApp मेसेज:"""

        content, is_ollama = self._call_ollama(prompt, max_tokens=150, language=language)
        
        personalization = []
        if prospect.name.lower() in content.lower():
            personalization.append("Name reference")
        if recent_post and any(word in content.lower() for word in recent_post.content.lower().split()[:3]):
            personalization.append("Recent post reference")
        
        if is_ollama:
            personalization.append("🤖 Generated by LLaMA 3")
        else:
            personalization.append("⚠️ Fallback generation")
        
        message = ChannelMessage(
            channel="whatsapp",
            content=content,
            word_count=len(content.split()),
            personalization_elements=personalization,
            language=language
        )
        
        # Add success scoring
        success_data = self._calculate_success_score(message, prospect)
        message.success_score = success_data["score"]
        message.response_probability = success_data["response_probability"]
        message.prob_color = success_data["prob_color"]
        message.scoring_factors = success_data["scoring_factors"]
        message.optimization_suggestions = success_data["optimization_suggestions"]
        
        return message
    
    def _generate_sms(self, prospect: ProspectProfile, language: Language = Language.ENGLISH) -> ChannelMessage:
        """Generate SMS message using Ollama"""
        
        # Get tone-aware instructions
        tone_analysis = self._get_tone_aware_instructions(prospect)
        tone_instructions = tone_analysis['prompt_instructions']
        
        recent_post = prospect.recent_activity[0] if prospect.recent_activity else None
        lang_instructions = self._get_language_instructions(language)
        
        if language == Language.ENGLISH:
            prompt = f"""Write a short SMS to {prospect.name}.

TONE GUIDANCE: {tone_instructions}
Style: {tone_analysis['primary_tone'].upper()}

Mention our AI solution. Keep it under 40 words.

SMS:"""

        elif language == Language.HINDI:
            prompt = f"""{prospect.name} को SMS भेजना है।

केवल हिंदी में लिखें। नाम अंग्रेजी में रखें।
AI समाधान के बारे में बताएं।
30 शब्दों में लिखें।

SMS:"""

        else:  # Marathi
            prompt = f"""एक SMS टेक्स्ट मेसेज लिहा।

प्राप्तकर्ता: {prospect.name} ({prospect.role})"""

            if recent_post:
                prompt += f"""
संदर्भ: त्यांची अलीकडील पोस्ट "{recent_post.content[:40]}..." बद्दल"""

            prompt += f"""

आवश्यकता:
- जास्तीत जास्त 25-45 मराठी शब्द (SMS लांबी)
- अतिशय संक्षिप्त आणि थेट
- त्यांच्या भूमिकेचा उल्लेख करा
- AI समाधानाचा संक्षिप्त उल्लेख करा
- स्पष्ट कॉल-टू-एक्शन
- फक्त मराठीत लिहा, व्यक्तिगत नावे इंग्रजीत ठेवा

SMS:"""

        content, is_ollama = self._call_ollama(prompt, max_tokens=100, language=language)
        
        personalization = []
        if prospect.name.lower() in content.lower():
            personalization.append("Name reference")
        if prospect.company.lower() in content.lower():
            personalization.append("Company mention")
        
        if is_ollama:
            personalization.append("🤖 Generated by LLaMA 3")
        else:
            personalization.append("⚠️ Fallback generation")
        
        message = ChannelMessage(
            channel="sms",
            content=content,
            word_count=len(content.split()),
            personalization_elements=personalization,
            language=language
        )
        
        # Add success scoring
        success_data = self._calculate_success_score(message, prospect)
        message.success_score = success_data["score"]
        message.response_probability = success_data["response_probability"]
        message.prob_color = success_data["prob_color"]
        message.scoring_factors = success_data["scoring_factors"]
        message.optimization_suggestions = success_data["optimization_suggestions"]
        
        return message
    
    def _generate_instagram_dm(self, prospect: ProspectProfile, language: Language = Language.ENGLISH) -> ChannelMessage:
        """Generate Instagram DM using Ollama"""
        
        # Get tone-aware instructions
        tone_analysis = self._get_tone_aware_instructions(prospect)
        tone_instructions = tone_analysis['prompt_instructions']
        
        recent_post = prospect.recent_activity[0] if prospect.recent_activity else None
        lang_instructions = self._get_language_instructions(language)
        
        if language == Language.ENGLISH:
            prompt = f"""Write an Instagram DM to {prospect.name}.

TONE GUIDANCE: {tone_instructions}
Style: {tone_analysis['primary_tone'].upper()}

Make it casual and friendly. Use 2-3 emojis.
Mention our AI solution. Keep it 60-90 words.

Instagram:"""

        elif language == Language.HINDI:
            prompt = f"""{prospect.name} को Instagram मैसेज भेजना है।

केवल हिंदी में लिखें। नाम अंग्रेजी में रखें।
AI समाधान के बारे में बताएं।
80 शब्दों में लिखें।
2 इमोजी का उपयोग करें।

मैसेज:"""

        else:  # Marathi
            prompt = f"""एक Instagram डायरेक्ट मेसेज लिहा।

प्राप्तकर्ता: {prospect.name} ({prospect.role} at {prospect.company})"""

            if recent_post:
                prompt += f"""
संदर्भ: त्यांची पोस्ट: "{recent_post.content[:60]}..." """

            prompt += f"""

आवश्यकता:
- 60-100 मराठी शब्द
- Instagram साठी अनौपचारिक/मैत्रीपूर्ण टोन
- 2-3 योग्य इमोजी वापरा
- त्यांच्या कामाचा/आवडींचा संदर्भ द्या
- AI समाधानाचा उल्लेख करा
- आकर्षक प्रश्नासह समाप्त करा
- फक्त मराठीत लिहा, व्यक्तिगत नावे इंग्रजीत ठेवा

Instagram DM:"""

        content, is_ollama = self._call_ollama(prompt, max_tokens=180, language=language)
        
        personalization = []
        if prospect.name.lower() in content.lower():
            personalization.append("Name reference")
        if recent_post and any(word in content.lower() for word in recent_post.content.lower().split()[:3]):
            personalization.append("Recent activity reference")
        
        if is_ollama:
            personalization.append("🤖 Generated by LLaMA 3")
        else:
            personalization.append("⚠️ Fallback generation")
        
        message = ChannelMessage(
            channel="instagram_dm",
            content=content,
            word_count=len(content.split()),
            personalization_elements=personalization,
            language=language
        )
        
        # Add success scoring
        success_data = self._calculate_success_score(message, prospect)
        message.success_score = success_data["score"]
        message.response_probability = success_data["response_probability"]
        message.prob_color = success_data["prob_color"]
        message.scoring_factors = success_data["scoring_factors"]
        message.optimization_suggestions = success_data["optimization_suggestions"]
        
        return message
    
    def _calculate_success_score(self, message: ChannelMessage, prospect: ProspectProfile) -> dict:
        """Calculate AI success score for a message"""
        score = 70  # Base score
        factors = []
        
        content = message.content.lower()
        
        # Personalization scoring
        if prospect.name.lower() in content:
            score += 8
            factors.append("Name mentioned (+8)")
        
        if prospect.company.lower() in content:
            score += 6
            factors.append("Company referenced (+6)")
        
        if prospect.role.lower() in content:
            score += 5
            factors.append("Role mentioned (+5)")
        
        # Recent activity scoring
        if prospect.recent_activity:
            recent_post = prospect.recent_activity[0]
            post_words = recent_post.content.lower().split()[:5]
            if any(word in content for word in post_words):
                score += 12
                factors.append("Recent activity referenced (+12)")
        
        # Communication style matching
        style = prospect.communication_style.formality_level.value
        if style == "casual" and any(emoji in message.content for emoji in ["👋", "🚀", "💪", "🔥", "😅"]):
            score += 7
            factors.append("Tone matched - casual (+7)")
        elif style == "formal" and not any(emoji in message.content for emoji in ["👋", "🚀", "💪", "🔥", "😅"]):
            score += 7
            factors.append("Tone matched - formal (+7)")
        elif style == "professional":
            score += 5
            factors.append("Professional tone (+5)")
        
        # Length optimization
        word_count = message.word_count
        if message.channel == "email" and 150 <= word_count <= 250:
            score += 5
            factors.append("Optimal email length (+5)")
        elif message.channel == "linkedin_dm" and 80 <= word_count <= 150:
            score += 5
            factors.append("Optimal LinkedIn length (+5)")
        elif message.channel == "whatsapp" and 40 <= word_count <= 80:
            score += 5
            factors.append("Optimal WhatsApp length (+5)")
        elif message.channel == "sms" and 20 <= word_count <= 50:
            score += 5
            factors.append("Optimal SMS length (+5)")
        
        # CTA presence
        cta_words = ["demo", "call", "chat", "meeting", "discuss", "connect", "show", "interested"]
        if any(word in content for word in cta_words):
            score += 8
            factors.append("Clear call-to-action (+8)")
        
        # Industry relevance
        interests = [interest.lower() for interest in prospect.interests]
        if any(interest in content for interest in interests):
            score += 6
            factors.append("Interest alignment (+6)")
        
        # Cap at 100
        score = min(score, 100)
        
        # Response probability based on score
        if score >= 90:
            response_prob = "Very High (85-95%)"
            prob_color = "text-green-600"
        elif score >= 80:
            response_prob = "High (70-85%)"
            prob_color = "text-green-500"
        elif score >= 70:
            response_prob = "Good (55-70%)"
            prob_color = "text-yellow-500"
        elif score >= 60:
            response_prob = "Fair (40-55%)"
            prob_color = "text-orange-500"
        else:
            response_prob = "Low (25-40%)"
            prob_color = "text-red-500"
        
        return {
            "score": score,
            "response_probability": response_prob,
            "prob_color": prob_color,
            "scoring_factors": factors,
            "optimization_suggestions": self._get_optimization_suggestions(score, factors, message, prospect)
        }
    
    def _get_optimization_suggestions(self, score: int, factors: list, message: ChannelMessage, prospect: ProspectProfile) -> list:
        """Generate optimization suggestions"""
        suggestions = []
        
        if score < 80:
            if not any("Name mentioned" in factor for factor in factors):
                suggestions.append("💡 Add prospect's name for better personalization")
            
            if not any("Recent activity" in factor for factor in factors):
                suggestions.append("💡 Reference their recent LinkedIn activity")
            
            if not any("call-to-action" in factor for factor in factors):
                suggestions.append("💡 Include a clearer call-to-action")
            
            if message.word_count > 200 and message.channel != "email":
                suggestions.append("💡 Consider shortening for better engagement")
        
        if score >= 90:
            suggestions.append("🎉 Excellent! This message is highly optimized")
        
        return suggestions

    def health_check(self) -> bool:
        """Check if LLM service is healthy"""
        return self.model_loaded
    
    async def simulate_reply(self, original_message: ChannelMessage, prospect: ProspectProfile) -> str:
        """Simulate a prospect's reply to the outreach message"""
        
        print(f"🎭 [SIMULATE-REPLY] Simulating reply for {prospect.name}")
        print(f"📱 [SIMULATE-REPLY] Channel: {original_message.channel}")
        print(f"💬 [SIMULATE-REPLY] Original message: {original_message.content[:100]}...")
        
        # Create context for reply simulation
        channel_context = {
            "email": "professional email response",
            "linkedin_dm": "LinkedIn direct message reply",
            "whatsapp": "casual WhatsApp response",
            "sms": "brief SMS reply",
            "instagram_dm": "Instagram DM response"
        }
        
        context = channel_context.get(original_message.channel, "message response")
        
        # Create prompt for reply simulation
        prompt = f"""You are {prospect.name}, {prospect.role} at {prospect.company}.

Someone sent you this message:
"{original_message.content}"

Write a realistic reply as {prospect.name}. Keep it short and natural.

Reply:"""

        # Call Ollama for reply simulation
        print("🤖 [SIMULATE-REPLY] Calling Ollama...")
        response, is_ollama = self._call_ollama(prompt, max_tokens=200, language=Language.ENGLISH)
        
        print(f"✅ [SIMULATE-REPLY] Generated response: {response[:100]}...")
        return response.strip()

# Import asyncio for async operations
import asyncio
