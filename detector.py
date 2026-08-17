# detector.py
# Beetles AI v2.0 - Multi-Model Forensic Detection Engine
# Built for journalists. Not developers.

from transformers import pipeline
from PIL import Image
from PIL.ExifTags import TAGS
import warnings
warnings.filterwarnings('ignore')

print("🪲 Loading Beetles AI v2.0 - Forensic Detection Engine")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# LOAD 3 AI MODELS FOR CONSENSUS DETECTION
# ═══════════════════════════════════════════════════════════

MODELS = {}

print("\n[1/3] Loading Primary Model: AI-Image-Detector...")
try:
    MODELS['primary'] = pipeline(
        "image-classification",
        model="umm-maybe/AI-image-detector"
    )
    print("      ✓ Loaded successfully")
except Exception as e:
    print(f"      ✗ Failed: {e}")
    MODELS['primary'] = None

print("\n[2/3] Loading Secondary Model: SDXL Detector...")
try:
    MODELS['secondary'] = pipeline(
        "image-classification",
        model="Organika/sdxl-detector"
    )
    print("      ✓ Loaded successfully")
except Exception as e:
    print(f"      ✗ Failed: {e}")
    MODELS['secondary'] = None
print("\n[3/3] Loading Tertiary Model: AI-vs-Real Detector...")
try:
    MODELS['tertiary'] = pipeline(
        "image-classification",
        model="dima806/ai_vs_real_image_detection"
    )
    print("      ✓ Loaded successfully")
except Exception as e:
    print(f"      ✗ Failed: {e}")
    MODELS['tertiary'] = None

active_models = sum(1 for m in MODELS.values() if m is not None)
print(f"\n{'=' * 60}")
print(f"✅ Beetles AI Ready - {active_models}/3 models active")
print(f"{'=' * 60}\n")


# ═══════════════════════════════════════════════════════════
# HELPER: Parse different model outputs
# ═══════════════════════════════════════════════════════════

def parse_model_output(results):
    """Convert varied model outputs to standard AI probability."""
    ai_score = 0
    human_score = 0

    for result in results:
        label = result['label'].lower()
        score = result['score']

        ai_keywords = ['artificial', 'ai', 'fake', 'generated',
                       'synthetic', 'sdxl', 'diffusion', 'gan']
        real_keywords = ['human', 'real', 'authentic',
                         'nature', 'natural', 'photo']

        if any(word in label for word in ai_keywords):
            ai_score = max(ai_score, score)
        elif any(word in label for word in real_keywords):
            human_score = max(human_score, score)

    return ai_score, human_score


# ═══════════════════════════════════════════════════════════
# METADATA FORENSIC ANALYSIS
# ═══════════════════════════════════════════════════════════

def analyze_metadata(image):
    """Extract EXIF metadata and detect suspicious patterns."""

    findings = {
        "has_camera_data": False,
        "has_gps_data": False,
        "has_software_tag": False,
        "software_used": None,
        "camera_make": None,
        "camera_model": None,
        "date_taken": None,
        "suspicious_flags": [],
        "positive_signals": [],
        "trust_score": 50
    }

    try:
        exif_data = image._getexif() if hasattr(image, '_getexif') else None

        if exif_data is None or len(exif_data) == 0:
            findings["suspicious_flags"].append(
                "No EXIF metadata found - AI-generated images typically strip metadata"
            )
            findings["trust_score"] = 20
            return findings

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)

            if tag_name == "Make":
                findings["has_camera_data"] = True
                findings["camera_make"] = str(value).strip()
                findings["trust_score"] += 20
                findings["positive_signals"].append(
                    f"Camera manufacturer detected: {value}"
                )

            elif tag_name == "Model":
                findings["camera_model"] = str(value).strip()
                findings["trust_score"] += 10

            elif tag_name == "Software":
                findings["has_software_tag"] = True
                findings["software_used"] = str(value).strip()

                ai_tools = ['midjourney', 'dall-e', 'dalle',
                           'stable diffusion', 'stability',
                           'pixverse', 'runway', 'leonardo',
                           'firefly', 'imagen']

                edit_tools = ['photoshop', 'gimp', 'lightroom',
                             'affinity']

                sw_lower = str(value).lower()
                if any(tool in sw_lower for tool in ai_tools):
                    findings["suspicious_flags"].append(
                        f"AI generation tool in metadata: {value}"
                    )
                    findings["trust_score"] = 10
                elif any(tool in sw_lower for tool in edit_tools):
                    findings["suspicious_flags"].append(
                        f"Image edited with: {value}"
                    )
                    findings["trust_score"] -= 10

            elif tag_name == "DateTime" or tag_name == "DateTimeOriginal":
                findings["date_taken"] = str(value)
                findings["positive_signals"].append(
                    f"Original capture date: {value}"
                )

            elif tag_name == "GPSInfo":
                findings["has_gps_data"] = True
                findings["trust_score"] += 10
                findings["positive_signals"].append(
                    "GPS location data present"
                )

        if not findings["has_camera_data"]:
            findings["suspicious_flags"].append(
                "No camera information - unusual for authentic photos"
            )
            findings["trust_score"] -= 20

        findings["trust_score"] = max(0, min(100, findings["trust_score"]))

    except Exception as e:
        findings["suspicious_flags"].append(f"Metadata read error: {str(e)}")

    return findings


