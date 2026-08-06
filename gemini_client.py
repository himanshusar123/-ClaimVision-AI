import os
import json
from PIL import Image
from pydantic import ValidationError
from config import ClaimVisionOutput, SCENARIOS

# Try importing the new Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

class MockGeminiClient:
    """
    Mock client that provides high-quality mock outputs when the API key is missing.
    Includes simple heuristics to analyze user-submitted custom text/images.
    """
    def __init__(self):
        pass

    def generate_content(
        self,
        customer_description: str,
        reported_time: str,
        claim_value: float,
        image_name: str,
        custom_image: bool = False
    ) -> ClaimVisionOutput:
        
        # If it's a known scenario, return its pre-baked mock output
        for key, scenario in SCENARIOS.items():
            if scenario["image_file"] == image_name and not custom_image:
                return ClaimVisionOutput(**scenario["mock_output"])
        
        # If it's a custom upload, run heuristic analysis on the text to simulate AI reasoning
        text_lower = customer_description.lower()
        
        # Default assessment
        vehicle_area = "Unknown / Undetermined"
        visible_damage = ["Scratches"]
        severity = "Low"
        observations = ["Visual inspection confirms body panels are present."]
        privacy_flags = []
        requires_human_review = False
        review_reasons = []
        limitations = ["Interior and engine compartment not visible from exterior photograph."]
        
        # Analyze area keywords
        if "front" in text_lower or "bumper" in text_lower and "rear" not in text_lower:
            vehicle_area = "Front Bumper"
            visible_damage = ["Dent", "Paint Scratch"]
            severity = "Medium"
            observations = [
                "Minor indentation visible on the front bumper center.",
                "Surface paint scrapes present."
            ]
        elif "rear" in text_lower:
            vehicle_area = "Rear Bumper"
            visible_damage = ["Dent", "Crease"]
            severity = "Medium"
            observations = [
                "Localized impact damage visible on the rear bumper cover.",
                "Slight panel misalignment near trunk seal."
            ]
        elif "hail" in text_lower or "roof" in text_lower or "hood" in text_lower:
            vehicle_area = "Roof & Hood"
            visible_damage = ["Dent"]
            severity = "Medium"
            observations = [
                "Multiple shallow circular dents visible across horizontal surfaces."
            ]
        elif "windshield" in text_lower or "glass" in text_lower:
            vehicle_area = "Windshield"
            visible_damage = ["Crack"]
            severity = "Low"
            observations = [
                "Impact point and spiderweb crack visible in front glass."
            ]

        # Overwrite values based on severity keyword
        if "severe" in text_lower or "heavy" in text_lower or "totaled" in text_lower:
            severity = "High"
            observations.append("Severe structural deformation visible.")
        
        # Check for claim value triggers
        if claim_value > 5000:
            requires_human_review = True
            review_reasons.append(f"Claim value (${claim_value:,.2f}) exceeds the auto-processing threshold ($5,000).")
            
        # Simulating a privacy flag if mentioned or randomly
        if "license" in text_lower or "plate" in text_lower:
            privacy_flags.append("Visible License Plate")
            requires_human_review = True
            review_reasons.append("Privacy check triggered: readable license plate detected.")
            
        if "face" in text_lower or "driver" in text_lower:
            privacy_flags.append("Visible Face")
            requires_human_review = True
            review_reasons.append("Privacy check triggered: face reflection visible in window.")

        # Consistency heuristics
        is_consistent = True
        consistent_details = []
        inconsistencies = []
        unverifiable_claims = [
            "Actual speed or force of impact.",
            "Pre-existing mechanical condition prior to collision."
        ]
        
        if vehicle_area != "Unknown / Undetermined":
            consistent_details.append(f"Damage found on {vehicle_area} matches claimant's description.")
        else:
            is_consistent = False
            inconsistencies.append("Visual evidence is inconclusive; cannot verify reported damage location.")
            requires_human_review = True
            review_reasons.append("Inconclusive visual evidence; requires manual inspection.")

        if severity == "High":
            requires_human_review = True
            review_reasons.append("Damage severity is classified as High.")
            
        # Final routing logic
        if requires_human_review or len(inconsistencies) > 0:
            routing = "Immediate Human Review (High Risk)"
            requires_human_review = True
        elif severity == "Medium":
            routing = "Escalate to Specialist (Medium Risk)"
        else:
            routing = "Auto-Process (Low Risk)"

        return ClaimVisionOutput(
            damage_assessment={
                "vehicle_area": vehicle_area,
                "visible_damage": visible_damage,
                "severity": severity,
                "observations": observations,
                "privacy_flags": privacy_flags,
                "requires_human_review": requires_human_review,
                "review_reasons": review_reasons,
                "limitations": limitations
            },
            claim_comparison={
                "is_consistent": is_consistent,
                "consistent_details": consistent_details,
                "inconsistencies": inconsistencies,
                "unverifiable_claims": unverifiable_claims
            },
            final_routing=routing
        )

def get_gemini_client():
    """
    Returns a live google-genai Client if GEMINI_API_KEY is in environment.
    Otherwise returns None (app will fallback to MockGeminiClient).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if SDK_AVAILABLE and api_key:
        try:
            client = genai.Client(api_key=api_key)
            return client
        except Exception:
            return None
    return None

def analyze_claim_multimodal(
    image: Image.Image,
    customer_description: str,
    reported_time: str,
    claim_value: float,
    image_name: str,
    prompt_text: str,
    custom_image: bool = False
) -> ClaimVisionOutput:
    """
    Primary API wrapper. Orchestrates live multimodal call to Gemini or falls back to mock data.
    """
    client = get_gemini_client()
    
    if client is not None:
        try:
            # Live API call using google-genai SDK
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt_text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ClaimVisionOutput,
                ),
            )
            
            # Parse response text back to Pydantic object
            data = json.loads(response.text)
            return ClaimVisionOutput(**data)
            
        except Exception as e:
            # Log error or print in debug, then fallback to mock to ensure zero crashes
            print(f"API Error: {e}. Falling back to mock client.")
            mock_client = MockGeminiClient()
            return mock_client.generate_content(
                customer_description=customer_description,
                reported_time=reported_time,
                claim_value=claim_value,
                image_name=image_name,
                custom_image=custom_image
            )
    else:
        # Offline fallback
        mock_client = MockGeminiClient()
        return mock_client.generate_content(
            customer_description=customer_description,
            reported_time=reported_time,
            claim_value=claim_value,
            image_name=image_name,
            custom_image=custom_image
        )
