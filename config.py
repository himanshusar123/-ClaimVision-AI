import os
from pydantic import BaseModel, Field
from typing import List, Optional

# ---------------------------------------------------------
# Pydantic Schemas for Structured Output
# ---------------------------------------------------------

class DamageAssessment(BaseModel):
    vehicle_area: str = Field(
        description="The specific area of the vehicle where damage is visible (e.g., 'Front Bumper', 'Rear Bumper', 'Left Front Door', 'Roof', 'Windshield')"
    )
    visible_damage: List[str] = Field(
        description="List of types of damage visible (e.g., 'Dent', 'Scratch', 'Crack', 'Shattered Glass', 'Paint Peeling', 'Missing Part')"
    )
    severity: str = Field(
        description="Apparent severity of the damage. Must be one of: 'Low', 'Medium', 'High'"
    )
    observations: List[str] = Field(
        description="Bullet points of objective visual observations in the image. Do not extrapolate."
    )
    privacy_flags: List[str] = Field(
        description="Privacy risks identified in the image, if any (e.g., 'Visible License Plate', 'Visible Face', 'Identifiable Document'). Leave empty if none."
    )
    requires_human_review: bool = Field(
        description="Set to true if there are contradictions, privacy concerns, high severity, or unclear evidence."
    )
    review_reasons: List[str] = Field(
        description="Reasons why human review is required. Leave empty if requires_human_review is false."
    )
    limitations: List[str] = Field(
        description="Limitations of the visual evidence (e.g., 'Poor lighting', 'Reflection obscuring damage', 'Angle does not show full bumper')"
    )

class ClaimComparison(BaseModel):
    is_consistent: bool = Field(
        description="True if the visual evidence supports the claimant's description. False if there are contradictions."
    )
    consistent_details: List[str] = Field(
        description="Details in the claimant description that are visually verified by the photograph."
    )
    inconsistencies: List[str] = Field(
        description="Specific discrepancies between the claimant description and the photograph (e.g., claimed rear damage but image shows front damage, or claimed night crash but photo shows daylight)."
    )
    unverifiable_claims: List[str] = Field(
        description="Claims made by the customer that cannot be verified from the image alone (e.g., internal engine damage, speed of collision)."
    )

class ClaimVisionOutput(BaseModel):
    damage_assessment: DamageAssessment
    claim_comparison: ClaimComparison
    final_routing: str = Field(
        description="Routing decision: 'Auto-Process (Low Risk)', 'Escalate to Specialist (Medium Risk)', or 'Immediate Human Review (High Risk)'"
    )

# ---------------------------------------------------------
# Prompt Templates
# ---------------------------------------------------------

WEAK_PROMPT = "What's in this image?"

IMPROVED_PROMPT_TEMPLATE = """You are ClaimVision AI, an expert multimodal insurance claims assessment assistant.
Analyze the provided vehicle damage photograph and the customer's claim description.

CLAIM DETAILS:
- Customer Description: "{customer_description}"
- Reported Time: {reported_time}
- Estimated Claim Value: ${claim_value}

Your task is to perform an objective assessment of the visual evidence and compare it to the customer's claims.

INSTRUCTIONS:
1. **Damage Assessment**: Identify the vehicle area, visible damage types, and apparent severity (Low/Medium/High). List objective visual observations only.
2. **Privacy Review**: Identify if any sensitive personal data is visible in the image, such as faces, license plates, or identity documents.
3. **Consistency Check**: Compare the image with the claimant description. Flag discrepancies like mismatched damage locations (e.g., front vs rear) or environmental cues (e.g., daytime photo for a 10 PM accident).
4. **Human Review Triggers**: Decide if human review is needed. Trigger human review if:
   - Severity is "High"
   - There are inconsistencies between the claim and the image
   - Privacy issues are detected
   - Visual limitations exist (blurry, bad angle)
   - Claim value is greater than $5,000

CONSTRAINTS (CRITICAL RESPONSIBLE AI GUIDELINES):
- DO NOT estimate repair costs in currency.
- DO NOT determine legal liability or declare fraud.
- DO NOT make legal conclusions. Speak in terms of "inconsistencies" or "unverifiable details".
- Limit observations strictly to what is visible. If something is not visible, flag it as a limitation.

Provide your analysis in the requested structured JSON schema matching the fields of ClaimVisionOutput.
"""

# ---------------------------------------------------------
# Scenarios Database for Offline / Mock Mode
# ---------------------------------------------------------

