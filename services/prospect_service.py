from typing import Dict, List, Optional
from models.prospect import ProspectProfile, CommunicationStyle, ActivityItem, FormalityLevel, LanguageType, ToneType
from datetime import datetime

class ProspectService:
    """Service for managing prospect data (mock data for demo)"""
    
    def __init__(self):
        self.demo_prospects = self._create_demo_prospects()
    
    def _create_demo_prospects(self) -> Dict[str, ProspectProfile]:
        """Create realistic demo prospect profiles"""
        
        prospects = {}
        
        # Tech Startup CTO
        prospects["linkedin.com/in/sarah-chen-cto"] = ProspectProfile(
            id="sarah-chen-001",
            name="Sarah Chen",
            company="TechFlow AI",
            role="Chief Technology Officer",
            industry="Artificial Intelligence",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/sarah-chen-cto",
            interests=["Machine Learning", "Team Building", "Open Source", "Startup Culture"],
            recent_activity=[
                ActivityItem(
                    type="post",
                    content="Just wrapped up our Q4 hiring sprint. Finding great ML engineers is harder than training the models! 🤖 #TechHiring #MachineLearning",
                    date="2024-02-10",
                    engagement=47
                ),
                ActivityItem(
                    type="article_share",
                    content="Shared: 'The Future of AI in Enterprise' - Great insights on practical AI implementation",
                    date="2024-02-08",
                    engagement=23
                )
            ],
            communication_style=CommunicationStyle(
                formality_level=FormalityLevel.PROFESSIONAL,
                language_type=LanguageType.TECHNICAL,
                tone_preference=ToneType.FRIENDLY,
                confidence_score=0.87,
                analysis_summary="Professional but approachable, uses tech terminology, includes emojis occasionally"
            ),
            about_section="Passionate CTO building the future of AI. 10+ years scaling engineering teams. Love solving complex problems and mentoring the next generation of tech leaders.",
            created_at=datetime.now()
        )
        
        # Marketing Director
        prospects["linkedin.com/in/james-rodriguez-marketing"] = ProspectProfile(
            id="james-rodriguez-002",
            name="James Rodriguez",
            company="GrowthLabs Inc",
            role="Director of Marketing",
            industry="Digital Marketing",
            location="Austin, TX",
            linkedin_url="https://linkedin.com/in/james-rodriguez-marketing",
            interests=["Growth Hacking", "Content Strategy", "Data Analytics", "B2B Marketing"],
            recent_activity=[
                ActivityItem(
                    type="post",
                    content="ROI on personalized email campaigns is insane! Just saw 340% increase in response rates with proper segmentation. Data doesn't lie 📊",
                    date="2024-02-12",
                    engagement=89
                ),
                ActivityItem(
                    type="job_change",
                    content="Excited to announce I'm joining GrowthLabs as Director of Marketing!",
                    date="2024-01-15",
                    engagement=156
                )
            ],
            communication_style=CommunicationStyle(
                formality_level=FormalityLevel.CASUAL,
                language_type=LanguageType.BUSINESS,
                tone_preference=ToneType.ENTHUSIASTIC,
                confidence_score=0.92,
                analysis_summary="Casual and enthusiastic, uses marketing metrics, emoji-heavy, data-driven language"
            ),
            about_section="Growth-obsessed marketer with a passion for data-driven strategies. Helped 50+ B2B companies scale from startup to IPO. Always testing, always optimizing.",
            created_at=datetime.now()
        )
        
        # Finance Executive
        prospects["linkedin.com/in/emily-watson-cfo"] = ProspectProfile(
            id="emily-watson-003",
            name="Emily Watson",
            company="Sterling Financial Group",
            role="Chief Financial Officer",
            industry="Financial Services",
            location="New York, NY",
            linkedin_url="https://linkedin.com/in/emily-watson-cfo",
            interests=["Financial Strategy", "Risk Management", "Corporate Governance", "ESG Investing"],
            recent_activity=[
                ActivityItem(
                    type="post",
                    content="Completed our annual audit ahead of schedule. Strong financial controls and transparency remain our top priorities in 2024.",
                    date="2024-02-09",
                    engagement=34
                ),
                ActivityItem(
                    type="article_share",
                    content="Shared: 'ESG Integration in Financial Planning' - Critical reading for modern CFOs",
                    date="2024-02-05",
                    engagement=18
                )
            ],
            communication_style=CommunicationStyle(
                formality_level=FormalityLevel.FORMAL,
                language_type=LanguageType.BUSINESS,
                tone_preference=ToneType.CONSERVATIVE,
                confidence_score=0.94,
                analysis_summary="Formal and conservative, uses financial terminology, focuses on compliance and governance"
            ),
            about_section="Experienced CFO with 15+ years in financial services. Expertise in risk management, regulatory compliance, and strategic financial planning. CPA, MBA from Wharton.",
            created_at=datetime.now()
        )
        
        return prospects
    
    def get_prospect_by_url(self, linkedin_url: str) -> Optional[ProspectProfile]:
        """Get prospect profile by LinkedIn URL"""
        # Normalize URL for lookup
        normalized_url = linkedin_url.replace("https://", "").replace("http://", "")
        return self.demo_prospects.get(normalized_url)
    
    def get_demo_prospects(self) -> List[Dict]:
        """Get list of available demo prospects"""
        return [
            {
                "name": prospect.name,
                "company": prospect.company,
                "role": prospect.role,
                "url": prospect.linkedin_url,
                "preview": f"{prospect.name} - {prospect.role} at {prospect.company}"
            }
            for prospect in self.demo_prospects.values()
        ]