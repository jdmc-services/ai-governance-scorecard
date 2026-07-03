import streamlit as st
import anthropic

st.set_page_config(
    page_title="AI Governance Readiness Assessment — Energy & Manufacturing",
    page_icon="⚡",
    layout="centered"
)

st.markdown("""
<style>
.main { max-width: 760px; margin: 0 auto; }
.domain-header {
    background: #1a1400;
    border: 1px solid #854f0b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}
.domain-title { color: #fde68a; font-size: 15px; font-weight: 600; margin-bottom: 2px; }
.domain-framework { color: #a16207; font-size: 11px; }
.q-label { font-size: 14px; color: #e5e7eb; line-height: 1.6; margin-bottom: 6px; }
.score-card {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    text-align: center;
}
.score-big { font-size: 52px; font-weight: 700; margin-bottom: 4px; }
.tier-1 { color: #f87171; }
.tier-2 { color: #fbbf24; }
.tier-3 { color: #60a5fa; }
.tier-4 { color: #34d399; }
.domain-score-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #1e293b;
    font-size: 13px;
}
.ai-report {
    background: #0a1628;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 1rem;
    font-size: 14px;
    line-height: 1.8;
    color: #cbd5e1;
}
.framework-footer {
    text-align: center;
    font-size: 11px;
    color: #4b5563;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #1e293b;
}
.brand-footer {
    text-align: center;
    font-size: 12px;
    color: #4b5563;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

DOMAINS = [
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

ANS_OPTIONS = {"Yes": 2, "Partial": 1, "No": 0}

TIER_INFO = {
    1: {"label": "Foundational", "color": "tier-1", "emoji": "🔴",
        "desc": "Significant gaps across critical domains. Immediate action required before expanding AI in operational environments."},
    2: {"label": "Developing", "color": "tier-2", "emoji": "🟡",
        "desc": "Key controls in place but major gaps remain. Prioritize regulatory alignment and vendor risk management."},
    3: {"label": "Managed", "color": "tier-3", "emoji": "🔵",
        "desc": "Solid governance foundation with targeted improvements needed. Focus on incident response maturity."},
    4: {"label": "Optimized", "color": "tier-4", "emoji": "🟢",
        "desc": "Strong AI governance posture. Focus on continuous improvement and framework updates as AI evolves."}
}

def get_tier(score):
    if score <= 6: return 1
    if score <= 10: return 2
    if score <= 14: return 3
    return 4

def get_domain_score(domain_id):
    total = 0
    for i in range(3):
        key = f"d{domain_id}_q{i}"
        ans = st.session_state.get(key, None)
        if ans:
            total += ANS_OPTIONS[ans]
    return total

def all_answered():
    for d in DOMAINS:
        for i in range(3):
            if not st.session_state.get(f"d{d['id']}_q{i}"):
                return False
    return True

def generate_report(total_score, domain_scores):
    tier = get_tier(total_score)
    tier_label = TIER_INFO[tier]["label"]

    domain_summary = "; ".join([
        f"{DOMAINS[i]['name']}: {domain_scores[i]}/6 ({'critical gap' if domain_scores[i]<=2 else 'partial coverage' if domain_scores[i]<=4 else 'strong'})"
        for i in range(5)
    ])

    weakest = sorted(range(5), key=lambda i: domain_scores[i])[:2]
    weakest_names = " and ".join([DOMAINS[i]["name"] for i in weakest])

    prompt = f"""You are an AI governance consultant specializing in energy and manufacturing environments. A client just completed an AI Governance Readiness Assessment.

Results:
- Overall score: {total_score}/30 — Tier {tier}: {tier_label}
- Domain scores: {domain_summary}
- Weakest domains: {weakest_names}
- Frameworks assessed: IEC 62443, NERC CIP, NIST CSF 2.0, ISO/IEC 42001, NIST AI RMF

Write a 3-paragraph gap analysis:
Paragraph 1: What their score means for their AI risk posture in operational environments (2-3 sentences, specific to their tier).
Paragraph 2: Their two most critical gaps and the specific risk they create in energy/manufacturing contexts (3-4 sentences).
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

def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "questions"
    if "report" not in st.session_state:
        st.session_state.report = None
    if "current_domain" not in st.session_state:
        st.session_state.current_domain = 0

def main():
    init_state()

    st.markdown("# ⚡ AI Governance Readiness Assessment")
    st.markdown("**Energy & Manufacturing** — 15 questions across 5 domains. Scored against IEC 62443, NERC CIP, NIST CSF 2.0, and ISO/IEC 42001.")
    st.divider()

    if st.session_state.phase == "results":
        show_results()
        return

    answered_count = sum(1 for d in DOMAINS for i in range(3) if st.session_state.get(f"d{d['id']}_q{i}"))
    st.progress(answered_count / 15, text=f"{answered_count} of 15 questions answered")

    domain_cols = st.columns(5)
    for i, d in enumerate(DOMAINS):
        domain_score = get_domain_score(d["id"])
        answered_in_domain = sum(1 for j in range(3) if st.session_state.get(f"d{d['id']}_q{j}"))
        with domain_cols[i]:
            if answered_in_domain == 3:
                st.markdown(f"✅ **{d['short']}**")
            elif i == st.session_state.current_domain:
                st.markdown(f"▶️ **{d['short']}**")
            else:
                st.markdown(f"⬜ {d['short']}")

    st.divider()

    d = DOMAINS[st.session_state.current_domain]

    st.markdown(f"### Domain {d['id']+1} of 5 — {d['name']}")
    st.caption(f"Framework: {d['framework']}")

    for i, q in enumerate(d["questions"]):
        key = f"d{d['id']}_q{i}"
        st.markdown(f"**{i+1}. {q}**")
        st.radio(
            f"q_{d['id']}_{i}",
            options=["Yes", "Partial", "No"],
            key=key,
            horizontal=True,
            index=None,
            label_visibility="collapsed"
        )
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
                domain_scores = [get_domain_score(d["id"]) for d in DOMAINS]
                total = sum(domain_scores)
                st.session_state.report = generate_report(total, domain_scores)
                st.session_state.phase = "results"
                st.rerun()
        elif answered_count == 15:
            if st.button("See my results →", type="primary", use_container_width=True):
                st.session_state.phase = "results"
                st.rerun()

    st.markdown('<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com</div>', unsafe_allow_html=True)


def show_results():
    domain_scores = [get_domain_score(d["id"]) for d in DOMAINS]
    total = sum(domain_scores)
    tier_num = get_tier(total)
    tier = TIER_INFO[tier_num]

    st.markdown(f"## {tier['emoji']} Your results")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"""
<div class="score-card">
  <div class="score-big {tier['color']}">{total}</div>
  <div style="font-size:14px;color:#94a3b8">out of 30</div>
  <div style="font-size:13px;font-weight:600;color:#e5e7eb;margin-top:8px">Tier {tier_num} — {tier['label']}</div>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"**{tier['label']}** — {tier['desc']}")
        st.markdown("")
        for i, d in enumerate(DOMAINS):
            s = domain_scores[i]
            bar = "🟢" if s >= 5 else "🟡" if s >= 3 else "🔴"
            st.markdown(f"{bar} **{d['short']}** — {s}/6")

    st.divider()

    if st.session_state.report:
        st.markdown("### Personalized gap analysis")
        st.markdown('<div class="ai-report">', unsafe_allow_html=True)
        for para in st.session_state.report.split("\n\n"):
            if para.strip():
                st.markdown(para)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("""
This assessment is based on publicly available frameworks including IEC 62443, NERC CIP, NIST CSF 2.0, ISO/IEC 42001, and NIST AI RMF.
It provides a directional snapshot of your AI governance posture — not a formal audit or compliance certification.
""")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.button("Book a consultation →", use_container_width=True):
            st.markdown("[jdmcservices.com](https://jdmcservices.com)")

    st.markdown('<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com<br>IEC 62443 · NERC CIP · NIST CSF 2.0 · ISO/IEC 42001 · NIST AI RMF</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()