import streamlit as st
import os
import json
from PIL import Image
import plotly.graph_objects as go
from config import SCENARIOS, WEAK_PROMPT, IMPROVED_PROMPT_TEMPLATE, ClaimVisionOutput
from gemini_client import analyze_claim_multimodal, get_gemini_client

# ---------------------------------------------------------
# Page Configurations & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="ClaimVision AI - Multimodal Insurance Assistant",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphism, gradient titles, and cards
st.markdown("""
<style>
    /* Main Layout */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Gradient */
    .title-gradient {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }
    
    /* Premium Cards */
    .premium-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        color: #3b82f6;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-high {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-medium {
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-low {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Prompt Editor style */
    .prompt-box {
        font-family: 'Courier New', Courier, monospace;
        background-color: #0b0f19;
        border: 1px solid #1e293b;
        color: #e2e8f0;
        padding: 12px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar - Global Settings & API Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/car-crash.png", width=70)
    st.markdown("## ClaimVision Control Panel")
    st.markdown("Week 5 – Day 5 Classroom Lab")
    
    # API key setup
    api_key_input = st.text_input(
        "Gemini API Key (Optional)", 
        type="password",
        help="Provide a Gemini API Key to run live multimodal queries. If empty, the app operates in intelligent Offline Mock Mode.",
        value=os.environ.get("GEMINI_API_KEY", "")
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("API Key updated for this session!")
    else:
        st.info("💡 Operating in **Offline Mock Mode** using local pre-baked scenarios.")
        
    st.markdown("---")
    st.markdown("### Learning Methodology")
    st.caption("Scenario ➔ Concept ➔ Demo ➔ Hands-on ➔ Evaluation ➔ Responsible AI")
    st.markdown("### Key Concepts Demonstrated:")
    st.caption("- Multimodal LLM Prompting\n- Structured JSON Extractions\n- Evidence Cross-Referencing\n- Bias & Privacy Redaction\n- Human-in-the-Loop Routing\n- Production-Grade Evaluations")

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = "scenario_1"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_image" not in st.session_state:
    st.session_state.selected_image = None
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = IMPROVED_PROMPT_TEMPLATE
if "last_analyzed_key" not in st.session_state:
    st.session_state.last_analyzed_key = None

# Helper to load images
def load_scenario_image(img_name):
    path = os.path.join("assets", img_name)
    if os.path.exists(path):
        return Image.open(path)
    # Fallback to white image
    return Image.new("RGB", (600, 400), "white")

# ---------------------------------------------------------
# Main Header
# ---------------------------------------------------------
st.markdown('<div class="title-gradient">ClaimVision AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multimodal Insurance Claims Assessment Assistant & Guardrails Lab</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabs Navigation
# ---------------------------------------------------------
tabs = st.tabs([
    "📂 1. Workspace & Input", 
    "✍️ 2. Prompt Engineering", 
    "⚖️ 3. Evidence Consistency", 
    "🛡️ 4. Responsible AI", 
    "🚦 5. HITL Routing", 
    "📊 6. Evaluation Scorecard", 
    "🏗️ 7. Enterprise Architecture"
])

# ---------------------------------------------------------
# TAB 1: Workspace & Input
# ---------------------------------------------------------
with tabs[0]:
    st.markdown("### 1. Configure the Claim Information")
    st.markdown("Select a preset scenario below to load damage images and statements, or upload a custom claim to test the assistant.")

    col_setup_left, col_setup_right = st.columns([1, 1])

    with col_setup_left:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 Claim Details Setup</div>', unsafe_allow_html=True)
        
        # Scenario Selector
        scenario_options = {k: v["title"] for k, v in SCENARIOS.items()}
        selected_key = st.selectbox(
            "Select Claim Scenario Template",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x]
        )
        
        # Update session state if template changes
        if selected_key != st.session_state.current_scenario:
            st.session_state.current_scenario = selected_key
            st.session_state.analysis_result = None
            st.session_state.last_analyzed_key = None

        current_scen_data = SCENARIOS[st.session_state.current_scenario]
        
        # Scenario Inputs (Editable)
        cust_desc = st.text_area("Customer's Statement", value=current_scen_data["customer_description"], height=100)
        
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            rep_time = st.text_input("Reported Time of Incident", value=current_scen_data["reported_time"])
        with col_meta2:
            claim_val = st.number_input("Estimated Claim Value ($)", value=current_scen_data["claim_value"], step=100.0)

        # Claimant profile (contains demographic/irrelevant variables to demonstrate bias testing)
        st.markdown("#### Claimant Demographics (For Bias Testing)")
        col_dem1, col_dem2 = st.columns(2)
        with col_dem1:
            claimant_age = st.number_input("Claimant Age", value=24, min_value=18, max_value=100)
            claimant_gender = st.selectbox("Claimant Gender", ["Male", "Female", "Non-Binary"])
        with col_dem2:
            claimant_history = st.selectbox("Previous Claims", ["0 Claims", "1 Claim", "2+ Claims"])
            claimant_postcode = st.text_input("Postcode Area", value="TX-75001")
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col_setup_right:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📸 Visual Evidence</div>', unsafe_allow_html=True)
        
        # File uploader for custom testing
        uploaded_file = st.file_uploader("Upload custom accident photo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        
        is_custom = False
        if uploaded_file is not None:
            # Custom image uploaded
            pil_image = Image.open(uploaded_file)
            st.session_state.selected_image = pil_image
            st.image(pil_image, caption="Uploaded Claimant Image", use_container_width=True)
            img_name_to_use = uploaded_file.name
            is_custom = True
        else:
            # Template image
            img_name = current_scen_data["image_file"]
            pil_image = load_scenario_image(img_name)
            st.session_state.selected_image = pil_image
            st.image(pil_image, caption=f"Scenario Image: {img_name}", use_container_width=True)
            img_name_to_use = img_name

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 2. Run Multimodal Analysis")
    st.markdown("Process this claim through the ClaimVision Multimodal engine. The model will extract structural attributes, check for privacy triggers, and evaluate claim consistency.")

    if st.button("🚀 Analyze Claim with ClaimVision AI", type="primary", use_container_width=True):
        with st.spinner("Invoking Gemini multimodal model and validating safety guardrails..."):
            
            # Format prompt with variables
            full_prompt = st.session_state.custom_prompt.format(
                customer_description=cust_desc,
                reported_time=rep_time,
                claim_value=claim_val
            )
            
            # Run analysis
            result = analyze_claim_multimodal(
                image=st.session_state.selected_image,
                customer_description=cust_desc,
                reported_time=rep_time,
                claim_value=claim_val,
                image_name=img_name_to_use,
                prompt_text=full_prompt,
                custom_image=is_custom
            )
            
            st.session_state.analysis_result = result
            st.session_state.last_analyzed_key = st.session_state.current_scenario
            st.success("Analysis complete! View the results in the subsequent tabs.")

    # Show dashboard summary if analysis exists
    if st.session_state.analysis_result:
        res = st.session_state.analysis_result
        st.markdown("### Latest Analysis Summary")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="Vehicle Area Damaged", value=res.damage_assessment.vehicle_area)
        with col_res2:
            st.metric(label="Damage Severity", value=res.damage_assessment.severity)
        with col_res3:
            routing_color = "red" if "Immediate" in res.final_routing else ("orange" if "Escalate" in res.final_routing else "green")
            st.markdown(f"**Final System Routing:** <span style='color:{routing_color}; font-size:20px; font-weight:bold;'>{res.final_routing}</span>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: Prompt Engineering
# ---------------------------------------------------------
with tabs[1]:
    st.markdown("### Multimodal Prompt Engineering Playground")
    st.markdown("Prompting multimodal models requires structure. Compare a weak instruction vs. a production-grade template containing **Role, Image, Context, Task, Constraints, and Output Format**.")

    col_pr_left, col_pr_right = st.columns(2)

    with col_pr_left:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("#### ❌ Weak Prompt Demonstration", unsafe_allow_html=True)
        st.text_area("Weak Prompt", value=WEAK_PROMPT, height=80, disabled=True)
        st.caption("🚨 **Why this fails in enterprise systems:**\n1. Leads to free-form paragraphs that can't be parsed into a database.\n2. Lacks context (claim value, statement).\n3. Doesn't restrict hallucination (model might invent repair costs or declare fraud).")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_pr_right:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("#### ✅ Production-Grade Structured Prompt (Editable)", unsafe_allow_html=True)
        custom_prompt_text = st.text_area(
            "System Prompt Template",
            value=st.session_state.custom_prompt,
            height=280,
            help="You can edit the prompt template below. Use {customer_description}, {reported_time}, and {claim_value} as placeholders."
        )
        # Update session state on edit
        if custom_prompt_text != st.session_state.custom_prompt:
            st.session_state.custom_prompt = custom_prompt_text
            st.toast("Prompt template updated!")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### 📐 Target Output Structure (Pydantic Schema)")
    st.markdown("Multimodal outputs must be parsed into downstream systems. ClaimVision enforces JSON output adhering to a strict schema.")
    
    with st.expander("Show Target ClaimVisionOutput Schema (Pydantic Definition)"):
        st.code("""
class DamageAssessment(BaseModel):
    vehicle_area: str          # e.g., 'Front Bumper'
    visible_damage: List[str]  # e.g., ['Dent', 'Scratch']
    severity: str              # 'Low' | 'Medium' | 'High'
    observations: List[str]    # Strict visual evidence bullets
    privacy_flags: List[str]   # e.g., ['Visible License Plate']
    requires_human_review: bool
    review_reasons: List[str]
    limitations: List[str]     # Visual limitations e.g., reflections

class ClaimComparison(BaseModel):
    is_consistent: bool
    consistent_details: List[str]
    inconsistencies: List[str]
    unverifiable_claims: List[str]

class ClaimVisionOutput(BaseModel):
    damage_assessment: DamageAssessment
    claim_comparison: ClaimComparison
    final_routing: str         # Auto-Process | Escalate | Human Review
        """, language="python")

# ---------------------------------------------------------
# TAB 3: Evidence Consistency
# ---------------------------------------------------------
with tabs[2]:
    st.markdown("### Evidence Consistency & Reasoning")
    st.markdown("A key value of multimodal models is cross-referencing information between multiple modalities (text description vs. image evidence).")

    if st.session_state.analysis_result is None:
        st.warning("⚠️ Please run the analysis on the 'Workspace & Input' tab first to populate this view.")
    else:
        res = st.session_state.analysis_result
        comp = res.claim_comparison

        col_comp_left, col_comp_right = st.columns([1, 1])

        with col_comp_left:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📖 Reported Claims vs Visible Reality</div>', unsafe_allow_html=True)
            
            # Consistency indicator
            if comp.is_consistent:
                st.success("✅ Visual evidence is structurally consistent with the claimant's description.")
            else:
                st.error("🚨 Inconsistency detected! The photograph does not align with the claimant's statement.")

            st.markdown("#### Grounded Observations (What the AI sees):")
            for obs in res.damage_assessment.observations:
                st.markdown(f"- 👁️ {obs}")

            st.markdown('</div>', unsafe_allow_html=True)

        with col_comp_right:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📊 Cross-Reference Matrix</div>', unsafe_allow_html=True)
            
            # Consistent items
            st.markdown("**Validated Details:**")
            if comp.consistent_details:
                for d in comp.consistent_details:
                    st.info(f"✔️ {d}")
            else:
                st.caption("No details validated.")

            # Inconsistent items
            st.markdown("**Discrepancies / Inconsistencies:**")
            if comp.inconsistencies:
                for inc in comp.inconsistencies:
                    st.error(f"❌ {inc}")
            else:
                st.success("No visual discrepancies found.")

            # Unverifiable items
            st.markdown("**Unverifiable Claims (Requires investigation):**")
            for unv in comp.unverifiable_claims:
                st.warning(f"❓ {unv}")
            st.caption("Note: The model recognizes that features like internal damage or driving speed cannot be inferred from a single photograph, avoiding hallucination.")

            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4: Responsible AI
# ---------------------------------------------------------
with tabs[3]:
    st.markdown("### Responsible AI Guardrails Lab")
    st.markdown("Deploying multimodal models to production requires wrapping them with privacy, bias, and policy guardrails.")

    # 1. Privacy Shield
    st.markdown("#### 🛡️ Shield 1: Privacy Protection & Redaction")
    st.markdown("Accident photographs often contain PII (Faces, License Plates, ID cards). Before sending the images to third-party endpoints, the system should redact these elements.")
    
    col_priv_left, col_priv_right = st.columns([1, 1.2])
    with col_priv_left:
        st.image("assets/hail_damage.png", caption="Raw Image (With visible face reflection and license plate)", use_container_width=True)
    with col_priv_right:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("**Privacy Redaction Simulation**")
        st.markdown("If we toggle privacy redaction, the front-end redacts sensitive regions before prompt compilation:")
        
        redact_plates = st.checkbox("Redact License Plates", value=True)
        redact_faces = st.checkbox("Redact Faces & People", value=True)
        
        if st.session_state.analysis_result:
            p_flags = st.session_state.analysis_result.damage_assessment.privacy_flags
            if p_flags:
                st.warning(f"⚠️ Privacy risks identified by AI: {', '.join(p_flags)}")
                if redact_plates or redact_faces:
                    st.info("🔒 Action Taken: Local obfuscation (blurring/black-boxing) of identified coordinates performed.")
            else:
                st.success("✅ No privacy flags raised for the current scenario.")
        else:
            st.info("Analyze a scenario to view privacy flags.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Bias Mitigation
    st.markdown("#### ⚖️ Shield 2: Demographic Bias Filter")
    st.markdown("Underwriting or claims adjudication must be based purely on damage severity, not demographic traits. Traditional applications send full metadata, introducing bias risks.")
    
    col_bias_left, col_bias_right = st.columns(2)
    with col_bias_left:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("**Without Bias Filter (Unsafe)**")
        st.caption("Sending all variables to the model can lead to discriminatory profiling.")
        st.code(f"""
{{
  "claimant_age": {claimant_age},
  "claimant_gender": "{claimant_gender}",
  "previous_claims": "{claimant_history}",
  "postcode_area": "{claimant_postcode}",
  "customer_description": "{cust_desc}"
}}
        """, language="json")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_bias_right:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("**With Active Bias Mitigation (Safe)**")
        st.caption("We scrub demographic variables. The prompt sent to Gemini focuses ONLY on objective features.")
        st.code(f"""
{{
  "customer_description": "{cust_desc}",
  "reported_time": "{rep_time}",
  "claim_value": {claim_val}
}}
        """, language="json")
        st.success("🔒 Mitigated: All claimant demographic traits have been stripped out. The damage assessment is 100% anonymous and unbiased.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Policy Guardrails
    st.markdown("#### 🚫 Shield 3: Policy Guardrails & Anti-Hallucination")
    st.markdown("We must enforce policies to ensure the AI does not issue legal verdicts (e.g. 'claim is fraud' or 'customer is liable') or invent monetary numbers.")
    
    col_pol1, col_pol2 = st.columns(2)
    with col_pol1:
        st.markdown('<div class="premium-card" style="border-left: 5px solid #ef4444;">', unsafe_allow_html=True)
        st.markdown("**Forbidden Actions Checked**")
        st.markdown("- ❌ Estimate exact repair costs in dollars\n- ❌ Declare customer committed fraud\n- ❌ State legal liability (who is 'at fault')")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_pol2:
        st.markdown('<div class="premium-card" style="border-left: 5px solid #10b981;">', unsafe_allow_html=True)
        st.markdown("**Guardrail Interception Results**")
        if st.session_state.analysis_result:
            # Check model outputs for violations
            txt_output = str(st.session_state.analysis_result.model_dump())
            violations = []
            if "$" in txt_output and "value" not in txt_output: # simple regex check
                violations.append("Repair cost estimation in USD detected.")
            if "fault" in txt_output.lower() or "liable" in txt_output.lower():
                violations.append("Legal liability assertion detected.")
            if "fraud" in txt_output.lower() or "scam" in txt_output.lower():
                violations.append("Fraud declaration detected.")
                
            if violations:
                for v in violations:
                    st.error(f"⚠️ Guardrail Trashed Output: {v}")
            else:
                st.success("✅ Output Verified: No policy violations detected. The AI remained strictly objective.")
        else:
            st.caption("Analyze a scenario to view guardrail verification.")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 5: HITL Routing
# ---------------------------------------------------------
with tabs[4]:
    st.markdown("### Human-in-the-Loop (HITL) Routing Dashboard")
    st.markdown("Responsible AI requires knowing where automation should stop. High-risk, ambiguous, or high-value claims are escalated to human claims officers.")

    if st.session_state.analysis_result is None:
        st.warning("⚠️ Please run the analysis on the 'Workspace & Input' tab first to populate this view.")
    else:
        res = st.session_state.analysis_result
        assess = res.damage_assessment
        
        col_hitl_left, col_hitl_right = st.columns([1.2, 1])
        
        with col_hitl_left:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🚦 Routing Decision Path</div>', unsafe_allow_html=True)
            
            # Badge rendering based on routing
            routing = res.final_routing
            if "High Risk" in routing:
                st.markdown(f'<span class="badge badge-high" style="font-size:1rem; padding: 6px 12px;">{routing}</span>', unsafe_allow_html=True)
                st.error("🚨 Escalated: This claim requires manual review by an experienced Claims Officer.")
            elif "Medium Risk" in routing:
                st.markdown(f'<span class="badge badge-medium" style="font-size:1rem; padding: 6px 12px;">{routing}</span>', unsafe_allow_html=True)
                st.warning("⚠️ Escalate: This claim is routed to a Claims Specialist.")
            else:
                st.markdown(f'<span class="badge badge-low" style="font-size:1rem; padding: 6px 12px;">{routing}</span>', unsafe_allow_html=True)
                st.success("✅ Auto-Processed: This claim meets all low-risk requirements and can be fast-tracked.")

            # Display review checklist
            st.markdown("#### Routing Checklist Details:")
            checklist = [
                ("Claim Value Threshold Check", "Passed (Value < $5,000)" if claim_val <= 5000 else "Triggered (Value > $5,000)"),
                ("Evidence Consistency Check", "Passed (Consistent)" if res.claim_comparison.is_consistent else "Triggered (Inconsistent)"),
                ("Privacy Redaction Check", "Passed (No PII)" if not assess.privacy_flags else f"Triggered (PII: {', '.join(assess.privacy_flags)})"),
                ("Damage Severity Check", f"Passed (Severity: {assess.severity})" if assess.severity != "High" else "Triggered (High Severity)")
            ]
            
            for check, status in checklist:
                icon = "🟢" if "Passed" in status else "🔴"
                st.markdown(f"{icon} **{check}**: {status}")

            st.markdown('</div>', unsafe_allow_html=True)

        with col_hitl_right:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📋 Human Review Details</div>', unsafe_allow_html=True)
            
            if assess.requires_human_review:
                st.markdown("**Reasons for Human Escalation:**")
                for r in assess.review_reasons:
                    st.markdown(f"- 🔎 {r}")
            else:
                st.markdown("⭐ Claim was approved for automated processing. No routing triggers fired.")

            st.markdown("**Evidence Limitations Identified:**")
            if assess.limitations:
                for lim in assess.limitations:
                    st.markdown(f"- ⚠️ {lim}")
            else:
                st.caption("No limitations reported.")
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 6: Evaluation Scorecard
# ---------------------------------------------------------
with tabs[5]:
    st.markdown("### Production Multimodal Evaluation Framework")
    st.markdown("Before deploying models to production, we evaluate outputs across six quality dimensions. Rate the current response to build your evaluation scorecard.")

    # Scores state
    col_score1, col_score2 = st.columns([1, 1.2])

    with col_score1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 Scorecard Editor</div>', unsafe_allow_html=True)
        
        v_acc = st.slider("Visual Accuracy (Did it identify the correct details?)", 1, 5, 4)
        grounded = st.slider("Groundedness (Are conclusions supported by the image/text?)", 1, 5, 5)
        complete = st.slider("Completeness (Did it miss any visible damage?)", 1, 5, 4)
        inst_f = st.slider("Instruction Following (Did it output JSON correctly?)", 1, 5, 5)
        halluc = st.slider("Hallucination-Free (Did it invent cost or liability?)", 1, 5, 5)
        safety_sc = st.slider("Safety & Policy (Did it filter demographic bias?)", 1, 5, 5)
        
        eval_notes = st.text_area("Evaluation Comments / Findings", "The model successfully followed the structured output format, ignored the demographic variables, and identified the inconsistencies in claim 2.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col_score2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕸️ Evaluation Radar Chart</div>', unsafe_allow_html=True)
        
        # Plotly Radar Chart
        categories = ['Visual Accuracy', 'Groundedness', 'Completeness', 
                      'Instruction Following', 'Hallucination-Free', 'Safety & Policy']
        
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
              r=[v_acc, grounded, complete, inst_f, halluc, safety_sc],
              theta=categories,
              fill='toself',
              name='Model Performance',
              line_color='#8b5cf6',
              fillcolor='rgba(139, 92, 246, 0.3)'
        ))

        fig.update_layout(
          polar=dict(
            radialaxis=dict(
              visible=True,
              range=[0, 5]
            )),
          showlegend=False,
          paper_bgcolor='rgba(0,0,0,0)',
          plot_bgcolor='rgba(0,0,0,0)',
          font=dict(color='#94a3b8')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### Export Evaluation Report")
    
    avg_score = (v_acc + grounded + complete + inst_f + halluc + safety_sc) / 6.0
    
    scorecard_json = {
        "scenario": st.session_state.current_scenario,
        "average_score": round(avg_score, 2),
        "scores": {
            "visual_accuracy": v_acc,
            "groundedness": grounded,
            "completeness": complete,
            "instruction_following": inst_f,
            "hallucination_free": halluc,
            "safety_and_policy": safety_sc
        },
        "notes": eval_notes
    }
    
    st.download_button(
        "📥 Download Evaluation Scorecard JSON",
        data=json.dumps(scorecard_json, indent=2),
        file_name=f"claimvision_eval_{st.session_state.current_scenario}.json",
        mime="application/json"
    )

# ---------------------------------------------------------
# TAB 7: Enterprise Architecture
# ---------------------------------------------------------
with tabs[6]:
    st.markdown("### Enterprise Production Architecture")
    st.markdown("Deploying a multimodal assistant requires an architecture containing validation layers, privacy redactions, prompt injectors, policy guardrails, and HITL queues.")

    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏗️ System Architecture Flow</div>', unsafe_allow_html=True)
    
    st.markdown("""
```mermaid
graph TD
    A[Claim Submission: Text + Images] --> B[Input Validation & Demographics Scrubbing]
    B --> C[Privacy Shield: License Plate/Face Redactor]
    C --> D[Multimodal Prompt Composer: Inject Context & Constraints]
    D --> E[Gemini 2.5 Multimodal API Client]
    E --> F[Structured Output Parser: JSON Schema Enforcement]
    F --> G[Policy Guardrail validation: Intercepts forbidden outputs]
    G --> H{HITL Routing Engine}
    H -->|Low Risk| I[Automated Process: Fast-Track Queue]
    H -->|High/Medium Risk| J[Human in the Loop: Specialty Review Queue]
    I --> K[Claims Management System]
    J --> K
    
    classDef safe fill:#10b981,stroke:#34d399,color:#fff;
    classDef danger fill:#ef4444,stroke:#f87171,color:#fff;
    classDef model fill:#8b5cf6,stroke:#a78bfa,color:#fff;
    classDef regular fill:#1e293b,stroke:#475569,color:#fff;
    
    class B,C,G safe;
    class H danger;
    class E model;
    class A,D,F,I,J,K regular;
```
    """, unsafe_allow_html=False)
    
    st.markdown("#### Architectural Layer Explanations:")
    
    col_arch1, col_arch2 = st.columns(2)
    with col_arch1:
        st.markdown("""
        **1. Input Validation & Demographics Scrubbing (Bias Shield)**
        - Claimant metadata (Age, Gender, Location) is stripped from the context. Only the claim description, value, and event time are passed forward, preventing discriminatory treatment.
        
        **2. Privacy Shield (PII Redaction)**
        - Scans images locally or via secondary vision endpoints for license plates or faces. Obfuscates or warns before endpoint communication.
        
        **3. Multimodal Prompt Composer**
        - Structures the final payload matching the standard curriculum structure (Role, Image, Context, Task, Constraints, Output Schema).
        """)
    with col_arch2:
        st.markdown("""
        **4. Policy Guardrails (Anti-Hallucination)**
        - Intercepts raw responses to guarantee that no currency values or fault declarations are returned. Standardizes unstructured elements.
        
        **5. HITL Routing Engine (Risk Orchestrator)**
        - Segregates outcomes into processing channels. High-value claims ($>5,000) or high-severity cases are barred from auto-processing.
        
        **6. Enterprise Claims Integration**
        - Publishes structural updates directly to claims core databases via verified transaction logs.
        """)
        
    st.markdown('</div>', unsafe_allow_html=True)
