import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURATION ---
st.set_page_config(page_title="Economic Flow Simulator", layout="wide")

# --- LOGIC ---
class MarkoEconomicSim:
    def __init__(self, population, qlt):
        self.QLT = qlt
        self.population = population

    def calculate(self, jobs_available, tvg, use_dividend, use_stabilization):
        workforce = min(jobs_available, self.population)
        
        # Origin Logic
        labor_val = workforce * 90.0 
        if labor_val > tvg: labor_val = tvg
        auto_val = tvg - labor_val

        # Distribution Logic
        standard_allocation = workforce * 50.0
        allocation = 0
        policy_status = "Standard Model"
        
        if use_dividend:
            allocation = tvg * 0.45
            policy_status = "National Dividend Active"
        elif use_stabilization:
            if tvg < 1000:
                allocation = self.QLT
                policy_status = "Stabilization Fund TRIGGERED"
            else:
                allocation = standard_allocation
                policy_status = "Stabilization Fund (Standby)"
        else:
            allocation = standard_allocation
            if tvg < 1000: 
                allocation = standard_allocation * (tvg / 1500)
                policy_status = "Recession Cutbacks"

        if allocation > tvg: allocation = tvg
        elite_surplus = tvg - allocation

        return {
            "labor": labor_val, "auto": auto_val,
            "public": allocation, "elites": elite_surplus, "policy": policy_status
        }

# --- DRAWING FUNCTION ---
def draw_system(tvg, jobs, population, qlt, policy):
    sim = MarkoEconomicSim(population, qlt)
    use_div = (policy == 'National Dividend')
    use_stab = (policy == 'Stabilization Fund')
    data = sim.calculate(jobs, tvg, use_div, use_stab)
    
    is_stable = data["public"] >= qlt
    status_color = '#2ecc71' if is_stable else '#e74c3c'
    status_text = "STABLE" if is_stable else "COLLAPSE"
    
    # Canvas Setup
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#2b2b2b')
    ax.set_facecolor('#2b2b2b')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    max_val = 3000
    scale = 25 / max_val

    # Helper: Draw Box
    def draw_box(x, y, width, height, color, label, sublabel=""):
        rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.5", 
                                      linewidth=1, edgecolor='white', facecolor=color)
        ax.add_patch(rect)
        ax.text(x + width/2, y + height/2 + 2, label, color='white', 
                ha='center', va='center', fontweight='bold', fontsize=10)
        ax.text(x + width/2, y + height/2 - 2, sublabel, color='white', 
                ha='center', va='center', fontsize=9)

    # Helper: Draw Arrow
    def draw_arrow(x1, y1, x2, y2, value, color):
        width = value * scale
        if width < 1: width = 1
        arrow = patches.FancyArrowPatch((x1, y1), (x2, y2), 
                                        arrowstyle='simple,head_length=10,head_width=10,tail_width=' + str(width),
                                        color=color, alpha=0.6, connectionstyle="arc3,rad=-0.1")
        ax.add_patch(arrow)

    # Draw Nodes
    draw_box(5, 65, 15, 10, '#3498db', "Labor Force", f"${data['labor']:.0f}B")
    draw_box(5, 25, 15, 10, '#9b59b6', "Automation", f"${data['auto']:.0f}B")
    draw_box(42, 40, 16, 20, '#34495e', "The Economy", f"Total: ${tvg}B")
    draw_box(80, 65, 15, 10, '#95a5a6', "Elites/Corps", f"${data['elites']:.0f}B")
    
    # Public Box (Water Level Logic)
    public_box_y = 15
    rect = patches.FancyBboxPatch((80, public_box_y), 15, 20, boxstyle="round,pad=0.5", 
                                  linewidth=1, edgecolor='white', facecolor='#222')
    ax.add_patch(rect)
    
    fill_percent = min(1.0, data['public'] / 1500)
    fill_height = 20 * fill_percent
    fill_rect = patches.FancyBboxPatch((80, public_box_y), 15, fill_height, boxstyle="round,pad=0.5", 
                                       linewidth=0, facecolor=status_color, alpha=0.8)
    ax.add_patch(fill_rect)
    
    qlt_percent = min(1.0, qlt / 1500)
    qlt_h = public_box_y + (20 * qlt_percent)
    ax.hlines(qlt_h, 79, 96, colors='white', linestyles='dashed', linewidth=2)
    ax.text(97, qlt_h, "QLT", color='white', va='center', fontsize=9, fontweight='bold')
    
    ax.text(87.5, public_box_y - 5, f"Public Allocation\n${data['public']:.0f}B", 
            color=status_color, ha='center', va='top', fontweight='bold')

    # Draw Flows
    draw_arrow(21, 70, 41, 55, data['labor'], '#3498db')
    draw_arrow(21, 30, 41, 45, data['auto'], '#9b59b6')
    draw_arrow(59, 55, 79, 70, data['elites'], '#95a5a6')
    draw_arrow(59, 45, 79, 25, data['public'], status_color)

    plt.suptitle(f"SYSTEM STATUS: {status_text}", fontsize=20, color=status_color, weight='bold', y=0.95)
    ax.text(50, 90, f"Active Policy: {data['policy']}", ha='center', color='white', fontsize=12)
    
    return fig

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Simulation Parameters")
tvg = st.sidebar.slider("Total Value ($B)", 500, 3000, 1500, 50)
jobs = st.sidebar.slider("Jobs (Millions)", 0.0, 20.0, 16.5, 0.5)
st.sidebar.divider()
population = st.sidebar.number_input("Population (M)", value=18.0)
qlt = st.sidebar.number_input("QLT Threshold ($B)", value=667)
policy = st.sidebar.selectbox("Active Policy", ['None', 'National Dividend', 'Stabilization Fund'])

# --- MAIN DISPLAY ---
st.title("Macro-Economic Flow Simulator")
st.write("Visualize how value flows from Labor/Automation to the Public/Elites.")

fig = draw_system(tvg, jobs, population, qlt, policy)
st.pyplot(fig)