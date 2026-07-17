import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="ICML Campaign Meta-Dashboard", layout="wide", page_icon="📊")

def load_data(file_path="metrics_manifest.json"):
    if not os.path.exists(file_path):
        st.error(f"Manifest file '{file_path}' not found. Please run monitor.py first.")
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def main():
    st.title("📊 ICML 2026 Campaign Meta-Dashboard")
    st.markdown("Centralized tracking for multi-agent paper reproduction spaces and budget usage.")
    
    data = load_data()
    if not data:
        return
        
    st.caption(f"Last updated: {data.get('timestamp', 'Unknown')}")
    
    # --- CALCULATE KPIs ---
    spaces = data.get("spaces", [])
    modal = data.get("modal", {})
    opencode = data.get("opencode", {})
    
    total_claims = sum(s.get("total_claims", 0) for s in spaces)
    verified_claims = sum(s.get("verified_claims", 0) for s in spaces)
    total_credits_left = modal.get("credit_remaining_usd", 0.0)
    current_spend = modal.get("current_billing_usage_usd", 0.0)
    
    efficiency_ratio = current_spend / verified_claims if verified_claims > 0 else 0.0
    
    # --- TOP KPI STRIP ---
    st.header("Financial & Claim Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Credits Left", f"${total_credits_left:.2f}")
    with col2:
        st.metric("Current Modal Spend", f"${current_spend:.2f}")
    with col3:
        st.metric("Total Claims Verified", f"{verified_claims} / {total_claims}")
    with col4:
        st.metric("Efficiency Ratio", f"${efficiency_ratio:.2f} / Claim")
        
    st.divider()
    
    # --- AGENT TRACKING TABLE ---
    st.header("Target Tracker")
    if spaces:
        df = pd.DataFrame(spaces)
        
        # Add a progress column for visual display
        df['progress'] = df.apply(lambda row: row['verified_claims'] / row['total_claims'] if row['total_claims'] > 0 else 0, axis=1)
        
        # Formatting the DataFrame for Streamlit display
        display_df = df[['paper_id', 'status', 'verified_claims', 'total_claims', 'url']].copy()
        display_df['Agent Used'] = "OpenCode (Nemotron/Deepseek)"  # Simulated column based on requirements
        
        st.data_editor(
            display_df,
            column_config={
                "url": st.column_config.LinkColumn("Logbook URL", display_text="Open Space"),
                "paper_id": "Paper ID",
                "status": "Current Status",
                "verified_claims": "Verified",
                "total_claims": "Total Claims",
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No tracking data available for spaces.")
        
    st.divider()
        
    # --- RESOURCE CHARTS ---
    st.header("Resource Cost Profiles")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Modal GPU Budget")
        modal_budget_fig = go.Figure(data=[go.Pie(
            labels=['Spent ($)', 'Remaining ($)'],
            values=[current_spend, total_credits_left],
            hole=.4,
            marker_colors=['#EF553B', '#00CC96']
        )])
        modal_budget_fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(modal_budget_fig, use_container_width=True)
        
    with col_chart2:
        st.subheader("OpenCode Token Usage")
        opencode_limit = opencode.get("session_limit", 1)
        opencode_used = opencode.get("session_used_tokens", 0)
        opencode_remaining = opencode.get("session_remaining", 0)
        
        oc_fig = go.Figure(data=[go.Bar(
            name='Used Tokens',
            x=['Session'],
            y=[opencode_used],
            marker_color='#EF553B'
        ), go.Bar(
            name='Remaining Tokens',
            x=['Session'],
            y=[opencode_remaining],
            marker_color='#00CC96'
        )])
        
        oc_fig.update_layout(barmode='stack', margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(oc_fig, use_container_width=True)

if __name__ == "__main__":
    main()
