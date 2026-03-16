"""
Krishi Mitra AI Service
Powered by Google Gemini for multilingual farming assistance
"""

import os
import json
import re
from typing import Tuple, List, Dict, Any, Optional
import google.generativeai as genai


# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """You are Krishi Mitra (कृषि मित्र / कृषी मित्र), a friendly and knowledgeable AI farming assistant 
for Indian farmers. You specialize in:
- Crop cultivation (Kharif, Rabi, Zaid crops)
- Pest and disease identification & treatment
- Soil health and fertilizer recommendations
- Weather-based agricultural advice
- Government schemes (PM-KISAN, PMFBY, etc.)
- Market prices and crop selling advice
- Organic and sustainable farming

You MUST respond in the language requested:
- 'en' = English
- 'hi' = Hindi (use Devanagari script)
- 'mr' = Marathi (use Devanagari script)

Keep responses practical, simple, and actionable. Use local crop names when relevant.
Format: Use clear paragraphs. For lists, use bullet points. Be warm and supportive like a trusted friend.

At the end of each response, suggest 3 follow-up questions the farmer might want to ask, formatted as:
SUGGESTIONS: ["question1", "question2", "question3"]
"""


class KrishiAIService:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=SYSTEM_PROMPT
        )

    def _parse_suggestions(self, text: str) -> Tuple[str, List[str]]:
        """Extract suggestions from AI response."""
        suggestions = []
        clean_text = text

        match = re.search(r'SUGGESTIONS:\s*(\[.*?\])', text, re.DOTALL)
        if match:
            try:
                suggestions = json.loads(match.group(1))
                clean_text = text[:match.start()].strip()
            except json.JSONDecodeError:
                pass

        return clean_text, suggestions

    def get_farming_advice(
        self,
        message: str,
        language: str = "en",
        context: Dict[str, Any] = {},
        history: List[Dict] = []
    ) -> Tuple[str, List[str]]:
        """Get AI farming advice with conversation history."""
        try:
            lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")

            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, ensure_ascii=False)}"

            # Build prompt with history
            full_message = f"[Respond in {lang_name}]{context_str}\n\nFarmer's question: {message}"

            # Convert history to Gemini chat format
            chat_history = []
            for msg in history[-8:]:  # Last 8 messages for context
                chat_history.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [msg["content"]]
                })

            chat = self.model.start_chat(history=chat_history)
            response = chat.send_message(full_message)
            return self._parse_suggestions(response.text)

        except Exception as e:
            fallback = {
                "en": "Sorry, I'm having trouble connecting. Please check your internet and try again.",
                "hi": "क्षमा करें, कनेक्शन में समस्या है। कृपया पुनः प्रयास करें।",
                "mr": "क्षमस्व, कनेक्शनमध्ये समस्या आहे. कृपया पुन्हा प्रयत्न करा."
            }
            return fallback.get(language, fallback["en"]), []

    def get_crop_specific_advice(self, crop_record) -> Tuple[str, List[str]]:
        """Get advice based on a crop record."""
        try:
            prompt = f"""
            Farmer has this crop:
            - Crop: {crop_record.crop_name}
            - Area: {crop_record.area_acres} acres
            - Season: {crop_record.season}
            - Stage: {crop_record.current_stage}
            - Soil: {crop_record.soil_type}
            - Irrigation: {crop_record.irrigation_type}
            - Issues: {crop_record.issues or 'None reported'}

            Provide detailed, actionable advice for this specific crop situation in English.
            """
            response = self.model.generate_content(prompt)
            return self._parse_suggestions(response.text)
        except Exception as e:
            return f"Error generating advice: {str(e)}", []

    def analyze_disease(self, crop_name: str, symptoms: str, language: str = "en") -> Dict:
        """Analyze crop disease from symptoms."""
        try:
            lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")
            prompt = f"""
            [Respond in {lang_name}]
            Crop: {crop_name}
            Symptoms: {symptoms}

            Analyze and provide:
            1. Likely disease/pest name
            2. Cause (fungal/bacterial/insect/deficiency)
            3. Immediate treatment steps
            4. Preventive measures for future
            5. Which pesticide/fungicide to use (give brand names available in India)

            Format as JSON with keys: disease_name, cause, immediate_treatment, prevention, chemicals
            """
            response = self.model.generate_content(prompt)
            text = response.text

            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass

            return {
                "disease_name": "Analysis Complete",
                "cause": "See details below",
                "immediate_treatment": text,
                "prevention": "",
                "chemicals": ""
            }
        except Exception as e:
            return {"error": str(e)}

    def get_market_insights(
        self, crop: Optional[str], state: str, language: str = "en"
    ) -> Dict:
        """Get market price insights."""
        try:
            lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")
            crop_str = f"for {crop}" if crop else "for major crops"
            prompt = f"""
            [Respond in {lang_name}]
            Provide current market insights {crop_str} in {state}, India.
            Include:
            1. Approximate mandi prices (₹/quintal)
            2. MSP (Minimum Support Price) if applicable
            3. Best time to sell
            4. Tips to get better price
            5. Nearest major mandis in {state}

            Keep it practical and useful for a small farmer.
            """
            response = self.model.generate_content(prompt)
            return {"insights": response.text, "state": state, "crop": crop}
        except Exception as e:
            return {"error": str(e)}

    def get_weather_advisory(self, location: str, season: Optional[str], language: str = "en") -> str:
        """Get weather-based farming advisory."""
        try:
            lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")
            prompt = f"""
            [Respond in {lang_name}]
            Location: {location}, India
            Current Season: {season or 'current'}

            Provide weather-based farming advisory including:
            1. What crops to sow now
            2. Irrigation advice
            3. Pest/disease risk in current weather
            4. Any weather warnings to watch for
            5. Field preparation tips
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def get_government_schemes(
        self, state: str, crop: Optional[str], language: str = "en"
    ) -> str:
        """Get relevant government schemes."""
        try:
            lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")
            crop_str = f"growing {crop}" if crop else ""
            prompt = f"""
            [Respond in {lang_name}]
            A farmer in {state} {crop_str} wants to know about government schemes.

            List all relevant schemes:
            1. Central government schemes (PM-KISAN, PMFBY, KCC, etc.)
            2. {state} state-specific schemes
            3. How to apply for each
            4. Benefits and eligibility
            5. Contact numbers or websites

            Be specific and include 2025-26 schemes.
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
