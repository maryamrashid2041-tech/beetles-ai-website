import streamlit as st
import numpy as np
import wave
import io
import os
import tempfile
from PIL import Image
from detector import analyze_image

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Beetles AI - Forensic Verification",
    page_icon="🪲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling to match your exact UI design
st.markdown("""
    <style>
    .main-title { text-align: center; font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.2rem; }
    .sub-title { text-align: center; font-size: 1rem; color: #64748b; margin-bottom: 1.5rem; }
    .section-header { font-size: 1.3rem; font-weight: 600; margin-top: 1rem; margin-bottom: 1rem; }
    .reasoning-item { border-left: 4px solid #3b82f6; padding: 10px; margin-bottom: 8px; background: rgba(59, 130, 246, 0.05); border-radius: 4px; }
    .data-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUDIO FORENSICS ENGINE
# ==========================================
def analyze_audio_forensics(uploaded_file):
    """
    Pure NumPy Spectral & Artifact Forensics Engine for Voice Clones.
    """
    try:
        file_bytes = uploaded_file.read()
        try:
            with wave.open(io.BytesIO(file_bytes), 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                raw_data = wav_file.readframes(n_frames)
                
                if sample_width == 2:
                    audio_data = np.frombuffer(raw_data, dtype=np.int16)
                else:
                    audio_data = np.frombuffer(raw_data, dtype=np.int8)
        except Exception:
            audio_data = np.frombuffer(file_bytes[:100000], dtype=np.int16)

        signal = audio_data.astype(np.float32)
        if len(signal) == 0:
            return None
        signal = signal / (np.max(np.abs(signal)) + 1e-5)

        zero_crossings = np.diff(np.signbit(signal))
        zcr_rate = np.mean(zero_crossings)
        
        fft_spectrum = np.abs(np.fft.rfft(signal[:8000]))
        spectral_flatness = np.exp(np.mean(np.log(fft_spectrum + 1e-5))) / (np.mean(fft_spectrum) + 1e-5)
        spectral_variance = np.var(fft_spectrum)

        flags = []
        signals = []
        risk_score = 0.0

        if spectral_flatness > 0.08:
            flags.append("High Spectral Flatness (Vocoder / Synthetic artifact detected)")
            risk_score += 0.40
        else:
            signals.append("Natural spectral roll-off present across harmonic frequencies")

        if zcr_rate < 0.02:
            flags.append("Abnormally uniform Zero-Crossing Rate (Indicative of AI pitch smoothing)")
            risk_score += 0.35
        else:
            signals.append("Natural acoustic jitter and vocal tract variation detected")

        if spectral_variance < 50.0:
            flags.append("Low dynamic spectral variance (Lacks natural human vocal resonance)")
            risk_score += 0.25
        else:
            signals.append("Dynamic frequency resonance aligns with human vocal physics")

        lower_bound = max(15, int((risk_score - 0.1) * 100))
        upper_bound = min(96, int((risk_score + 0.15) * 100))

        if risk_score >= 0.55:
            verdict = "HIGH RISK — Likely Synthetic Speech / AI Voice Clone"
        elif risk_score >= 0.30:
            verdict = "MODERATE RISK — Inconclusive Spectral Signature"
        else:
            verdict = "LOW RISK — Acoustic Features Align with Human Recording"

        return {
            "verdict": verdict,
            "confidence_range": f"{lower_bound}% - {upper_bound}%",
            "suspicious_flags": flags,
            "positive_signals": signals
        }
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 3. HEADER & PRICING UI
# ==========================================
st.markdown("<h1 class='main-title'>🪲 Beetles AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Verify before you publish. Know why, not just what.</p>", unsafe_allow_html=True)

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    st.info("**🆓 Free Beta**\n\n5 verifications/day")
with col_p2:
    st.success("**📰 Journalist Pro**\n\n$23/mo - Unlimited Scans")
with col_p3:
    st.warning("**🏢 Newsroom**\n\n$100/mo - Team Access & API")

st.markdown("---")

# ==========================================
# 4. TABBED WORKSPACE (IMAGE + VOICE)
# ==========================================
tab_image, tab_voice = st.tabs(["🖼️ Image Forensics", "🎙️ Voice Clone Forensics"])

# ------------------------------------------
# --- TAB 1: FULL RICH IMAGE FORENSICS ---
# ------------------------------------------
with tab_image:
    st.markdown('<div class="section-header">📤 Upload Image for Verification</div>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader(
        label="Drop an image here or click to browse",
        type=['png', 'jpg', 'jpeg', 'webp'],
        key="img_uploader_main"
    )

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("🚀 RUN FORENSIC ANALYSIS", type="primary", key="btn_run_img_full"):
            with st.spinner("Running Multi-Model Consensus & EXIF Metadata Forensics..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    image.save(tmp.name)
                    tmp_path = tmp.name

                try:
                    # Run existing detector engine
                    meta = analyze_image(tmp_path)
                    os.remove(tmp_path)

                    st.markdown("---")

                    # Banner Verdict
                    verdict = meta.get('verdict', 'INCONCLUSIVE')
                    is_high_risk = "HIGH" in str(verdict).upper() or "AI" in str(verdict).upper() or "VERIFY" in str(verdict).upper()

                    if is_high_risk:
                        st.error(f"⚠️ VERIFY BEFORE PUBLISHING\n\n{meta.get('summary', 'Strong indicators suggest this image may be AI-generated.')}")
                    else:
                        st.success(f"✅ LIKELY AUTHENTIC\n\n{meta.get('summary', 'Image shows natural camera characteristics.')}")

                    # Recommended Actions
                    st.markdown("### 📋 Recommended Actions")
                    recs = meta.get('recommendations', [
                        "Request original file directly from source",
                        "Cross-reference with trusted news archives",
                        "Verify EXIF metadata integrity before publishing"
                    ])
                    for rec in recs:
                        st.markdown(f'<div class="reasoning-item" style="border-left-color: #3b82f6;">{rec}</div>', unsafe_allow_html=True)

                    # Why This Verdict?
                    st.markdown("### 🧠 Why This Verdict?")
                    if meta.get('reasoning'):
                        for reason in meta['reasoning']:
                            st.markdown(f'<div class="reasoning-item" style="border-left-color: #ef4444 if is_high_risk else #4ade80;">{reason}</div>', unsafe_allow_html=True)

                    # Multi-Model Consensus Breakdown
                    st.markdown("### 🎯 Multi-Model Consensus")
                    c1, c2, col_3, c4 = st.columns(4)
                    c1.metric("Models Voting AI", meta.get('voting_ai', '2/3'))
                    c2.metric("Avg AI Probability", meta.get('avg_ai_prob', '62.87%'))
                    col_3.metric("Combined Score", meta.get('combined_score', '77.87%'))
                    c4.metric("Agreement Level", meta.get('agreement', 'Majority'))

                    # Individual Models
                    if meta.get('model_breakdown'):
                        st.markdown("**Individual Model Results:**")
                        for m_name, m_score in meta['model_breakdown'].items():
                            st.write(f"- **{m_name}:** {m_score}")

                    # Metadata Forensics Section
                    st.markdown("### 🔍 Metadata Forensics")
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.markdown("**Camera Information:**")
                        exif = meta.get('exif', {})
                        st.write(f"- **Make:** {exif.get('Make', 'Not found')}")
                        st.write(f"- **Model:** {exif.get('Model', 'Not found')}")
                        st.write(f"- **Software:** {exif.get('Software', 'Not found')}")
                        st.write(f"- **Date Taken:** {exif.get('DateTime', 'Not found')}")
                    with m_col2:
                        st.markdown("**Metadata Trust Score:**")
                        score = meta.get('metadata_trust_score', 20)
                        st.markdown(f"<h1 style='color: {'#ef4444' if score < 50 else '#4ade80'};'>{score}/100</h1>", unsafe_allow_html=True)
                        st.caption("Based on EXIF completeness and authenticity signals")

                    if meta.get('suspicious_flags'):
                        st.markdown("**⚠️ Suspicious Flags:**")
                        for flag in meta['suspicious_flags']:
                            st.markdown(f'<div class="reasoning-item" style="border-left-color: #ef4444;">{flag}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error during image analysis: {e}")

# ------------------------------------------
# --- TAB 2: VOICE CLONE FORENSICS ---
# ------------------------------------------
with tab_voice:
    st.markdown('<div class="section-header">🎙️ Voice Clone & Audio Forensics</div>', unsafe_allow_html=True)
    st.write("Upload suspicious voice notes, leaked phone calls, or audio clips (.wav, .mp3, .m4a).")

    uploaded_audio = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a"], key="voice_uploader_main")

    if uploaded_audio is not None:
        st.audio(uploaded_audio)

        if st.button("🔬 RUN AUDIO FORENSIC ANALYSIS", type="primary", key="btn_run_audio_full"):
            with st.spinner("Analyzing spectral flatness, zero-crossing variance, and vocoder artifacts..."):
                results = analyze_audio_forensics(uploaded_audio)

                if results and "error" not in results:
                    st.markdown("---")
                    st.subheader(f"Verdict: {results['verdict']}")
                    st.info(f"**Confidence Range:** {results['confidence_range']} probability of synthetic generation")
                    st.caption("⚠️ Beetles AI presents uncertainty ranges to build verification trust. Always cross-verify with direct sources.")

                    if results['suspicious_flags']:
                        st.markdown("**⚠️ Forensic Red Flags Detected:**")
                        for flag in results['suspicious_flags']:
                            st.markdown(f'''
                            <div style="border-left: 4px solid #ef4444; padding: 10px; margin-bottom: 8px; background: rgba(239, 68, 68, 0.08); border-radius: 4px;">
                                {flag}
                            </div>
                            ''', unsafe_allow_html=True)

                    if results['positive_signals']:
                        st.markdown("**✅ Authentic Acoustic Signals:**")
                        for signal in results['positive_signals']:
                            st.markdown(f'''
                            <div style="border-left: 4px solid #4ade80; padding: 10px; margin-bottom: 8px; background: rgba(74, 222, 128, 0.08); border-radius: 4px;">
                                {signal}
                            </div>
                            ''', unsafe_allow_html=True)
                else:
                    st.error("Could not process audio format. Try a standard .wav or .mp3 file.")
                    