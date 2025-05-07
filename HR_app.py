import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, FuncFormatter

# Page Title
st.set_page_config(page_title="Interactive H-R Diagram Tool", layout="wide")
st.title("🌌 Interactive Hertzsprung-Russell Diagram Maker")

# Sidebar Instructions
st.sidebar.header("Upload Your Dataset")
st.sidebar.markdown("""
- Must contain the following columns:
  - `Temperature (K)`
  - `Luminosity(L/Lo)`
  - `Absolute magnitude(Mv)`
  - `Star type`
  - `Spectral Class`
- Supported format: `.csv`
""")

# File Upload
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type="csv")

# Function to Load and Validate Data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = ['Temperature (K)', 'Luminosity(L/Lo)', 'Absolute magnitude(Mv)', 'Star type', 'Spectral Class']
        if not all(col in df.columns for col in required_columns):
            st.error("Dataset is missing one or more required columns.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to Map Star Types
def map_star_types(df):
    star_type_map = {
        0: ('Red Dwarf', 30, 'red'),
        1: ('Brown Dwarf', 20, 'maroon'),
        2: ('White Dwarf', 25, 'green'),
        3: ('Main Sequence', 50, 'blue'),
        4: ('Giant', 80, 'orange'),
        5: ('Supergiant', 100, 'purple')
    }
    df['Star type label'] = df['Star type'].map(lambda x: star_type_map[x][0])
    df['Marker size'] = df['Star type'].map(lambda x: star_type_map[x][1])
    df['Color'] = df['Star type'].map(lambda x: star_type_map[x][2])
    return df

# Function to Create Spectral Class Axis
def create_spectral_class_axis(ax, temp_range):
    spectral_classes = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    temp_bounds = [40000, 30000, 10000, 7500, 6000, 3700, 2000]
    ax2 = ax.twiny()
    ax2.set_xscale('log')
    ax2.set_xlim(temp_range)
    ax2.set_xticks(temp_bounds)
    ax2.set_xticklabels(spectral_classes)
    ax2.set_xlabel('Spectral Class', fontsize=12)
    ax2.invert_xaxis()
    return ax2

# Function to Create Luminosity Axis
def create_luminosity_axis(ax, mv_range):
    ax3 = ax.twinx()
    l_min = 1e-6
    l_max = 1e6
    ax3.set_yscale('log')
    ax3.set_ylim(l_min, l_max)

    l_ticks = [10**i for i in range(-6, 7)]
    l_labels = [f'$10^{{{i}}}$' for i in range(-6, 7)]
    ax3.set_yticks(l_ticks)
    ax3.set_yticklabels(l_labels)

    ax3.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(1, 10)))
    ax3.set_ylabel('Luminosity (L/Lo)', fontsize=12)
    return ax3

# Function to Plot H-R Diagram
def plot_hr_diagram(df):
    fig, ax = plt.subplots(figsize=(14, 10))

    for s_type, color in zip(df['Star type label'].unique(), df['Color'].unique()):
        subset = df[df['Star type label'] == s_type]
        if not subset.empty:
            ax.scatter(
                subset['Temperature (K)'],
                subset['Absolute magnitude(Mv)'],
                c=color,
                s=subset['Marker size'].iloc[0],
                label=s_type,
                alpha=0.7,
                edgecolors='black',
                linewidth=0.5
            )

    ax.set_xscale('log')
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_xlabel('Temperature (K)', fontsize=12)
    ax.set_ylabel('Absolute Magnitude (Mv)', fontsize=12)
    ax.set_title('Hertzsprung-Russell Diagram', fontsize=14, pad=30)
    ax.legend(title='Stellar Classification', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, which="both", ls="--", alpha=0.6)

    temp_min, temp_max = df['Temperature (K)'].min() * 0.9, df['Temperature (K)'].max() * 1.1
    mv_min, mv_max = df['Absolute magnitude(Mv)'].min() - 1, df['Absolute magnitude(Mv)'].max() + 1
    ax.set_xlim(temp_max, temp_min)
    ax.set_ylim(mv_max, mv_min)

    major_ticks = [40000, 30000, 20000, 10000, 7500, 6000, 5000, 3000]
    ax.set_xticks(major_ticks)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x)}"))
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)))
    ax.tick_params(which='minor', length=4)

    create_spectral_class_axis(ax, (temp_min, temp_max))
    create_luminosity_axis(ax, (mv_min, mv_max))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig

# Main App Logic
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        df = map_star_types(df)
        fig = plot_hr_diagram(df)
        st.pyplot(fig)
else:
    st.info("Please upload a CSV file to generate the H-R diagram.")