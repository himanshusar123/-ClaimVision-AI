# ClaimVision AI: Multimodal Claims Assessment Assistant & Guardrails Lab

Welcome to the **Week 5 – Day 5 Classroom Project** repository. This project is a fully functional, highly interactive Streamlit application designed to teach **Multimodal AI, Responsible AI, and Production Evaluation** in enterprise AI workflows.

---

## 🎯 Learning Objectives

By the end of this lab, participants will be able to:
1. **Explain Multimodal LLMs**: Understand how models like Gemini 2.5 and GPT-4o combine image and text inputs.
2. **Design Multimodal Prompts**: Implement structured prompt engineering (Role + Image + Context + Task + Constraints + Output Schema).
3. **Perform Structured Extraction**: Extract structured data (JSON) directly from image observations.
4. **Identify Hallucinations & Bias**: Implement safety controls to mitigate risks and prevent models from making legal or financial decisions.
5. **Establish Privacy Shields**: Redact PII (Faces, License Plates) before third-party model inference.
6. **Implement Human-in-the-Loop (HITL)**: Design automated routing rules based on risk levels.
7. **Perform Production Evaluations**: Score model accuracy, groundedness, and safety using a radar-chart assessment scorecard.

---

## 🏗️ Enterprise Production Architecture

The codebase models a real-world enterprise pipeline where raw claims go through multiple guardrails before processing:

```text
              Claim Submission (Text + Images)
                             │
                             ▼
             Input Validation & Demographics Scrubbing
                             │
                             ▼
             Privacy Shield (Obfuscate Faces/Plates)
                             │
                             ▼
             Multimodal Prompt Composer (Inject Constraints)
                             │
                             ▼
                    Gemini Multimodal Client
                             │
                             ▼
             Structured Output Parser (JSON Schema)
                             │
                             ▼
            Policy Guardrails (Anti-Hallucination)
                             │
                             ▼
                  HITL Risk Routing Engine
                   ┌─────────┴─────────┐
                   ▼                   ▼
             [Low Risk]          [High/Med Risk]
            Auto-Process        Human Escalation
                   │                   │
                   └─────────┬─────────┘
                             ▼
                Claims Management Database
```

---

## 📁 Codebase Structure

*   `app.py`: The frontend dashboard with interactive tabs demonstrating each curriculum stage.
*   `gemini_client.py`: API integration layer supporting the live `google-genai` client and an intelligent **Offline Mock Mode** fallback.
*   `config.py`: Structured Pydantic schemas, prompt templates, and the offline scenario database.
*   `generate_assets.py`: Utilities to draw stylized mock accident photos programmatically.
*   `requirements.txt`: Python package dependencies.
*   `.gitignore`: File exclusions.

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Installation
Clone the repository and install the dependencies:
```powershell
# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Mock Images
Run the script to programmatically draw and place the stylized scenario images in the `assets/` directory:
```powershell
python generate_assets.py
```

### 4. Run the Application
Start the Streamlit application:
```powershell
streamlit run app.py
```

### 5. Live Mode (Optional)
To connect the application to a live Gemini model:
1. Provide a **Gemini API Key** in the sidebar text field, or
2. Set the environment variable:
   ```powershell
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
   The app will automatically detect it and transition from Mock Mode to Live Mode.

---

## 📘 Interactive Classroom Activities

### Lab 1: Multimodal Prompt Engineering (Tab 2)
1. Observe the difference between the **Weak Prompt** (`"What's in this image?"`) and the **Improved Prompt**.
2. Edit the prompt in the text area to inject a new constraint: *e.g., "Must identify if weather was rainy based on image reflections."*
3. Run the analysis and verify if the structured JSON outputs the new information.

### Lab 2: Evidence Consistency Checking (Tab 3)
1. Select **Scenario 2 (Claim Discrepancy)**.
2. Note the contradiction: Customer description claims *rear damage*, but the photo shows *front bumper damage*.
3. Notice how the model correctly flags `is_consistent: False` and adds this discrepancy to `inconsistencies`.

### Lab 3: Responsible AI & Guardrails (Tab 4 & 5)
1. **Privacy Shield**: Test **Scenario 3 (Hail Damage)** and observe the flagged privacy risks (license plate and face visible).
2. **Bias Scrubbing**: Toggle demographic filters to review how claimant metadata is withheld from the model context to prevent underwriting bias.
3. **Policy Guardrails**: Verify that the model never outputs exact repair costs or liability statements, as constrained by the system prompts.

### Lab 4: Production Evaluation Scorecard (Tab 6)
1. Evaluate the model response on the 6 quality dimensions (Visual Accuracy, Groundedness, Completeness, etc.).
2. Create and download your custom **Evaluation Scorecard JSON** for audit tracking.

---

## 🎓 Trainer Assessment Questions

Instructors can gauge understanding using the following review questions:
1. **What is Multimodal AI?** Combining info from multiple modalities (image, text) in a single task.
2. **Why does prompt engineering still matter for vision models?** To ensure the response remains grounded in visual evidence, follows schema format, and obeys policy boundaries.
3. **Why use structured outputs like JSON?** So downstream automated claims software can ingest the decision parameters directly without needing regex-parsing on raw text.
4. **What is multimodal hallucination?** Confidently making assertions not supported by the image (e.g. estimating repair costs or speeds).
5. **What is the goal of Human-in-the-Loop?** Creating automated escalations for edge cases, high value, or privacy triggers rather than completely automating risky processes.
