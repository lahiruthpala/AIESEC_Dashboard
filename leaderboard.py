import streamlit as st
import pandas as pd
import time
import os

# --- Paths ---
ICON_PATH = os.path.join(os.path.dirname(__file__), "AIESEC-Human-White.png")      # local PNG icon
GIF_PATH = os.path.join(os.path.dirname(__file__), "giphy.gif")    # local GIF

# --- Streamlit Page Config ---
st.set_page_config(
    layout="wide",
    page_title="National B2B Hunt Dashboard",
    page_icon=ICON_PATH
)


# --- Public Google Sheets URLs ---
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
    df = df.groupby(df.index).sum(numeric_only=True)  # Aggregate duplicates
    return df.add_prefix(prefix)

# --- Loading Animation ---
with st.spinner("Loading AIESEC Dashboard..."):
    time.sleep(2)  # simulate loading

# --- Load all data ---
cm_df = load_data(CM_URL)
mou_df = load_data(MOU_URL)
slot_df = load_data(SLOT_URL)
showcasing_df = load_data(SHOWCASING_URL)
total_df = load_data(TOTAL_URL)

# --- Main Dashboard ---
st.title("National B2B Hunt Dashboard")

# --- Total Marks Table ---
# --- Total Marks Table ---
if not total_df.empty:
    st.subheader("Total Marks by Entity")
    total_df = total_df.iloc[:-1]

    # Ensure unique entities in Total sheet
    total_df = total_df.set_index("Entity")
    total_df = total_df.groupby(total_df.index).sum(numeric_only=True)
    total_df = total_df.reset_index()

    # --- Highlight Top 3 with Pandas Styler ---
    total_df_styled = total_df.sort_values(by='Total Marks', ascending=False).reset_index(drop=True)

    # Add a 'Rank' column with emojis
    total_df_styled.insert(0, 'Rank', '')
    total_df_styled.loc[0, 'Rank'] = '🥇 1'
    total_df_styled.loc[1, 'Rank'] = '🥈 2'
    total_df_styled.loc[2, 'Rank'] = '🥉 3'

    def highlight_top_3(row):
        """Applies a color gradient to the top 3 rows."""
        if row.name == 0:
            return [''] * len(row) # Gold
        elif row.name == 1:
            return [''] * len(row) # Silver
        elif row.name == 2:
            return [''] * len(row) # Bronze
        return [''] * len(row)

    styled_df = total_df_styled.style.apply(highlight_top_3, axis=1)

    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.markdown("---")

# --- Function-specific Graphs ---
if not cm_df.empty and not mou_df.empty and not slot_df.empty and not showcasing_df.empty:
    st.subheader("Performance by Function")

    # Standardize and clean dataframes
    cm_df = prepare_df(cm_df, "CM_")
    mou_df = prepare_df(mou_df, "MOU_")
    slot_df = prepare_df(slot_df, "Slot_")
    showcasing_df = prepare_df(showcasing_df, "Showcasing_")

    all_functions = ["iGV", "iGTa", "iGTe"]

    with st.sidebar:
        st.header("Filter Options")
        selected_function = st.selectbox("Select a Function:", all_functions, index=0)

    if selected_function:
        st.write(f"Displaying data for function: **{selected_function}**")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        # CM Chart
        with col1:
            st.markdown(f"**Company Meeting Analysis**")
            col_name = f"CM_{selected_function} Marks"
            if col_name in cm_df.columns:
                st.bar_chart(cm_df[col_name])
            else:
                st.info(f"'{col_name}' not found in CM_Marks.")

        # MOU Chart
        with col2:
            st.markdown(f"**MOU / Contract Analysis**")
            col_name = f"MOU_{selected_function} Marks"
            if col_name in mou_df.columns:
                st.bar_chart(mou_df[col_name])
            else:
                st.info(f"'{col_name}' not found in MOU_Marks.")

        # Slot Chart
        with col3:
            st.markdown(f"**Created Slot Analysis**")
            col_name = f"Slot_{selected_function}"
            if col_name in slot_df.columns:
                st.bar_chart(slot_df[col_name])
            else:
                st.info(f"'{col_name}' not found in Slot_Marks.")

        # Showcasing Chart
        with col4:
            st.markdown(f"**B2B Showcasing Analysis**")
            col_name = f"Showcasing_{selected_function} Marks"
            if col_name in showcasing_df.columns:
                st.bar_chart(showcasing_df[col_name])
            else:
                st.info(f"'{col_name}' not found in Showcasing_Marks.")