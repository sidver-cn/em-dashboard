import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Shredder Fleet Command",
    layout="wide",
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it look like a Professional SCADA System
st.markdown("""
<style>
    /* Light Industrial Background */
    .stApp { background-color: #F5F5F5; }
    
    /* Machine Card Styling - force white background in all themes */
    .machine-card-container {
        background-color: #FFFFFF !important;
        border: 1px solid #DDDDDD !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Remove default streamlit styling that might interfere */
    .stButton > button {
        width: 100%;
        background-color: #FFFFFF !important;
        color: #1a1a1a !important;
        border: 1px solid #DDDDDD !important;
        border-radius: 4px;
        padding: 8px;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #F5F5F5 !important;
        border-color: #00E396 !important;
    }
    
    /* Ensure page titles and headers are visible in dark mode */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }
    
    /* Alerts */
    .alert-box {
        background-color: #FFEBEE !important;
        border-left: 5px solid #FF4560;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    
    .alert-box p, .alert-box h3 {
        color: #1a1a1a !important;
    }




</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MOCK DATA ENGINE (Simulating your PLC/Sensor Data)
# -----------------------------------------------------------------------------
def get_machine_status(machine_name):
    """
    Returns simulated live data.
    NOTE: I have hardcoded 'Mill 2' to be in a CRITICAL state for demo purposes.
    """
    # Default Healthy State
    data = {
        "status": "RUNNING",
        "amps": np.random.randint(380, 420),
        "vib": np.random.uniform(2.1, 3.5),
        "temp": np.random.randint(60, 75),
        "jams": 0,
        "oee": 88
    }
    
    # Specific logic for Mill 2 (The Problem Child)
    if machine_name == "Mill 2":
        data["status"] = "CRITICAL"
        data["vib"] = 12.5  # Very High Vibration
        data["temp"] = 88   # High Temp
        data["amps"] = 450
    
    # Specific logic for Shredder 2 (The Jammed Machine)
    if machine_name == "Shredder 2":
        data["status"] = "JAMMED"
        data["amps"] = 0
        data["jams"] = 4
        data["vib"] = 2.9
        
    return data

# Inventory & Maintenance Database
maintenance_db = {
    "Shredder 1": {"Next": "Blade Rotation", "Due": "140 hrs", "Spare_Status": "OK"},
    "Shredder 2": {"Next": "Hardfacing", "Due": "12 hrs", "Spare_Status": "OK"},
    "Mill 1": {"Next": "Greasing", "Due": "4 hrs", "Spare_Status": "OK"},
    "Mill 2": {"Next": "Bearing Replacement", "Due": "OVERDUE", "Spare_Status": "MISSING"}, # <--- The Trap
    "Mill 3": {"Next": "Filter Change", "Due": "200 hrs", "Spare_Status": "OK"},
    "Unit 2 Shredder": {"Next": "Gear Oil", "Due": "48 hrs", "Spare_Status": "LOW"},
    "Unit 2 Crusher": {"Next": "Liner Check", "Due": "72 hrs", "Spare_Status": "OK"},
}

# -----------------------------------------------------------------------------
# 3. NAVIGATION & STATE
# -----------------------------------------------------------------------------
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Unit 1"
if 'selected_machine' not in st.session_state:
    st.session_state.selected_machine = None

def set_view(view):
    st.session_state.current_view = view
    st.session_state.selected_machine = None # Reset machine selection when changing units

def select_machine(name):
    st.session_state.current_view = "Detail"
    st.session_state.selected_machine = name

# -----------------------------------------------------------------------------
# 4. UI COMPONENTS
# -----------------------------------------------------------------------------

def render_machine_card(name):
    """Draws a clickable card for a machine"""
    data = get_machine_status(name)
    
    # Color Logic
    border_color = "#00E396" # Green
    status_icon = "🟢"
    vib_color = "#00E396"
    
    if data['status'] == "JAMMED": 
        border_color = "#FEB019" # Amber/Orange
        status_icon = "🟠"
        vib_color = "#FEB019"
    elif data['status'] == "CRITICAL": 
        border_color = "#FF4560" # Red
        status_icon = "🔴"
        vib_color = "#FF4560"

    # The Card Layout with inline styling for border
    st.markdown(f"""
    <div class="machine-card-container" style="
        border-top: 4px solid {border_color};
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    ">
        <h4 style="margin-bottom: 15px; font-weight: 600; color: #1a1a1a !important;">{status_icon} {name}</h4>
        <div style="display:flex; justify-content:space-around; margin-bottom: 10px;">
            <div>
                <div style="font-size: 26px; font-weight: bold; color: #1a1a1a !important;">{data['amps']} A</div>
                <div style="font-size: 12px; color: #666 !important; text-transform: uppercase;">Load</div>
            </div>
            <div>
                <div style="font-size: 26px; font-weight: bold; color:{vib_color} !important;">{data['vib']:.1f}</div>
                <div style="font-size: 12px; color: #666 !important; text-transform: uppercase;">Vib (mm/s)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # The "Click" Mechanism - placed after the card
    if st.button(f"Select {name}", key=f"btn_{name}"):
        select_machine(name)
        st.rerun()

# -----------------------------------------------------------------------------
# 5. VIEWS
# -----------------------------------------------------------------------------

# --- VIEW A: UNIT 1 OVERVIEW ---
def view_unit_1():
    st.title("🏭 Unit 1 Overview")
    st.markdown("### Flow: Shredding (Prep) ➔ Milling (Finish)")
    
    col_shred, col_arrow, col_mill = st.columns([1, 0.2, 1])
    
    with col_shred:
        st.subheader("Step 1: Shredders")
        render_machine_card("Shredder 1")
        render_machine_card("Shredder 2")
        
    with col_arrow:
        st.markdown("<br><br><br><br><h1 style='color: #888888 !important;'>➡</h1>", unsafe_allow_html=True)
        
    with col_mill:
        st.subheader("Step 2: Mills")
        render_machine_card("Mill 1")
        render_machine_card("Mill 2")
        render_machine_card("Mill 3")

# --- VIEW B: UNIT 2 OVERVIEW ---
def view_unit_2():
    st.title("🏭 Unit 2 Overview")
    st.markdown("### Flow: Shredder ➔ Crusher Tandem")
    
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.subheader("Primary")
        render_machine_card("Unit 2 Shredder")
    with c2:
        st.markdown("<br><br><h1 style='color: #888888 !important;'>➡</h1>", unsafe_allow_html=True)
    with c3:
        st.subheader("Secondary")
        render_machine_card("Unit 2 Crusher")

# --- VIEW C: MACHINE DETAIL (THE CLICK DESTINATION) ---
def view_detail():
    name = st.session_state.selected_machine
    if st.button("⬅ Back to Fleet"):
        # Determine which unit to return to
        if name in ["Shredder 1", "Shredder 2", "Mill 1", "Mill 2", "Mill 3"]:
            set_view("Unit 1")
        else:
            set_view("Unit 2")
        st.rerun()
    
    st.title(f"🔍 Analysis: {name}")
    data = get_machine_status(name)
    maint = maintenance_db.get(name, {})
    
    # 1. TOP RIBBON: VITALS
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Current (Amps)", f"{data['amps']} A", "High" if data['amps']>440 else "Normal")
    k2.metric("Vibration (RMS)", f"{data['vib']} mm/s", "CRITICAL" if data['vib']>8 else "Normal", delta_color="inverse")
    k3.metric("Temperature", f"{data['temp']} °C")
    k4.metric("Jams (Shift)", f"{data['jams']}")
    
    st.divider()
    
    # 2. MAIN INTERFACE (Tabs)
    tab1, tab2, tab3 = st.tabs(["📈 Live Trends", "🛠 Maintenance & Spares", "📋 Production Log"])
    
    with tab1:
        # Live Graph Simulation
        st.subheader("Amps vs Vibration Correlation")
        
        # Create mock history
        x = list(range(60))
        y_amps = np.random.normal(data['amps'], 10, 60)
        y_vib = np.random.normal(data['vib'], 0.5, 60)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y_amps, name='Current (Amps)', line=dict(color='#00E396')))
        fig.add_trace(go.Scatter(x=x, y=y_vib, name='Vibration (mm/s)', yaxis='y2', line=dict(color='#FF4560')))
        
        fig.update_layout(
            template="plotly_white",
            yaxis=dict(title="Current", side="left"),
            yaxis2=dict(title="Vibration", side="right", overlaying="y"),
            height=400,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Maintenance Schedule")
            st.info(f"**Next Job:** {maint['Next']}")
            
            if maint['Due'] == "OVERDUE":
                st.error(f"🚨 JOB OVERDUE")
            else:
                st.success(f"Due in: {maint['Due']}")
                
        with c2:
            st.subheader("Spares Inventory Check")
            
            # LOGIC: If Spares are missing AND Maintenance is Due -> RED ALERT
            if maint['Spare_Status'] == "MISSING":
                st.markdown(f"""
                <div class="alert-box">
                    <h3 style="color: #FF4560 !important; margin-top: 0;">🚫 SPARES MISSING</h3>
                    <p style="color: #1a1a1a !important;">Cannot perform <b>{maint['Next']}</b>. Spare parts stock is 0.</p>
                    <p style="color: #D32F2F !important;">⚠️ ORDER IMMEDIATELY</p>
                </div>
                """, unsafe_allow_html=True)
            elif maint['Spare_Status'] == "LOW":
                st.warning("⚠️ Stock Low: Re-order suggested.")
            else:
                st.success("✅ Spares Available")

    with tab3:
        st.dataframe(pd.DataFrame({
            "Time": ["10:00", "10:15", "10:30"],
            "Event": ["Start", "Load Increase", "Steady State"],
            "Operator": ["John D.", "John D.", "John D."]
        }), use_container_width=True)

# -----------------------------------------------------------------------------
# 6. MAIN APP CONTROLLER
# -----------------------------------------------------------------------------

# Sidebar Navigation
with st.sidebar:
    st.title("🎛 Control Panel")
    if st.button("Unit 1 (5 Equipments)", use_container_width=True):
        set_view("Unit 1")
        st.rerun()
    if st.button("Unit 2 (2 Equipments)", use_container_width=True):
        set_view("Unit 2")
        st.rerun()
    
    st.divider()
    st.caption("System Status: ONLINE")
    st.caption("Server: PLC_GATEWAY_01")

# Render Active View
if st.session_state.current_view == "Unit 1":
    view_unit_1()
elif st.session_state.current_view == "Unit 2":
    view_unit_2()
elif st.session_state.current_view == "Detail":
    view_detail()