# ═══════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════

def analyze_image(image_input):
    """Full forensic analysis using multi-model consensus."""

    if isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        image = image_input

    image_rgb = image.convert("RGB")

    # Run all models
    model_results = []

    for model_name, model in MODELS.items():
        if model is None:
            continue

        try:
            results = model(image_rgb)
            ai_prob, human_prob = parse_model_output(results)

            model_results.append({
                "name": model_name.title() + " Detector",
                "ai_probability": round(ai_prob * 100, 2),
                "human_probability": round(human_prob * 100, 2),
                "verdict": "AI" if ai_prob > 0.5 else "REAL",
                "confidence": round(max(ai_prob, human_prob) * 100, 2)
            })
        except Exception as e:
            print(f"Model {model_name} error: {e}")

    if not model_results:
        return {"error": "All detection models failed"}

    # Calculate consensus
    ai_votes = sum(1 for m in model_results if m["verdict"] == "AI")
    total_votes = len(model_results)
    avg_ai_prob = sum(m["ai_probability"] for m in model_results) / total_votes

    # Metadata analysis
    metadata = analyze_metadata(image)

    # Combined score
    combined_score = avg_ai_prob
    if metadata["trust_score"] < 30:
        combined_score = min(100, combined_score + 15)
    elif metadata["trust_score"] > 70:
        combined_score = max(0, combined_score - 10)

    # Shareability verdict
    verdict = generate_shareability_verdict(
        combined_score, ai_votes, total_votes, metadata
    )

    # Explanation
    explanation = generate_explanation(
        model_results, metadata, combined_score
    )

    return {
        "shareability_verdict": verdict,
        "consensus": {
            "ai_votes": f"{ai_votes}/{total_votes}",
            "average_ai_probability": round(avg_ai_prob, 2),
            "combined_score": round(combined_score, 2),
            "agreement_level": get_agreement_level(model_results)
        },
        "model_results": model_results,
        "metadata": metadata,
        "explanation": explanation,
        "image_info": {
            "dimensions": f"{image.width} x {image.height}",
            "format": image.format if image.format else "Unknown",
            "mode": image.mode
        }
    }


def generate_shareability_verdict(score, ai_votes, total_votes, metadata):
    """Actionable verdict for journalists."""

    if score > 80 and ai_votes == total_votes:
        return {
            "decision": "DO NOT PUBLISH",
            "color": "#dc2626",
            "bg_color": "#fee2e2",
            "icon": "🚨",
            "risk_level": "CRITICAL",
            "message": "This image is almost certainly AI-generated. Publishing could damage your credibility.",
            "action_items": [
                "Do not publish without verification from original source",
                "Perform reverse image search",
                "Contact source directly for original camera file",
                "Check for C2PA content credentials"
            ]
        }
    elif score > 65:
        return {
            "decision": "VERIFY BEFORE PUBLISHING",
            "color": "#ea580c",
            "bg_color": "#ffedd5",
            "icon": "⚠️",
            "risk_level": "HIGH",
            "message": "Strong indicators suggest this image may be AI-generated or manipulated.",
            "action_items": [
                "Request original file from source",
                "Verify with additional detection tools",
                "Cross-reference with news sources",
                "Consider consulting expert"
            ]
        }
    elif score > 45:
        return {
            "decision": "MANUAL REVIEW REQUIRED",
            "color": "#ca8a04",
            "bg_color": "#fef3c7",
            "icon": "🔍",
            "risk_level": "MEDIUM",
            "message": "Detection results are mixed. Human review recommended.",
            "action_items": [
                "Review image details carefully",
                "Check context and source credibility",
                "Verify caption matches image content",
                "Second opinion recommended"
            ]
        }
    elif score > 25:
        return {
            "decision": "PUBLISH WITH STANDARD REVIEW",
            "color": "#16a34a",
            "bg_color": "#dcfce7",
            "icon": "✅",
            "risk_level": "LOW",
            "message": "Image appears authentic. Standard editorial review sufficient.",
            "action_items": [
                "Standard fact-check procedures apply",
                "Verify caption accuracy",
                "Confirm publication rights"
            ]
        }
    else:
        return {
            "decision": "SAFE TO PUBLISH",
            "color": "#059669",
            "bg_color": "#d1fae5",
            "icon": "✅",
            "risk_level": "MINIMAL",
            "message": "Image shows strong signals of authenticity.",
            "action_items": [
                "No detection concerns identified",
                "Proceed with standard editorial workflow"
            ]
        }


