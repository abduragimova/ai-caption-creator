from pydantic import BaseModel, Field
from typing import List, Optional

class TextBriefRequest(BaseModel):
    """Request model for text brief caption generation"""
    text_brief: str = Field(..., min_length=1, max_length=1000, description="Product description or brief")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_brief": "Eco-friendly bamboo toothbrush with soft bristles"
            }
        }

class CaptionSet(BaseModel):
    """Model for a single caption with hashtags"""
    caption: str
    tone: str  # e.g., "Professional", "Casual", "Playful"

class HashtagSet(BaseModel):
    """Model for a set of hashtags"""
    hashtags: List[str]
    category: str  # e.g., "Trending", "Niche", "Branded"

class PostingTime(BaseModel):
    """Model for suggested posting time"""
    time: str
    day: str
    reason: str

class CaptionResponse(BaseModel):
    """Response model for caption generation"""
    captions: List[CaptionSet]
    hashtag_sets: List[HashtagSet]
    posting_time: PostingTime
    content_type: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "captions": [
                    {"caption": "Transform your smile naturally! 🌱", "tone": "Casual"},
                    {"caption": "Sustainable oral care starts here.", "tone": "Professional"},
                    {"caption": "Because the planet deserves a smile too! 😊", "tone": "Playful"}
                ],
                "hashtag_sets": [
                    {"hashtags": ["#EcoFriendly", "#SustainableLiving", "#GreenProducts"], "category": "Trending"},
                    {"hashtags": ["#BambooToothbrush", "#ZeroWaste", "#PlasticFree"], "category": "Niche"},
                    {"hashtags": ["#YourBrand", "#NaturalCare", "#EcoWarrior"], "category": "Branded"}
                ],
                "posting_time": {
                    "time": "7:00 AM - 9:00 AM",
                    "day": "Tuesday or Thursday",
                    "reason": "Morning routine content performs best during commute hours on weekdays"
                },
                "content_type": "Product - Eco/Lifestyle"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str