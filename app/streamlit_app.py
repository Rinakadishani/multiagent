import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'agents'))

from graph import HealthcareMultiAgentSystem

st.set_page_config(
    page_title="Healthcare Multi-Agent Copilot",
    page_icon="",
    layout="wide"
)

@st.cache_resource
def get_system():
    return HealthcareMultiAgentSystem()

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Healthcare Multi-Agent Copilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by LangGraph | Genpact Giga Academy Project #6</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuration")
    
    output_mode = st.selectbox(
        "Output Mode",
        options=["executive", "analyst"],
        help="Executive: Strategic insights for C-suite | Analyst: Detailed technical analysis"
    )
    
    st.markdown("---")
    st.markdown("### System Info")
    st.info("Agents: Planner → Research → Writer → Verifier\n\nFeatures:\n- Multi-agent orchestration\n- Evidence-based retrieval\n- Citation verification\n- Hallucination detection\n- Multi-output mode")
    
    st.markdown("---")
    st.markdown("### Sample Queries")
    st.caption("- What are best practices for hand hygiene in healthcare?\n- How can hospitals prevent C. difficile infections?\n- What infection control measures are needed for NICUs?")

st.header("Submit Your Request")

user_query = st.text_area(
    "Healthcare Analytics Question",
    placeholder="Example: What are the best practices for preventing healthcare-associated infections?",
    height=100,
    help="Ask any question about healthcare operations, patient safety, or clinical protocols"
)

col1, col2 = st.columns([1, 5])
with col1:
    submit_btn = st.button("Execute", type="primary", use_container_width=True)
with col2:
    if st.button("Clear Results", use_container_width=True):
        if 'last_result' in st.session_state:
            del st.session_state['last_result']
        st.rerun()

