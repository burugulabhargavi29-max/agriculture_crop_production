import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import json
from pathlib import Path

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Agriculture Crop Production Analysis",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp {background: linear-gradient(180deg, #f5fbf4 0%, #ffffff 45%);}
[data-testid="stSidebar"] {background-color: #eaf4e8;}
.hero {
    padding: 1.5rem 1.7rem; border-radius: 18px;
    background: linear-gradient(120deg, #14532d, #2f855a);
    color: white; margin-bottom: 1rem;
}
.hero h1 {color: white; margin-bottom: .3rem;}
.hero p {color: #e7f7e8; font-size: 1.05rem;}
div[data-testid="stMetric"] {
    background: white; border: 1px solid #dcebd9;
    padding: 14px; border-radius: 14px;
}
.small-note {color: #536455; font-size: .88rem;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIMPLE LOCAL ACCOUNT DEMO ----------------
# Important: this is a classroom/demo login, not secure production authentication.
ACCOUNTS_FILE = Path("accounts_demo.json")

def load_accounts():
    if ACCOUNTS_FILE.exists():
        try:
            return json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_accounts(accounts):
    ACCOUNTS_FILE.write_text(json.dumps(accounts), encoding="utf-8")

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Login"

# ---------------- AUTH PAGE ----------------
if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero">
      <h1>🌾 Agriculture Crop Production Analysis System</h1>
      <p>Explore crop production, cultivated area, yield and rainfall patterns.</p>
    </div>
    """, unsafe_allow_html=True)
    login_tab, signup_tab = st.tabs(["Login", "Sign up"])
    with login_tab:
        st.subheader("Welcome back")
        with st.form("login_form"):
            login_user = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submit = st.form_submit_button("Login", use_container_width=True)
        if login_submit:
            accounts = load_accounts()
            saved_hash = accounts.get(login_user.strip())
            if saved_hash and saved_hash == hash_password(login_password):
                st.session_state.authenticated = True
                st.session_state.username = login_user.strip()
                st.rerun()
            else:
                st.error("Login details not found. Please sign up first or check your username and password.")
    with signup_tab:
        st.subheader("Create an account")
        st.info("Demo account storage is temporary on free hosting and is not suitable for private or sensitive information.")
        with st.form("signup_form"):
            new_user = st.text_input("Choose a username", key="signup_user")
            new_password = st.text_input("Choose a password (8+ characters)", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
            signup_submit = st.form_submit_button("Create account", use_container_width=True)
        if signup_submit:
            accounts = load_accounts()
            username = new_user.strip()
            if len(username) < 3:
                st.error("Username must contain at least 3 characters.")
            elif len(new_password) < 8:
                st.error("Please use a password with at least 8 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif username in accounts:
                st.error("That username already exists. Please choose another.")
            else:
                accounts[username] = hash_password(new_password)
                save_accounts(accounts)
                st.success("Account created for this demo. Open the Login tab to sign in.")
    st.caption("Educational project demo. For production use, connect a secure authentication provider.")
    st.stop()


# ---------------- HEADER / SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🌾 Crop Analysis")
    st.write(f"Signed in as **{st.session_state.username}**")
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    st.divider()
    page = st.radio(
        "Navigate",
        ["Dashboard", "Crop Analysis", "State Comparison", "Rainfall Analysis",
         "Data Quality", "View / Download Data", "About Project"],
        label_visibility="visible"
    )
    st.divider()
    st.markdown("### Upload dataset")
    uploaded_file = st.file_uploader(
        "CSV or Excel file", type=["csv", "xlsx", "xls"],
        help="Upload your real agriculture dataset here."
    )

# ---------------- DATA LOADING / NORMALIZATION ----------------
def read_uploaded_file(file):
    if file is None:
        return None
    try:
        if file.name.lower().endswith(".csv"):
            return pd.read_csv(file)
        return pd.read_excel(file)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
        return None

def normalize_columns(frame):
    df = frame.copy()
    df.columns = [str(c).strip().lower().replace("-", "_") for c in df.columns]
    aliases = {
        "state/region": "state", "state_region": "state", "region": "state",
        "state_name": "state", "crop name": "crop", "crop_name": "crop",
        "crop type": "crop", "crop_type": "crop",
        "year": "year", "season_name": "season",
        "area cultivated": "area", "area_cultivated": "area",
        "area cultivated (ha)": "area", "area_ha": "area",
        "cultivated_area": "area", "area (hectares)": "area",
        "production (tonnes)": "production", "crop_production": "production",
        "production_tonnes": "production", "production (tons)": "production",
        "yield_per_hectare": "yield", "crop_yield": "yield",
        "rainfall (mm)": "rainfall", "rainfall_mm": "rainfall",
        "annual_rainfall": "rainfall", "precipitation": "rainfall",

        "rainfall (millimeters)": "rainfall"
    }
    df = df.rename(columns={c: aliases[c] for c in df.columns if c in aliases})
    return df

uploaded_df = read_uploaded_file(uploaded_file)
if uploaded_df is not None:
    df = normalize_columns(uploaded_df)
    st.sidebar.success("Uploaded dataset loaded.")
else:
    # Clearly labelled demonstration data only
    rows = []
    states = ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"]
    crops = ["Rice", "Maize", "Cotton", "Groundnut"]
    seasons = ["Kharif", "Rabi"]
    for si, state in enumerate(states):
        for ci, crop in enumerate(crops):
            for year in range(2020, 2026):
                area = 800 + si * 150 + ci * 110 + (year - 2020) * 20
                production = area * (2.1 + ci * 0.28 + si * 0.1 + (year - 2020) * 0.025)
                rows.append({
                    "state": state, "crop": crop, "year": year,
                    "area": area, "production": round(production, 2),
                    "yield": round(production / area, 2),
                    "season": seasons[(year + ci) % 2]
                })
    df = pd.DataFrame(rows)
    st.sidebar.warning("Demo data in use")

if df.empty:
    st.error("The dataset has no rows.")
    st.stop()

# ---------------- PAGES ----------------
if page == "Dashboard":
    st.subheader("📊 Dashboard overview")
if uploaded_df is None:
  st.info("These are illustrative demo values, not official agricultural statistics. Upload your actual dataset in the sidebar.")

  # Set up filters
   chosen_states = st.sidebar.multiselect(
     "Select States",
      sorted(df["state"].astype(str).unique()),
      default=sorted(df["state"].astype(str).unique())
   )

   chosen_crops = st.sidebar.multiselect(
      "Select Crops",
       sorted(df["crop"].astype(str).unique()),
       default=sorted(df["crop"].astype(str).unique())
)

   chosen_seasons = st.sidebar.multiselect(
     "Select Seasons",
      sorted(df["season"].astype(str).unique()),
      default=sorted(df["season"].astype(str).unique())
)

   chosen_years = st.sidebar.multiselect(
     "Select Years",
      sorted(df["year"].unique()),
      default=sorted(df["year"].unique())
)

filtered = df[
    df["state"].astype(str).isin(chosen_states)
    & df["crop"].astype(str).isin(chosen_crops)
    & df["season"].astype(str).isin(chosen_seasons)
    & df["year"].isin(chosen_years)
].copy()

total_prod = filtered["production"].sum()
total_area = filtered["area"].sum()
weighted_yield = total_prod / total_area if total_area else 0
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total production", f"{total_prod:,.2f}")
    k2.metric("Cultivated area", f"{total_area:,.2f}")
    k3.metric("Overall yield", f"{weighted_yield:,.2f}")
    k4.metric("Crop types", f"{filtered['crop'].nunique():,}")

    left, right = st.columns(2)
    with left:
        trend = filtered.groupby("year", as_index=False)["production"].sum()
        st.plotly_chart(px.line(trend, x="year", y="production", markers=True,
                                title="Yearly production trend"), use_container_width=True)
    with right:
        crop_sum = filtered.groupby("crop", as_index=False)["production"].sum().sort_values("production", ascending=False)
        st.plotly_chart(px.bar(crop_sum, x="crop", y="production", color="crop",
                               title="Production by crop"), use_container_width=True)
    left2, right2 = st.columns(2)
    with left2:
        state_sum = filtered.groupby("state", as_index=False)["production"].sum().sort_values("production", ascending=False)
        st.plotly_chart(px.bar(state_sum, x="state", y="production", title="Production by state"),
                        use_container_width=True)
    with right2:
        season_sum = filtered.groupby("season", as_index=False)["production"].sum()
        st.plotly_chart(px.pie(season_sum, names="season", values="production",
                               title="Production share by season", hole=0.35), use_container_width=True)
    st.caption("Metric units depend on the units used in your uploaded dataset.")

elif page == "Crop Analysis":
    st.subheader("🌾 Crop analysis")
    selected_crop = st.selectbox("Choose a crop", sorted(filtered["crop"].astype(str).unique()))
    crop_df = filtered[filtered["crop"].astype(str) == selected_crop]
    a, b = st.columns(2)
    with a:
        by_year = crop_df.groupby("year", as_index=False)["production"].sum()
        st.plotly_chart(px.line(by_year, x="year", y="production", markers=True,
                                title=f"{selected_crop}: production by year"), use_container_width=True)
    with b:
        by_state = crop_df.groupby("state", as_index=False)["production"].sum().sort_values("production", ascending=False)
        st.plotly_chart(px.bar(by_state, x="state", y="production",
                               title=f"{selected_crop}: production by state"), use_container_width=True)
    c, d = st.columns(2)
    with c:
        area_year = crop_df.groupby("year", as_index=False)["area"].sum()
        st.plotly_chart(px.area(area_year, x="year", y="area", title="Cultivated area over time"),
                        use_container_width=True)
    with d:
        yield_df = crop_df.dropna(subset=["yield"])
        if not yield_df.empty:
            st.plotly_chart(px.scatter(yield_df, x="area", y="production", color="state",
                                       hover_data=["year"], title="Area vs production"),
                            use_container_width=True)
        else:
            st.info("Yield/area comparison is unavailable for this dataset.")

elif page == "State Comparison":
    st.subheader("🗺️ State comparison")
    state_summary = filtered.groupby("state", as_index=False).agg(
        production=("production", "sum"), area=("area", "sum"), crop_count=("crop", "nunique")
    )
    state_summary["overall_yield"] = state_summary["production"] / state_summary["area"].replace(0, pd.NA)
    st.dataframe(state_summary.sort_values("production", ascending=False), use_container_width=True)
    st.plotly_chart(px.bar(state_summary.sort_values("production", ascending=False),
                           x="state", y="production", color="state",
                           title="Total production comparison"), use_container_width=True)
    st.plotly_chart(px.bar(state_summary.sort_values("overall_yield", ascending=False),
                           x="state", y="overall_yield",
                           title="Overall yield comparison"), use_container_width=True)

elif page == "Rainfall Analysis":
    st.subheader("🌧️ Rainfall analysis")
    if "rainfall" not in filtered.columns or filtered["rainfall"].notna().sum() == 0:
        st.warning("Rainfall data is not available. Upload a dataset with a numeric `rainfall` column (for example, rainfall in millimetres) to enable this analysis.")
        st.markdown("Suggested columns: `state`, `crop`, `year`, `area`, `production`, `rainfall`.")
    else:
        rain = filtered.dropna(subset=["rainfall"])
        left, right = st.columns(2)
        with left:
            rain_year = rain.groupby("year", as_index=False).agg(
                rainfall=("rainfall", "mean"), production=("production", "sum")
            )
            st.plotly_chart(px.line(rain_year, x="year", y="rainfall", markers=True,
                                    title="Average rainfall by year"), use_container_width=True)
        with right:
            st.plotly_chart(px.scatter(rain, x="rainfall", y="production", color="state",
                                       hover_data=["crop", "year"],
                                       title="Rainfall vs production"), use_container_width=True)
        corr_data = rain[["rainfall", "production"]].dropna()
        if len(corr_data) >= 2 and corr_data["rainfall"].nunique() > 1 and corr_data["production"].nunique() > 1:
            corr = corr_data["rainfall"].corr(corr_data["production"])
            st.metric("Correlation (rainfall and production)", f"{corr:.2f}")
            st.caption("Correlation shows association, not proof that rainfall caused production changes.")
        else:
            st.info("There are not enough different rainfall and production values to calculate correlation.")

elif page == "Data Quality":
    st.subheader("🧹 Data quality checks")
    q1, q2, q3 = st.columns(3)
    q1.metric("Rows", f"{len(df):,}")
    q2.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")
    q3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
    missing_table = pd.DataFrame({
        "Column": df.columns,
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Data type": [str(df[c].dtype) for c in df.columns]
    })
    st.dataframe(missing_table, use_container_width=True)
    st.write("Preview of duplicate rows")
    duplicates = df[df.duplicated(keep=False)]
    if duplicates.empty:
        st.success("No duplicate rows found.")
    else:
        st.dataframe(duplicates, use_container_width=True)
    st.caption("This page reports data issues; it does not silently delete rows from your original file.")

elif page == "View / Download Data":
    st.subheader("📥 View and download filtered data")
    st.write(f"Showing {len(filtered):,} rows after applying filters.")
    st.dataframe(filtered, use_container_width=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", csv_bytes,
                       file_name="filtered_agriculture_data.csv", mime="text/csv")
    try:
        import io
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            filtered.to_excel(writer, index=False, sheet_name="Filtered Data")
        st.download_button("Download filtered Excel", excel_buffer.getvalue(),
                           file_name="filtered_agriculture_data.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        st.caption("Excel export needs openpyxl; CSV export is available.")

elif page == "About Project":
    st.subheader("📘 About the project")
    st.markdown("""
    **Abstract**

    The Agriculture Crop Production Analysis System is a data-analysis website
    designed to explore agricultural production, cultivated area, crop yield,
    and seasonal trends. Users can upload a CSV or Excel dataset, filter records
    by state, crop, season and year, and view interactive charts and summary
    statistics. If rainfall measurements are included, the system also displays
    rainfall trends and rainfall-production relationships. The system supports
    data quality checks and allows filtered results to be downloaded for further
    study. Findings depend on the quality, coverage and units of the uploaded data.

    **Objectives**
    - Analyze crop production and cultivated area across states and years.
    - Compare crops, seasons and state-level results.
    - Visualize trends using interactive charts.
    - Check missing values and duplicate records.
    - Explore rainfall alongside production when rainfall data is available.
    - Export filtered data for reports and further analysis.

    **Methodology**

    Data Collection → Data Upload → Column Validation → Data Cleaning Checks →
    Filtering → Statistical Analysis → Visualization → Interpretation → Export

    **Tools and technologies**
    - Python
    - Streamlit
    - Pandas
    - Plotly
    - CSV / Excel datasets

    **Scope and limitation**

    This is a descriptive data-analysis project, not a machine-learning prediction
    system. Demo data is illustrative only. Use a reliable official dataset and
    document its source, date range and measurement units in your final report.
    """)
    st.markdown("**Dataset columns:** `state`, `crop`, `year`, `area`, `production`; optional: `yield`, `season`, `rainfall`.")

st.divider()
st.caption("Agriculture Crop Production Analysis System • Student project • Validate dataset sources and units before reporting results.")
