import google.generativeai as genai
from PIL import Image
import json
import time
from typing import Dict, List


class AIService:
    """
    Handles AI interactions using Google Gemini API for caption generation.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize AI service with Gemini model.
        
        Args:
            api_key: Google API key for Gemini
        """
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel('gemini-2.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # System prompt for caption generation
        self.caption_prompt = """You are a creative social media expert specializing in crafting engaging captions and hashtags.

Your task is to generate social media content that is:
- Engaging and attention-grabbing
- Platform-appropriate (Instagram/Facebook/Twitter style)
- Includes emojis where appropriate
- Optimized for maximum engagement
- Authentic and relatable

Generate content in JSON format ONLY, with no additional text or markdown formatting."""
    
    def generate_captions_from_image(self, image_path: str) -> Dict:
        """
        Generate captions from product image.
        
        Args:
            image_path: Path to the product image
            
        Returns:
            Dictionary containing captions, hashtags, and posting time
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            prompt = f"""{self.caption_prompt}

Analyze this product image and generate social media content.

Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
{{
  "captions": [
    {{"caption": "first creative caption here", "tone": "Casual"}},
    {{"caption": "second creative caption here", "tone": "Professional"}},
    {{"caption": "third creative caption here", "tone": "Playful"}}
  ],
  "hashtag_sets": [
    {{"hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"], "category": "Trending"}},
    {{"hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"], "category": "Niche"}},
    {{"hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"], "category": "Branded"}}
  ],
  "posting_time": {{
    "time": "recommended time range",
    "day": "recommended day(s)",
    "reason": "brief explanation why"
  }},
  "content_type": "detected content category"
}}

Make captions creative, engaging, and emoji-rich. Ensure hashtags are relevant and trending."""
            
            # Generate response
            response = self.vision_model.generate_content(
                [prompt, img],
                generation_config={
                    'temperature': 0.9,  # Higher creativity
                    'top_p': 0.95,
                    'max_output_tokens': 2048,
                }
            )
            
            # Parse response
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            print(f"Error generating captions from image: {str(e)}")
            return self._get_fallback_response("product image")
    
    def generate_captions_from_text(self, text_brief: str) -> Dict:
        """
        Generate captions from text brief.
        
        Args:
            text_brief: Product description or brief
            
        Returns:
            Dictionary containing captions, hashtags, and posting time
        """
        try:
            prompt = f"""{self.caption_prompt}

Product/Content Brief: {text_brief}

Based on this brief, generate creative social media content.

Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
{{
  "captions": [
    {{"caption": "first creative caption here", "tone": "Casual"}},
    {{"caption": "second creative caption here", "tone": "Professional"}},
    {{"caption": "third creative caption here", "tone": "Playful"}}
  ],
  "hashtag_sets": [
    {{"hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"], "category": "Trending"}},
    {{"hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"], "category": "Niche"}},
    {{"hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"], "category": "Branded"}}
  ],
  "posting_time": {{
    "time": "recommended time range",
    "day": "recommended day(s)",
    "reason": "brief explanation why"
  }},
  "content_type": "detected content category"
}}

Make captions creative, engaging, and emoji-rich. Ensure hashtags are relevant and trending."""
            
            # Generate response
            response = self.text_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.9,
                    'top_p': 0.95,
                    'max_output_tokens': 2048,
                }
            )
            
            # Parse response
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            print(f"Error generating captions from text: {str(e)}")
            return self._get_fallback_response(text_brief)
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Parse AI response text into structured format.
        
        Args:
            response_text: Raw AI response
            
        Returns:
            Parsed dictionary
        """
        try:
            # Remove markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith('```'):
                # Remove ```json and ``` markers
                clean_text = clean_text.split('```')[1]
                if clean_text.startswith('json'):
                    clean_text = clean_text[4:]
            
            clean_text = clean_text.strip()
            
            # Parse JSON
            data = json.loads(clean_text)
            
            # Validate structure
            required_keys = ['captions', 'hashtag_sets', 'posting_time', 'content_type']
            if not all(key in data for key in required_keys):
                raise ValueError("Missing required keys in response")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Raw response: {response_text[:500]}")
            return self._get_fallback_response("content")
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return self._get_fallback_response("content")
    
    def _get_fallback_response(self, content_hint: str) -> Dict:
        """
        Generate fallback response when AI fails.
        
        Args:
            content_hint: Hint about content type
            
        Returns:
            Fallback response dictionary
        """
        return {
            "captions": [
                {
                    "caption": f"✨ Discover something amazing! Check out this {content_hint} 🌟",
                    "tone": "Casual"
                },
                {
                    "caption": f"Introducing our latest offering. Quality you can trust. 💼",
                    "tone": "Professional"
                },
                {
                    "caption": f"You're going to love this! 😍 Swipe to see why everyone's talking about it! 👉",
                    "tone": "Playful"
                }
            ],
            "hashtag_sets": [
                {
                    "hashtags": ["#NewArrival", "#MustHave", "#Trending", "#InstaGood", "#DailyInspiration"],
                    "category": "Trending"
                },
                {
                    "hashtags": ["#ProductLaunch", "#Innovation", "#QualityProducts", "#ShopNow", "#LimitedEdition"],
                    "category": "Niche"
                },
                {
                    "hashtags": ["#YourBrand", "#BrandStory", "#WeDeliver", "#CustomerFirst", "#ShopLocal"],
                    "category": "Branded"
                }
            ],
            "posting_time": {
                "time": "12:00 PM - 2:00 PM",
                "day": "Wednesday or Thursday",
                "reason": "Lunch break hours on mid-week days typically see high engagement"
            },
            "content_type": "General Product/Service"
        }
    
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            response = self.text_model.generate_content("Hello")
            return response and response.text is not None
        except Exception as e:
            print(f"API key validation failed: {str(e)}")
            return False