if submit_btn and user_query:
    with st.spinner("Multi-agent system working..."):
        try:
            system = get_system()
            result = system.run(user_query, output_mode)
            st.session_state['last_result'] = result
            st.success("Analysis Complete!")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if 'last_result' in st.session_state:
    result = st.session_state['last_result']
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Deliverables",
        "Sources & Citations",
        "Verification",
        "Observability",
        "Agent Trace"
    ])
    
    with tab1:
        st.subheader("Executive Summary")
        st.info(result['executive_summary'])
        
        st.subheader("Client-Ready Email")
        st.text_area(
            "Email Draft",
            result['email_draft'],
            height=300,
            help="Copy this email to send to stakeholders"
        )
        
        st.subheader("Action Items")
        if result['action_items']:
            df_actions = pd.DataFrame(result['action_items'])
            st.dataframe(
                df_actions,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No action items generated")
    
    with tab2:
        st.subheader("Source Documents")
        
        if result['sources']:
            for i, source in enumerate(result['sources'], 1):
                with st.expander(f"{i}. {source['document']}", expanded=(i==1)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Pages Referenced", len(source['pages']))
                        st.caption(f"Pages: {', '.join(map(str, source['pages']))}")
                    with col2:
                        st.metric("Chunks Used", source['chunk_count'])
        else:
            st.warning("No sources found")
    
    with tab3:
        st.subheader("Verification Report")
        
        
        if result['verification_status'] == 'PASSED':
            st.markdown('<div class="success-box">Verification PASSED - All claims supported by sources</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">Issues Found - Review flagged items below</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Verification Status", result['verification_status'])
        
        with col2:
            total_issues = len(result['hallucinations']) + len(result['missing_evidence'])
            st.metric("Total Issues", total_issues)
        
        if result['hallucinations']:
            st.markdown("#### Potential Hallucinations")
            for h in result['hallucinations']:
                st.error(h)
        
        if result['missing_evidence']:
            st.markdown("#### Missing Evidence")
            for m in result['missing_evidence']:
                st.warning(m)
        
        if not result['hallucinations'] and not result['missing_evidence']:
            st.success("All claims verified against sources")
    
    with tab4:
        st.subheader("Observability Dashboard")
        
        obs = result['observability']
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Latency", f"{obs['total_latency_seconds']}s")
        col2.metric("Total Tokens", f"{obs['total_tokens_used']:,}")
        col3.metric("Agents Executed", obs['total_agents_executed'])
        col4.metric("Errors", obs['error_count'])
        
        st.subheader("Agent Performance Breakdown")
        
        trace_data = []
        for trace in obs['detailed_trace']:
            if 'latency_seconds' in trace:
                trace_data.append({
                    "Agent": trace['agent'],
                    "Status": trace['status'],
                    "Latency (s)": trace.get('latency_seconds', 0),
                    "Tokens": trace.get('tokens_used', 0),
                    "Timestamp": trace['timestamp']
                })
        
        if trace_data:
            df_trace = pd.DataFrame(trace_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Latency by Agent**")
                latency_chart = df_trace.groupby('Agent')['Latency (s)'].sum().reset_index()
                st.bar_chart(latency_chart.set_index('Agent'))
            
            with col2:
                st.markdown("**Token Usage by Agent**")
                token_chart = df_trace.groupby('Agent')['Tokens'].sum().reset_index()
                st.bar_chart(token_chart.set_index('Agent'))
            
            st.markdown("**Detailed Execution Log**")
            st.dataframe(df_trace, use_container_width=True, hide_index=True)
            
            total_time = obs['total_latency_seconds']
            if total_time > 0:
                st.markdown("**Performance Insights**")

                slowest = df_trace.loc[df_trace['Latency (s)'].idxmax()]
                st.info(f"Slowest Agent: {slowest['Agent']} ({slowest['Latency (s)']}s)")
                
                if obs['total_tokens_used'] > 0:
                    tokens_per_sec = obs['total_tokens_used'] / total_time
                    cost = obs['total_tokens_used'] * 0.000003
                    st.info(f"Token Processing Rate: {tokens_per_sec:.1f} tokens/second")
                    st.info(f"Estimated Cost: ${cost:.4f}")
    
    with tab5:
        st.subheader("Detailed Agent Trace Log")
        st.json(obs['detailed_trace'], expanded=False)
    
    st.markdown("---")
    st.subheader("Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "Download Full Report (JSON)",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        summary_lines = [
            "HEALTHCARE ANALYSIS REPORT",
            "=" * 80,
            "",
            f"QUERY: {result['user_query']}",
            f"MODE: {result['output_mode']}",
            f"TIMESTAMP: {result['timestamp']}",
            "",
            "=" * 80,
            "EXECUTIVE SUMMARY",
            "=" * 80,
            result['executive_summary'],
            "",
            "=" * 80,
            "EMAIL DRAFT",
            "=" * 80,
            result['email_draft'],
            "",
            "=" * 80,
            "ACTION ITEMS",
            "=" * 80
        ]
        
        for i, action in enumerate(result['action_items'], 1):
            summary_lines.append(f"{i}. {action['task']}")
            summary_lines.append(f"   Owner: {action['owner']} | Due: {action['due_date']} | Confidence: {action['confidence']}")
        
        summary_lines.extend([
            "",
            "=" * 80,
            "SOURCES",
            "=" * 80
        ])
        
        for source in result['sources']:
            summary_lines.append(f"- {source['document']}")
            summary_lines.append(f"  Pages: {source['pages']}")
        
        summary_lines.extend([
            "",
            "=" * 80,
            f"VERIFICATION: {result['verification_status']}",
            "=" * 80
        ])
        
        summary_text = "\n".join(summary_lines)
        
        st.download_button(
            "Download Summary (TXT)",
            data=summary_text,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        if result['action_items']:
            csv = pd.DataFrame(result['action_items']).to_csv(index=False)
            st.download_button(
                "Download Actions (CSV)",
                data=csv,
                file_name=f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

st.markdown("---")
st.caption("Built with LangGraph | Genpact Giga Academy Cohort IV | February 2025")