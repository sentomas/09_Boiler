import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# App styling and title configuration
st.set_page_config(page_title="Industrial Boiler Thermal Decay Twin", layout="wide")
st.title("🏭 Industrial Boiler Thermal Decay Twin")
st.markdown("""
This simulator is developed by Serin Thomas, uses **Newton's Law of Cooling** to model the transient thermal decay of an industrial boiler system after shutdown. 
It resolves the explicit system cooling constant ($k$) and tracks convergence toward environmental equilibrium. The technical blog for this app is in the following link:
https://serinthomas.co.in/2026/06/19/the-thermodynamics-of-a-spilled-drink/
""")

st.divider()

# Sidebar Layout for Inputs
st.sidebar.header("System Parameters")

T0 = st.sidebar.number_input("Initial Boiler Temperature (T₀ in °C)", min_value=0.0, max_value=1500.0, value=450.0, step=10.0)
Ts = st.sidebar.number_input("Ambient Factory Temperature (Ts in °C)", min_value=0.0, max_value=60.0, value=30.0, step=1.0)

st.sidebar.subheader("Calibration Milestone")
st.sidebar.markdown("Input a known historical measurement point to calculate the system boundary conditions ($k$).")
t_bench = st.sidebar.number_input("Observed Time Elapsed (minutes)", min_value=1.0, max_value=1440.0, value=60.0)

# FIX: We use a standard input without strict min/max constraints to prevent runtime app crashes.
# Validation is handled safely below via conditional code blocks.
T_bench = st.sidebar.number_input("Observed Temperature at that Time (°C)", value=280.0)

# Programmatic Thermodynamic Validation
if T0 <= Ts:
    st.error(f"❌ System Parameters Error: Initial Boiler Temperature ({T0}°C) must be strictly higher than the Ambient Factory Temperature ({Ts}°C).")

elif T_bench >= T0:
    st.error(f"❌ Calibration Error: The observed milestone temperature ({T_bench}°C) cannot be higher than or equal to the starting temperature ({T0}°C).")

elif T_bench <= Ts:
    st.error(f"❌ Calibration Error: The observed milestone temperature ({T_bench}°C) must be higher than the target ambient floor ({Ts}°C) to show active cooling.")

else:
    # -------------------------------------------------------------
    # MATHEMATICAL COMPUTATIONS (Calculus & First Principles)
    # -------------------------------------------------------------
    # 1. Convert benchmark time to seconds for standard SI calculation
    t_bench_sec = t_bench * 60
    
    # 2. Derive cooling constant 'k' from first principles
    # T(t) = Ts + (T0 - Ts)e^(-kt) -> (T(t) - Ts)/(T0 - Ts) = e^(-kt)
    gradient_ratio = (T_bench - Ts) / (T0 - Ts)
    k = -np.log(gradient_ratio) / t_bench_sec
    
    # 3. Calculate Characteristic Decay Time Constant (tau)
    tau_sec = 1 / k
    tau_min = tau_sec / 60

    # UI Metrics Layout
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Cooling Constant (k)", value=f"{k:.6f} s⁻¹")
    col2.metric(label="Time Constant (τ)", value=f"{tau_min:.1f} mins")
    col3.metric(label="Equilibrium Horizon (5τ)", value=f"{(5 * tau_min / 60):.2f} hours")

    st.divider()

    # Time array generation for the simulation timeline (up to 5 tau)
    t_max_sec = 5 * tau_sec
    t_array_sec = np.linspace(0, t_max_sec, 1000)
    t_array_min = t_array_sec / 60
    
    # Absolute Temperature Tracking Formula: Equation (10)
    T_array = Ts + (T0 - Ts) * np.exp(-k * t_array_sec)

    # -------------------------------------------------------------
    # PLOT GENERATION (Matplotlib Engine)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(t_array_min, T_array, color='#d9534f', linewidth=2.5, label='Boiler Core Temp')
    ax.axhline(Ts, color='gray', linestyle='--', linewidth=1.2, label=f'Ambient Baseline ({Ts}°C)')
    
    # Labeling Time Constant Milestones directly on the plot
    milestones_min = [tau_min, 3 * tau_min, 5 * tau_min]
    for m in milestones_min:
        m_sec = m * 60
        m_temp = Ts + (T0 - Ts) * np.exp(-k * m_sec)
        ax.plot(m, m_temp, 'ko')
        ax.annotate(f"{m_temp:.1f}°C", (m, m_temp), textcoords="offset points", xytext=(10, 5), ha='left', fontsize=9, weight='bold')

    ax.set_title('Transient Thermal Dissipation Curve', fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel('Time elapsed since shutdown (Minutes)', fontsize=10)
    ax.set_ylabel('Boiler Internal Temperature (°C)', fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right')
    
    # Render the chart natively inside the web layout
    st.pyplot(fig)

    # Raw Data Inspection Table
    with st.expander("View Raw Simulation Dataset"):
        milestone_data = {
            "Milestone": ["Shutdown (t=0)", "1 Time Constant (τ)", "3 Time Constants (3τ)", "Practical Equilibrium (5τ)"],
            "Time (Minutes)": [0.0, round(tau_min, 1), round(3*tau_min, 1), round(5*tau_min, 1)],
            "Temperature (°C)": [
                round(T0, 1), 
                round(Ts + (T0 - Ts)*np.exp(-1), 1), 
                round(Ts + (T0 - Ts)*np.exp(-3), 1), 
                round(Ts + (T0 - Ts)*np.exp(-5), 1)
            ]
        }
        st.table(milestone_data)