import streamlit as st
import anthropic

st.set_page_config(
    page_title="AI Governance Readiness Assessment",
    page_icon="🏛",
    layout="centered"
)

st.markdown("""
<style>
.main { max-width: 760px; margin: 0 auto; }
.industry-card {
    background: #1a1a2e;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    border: 1px solid #2a2a4a;
}
.brand-footer {
    text-align: center;
    font-size: 12px;
    color: #6b7280;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

INDUSTRIES = {
    "healthcare": {
        "label": "Healthcare",
        "icon": "🏥",
        "color": "#E24B4A",
        "tagline": "HIPAA · NIST AI RMF · OWASP LLM Top 10 · MITRE ATLAS",
        "consultant_context": "healthcare and clinical AI environments",
        "domains": [
            {
                "id": 0,
                "name": "PHI and data governance",
                "short": "PHI governance",
                "framework": "HIPAA Privacy Rule · NIST AI RMF Govern 1.4",
                "questions": [
                    "Is patient data (PHI) classified before being used to train or inform AI models?",
                    "Do you have documented data retention and deletion policies for AI training data derived from patient records?",
                    "Is there an audit trail for AI-generated outputs that reference or affect patient data?"
                ]
            },
            {
                "id": 1,
                "name": "AI vendor risk and BAA coverage",
                "short": "Vendor / BAA",
                "framework": "HIPAA BAA Requirements · OWASP LLM05 Supply Chain Risk",
                "questions": [
                    "Do your Business Associate Agreements explicitly cover AI model training and inference on patient data?",
                    "Has your organization reviewed AI vendor SOC 2 reports or equivalent attestations in the last 12 months?",
                    "Do AI vendor contracts include model update notification requirements before changes are deployed?"
                ]
            },
            {
                "id": 2,
                "name": "Regulatory alignment",
                "short": "Regulatory",
                "framework": "HIPAA Security Rule · ONC AI Guidance · FDA SaMD",
                "questions": [
                    "Has your organization assessed whether any deployed AI systems qualify as Software as a Medical Device (SaMD) under FDA guidance?",
                    "Do you have documented controls addressing HIPAA Security Rule requirements for AI systems that access ePHI?",
                    "Is there a designated owner responsible for AI regulatory compliance across your organization?"
                ]
            },
            {
                "id": 3,
                "name": "AI incident response",
                "short": "IR readiness",
                "framework": "NIST AI RMF Map 5.1 · HIPAA Breach Notification Rule",
                "questions": [
                    "Does your organization have an AI-specific incident response plan separate from your cybersecurity IR plan?",
                    "Has your team conducted a tabletop exercise for an AI failure scenario in a clinical environment?",
                    "Is there a defined process to determine when an AI output error triggers HIPAA breach notification obligations?"
                ]
            },
            {
                "id": 4,
                "name": "Shadow AI governance",
                "short": "Shadow AI",
                "framework": "NIST AI RMF Govern 1.1 · OWASP LLM09 Overreliance",
                "questions": [
                    "Does your organization maintain an inventory of AI tools in use across clinical and operational staff?",
                    "Is there a defined policy specifying which AI tools are approved, which require approval, and which are prohibited?",
                    "Are clinical staff provided with approved AI tools that meet their workflow needs as an alternative to unsanctioned tools?"
                ]
            }
        ]
    },
    "education": {
        "label": "Education & EdTech",
        "icon": "🎓",
        "color": "#1D9E75",
        "tagline": "FERPA · NIST AI RMF · ISO/IEC 42001 · OWASP LLM Top 10",
        "consultant_context": "education technology and higher education environments",
        "domains": [
            {
                "id": 0,
                "name": "Student data governance",
                "short": "Student data",
                "framework": "FERPA · COPPA · NIST AI RMF Govern 1.4",
                "questions": [
                    "Is student data classified before being used to train or inform AI models?",
                    "Do your FERPA disclosures explicitly cover student data used by or shared with AI systems?",
                    "Is there an audit trail for AI-generated recommendations that affect student academic pathways?"
                ]
            },
            {
                "id": 1,
                "name": "AI vendor risk for EdTech",
                "short": "Vendor risk",
                "framework": "FERPA School Official Standard · OWASP LLM05 Supply Chain Risk",
                "questions": [
                    "Are AI vendors accessing student data formally qualified as school officials under FERPA's legitimate educational interest standard?",
                    "Has your organization reviewed AI vendor data processing agreements and security attestations in the last 12 months?",
                    "Do AI vendor contracts include model update notification requirements before changes are deployed?"
                ]
            },
            {
                "id": 2,
                "name": "Regulatory alignment",
                "short": "Regulatory",
                "framework": "FERPA · State AI in Education Laws · Accreditation Standards",
                "questions": [
                    "Has your organization mapped its AI deployments to applicable state AI in education regulations?",
                    "Do you have documented controls for AI systems used in accreditation-sensitive processes such as grading and admissions?",
                    "Is there a designated owner responsible for AI regulatory compliance across your institution or platform?"
                ]
            },
            {
                "id": 3,
                "name": "AI incident response",
                "short": "IR readiness",
                "framework": "NIST AI RMF Map 5.1 · FERPA Breach Notification",
                "questions": [
                    "Does your organization have an AI-specific incident response plan separate from your cybersecurity IR plan?",
                    "Has your team conducted a tabletop exercise for an AI failure scenario affecting student records or academic decisions?",
                    "Is there a defined process for notifying students and families when an AI system error affects their academic records?"
                ]
            },
            {
                "id": 4,
                "name": "Academic integrity governance",
                "short": "AI integrity",
                "framework": "ISO/IEC 42001 · NIST AI RMF Govern 1.1 · Institutional Policy",
                "questions": [
                    "Does your institution or platform have a documented AI use policy covering students, faculty, and staff?",
                    "Are AI detection tools in use assessed for accuracy and equitable performance across diverse student populations?",
                    "Is there a transparency framework requiring disclosure when AI is used to evaluate, grade, or recommend academic outcomes?"
                ]
            }
        ]
    },
    "financial": {
        "label": "Financial Services",
        "icon": "🏦",
        "color": "#7F77DD",
        "tagline": "SR 11-7 · DORA · NIST AI RMF · OWASP LLM Top 10",
        "consultant_context": "financial services and banking environments",
        "domains": [
            {
                "id": 0,
                "name": "Model risk governance",
                "short": "Model risk",
                "framework": "SR 11-7 · OCC Model Risk Guidance · NIST AI RMF",
                "questions": [
                    "Has your organization extended SR 11-7 model risk management guidance to cover generative AI and LLM deployments?",
                    "Do you have documented model development and validation processes for AI systems used in customer-facing decisions?",
                    "Is there ongoing monitoring for model drift and performance degradation in deployed AI systems?"
                ]
            },
            {
                "id": 1,
                "name": "AI vendor and concentration risk",
                "short": "Vendor risk",
                "framework": "DORA Third-Party Risk · OWASP LLM05 Supply Chain Risk",
                "questions": [
                    "Has your organization assessed AI vendor concentration risk across your AI tool portfolio?",
                    "Do AI vendor contracts include model update notification requirements and documented exit strategies?",
                    "Has your organization reviewed AI vendor SOC 2 reports or equivalent attestations in the last 12 months?"
                ]
            },
            {
                "id": 2,
                "name": "Regulatory alignment",
                "short": "Regulatory",
                "framework": "DORA · OCC · CFPB · Federal Reserve SR 11-7",
                "questions": [
                    "Has your organization assessed DORA obligations for AI systems and AI vendors if operating in or with EU entities?",
                    "Do you have documented controls addressing OCC and CFPB expectations for AI used in credit and lending decisions?",
                    "Is there a designated owner responsible for AI regulatory compliance across your organization?"
                ]
            },
            {
                "id": 3,
                "name": "AI audit trails and explainability",
                "short": "Audit trails",
                "framework": "SR 11-7 · CFPB Adverse Action · DORA ICT Incident Reporting",
                "questions": [
                    "Does your organization maintain input and output logs for AI systems used in regulated decisions?",
                    "Can your organization produce a compliant adverse action notice for any AI-assisted credit or lending decision?",
                    "Is there version tracking for AI models so specific outputs can be traced to a specific model version?"
                ]
            },
            {
                "id": 4,
                "name": "Operational resilience for AI",
                "short": "Resilience",
                "framework": "DORA Article 6 · NIST AI RMF Map 5.1 · SR 11-7",
                "questions": [
                    "Are AI systems included in your digital operational resilience testing program under DORA or equivalent frameworks?",
                    "Does your organization have an AI-specific incident response plan separate from your cybersecurity IR plan?",
                    "Has your team conducted a tabletop exercise for an AI failure scenario affecting regulated financial operations?"
                ]
            }
        ]
    },
    "energy": {
        "label": "Energy & Manufacturing",
        "icon": "⚡",
        "color": "#EF9F27",
        "tagline": "IEC 62443 · NERC CIP · NIST CSF 2.0 · ISO/IEC 42001",
        "consultant_context": "energy and manufacturing operational technology environments",
        "domains": [
            {
                "id": 0,
                "name": "OT/IT convergence readiness",
                "short": "OT/IT",
                "framework": "IEC 62443-3-3 · NIST CSF 2.0 PR.AC",
                "questions": [
                    "Has your organization conducted a formal risk assessment for AI systems operating in or adjacent to OT environments?",
                    "Do you have documented network segmentation policies that account for AI data flows between IT and OT layers?",
                    "Is there a defined approval process before an AI tool can connect to operational technology systems?"
                ]
            },
            {
                "id": 1,
                "name": "AI vendor risk",
                "short": "Vendor risk",
                "framework": "IEC 62443-2-1 · OWASP LLM05 Supply Chain Risk",
                "questions": [
                    "Do your AI vendor contracts include model update notification requirements?",
                    "Has your organization reviewed AI vendor SOC 2 reports or equivalent security attestations in the last 12 months?",
                    "Do you maintain an inventory of all third-party AI tools with access to operational data?"
                ]
            },
            {
                "id": 2,
                "name": "Regulatory alignment",
                "short": "Regulatory",
                "framework": "IEC 62443 · NERC CIP · ISO/IEC 42001",
                "questions": [
                    "Has your organization mapped its AI deployments to IEC 62443 security levels?",
                    "Do you have documented controls addressing NERC CIP requirements for AI systems in grid-adjacent environments?",
                    "Is there a designated owner responsible for AI regulatory compliance in your organization?"
                ]
            },
            {
                "id": 3,
                "name": "AI incident response",
                "short": "IR readiness",
                "framework": "NIST AI RMF Map 5.1 · IEC 62443-2-1",
                "questions": [
                    "Does your organization have an AI-specific incident response plan separate from your cybersecurity IR plan?",
                    "Has your team conducted a tabletop exercise for an AI failure scenario in an operational environment?",
                    "Is there a defined rollback procedure for AI models deployed in production or operational systems?"
                ]
            },
            {
                "id": 4,
                "name": "Data governance for operational AI",
                "short": "Data governance",
                "framework": "NIST AI RMF Govern 1.4 · ISO/IEC 42001 A.8",
                "questions": [
                    "Is operational data classified before being used to train or inform AI models?",
                    "Do you have documented data retention and deletion policies for AI training data derived from operational systems?",
                    "Is there an audit trail for AI-generated decisions that affect operational processes or outputs?"
                ]
            }
        ]
    }
}

ANS_OPTIONS = ["Yes", "Partial", "No"]
ANS_POINTS = {"Yes": 2, "Partial": 1, "No": 0}

TIER_INFO = {
    1: {"label": "Foundational", "emoji": "🔴",
        "desc": "Significant gaps across critical domains. Immediate action required before expanding AI deployments."},
    2: {"label": "Developing", "emoji": "🟡",
        "desc": "Key controls in place but major gaps remain. Prioritize regulatory alignment and vendor risk management."},
    3: {"label": "Managed", "emoji": "🔵",
        "desc": "Solid governance foundation with targeted improvements needed. Focus on incident response maturity."},
    4: {"label": "Optimized", "emoji": "🟢",
        "desc": "Strong AI governance posture. Focus on continuous improvement as AI evolves in your environment."}
}

def init_state():
    defaults = {
        "phase": "select",
        "industry": None,
        "current_domain": 0,
        "answers": {},
        "report": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_answer(domain_id, q_idx):
    return st.session_state.answers.get(f"{domain_id}_{q_idx}", None)

def set_answer(domain_id, q_idx, value):
    st.session_state.answers[f"{domain_id}_{q_idx}"] = value

def domain_answered_count(domain_id):
    return sum(1 for i in range(3) if get_answer(domain_id, i) is not None)

def domain_score(domain_id):
    return sum(ANS_POINTS.get(get_answer(domain_id, i) or "", 0) for i in range(3))

def total_answered():
    return sum(domain_answered_count(d["id"]) for d in get_domains())

def all_answered():
    return total_answered() == 15

def get_domains():
    ind = st.session_state.industry
    if ind and ind in INDUSTRIES:
        return INDUSTRIES[ind]["domains"]
    return []

def get_tier(score):
    if score <= 6: return 1
    if score <= 10: return 2
    if score <= 14: return 3
    return 4

def generate_report(total_score, domain_scores):
    ind = INDUSTRIES[st.session_state.industry]
    domains = get_domains()
    tier = get_tier(total_score)
    tier_label = TIER_INFO[tier]["label"]
    domain_summary = "; ".join([
        f"{domains[i]['name']}: {domain_scores[i]}/6 ({'critical gap' if domain_scores[i]<=2 else 'partial coverage' if domain_scores[i]<=4 else 'strong'})"
        for i in range(5)
    ])
    weakest = sorted(range(5), key=lambda i: domain_scores[i])[:2]
    weakest_names = " and ".join([domains[i]["name"] for i in weakest])

    prompt = f"""You are an AI governance consultant specializing in {ind['consultant_context']}. A client just completed an AI Governance Readiness Assessment.

Results:
- Industry: {ind['label']}
- Overall score: {total_score}/30 — Tier {tier}: {tier_label}
- Domain scores: {domain_summary}
- Weakest domains: {weakest_names}
- Frameworks assessed: {ind['tagline']}

Write a 3-paragraph gap analysis:
Paragraph 1: What their score means for their AI risk posture in {ind['consultant_context']} (2-3 sentences, specific to their tier and industry).
Paragraph 2: Their two most critical gaps and the specific risk they create in {ind['label']} contexts (3-4 sentences).
Paragraph 3: Three prioritized next steps, numbered, each one sentence. Reference specific frameworks by name.

Be direct and specific. No filler. No generic advice. Write as a senior consultant, not a chatbot."""

    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    with st.spinner("Generating your personalized gap analysis..."):
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
    return message.content[0].text

def main():
    init_state()

    if st.session_state.phase == "select":
        show_industry_select()
    elif st.session_state.phase == "questions":
        show_questions()
    elif st.session_state.phase == "results":
        show_results()

def show_industry_select():
    st.markdown("# 🏛 AI Governance Readiness Assessment")
    st.markdown("15 questions. 5 domains. One score. Claude delivers a personalized gap analysis based on your industry's regulatory frameworks.")
    st.divider()
    st.markdown("### Select your industry to begin")
    st.markdown("")

    for key, ind in INDUSTRIES.items():
        col1, col2 = st.columns([1, 8])
        with col1:
            st.markdown(f"### {ind['icon']}")
        with col2:
            if st.button(f"**{ind['label']}** — {ind['tagline']}", key=f"ind_{key}", use_container_width=True):
                st.session_state.industry = key
                st.session_state.phase = "questions"
                st.session_state.answers = {}
                st.session_state.current_domain = 0
                st.session_state.report = None
                st.rerun()

    st.markdown('<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com<br>Healthcare · Education · Energy · Financial Services</div>', unsafe_allow_html=True)

def show_questions():
    ind = INDUSTRIES[st.session_state.industry]
    domains = get_domains()

    st.markdown(f"# {ind['icon']} AI Governance Readiness Assessment")
    st.markdown(f"**{ind['label']}** — {ind['tagline']}")

    if st.button("← Change industry", key="change_industry"):
        st.session_state.phase = "select"
        st.rerun()

    st.divider()

    answered = total_answered()
    st.progress(answered / 15, text=f"{answered} of 15 questions answered")

    cols = st.columns(5)
    for i, d in enumerate(domains):
        cnt = domain_answered_count(d["id"])
        with cols[i]:
            if cnt == 3:
                st.markdown(f"✅ **{d['short']}**")
            elif i == st.session_state.current_domain:
                st.markdown(f"▶️ **{d['short']}**")
            else:
                st.markdown(f"⬜ {d['short']}")

    st.divider()

    d = domains[st.session_state.current_domain]
    st.markdown(f"### Domain {d['id']+1} of 5 — {d['name']}")
    st.caption(f"Framework: {d['framework']}")
    st.markdown("")

    for i, q in enumerate(d["questions"]):
        st.markdown(f"**{i+1}. {q}**")
        current_ans = get_answer(d["id"], i)
        col_yes, col_partial, col_no, col_spacer = st.columns([1, 1, 1, 3])
        with col_yes:
            if st.button("Yes", key=f"yes_{d['id']}_{i}",
                        type="primary" if current_ans == "Yes" else "secondary",
                        use_container_width=True):
                set_answer(d["id"], i, "Yes")
                st.rerun()
        with col_partial:
            if st.button("Partial", key=f"partial_{d['id']}_{i}",
                        type="primary" if current_ans == "Partial" else "secondary",
                        use_container_width=True):
                set_answer(d["id"], i, "Partial")
                st.rerun()
        with col_no:
            if st.button("No", key=f"no_{d['id']}_{i}",
                        type="primary" if current_ans == "No" else "secondary",
                        use_container_width=True):
                set_answer(d["id"], i, "No")
                st.rerun()
        if current_ans:
            st.caption(f"Answered: {current_ans}")
        st.markdown("")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.session_state.current_domain > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.current_domain -= 1
                st.rerun()
    with col2:
        if st.session_state.current_domain < 4:
            if st.button("Next →", use_container_width=True):
                st.session_state.current_domain += 1
                st.rerun()
    with col3:
        if all_answered():
            if st.button("See my results →", type="primary", use_container_width=True):
                domains_list = get_domains()
                d_scores = [domain_score(d["id"]) for d in domains_list]
                total = sum(d_scores)
                st.session_state.report = generate_report(total, d_scores)
                st.session_state.phase = "results"
                st.rerun()

    st.markdown('<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com</div>', unsafe_allow_html=True)

def show_results():
    ind = INDUSTRIES[st.session_state.industry]
    domains = get_domains()
    domain_scores = [domain_score(d["id"]) for d in domains]
    total = sum(domain_scores)
    tier_num = get_tier(total)
    tier = TIER_INFO[tier_num]

    st.markdown(f"## {ind['icon']} {tier['emoji']} Your results — {ind['label']}")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall score", f"{total} / 30")
        st.markdown(f"**Tier {tier_num} — {tier['label']}**")
    with col2:
        st.markdown(tier["desc"])
        st.markdown("")
        for i, d in enumerate(domains):
            s = domain_scores[i]
            bar = "🟢" if s >= 5 else "🟡" if s >= 3 else "🔴"
            st.markdown(f"{bar} **{d['short']}** — {s}/6")

    st.divider()

    if st.session_state.report:
        st.markdown("### Personalized gap analysis")
        for para in st.session_state.report.split("\n\n"):
            if para.strip():
                st.markdown(para)
                st.markdown("")

    st.divider()
    st.caption(f"This assessment is based on {ind['tagline']}. It provides a directional snapshot — not a formal audit or compliance certification.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.button("Book a consultation →", type="primary", use_container_width=True):
            st.markdown("Visit [jdmcservices.com](https://jdmcservices.com) to book a consultation.")

    st.markdown(f'<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com<br>{ind["tagline"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
