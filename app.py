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

ANS_OPTIONS = ["Yes", "Partial", "No"]
ANS_POINTS = {"Yes": 2, "Partial": 1, "No": 0}

TIER_INFO = {
    1: {"label": "Foundational", "emoji": "🔴",
        "desc": "Significant gaps across critical domains. Immediate action required before expanding AI in operational environments."},
    2: {"label": "Developing", "emoji": "🟡",
        "desc": "Key controls in place but major gaps remain. Prioritize regulatory alignment and vendor risk management."},
    3: {"label": "Managed", "emoji": "🔵",
        "desc": "Solid governance foundation with targeted improvements needed. Focus on incident response maturity."},
    4: {"label": "Optimized", "emoji": "🟢",
        "desc": "Strong AI governance posture. Focus on continuous improvement and framework updates as AI evolves."}
}

def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "questions"
    if "current_domain" not in st.session_state:
        st.session_state.current_domain = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "report" not in st.session_state:
        st.session_state.report = None

def get_answer(domain_id, q_idx):
    return st.session_state.answers.get(f"{domain_id}_{q_idx}", None)

def set_answer(domain_id, q_idx, value):
    st.session_state.answers[f"{domain_id}_{q_idx}"] = value

def domain_answered_count(domain_id):
    return sum(1 for i in range(3) if get_answer(domain_id, i) is not None)

def domain_score(domain_id):
    total = 0
    for i in range(3):
        ans = get_answer(domain_id, i)
        if ans:
            total += ANS_POINTS[ans]
    return total

def total_answered():
    return sum(domain_answered_count(d["id"]) for d in DOMAINS)

def all_answered():
    return total_answered() == 15

def get_tier(score):
    if score <= 6: return 1
    if score <= 10: return 2
    if score <= 14: return 3
    return 4

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

def main():
    init_state()

    st.markdown("# ⚡ AI Governance Readiness Assessment")
    st.markdown("**Energy & Manufacturing** — 15 questions across 5 domains. Scored against IEC 62443, NERC CIP, NIST CSF 2.0, and ISO/IEC 42001.")
    st.divider()

    if st.session_state.phase == "results":
        show_results()
        return

    # Progress
    answered = total_answered()
    st.progress(answered / 15, text=f"{answered} of 15 questions answered")

    # Domain status indicators
    cols = st.columns(5)
    for i, d in enumerate(DOMAINS):
        cnt = domain_answered_count(d["id"])
        with cols[i]:
            if cnt == 3:
                st.markdown(f"✅ **{d['short']}**")
            elif i == st.session_state.current_domain:
                st.markdown(f"▶️ **{d['short']}**")
            else:
                st.markdown(f"⬜ {d['short']}")

    st.divider()

    d = DOMAINS[st.session_state.current_domain]
    st.markdown(f"### Domain {d['id']+1} of 5 — {d['name']}")
    st.caption(f"Framework: {d['framework']}")
    st.markdown("")

    # Render each question with explicit answer storage
    for i, q in enumerate(d["questions"]):
        st.markdown(f"**{i+1}. {q}**")
        current_ans = get_answer(d["id"], i)
        current_idx = ANS_OPTIONS.index(current_ans) if current_ans else None

        col_yes, col_partial, col_no, col_spacer = st.columns([1, 1, 1, 3])

        with col_yes:
            yes_style = "primary" if current_ans == "Yes" else "secondary"
            if st.button("Yes", key=f"yes_{d['id']}_{i}", type=yes_style, use_container_width=True):
                set_answer(d["id"], i, "Yes")
                st.rerun()

        with col_partial:
            partial_style = "primary" if current_ans == "Partial" else "secondary"
            if st.button("Partial", key=f"partial_{d['id']}_{i}", type=partial_style, use_container_width=True):
                set_answer(d["id"], i, "Partial")
                st.rerun()

        with col_no:
            no_style = "primary" if current_ans == "No" else "secondary"
            if st.button("No", key=f"no_{d['id']}_{i}", type=no_style, use_container_width=True):
                set_answer(d["id"], i, "No")
                st.rerun()

        if current_ans:
            st.caption(f"✓ Answered: {current_ans}")
        st.markdown("")

    # Navigation
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
                d_scores = [domain_score(d["id"]) for d in DOMAINS]
                total = sum(d_scores)
                st.session_state.report = generate_report(total, d_scores)
                st.session_state.phase = "results"
                st.rerun()

    st.markdown('<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com</div>', unsafe_allow_html=True)


def show_results():
    domain_scores = [domain_score(d["id"]) for d in DOMAINS]
    total = sum(domain_scores)
    tier_num = get_tier(total)
    tier = TIER_INFO[tier_num]

    st.markdown(f"## {tier['emoji']} Your results")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall score", f"{total} / 30")
        st.markdown(f"**Tier {tier_num} — {tier['label']}**")

    with col2:
        st.markdown(tier["desc"])
        st.markdown("")
        for i, d in enumerate(DOMAINS):
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

    st.caption("This assessment is based on IEC 62443, NERC CIP, NIST CSF 2.0, ISO/IEC 42001, and NIST AI RMF. It provides a directional snapshot — not a formal audit or compliance certification.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.button("Book a consultation →", use_container_width=True):
            st.markdown("Visit [jdmcservices.com](https://jdmcservices.com)")

    st.markdown('<div class="brand-footer">JDMC Services · AI Governance for Regulated Industries · jdmcservices.com<br>IEC 62443 · NERC CIP · NIST CSF 2.0 · ISO/IEC 42001 · NIST AI RMF</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
