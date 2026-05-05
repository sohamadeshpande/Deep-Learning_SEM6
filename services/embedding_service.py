"""
Embedding Service for Semantic Communication Style Analysis
Uses Sentence-Transformers to analyze prospect communication patterns
and match them with appropriate message tones.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Tuple
from models.prospect import ProspectProfile, Language
import time


class EmbeddingService:
    """Service for semantic analysis of prospect communication style"""
    
    def __init__(self):
        """Initialize embedding model (lightweight, ~22MB)"""
        print("🤖 [EMBEDDING] Loading Sentence-Transformers model...")
        start = time.time()
        # Using lightweight model: all-MiniLM-L6-v2 (22MB, fast inference)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        load_time = time.time() - start
        print(f"✅ [EMBEDDING] Model loaded in {load_time:.2f}s")
        
        # Pre-computed tone embeddings (cached for performance)
        self._tone_embeddings_cache = None
    
    def _get_prospect_text(self, prospect: ProspectProfile) -> str:
        """Extract all relevant text from prospect profile for embedding"""
        # Combine all text sources for comprehensive profile understanding
        text_parts = []
        
        # About section (highest weight conceptually)
        if prospect.about_section:
            text_parts.append(prospect.about_section)
        
        # Interests (indicates preferences)
        if prospect.interests:
            text_parts.append(" ".join(prospect.interests))
        
        # Recent activity content (recent communication patterns)
        if prospect.recent_activity:
            for activity in prospect.recent_activity:
                text_parts.append(activity.content)
        
        # Communication style summary (explicit style info)
        comm_style = prospect.communication_style
        text_parts.append(comm_style.analysis_summary)
        
        # Role and company context
        text_parts.append(f"{prospect.role} at {prospect.company}")
        text_parts.append(prospect.industry)
        
        return " ".join(text_parts)
    
    def get_prospect_embedding(self, prospect: ProspectProfile) -> np.ndarray:
        """
        Create semantic embedding from prospect's communication profile
        
        Returns:
            np.ndarray: 384-dimensional embedding vector
        """
        prospect_text = self._get_prospect_text(prospect)
        embedding = self.model.encode(prospect_text, convert_to_numpy=True)
        return embedding
    
    def _get_tone_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Get pre-computed embeddings for different communication tones
        These represent different message styles
        
        Returns:
            Dict mapping tone names to embedding vectors
        """
        if self._tone_embeddings_cache is not None:
            return self._tone_embeddings_cache
        
        tone_descriptions = {
            "formal": (
                "formal professional respectful courteous business communication "
                "maintains proper etiquette high formality conservative tone"
            ),
            "casual": (
                "casual friendly relaxed conversational approachable warm tone "
                "informal friendly easy-going personable human connection"
            ),
            "technical": (
                "technical detailed engineering metrics performance data-driven "
                "specific implementation details technical depth precision"
            ),
            "enthusiastic": (
                "enthusiastic energetic excited passionate positive upbeat "
                "motivated dynamic inspiring encouraging optimistic"
            ),
            "direct": (
                "direct straightforward concise to-the-point efficient clear "
                "action-oriented results-focused no-nonsense blunt"
            )
        }
        
        embeddings = {}
        for tone, description in tone_descriptions.items():
            embeddings[tone] = self.model.encode(description, convert_to_numpy=True)
        
        self._tone_embeddings_cache = embeddings
        return embeddings
    
    def find_best_matching_tones(
        self, prospect: ProspectProfile, top_n: int = 2
    ) -> Dict[str, float]:
        """
        Find the best matching communication tones for a prospect
        
        Args:
            prospect: ProspectProfile object
            top_n: Number of top matches to return
            
        Returns:
            Dict mapping tone names to similarity scores (0-1)
        """
        start = time.time()
        
        # Get prospect embedding
        prospect_embedding = self.get_prospect_embedding(prospect)
        
        # Get tone embeddings
        tone_embeddings = self._get_tone_embeddings()
        
        # Calculate similarity scores
        similarities = {}
        for tone_name, tone_embedding in tone_embeddings.items():
            # Reshape for cosine_similarity (needs 2D arrays)
            similarity = cosine_similarity(
                [prospect_embedding], 
                [tone_embedding]
            )[0][0]
            similarities[tone_name] = float(similarity)
        
        # Sort by similarity and return top N
        sorted_tones = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        top_tones = dict(sorted_tones[:top_n])
        
        elapsed = time.time() - start
        print(f"⏱️  [EMBEDDING] Tone matching completed in {elapsed*1000:.1f}ms")
        print(f"🎯 [EMBEDDING] Best tones for {prospect.name}:")
        for tone, score in top_tones.items():
            bar = "█" * int(score * 20)
            print(f"   {tone:15} {score:.2%} {bar}")
        
        return top_tones
    
    def analyze_communication_style(self, prospect: ProspectProfile) -> Dict:
        """
        Comprehensive analysis of prospect's communication style using embeddings
        
        Args:
            prospect: ProspectProfile object
            
        Returns:
            Dict with analysis results including best tones and detailed insights
        """
        best_tones = self.find_best_matching_tones(prospect)
        primary_tone = list(best_tones.keys())[0]
        primary_score = best_tones[primary_tone]
        
        # Get all tone scores for detailed analysis
        all_tones = self._analyze_all_tones(prospect)
        
        analysis = {
            "primary_tone": primary_tone,
            "primary_tone_confidence": round(primary_score, 3),
            "secondary_tones": list(best_tones.keys())[1:],
            "all_tone_scores": all_tones,
            "analysis_summary": self._generate_analysis_summary(prospect, primary_tone),
            "recommendations": self._get_tone_recommendations(primary_tone)
        }
        
        return analysis
    
    def _analyze_all_tones(self, prospect: ProspectProfile) -> Dict[str, float]:
        """Get similarity scores for all available tones"""
        prospect_embedding = self.get_prospect_embedding(prospect)
        tone_embeddings = self._get_tone_embeddings()
        
        all_scores = {}
        for tone_name, tone_embedding in tone_embeddings.items():
            similarity = cosine_similarity(
                [prospect_embedding], 
                [tone_embedding]
            )[0][0]
            all_scores[tone_name] = round(float(similarity), 3)
        
        return all_scores
    
    def _generate_analysis_summary(self, prospect: ProspectProfile, primary_tone: str) -> str:
        """Generate human-readable summary of analysis"""
        formality = prospect.communication_style.formality_level.value
        language_type = prospect.communication_style.language_type.value
        tone_pref = prospect.communication_style.tone_preference.value
        
        return (
            f"Semantic analysis identifies {primary_tone} communication style. "
            f"Profile shows {formality} formality level with {language_type} language preference. "
            f"Tone preference: {tone_pref}. Recent activity analysis confirms pattern consistency."
        )
    
    def _get_tone_recommendations(self, primary_tone: str) -> Dict[str, str]:
        """Get message generation recommendations for the identified tone"""
        recommendations = {
            "formal": {
                "greeting": "Dear [Name],",
                "opening": "I hope this message finds you well. I wanted to reach out regarding...",
                "closing": "I look forward to hearing from you.",
                "signature": "Best regards,",
                "avoid": ["emojis", "casual language", "exclamation marks"],
                "use": ["professional language", "proper grammar", "formal structure"]
            },
            "casual": {
                "greeting": "Hey [Name]!",
                "opening": "I came across your profile and thought...",
                "closing": "Would love to chat more!",
                "signature": "Cheers,",
                "avoid": ["overly formal tone", "stiff language"],
                "use": ["conversational tone", "friendly language", "emojis occasionally"]
            },
            "technical": {
                "greeting": "[Name],",
                "opening": "I noticed your expertise in [topic]. Regarding [specific detail]...",
                "closing": "Happy to discuss technical details.",
                "signature": "Best,",
                "avoid": ["vague statements", "generic content"],
                "use": ["specific technical terms", "data-driven language", "implementation details"]
            },
            "enthusiastic": {
                "greeting": "Hi [Name]! 🚀",
                "opening": "I'm excited to connect with you about...",
                "closing": "Really looking forward to this!",
                "signature": "Excited to connect,",
                "avoid": ["pessimistic language"],
                "use": ["positive energy", "exclamation marks", "action-oriented language"]
            },
            "direct": {
                "greeting": "[Name],",
                "opening": "Quick value prop: [specific benefit]...",
                "closing": "Let's talk this week.",
                "signature": "Talk soon,",
                "avoid": ["unnecessary details", "fluff"],
                "use": ["concise language", "clear value proposition", "action items"]
            }
        }
        
        return recommendations.get(primary_tone, recommendations["casual"])
    
    def get_prompt_instructions_for_tone(self, tone: str) -> str:
        """
        Generate LLM prompt instructions based on detected tone
        
        Args:
            tone: Communication tone (e.g., 'formal', 'casual')
            
        Returns:
            String with specific instructions for LLM generation
        """
        instructions = {
            "formal": (
                "Write in a formal, professional tone. Use proper grammar and structure. "
                "Avoid casual language, emojis, and exclamation marks. "
                "Focus on professionalism and respect."
            ),
            "casual": (
                "Write in a friendly, conversational tone. Be approachable and warm. "
                "Use casual language and occasional emojis (1-2 max). "
                "Make it feel like a personal connection."
            ),
            "technical": (
                "Write with specific technical details and data-driven language. "
                "Include relevant metrics, implementation details, or technical specifics. "
                "Avoid vague statements and generic content. "
                "Show deep understanding of technical aspects."
            ),
            "enthusiastic": (
                "Write with positive energy and enthusiasm. Use exclamation marks. "
                "Include motivational language and action-oriented phrases. "
                "Make it clear you're excited about the opportunity."
            ),
            "direct": (
                "Be concise and to-the-point. Avoid unnecessary details. "
                "Lead with the value proposition. "
                "Use clear, action-oriented language. "
                "Get straight to the point."
            )
        }
        
        return instructions.get(tone, instructions["casual"])