def generate_explanation(model_results, metadata, combined_score):
    """Explain WHY, not just WHAT. Key differentiator vs competitors."""

    reasoning = []
    confidence_factors = []

    ai_verdicts = [m for m in model_results if m["verdict"] == "AI"]
    real_verdicts = [m for m in model_results if m["verdict"] == "REAL"]

    if len(ai_verdicts) == len(model_results):
        reasoning.append(
            f"🤖 All {len(model_results)} AI detection models agree this image is AI-generated"
        )
        confidence_factors.append("Strong model consensus")
    elif len(real_verdicts) == len(model_results):
        reasoning.append(
            f"👤 All {len(model_results)} AI detection models agree this image is authentic"
        )
        confidence_factors.append("Strong model consensus")
    else:
        reasoning.append(
            f"⚖️ Models disagree: {len(ai_verdicts)} say AI, {len(real_verdicts)} say Real"
        )
        confidence_factors.append("Model disagreement - lower confidence")

    strongest = max(model_results, key=lambda x: x["confidence"])
    reasoning.append(
        f"🎯 Strongest signal: {strongest['name']} is {strongest['confidence']}% confident it's {strongest['verdict']}"
    )

    if metadata["suspicious_flags"]:
        reasoning.append("📋 Metadata concerns detected:")
        for flag in metadata["suspicious_flags"][:3]:
            reasoning.append(f"   • {flag}")

    if metadata["positive_signals"]:
        reasoning.append("✓ Authentic signals found:")
        for signal in metadata["positive_signals"][:3]:
            reasoning.append(f"   • {signal}")

    if metadata["trust_score"] < 30:
        reasoning.append(
            f"⚠️ Metadata trust score: {metadata['trust_score']}/100 (Low - typical of AI images)"
        )
    elif metadata["trust_score"] > 70:
        reasoning.append(
            f"✓ Metadata trust score: {metadata['trust_score']}/100 (High - authentic signals)"
        )
    else:
        reasoning.append(
            f"⚖️ Metadata trust score: {metadata['trust_score']}/100 (Neutral)"
        )

    return {
        "reasoning": reasoning,
        "confidence_factors": confidence_factors,
        "summary": generate_summary(combined_score, model_results, metadata)
    }


def generate_summary(score, model_results, metadata):
    """1-sentence summary for busy journalists."""
    if score > 80:
        return "High-confidence AI detection based on multiple model consensus and metadata analysis."
    elif score > 60:
        return "Moderate AI indicators present. Additional verification recommended."
    elif score > 40:
        return "Detection results are ambiguous. Manual review needed."
    elif score > 20:
        return "Image appears authentic with minor anomalies."
    else:
        return "Strong authenticity signals detected across all analysis methods."


def get_agreement_level(model_results):
    """Calculate how much models agree."""
    if not model_results:
        return "No data"

    verdicts = [m["verdict"] for m in model_results]

    if len(set(verdicts)) == 1:
        return "Unanimous"
    elif len(model_results) >= 3:
        counts = {v: verdicts.count(v) for v in set(verdicts)}
        max_count = max(counts.values())
        if max_count >= 2:
            return "Majority"
    return "Split"


# TEST
if __name__ == "__main__":
    print("=== BEETLES AI v2.0 TEST ===")
    print(f"Models active: {active_models}/3")
    print("Ready for forensic analysis")
    print("Run 'streamlit run app.py' to start")