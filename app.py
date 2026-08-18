# app.py
# Beetles AI v2.0 - Professional Web Application
# Built for journalists. Not developers.

import streamlit as st
from PIL import Image
import tempfile
import os
from detector import analyze_image

# ═══════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Beetles AI - Forensic Image Verification",
    page_icon="🪲",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══════════════════════════════════════════════════════════
# PROFESSIONAL STYLING
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Brand header */
    .brand-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 2rem;
    }
    .brand-name {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .brand-tagline {
        color: #888;
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* Trust badges */
    .trust-badges {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 1rem 0;
        color: #666;
        font-size: 0.9rem;
    }

    /* Verdict box */
    .verdict-box {
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border-left: 6px solid;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .verdict-decision {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .verdict-message {
        font-size: 1.05rem;
        line-height: 1.6;
        opacity: 0.9;
    }
    .verdict-risk {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-top: 1rem;
        background: rgba(0,0,0,0.1);
    }

    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(0,255,136,0.2);
    }

    /* Data cards */
    .data-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Model badge */
    .model-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .model-ai {
        background: rgba(220,38,38,0.15);
        color: #ff6b6b;
        border: 1px solid rgba(220,38,38,0.3);
    }
    .model-real {
        background: rgba(5,150,105,0.15);
        color: #4ade80;
        border: 1px solid rgba(5,150,105,0.3);
    }

    /* Reasoning list */
    .reasoning-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: rgba(255,255,255,0.03);
        border-left: 3px solid #00d4ff;
        border-radius: 4px;
    }

    /* Action items */
    .action-item {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        background: rgba(0,212,255,0.05);
        border-left: 3px solid #00d4ff;
        border-radius: 4px;
        display: flex;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# HEADER SECTION
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
    <div class="brand-name">🪲 Beetles AI</div>
    <div class="brand-tagline">
        Verify before you publish. Know why, not just what.
    </div>
    <div class="trust-badges">
        <span>🔬 3 AI Models</span>
        <span>📋 Metadata Forensics</span>
        <span>📰 Built for Newsrooms</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# INFO BAR
# ═══════════════════════════════════════════════════════════
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem; background: rgba(0,255,136,0.08); border-radius: 8px;">
        <strong>🆓 Free Beta</strong><br>
        <small>5 verifications/day</small>
    </div>
    """, unsafe_allow_html=True)
with col_info2:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem; background: rgba(0,212,255,0.08); border-radius: 8px;">
        <strong>📰 Journalist Pro</strong><br>
        <small>$19/mo - 100 scans</small>
    </div>
    """, unsafe_allow_html=True)
with col_info3:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem; background: rgba(139,92,246,0.08); border-radius: 8px;">
        <strong>🏢 Newsroom</strong><br>
        <small>$99/mo - Team access</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FILE UPLOAD
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📤 Upload Image for Verification</div>',
            unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="Drop an image here or click to browse",
    type=['png', 'jpg', 'jpeg', 'webp'],
    help="Supported: PNG, JPG, JPEG, WEBP. Max 10MB.",
    label_visibility="collapsed"
)


# ═══════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════
if uploaded_file is not None:

    image = Image.open(uploaded_file)

    # Show image
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image(image, caption=f"📁 {uploaded_file.name}",
                use_container_width=True)

    # Analyze button
    if st.button("🔬 RUN FORENSIC ANALYSIS", type="primary",
                 use_container_width=True):

        with st.spinner("🧠 Running multi-model forensic analysis... (10-30 seconds)"):
            try:
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    image_rgb = image.convert('RGB')
                    image_rgb.save(tmp.name)
                    tmp_path = tmp.name

                # Analyze
                results = analyze_image(tmp_path)
                os.unlink(tmp_path)

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.stop()

        if "error" in results:
            st.error(f"❌ {results['error']}")
            st.stop()

        # ═══════════════════════════════════════════════
        # SHAREABILITY VERDICT (KEY DIFFERENTIATOR)
        # ═══════════════════════════════════════════════
        verdict = results['shareability_verdict']

        st.markdown(f"""
        <div class="verdict-box" style="
            background: {verdict['bg_color']};
            border-left-color: {verdict['color']};
        ">
            <div class="verdict-decision" style="color: {verdict['color']};">
                {verdict['icon']} {verdict['decision']}
            </div>
            <div class="verdict-message" style="color: {verdict['color']};">
                {verdict['message']}
            </div>
            <div class="verdict-risk" style="color: {verdict['color']};">
                RISK LEVEL: {verdict['risk_level']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════
        # ACTION ITEMS
        # ═══════════════════════════════════════════════
        st.markdown('<div class="section-header">📋 Recommended Actions</div>',
                    unsafe_allow_html=True)

        for item in verdict['action_items']:
            st.markdown(f"""
            <div class="action-item">
                <span>{item}</span>
            </div>
            """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════
        # WHY - EXPLANATION (KEY DIFFERENTIATOR)
        # ═══════════════════════════════════════════════
        st.markdown('<div class="section-header">🧠 Why This Verdict?</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div class="data-card">
            <strong style="color: #00d4ff;">Summary:</strong><br>
            <span style="font-size: 1.05rem;">{results['explanation']['summary']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Reasoning:**")
        for item in results['explanation']['reasoning']:
            st.markdown(f"""
            <div class="reasoning-item">
                {item}
            </div>
            """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════
        # CONSENSUS DATA
        # ═══════════════════════════════════════════════
        st.markdown('<div class="section-header">🤖 Multi-Model Consensus</div>',
                    unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Models Voting AI",
                     results['consensus']['ai_votes'])
        with col2:
            st.metric("Avg AI Probability",
                     f"{results['consensus']['average_ai_probability']}%")
        with col3:
            st.metric("Combined Score",
                     f"{results['consensus']['combined_score']}%")
        with col4:
            st.metric("Agreement Level",
                     results['consensus']['agreement_level'])

        # Individual model breakdown
        st.markdown("**Individual Model Results:**")
        for model in results['model_results']:
            verdict_class = "model-ai" if model['verdict'] == "AI" else "model-real"

            st.markdown(f"""
            <div class="data-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{model['name']}</strong><br>
                        <span class="model-badge {verdict_class}">
                            {model['verdict']}
                        </span>
                        <span style="color: #888; font-size: 0.9rem;">
                            {model['confidence']}% confident
                        </span>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #ff6b6b;">
                            AI: {model['ai_probability']}%
                        </div>
                        <div style="color: #4ade80;">
                            Real: {model['human_probability']}%
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════
        # METADATA FORENSICS
        # ═══════════════════════════════════════════════
        st.markdown('<div class="section-header">🔍 Metadata Forensics</div>',
                    unsafe_allow_html=True)

        meta = results['metadata']

        col_meta1, col_meta2 = st.columns(2)

        with col_meta1:
            st.markdown(f"""
            <div class="data-card">
                <strong>📷 Camera Information</strong><br>
                Make: {meta.get('camera_make') or 'Not found'}<br>
                Model: {meta.get('camera_model') or 'Not found'}<br>
                Software: {meta.get('software_used') or 'Not found'}<br>
                Date Taken: {meta.get('date_taken') or 'Not found'}
            </div>
            """, unsafe_allow_html=True)

        with col_meta2:
            trust_color = "#4ade80" if meta['trust_score'] > 60 else (
                "#ff6b6b" if meta['trust_score'] < 30 else "#eab308"
            )
            st.markdown(f"""
            <div class="data-card">
                <strong>🎯 Metadata Trust Score</strong><br>
                <div style="font-size: 2.5rem; font-weight: 800; color: {trust_color};">
                    {meta['trust_score']}/100
                </div>
                <small>Based on EXIF completeness and authenticity signals</small>
            </div>
            """, unsafe_allow_html=True)

        # Flags
        if meta['suspicious_flags']:
            st.markdown("**⚠️ Suspicious Flags:**")
            for flag in meta['suspicious_flags']:
                st.markdown(f"""
                <div class="reasoning-item" style="border-left-color: #ff6b6b;">
                    {flag}
                </div>
                """, unsafe_allow_html=True)

        if meta['positive_signals']:
            st.markdown("**✅ Authentic Signals:**")
            for signal in meta['positive_signals']:
                st.markdown(f"""
                <div class="reasoning-item" style="border-left-color: #4ade80;">
                    {signal}
                </div>
                """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════
        # UPGRADE CTA
        # ═══════════════════════════════════════════════
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,212,255,0.1)); border-radius: 16px;">
            <h3>🚀 Ready to verify at scale?</h3>
            <p>Beetles AI Pro includes bulk upload, PDF reports, API access, and more.</p>
            <p><strong>📧 Contact: your.email@example.com </strong></p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# EMPTY STATE
# ═══════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; opacity: 0.6;">
        <h3>👆 Upload an image to begin forensic analysis</h3>
        <p>Beetles AI will run 3 detection models, analyze metadata,<br>
        and give you a clear verdict on whether to publish.</p>
    </div>
    """, unsafe_allow_html=True)

    # Show features when idle
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("""
        <div class="data-card">
            <h4>🤖 Multi-Model Consensus</h4>
            <p style="opacity: 0.8;">
                We run your image through 3 different AI models
                and combine their verdicts for higher accuracy.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f2:
        st.markdown("""
        <div class="data-card">
            <h4>🔍 Metadata Forensics</h4>
            <p style="opacity: 0.8;">
                We extract EXIF data and detect suspicious patterns
                that indicate AI generation or manipulation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f3:
        st.markdown("""
        <div class="data-card">
            <h4>📰 Journalist-Friendly</h4>
            <p style="opacity: 0.8;">
                Clear verdicts like "DO NOT PUBLISH" with actionable
                next steps, not confusing probability scores.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    🪲 <strong>Beetles AI v2.0</strong> |
    Verify before you publish |
    Built from Pakistan 🇵🇰 |
    <a href="https://x.com/yourhandle" style="color: #00d4ff;">Follow on X</a>
</div>
""", unsafe_allow_html=True)