SCENARIOS = {
    "scenario_1": {
        "title": "Rear-End Collision (Consistent)",
        "customer_description": "I was waiting at a red light when another car bumped into my rear. My rear bumper is badly dented and cracked.",
        "reported_time": "12:30 PM (Daylight)",
        "claim_value": 1800.0,
        "image_file": "rear_bumper_dent.png",
        "mock_output": {
            "damage_assessment": {
                "vehicle_area": "Rear Bumper",
                "visible_damage": ["Dent", "Crack", "Paint Scratch"],
                "severity": "Medium",
                "observations": [
                    "Large impact dent in the center of the rear bumper.",
                    "Horizontal crack in the bumper plastic approximately 15cm long.",
                    "Scratched paint revealing grey undercoat around the impact point."
                ],
                "privacy_flags": [],
                "requires_human_review": False,
                "review_reasons": [],
                "limitations": ["Underbody damage cannot be inspected from this exterior photo."]
            },
            "claim_comparison": {
                "is_consistent": True,
                "consistent_details": [
                    "Damage is located on the rear bumper as described.",
                    "Bumper is dented and cracked as stated."
                ],
                "inconsistencies": [],
                "unverifiable_claims": [
                    "That the vehicle was waiting at a red light.",
                    "That the collision was caused by another vehicle."
                ]
            },
            "final_routing": "Auto-Process (Low Risk)"
        }
    },
    "scenario_2": {
        "title": "Claim Discrepancy (Inconsistent Area)",
        "customer_description": "My car was hit from behind while parked. The rear bumper and left door were damaged.",
        "reported_time": "3:00 PM (Daylight)",
        "claim_value": 3500.0,
        "image_file": "front_bumper_dent.png",
        "mock_output": {
            "damage_assessment": {
                "vehicle_area": "Front Bumper & Grille",
                "visible_damage": ["Dent", "Missing Part", "Crack"],
                "severity": "Medium",
                "observations": [
                    "Significant dent on the front bumper left side.",
                    "Front grille is cracked and partially missing.",
                    "Left headlamp assembly appears loose but intact."
                ],
                "privacy_flags": [],
                "requires_human_review": True,
                "review_reasons": [
                    "Severe discrepancy between customer's statement (rear damage) and the provided image (front damage)."
                ],
                "limitations": ["Photo only shows front profile; rear and left door are not visible in this image."]
            },
            "claim_comparison": {
                "is_consistent": False,
                "consistent_details": [],
                "inconsistencies": [
                    "Customer claimed rear bumper and left door damage, but the submitted image shows front bumper and grille damage."
                ],
                "unverifiable_claims": [
                    "That the vehicle was parked when hit.",
                    "Whether any rear or side damage exists, as it is not shown in this photo."
                ]
            },
            "final_routing": "Immediate Human Review (High Risk)"
        }
    },
    "scenario_3": {
        "title": "Hail Damage (Privacy Risk & High Value)",
        "customer_description": "A sudden hailstorm dented my hood, roof, and cracked my windshield. I was parked in my driveway.",
        "reported_time": "10:00 PM (Night)",
        "claim_value": 7500.0,
        "image_file": "hail_damage.png",
        "mock_output": {
            "damage_assessment": {
                "vehicle_area": "Windshield, Hood & Roof",
                "visible_damage": ["Crack", "Dent"],
                "severity": "High",
                "observations": [
                    "Spiderweb crack on the front windshield center-right.",
                    "Multiple small, shallow circular dents scattered across the hood.",
                    "A human face is visible in the reflection of the driver's side window.",
                    "The license plate is clearly readable at the bottom of the frame."
                ],
                "privacy_flags": ["Visible License Plate", "Visible Face"],
                "requires_human_review": True,
                "review_reasons": [
                    "Privacy risks detected (license plate and face visible in photo reflections).",
                    "Claim value ($7,500) exceeds auto-processing threshold ($5,000).",
                    "High damage severity."
                ],
                "limitations": [
                    "Dents on the roof are difficult to confirm due to light reflection and angle.",
                    "Windshield damage blocks internal view."
                ]
            },
            "claim_comparison": {
                "is_consistent": True,
                "consistent_details": [
                    "Windshield is cracked as described.",
                    "Hood shows multiple small dents consistent with hail."
                ],
                "inconsistencies": [
                    "The accident was reported to occur at 10:00 PM (Night), but the image is clearly taken in bright daylight."
                ],
                "unverifiable_claims": [
                    "That the damage occurred during the specific hailstorm mentioned.",
                    "That the car was parked in the driveway."
                ]
            },
            "final_routing": "Immediate Human Review (High Risk)"
        }
    }
}
