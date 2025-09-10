import streamlit as st
import pandas as pd

# --- Main App Layout ---
st.set_page_config(layout="wide", page_title="Organizational Dashboard")

# --- Public Google Sheets URL ---
CM_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQu9p7UvibTYDWtD38emvrFPu_ChduAUFMrZWiSsLV_e1vZGAWH3TNk_uHzV0qTyCwZb1VD_vcIojcw/pub?gid=2019645511&single=true&output=csv"
MOU_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQu9p7UvibTYDWtD38emvrFPu_ChduAUFMrZWiSsLV_e1vZGAWH3TNk_uHzV0qTyCwZb1VD_vcIojcw/pub?gid=77788075&single=true&output=csv"
SLOT_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQu9p7UvibTYDWtD38emvrFPu_ChduAUFMrZWiSsLV_e1vZGAWH3TNk_uHzV0qTyCwZb1VD_vcIojcw/pub?gid=2103710827&single=true&output=csv"
SHOWCASING_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQu9p7UvibTYDWtD38emvrFPu_ChduAUFMrZWiSsLV_e1vZGAWH3TNk_uHzV0qTyCwZb1VD_vcIojcw/pub?gid=1782517945&single=true&output=csv"
TOTAL_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQu9p7UvibTYDWtD38emvrFPu_ChduAUFMrZWiSsLV_e1vZGAWH3TNk_uHzV0qTyCwZb1VD_vcIojcw/pub?gid=929949898&single=true&output=csv"

# --- Data Loading Function ---
@st.cache_data(ttl=600)
def load_data(url):
    """Loads a public Google Sheet URL into a pandas DataFrame."""
    try:
        df = pd.read_csv(url)
        if not df.empty:
            df.rename(columns={df.columns[0]: 'Entity'}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data from URL: {e}")
        return pd.DataFrame()

# --- Prep function (ensures unique entities & prefixes) ---
def prepare_df(df, prefix):
    if df.empty:
        return pd.DataFrame()
    df = df.set_index("Entity")
    df = df.groupby(df.index).sum(numeric_only=True)   # ✅ aggregate duplicates
    return df.add_prefix(prefix)

# Load all data
cm_df = load_data(CM_URL)
mou_df = load_data(MOU_URL)
slot_df = load_data(SLOT_URL)
showcasing_df = load_data(SHOWCASING_URL)
total_df = load_data(TOTAL_URL)

st.title("Performance Dashboard")
st.markdown("### A visual summary of marks and openings")

# --- Total Marks Table ---
if not total_df.empty:
    st.subheader("Total Marks by Entity")

    total_df = total_df.iloc[:-1]
    
    # Ensure unique entities in Total sheet
    total_df = total_df.set_index("Entity")
    total_df = total_df.groupby(total_df.index).sum(numeric_only=True)
    total_df = total_df.reset_index()

    # Show table from TOTAL_URL
    st.dataframe(total_df.sort_values(by='Total Marks', ascending=False), use_container_width=True)

    st.markdown("---")

# --- Function-specific Graphs ---
if not cm_df.empty and not mou_df.empty and not slot_df.empty and not showcasing_df.empty:
    st.subheader("Performance by Function")

    # Standardize and clean dataframes
    cm_df = prepare_df(cm_df, "CM_")
    mou_df = prepare_df(mou_df, "MOU_")
    slot_df = prepare_df(slot_df, "Slot_")
    showcasing_df = prepare_df(showcasing_df, "Showcasing_")

    # Get all unique functions (strip prefixes)
    all_functions = ["GV", "GTa", "GTe"]

    with st.sidebar:
        st.header("Filter Options")
        selected_function = st.selectbox("Select a Function:", all_functions, index=None, placeholder="Choose a Function...")
        selected_entity = None
        if selected_function:
            entities = total_df["Entity"].unique().tolist()
            selected_entity = st.selectbox("Select an Entity:", entities, index=None, placeholder="Choose an Entity...")

    if selected_function:
        st.write(f"Displaying data for function: **{selected_function}**")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        # Bar chart 1: CM_Marks
        with col1:
            st.markdown(f"**CM Marks for i{selected_function}**")
            col_name = f"CM_i{selected_function} Marks"
            if col_name in cm_df.columns:
                st.bar_chart(cm_df[col_name])
            else:
                st.info(f"'{col_name}' not found in CM_Marks.")

        # Bar chart 2: MOU_Marks
        with col2:
            st.markdown(f"**MOU Marks for i{selected_function}**")
            col_name = f"MOU_i{selected_function} Marks"
            if col_name in mou_df.columns:
                st.bar_chart(mou_df[col_name])
            else:
                st.info(f"'{col_name}' not found in MOU_Marks.")

        # Bar chart 3: Slot_Marks
        with col3:
            st.markdown(f"**Slot Marks for {selected_function}**")
            col_name = f"Slot_{selected_function}"
            if col_name in slot_df.columns:
                st.bar_chart(slot_df[col_name])
            else:
                st.info(f"'{col_name}' not found in Slot_Marks.")

        # Bar chart 4: Showcasing_Marks
        with col4:
            st.markdown(f"**Showcasing Marks for i{selected_function}**")
            col_name = f"Showcasing_i{selected_function} Marks"
            if col_name in showcasing_df.columns:
                st.bar_chart(showcasing_df[col_name])
            else:
                st.info(f"'{col_name}' not found in Showcasing_Marks.")
    else:
        st.info("Please select a function from the sidebar to view the graphs.")
