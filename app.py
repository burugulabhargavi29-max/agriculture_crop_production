
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import hashlib

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AgriScope | Crop Production Analysis",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f8f2;
}
[data-testid="stSidebar"] {
    background-color: #e7f0e3;
}
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #245c37;
}
.subtitle {
    color: #657765;
    font-size: 16px;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce8d8;
    padding: 18px;
    border-radius: 12px;
}
div[data-testid="stMetricValue"] {
    color: #245c37;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DEMONSTRATION DATA ----------------
def create_demo_data():
    rows = [
        ("Andhra Pradesh", "Rice", 2020, "Kharif", 120, 420, 720),
        ("Andhra Pradesh", "Rice", 2021, "Kharif", 125, 450, 680),
        ("Andhra Pradesh", "Rice", 2022, "Kharif", 130, 468, 710),
        ("Telangana", "Rice", 2020, "Kharif", 110, 385, 750),
        ("Telangana", "Rice", 2021, "Kharif", 115, 414, 790),
        ("Telangana", "Cotton", 2022, "Kharif", 95, 190, 650),
        ("Karnataka", "Ragi", 2020, "Kharif", 80, 144, 600),
        ("Karnataka", "Ragi", 2021, "Kharif", 85, 153, 620),
        ("Tamil Nadu", "Rice", 2022, "Rabi", 100, 400, 900),
        ("Maharashtra", "Cotton", 2021, "Kharif", 140, 280, 700),
        ("Punjab", "Wheat", 2020, "Rabi", 150, 600, 500),
        ("Punjab", "Wheat", 2021, "Rabi", 155, 635, 520),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "State", "Crop", "Year", "Season",
            "Area", "Production", "Rainfall"
        ]
    )

# ---------------- SESSION STATE ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "users" not in st.session_state:
    st.session_state.users = {}

if "page" not in st.session_state:
    st.session_state.page = "Login"

# ---------------- LOGIN / SIGNUP ----------------
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authentication_page():
    st.markdown(
        '<div class="main-title">🌾 AgriScope</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Agriculture Crop Production Analysis System</div>',
        unsafe_allow_html=True
    )
    st.divider()

    left, right = st.columns([1, 1.2])

    with left:
        st.image(
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef"
            "?auto=format&fit=crop&w=1000&q=80",
            use_container_width=True
        )
        st.subheader("Understand agriculture through data")
        st.write(
            "Explore crop production, cultivated area, yield, "
            "rainfall, and agricultural trends using data analysis."
        )

    with right:
        login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

        with login_tab:
            st.subheader("Welcome back")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button(
                    "Login", use_container_width=True
                )

            if login_button:
                saved = st.session_state.users.get(username)
                if saved and saved == make_hash(password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error(
                        "Invalid username or password. "
                        "Please sign up first or check your details."
                    )

            st.caption(
                "Demo only: accounts are stored temporarily in the "
                "current Streamlit session."
            )

        with signup_tab:
            st.subheader("Create an account")
            with st.form("signup_form"):
                new_username = st.text_input("Choose a username")
                new_password = st.text_input(
                    "Choose a password", type="password"
                )
                confirm_password = st.text_input(
                    "Confirm password", type="password"
                )
                signup_button = st.form_submit_button(
                    "Create Account", use_container_width=True
                )

            if signup_button:
                if not new_username.strip() or not new_password:
                    st.error("Please enter a username and password.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif new_username in st.session_state.users:
                    st.error("That username already exists.")
                else:
                    st.session_state.users[new_username] = make_hash(
                        new_password
                    )
                    st.success("Account created. You can now log in.")

# ---------------- DATA HELPERS ----------------
def read_uploaded_file(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)

def find_column(columns, keywords):
    for col in columns:
        normalized = str(col).strip().lower().replace("_", " ")
        if normalized in keywords:
            return col
    for col in columns:
        normalized = str(col).strip().lower().replace("_", " ")
        if any(word in normalized for word in keywords):
            return col
    return None

def number_series(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")

def safe_sum(series):
    return float(series.sum()) if series.notna().any() else 0.0

def display_number(value):
    return f"{value:,.2f}"

# ---------------- MAIN DASHBOARD ----------------
def dashboard():
    st.markdown(
        '<div class="main-title">🌾 AgriScope Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Agriculture Crop Production Analysis System</div>',
        unsafe_allow_html=True
    )

    st.sidebar.title("🌿 Navigation")
    st.sidebar.write(
        f"Welcome, **{st.session_state.get('username', 'User')}**"
    )

    page = st.sidebar.radio(
        "Go to",
        [
            "Dashboard",
            "Crop Analysis",
            "Trends & Rainfall",
            "Data Explorer",
            "Project Information"
        ]
    )

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("📂 Upload Dataset")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            raw_df = read_uploaded_file(uploaded_file)
            source_label = "Uploaded dataset"
        except Exception as error:
            st.error(f"Could not read the uploaded file: {error}")
            return
    else:
        raw_df = create_demo_data()
        source_label = "Illustrative demonstration data"
        st.info(
            "You are viewing illustrative demo values, not official "
            "agricultural statistics. Upload your own dataset in the "
            "sidebar to analyze your actual data."
        )

    if raw_df.empty:
        st.error("The dataset has no rows.")
        return

    st.caption(f"Data source: {source_label}")

    # ---------------- COLUMN MAPPING ----------------
    st.sidebar.subheader("🧩 Map Dataset Columns")
    columns = list(raw_df.columns)

    crop_guess = find_column(columns, ["crop", "crop name", "commodity"])
    state_guess = find_column(columns, ["state", "region", "district"])
    year_guess = find_column(columns, ["year", "crop year"])
    season_guess = find_column(columns, ["season"])
    area_guess = find_column(columns, ["area", "area cultivated", "cultivated area"])
    production_guess = find_column(columns, ["production", "produce", "output"])
    yield_guess = find_column(columns, ["yield", "productivity"])
    rainfall_guess = find_column(columns, ["rainfall", "rain", "precipitation"])

    def choose_column(label, guess, required=False):
        options = ["-- Not available --"] + columns
        default_index = options.index(guess) if guess in columns else 0
        choice = st.sidebar.selectbox(
            label,
            options,
            index=default_index,
            key=f"mapping_{label}"
        )
        if choice == "-- Not available --":
            return None
        return choice

    crop_col = choose_column("Crop name column", crop_guess, True)
    state_col = choose_column("State / Region column", state_guess)
    year_col = choose_column("Year column", year_guess)
    season_col = choose_column("Season column", season_guess)
    area_col = choose_column("Cultivated area column", area_guess, True)
    production_col = choose_column(
        "Production column", production_guess, True
    )
    yield_col = choose_column("Yield column", yield_guess)
    rainfall_col = choose_column("Rainfall column", rainfall_guess)

    if crop_col is None or area_col is None or production_col is None:
        st.error(
            "Please map the crop, cultivated area, and production columns "
            "using the sidebar. These three columns are required."
        )
        return

    # ---------------- CLEAN AND STANDARDIZE ----------------
    df = pd.DataFrame(index=raw_df.index)
    df["Crop"] = raw_df[crop_col].astype("string").str.strip()
    df["Area"] = number_series(raw_df[area_col])
    df["Production"] = number_series(raw_df[production_col])

    if state_col:
        df["State"] = raw_df[state_col].astype("string").str.strip()
    else:
        df["State"] = "Not specified"

    if year_col:
        df["Year"] = number_series(raw_df[year_col])
    else:
        df["Year"] = np.nan

    if season_col:
        df["Season"] = raw_df[season_col].astype("string").str.strip()
    else:
        df["Season"] = "Not specified"

    if yield_col:
        df["Yield"] = number_series(raw_df[yield_col])
    else:
        df["Yield"] = np.where(
            df["Area"] > 0,
            df["Production"] / df["Area"],
            np.nan
        )

    if rainfall_col:
        df["Rainfall"] = number_series(raw_df[rainfall_col])

    df = df.replace([np.inf, -np.inf], np.nan)
    missing_before = int(df.isna().sum().sum())
    duplicates_before = int(df.duplicated().sum())

    df = df.dropna(subset=["Crop", "Area", "Production"])
    df = df[df["Crop"].str.len() > 0]
    df = df[(df["Area"] >= 0) & (df["Production"] >= 0)]
    df = df.drop_duplicates().reset_index(drop=True)

    if df.empty:
        st.error(
            "No valid rows remain after cleaning. Check the selected "
            "columns and numeric values in your dataset."
        )
        return

    # ---------------- FILTERS ----------------
    st.sidebar.subheader("🔎 Filter Data")

    state_options = sorted(df["State"].dropna().astype(str).unique())
    crop_options = sorted(df["Crop"].dropna().astype(str).unique())
    season_options = sorted(df["Season"].dropna().astype(str).unique())

    selected_states = st.sidebar.multiselect(
        "Select states / regions",
        state_options,
        default=state_options
    )
    selected_crops = st.sidebar.multiselect(
        "Select crops",
        crop_options,
        default=crop_options
    )
    selected_seasons = st.sidebar.multiselect(
        "Select seasons",
        season_options,
        default=season_options
    )

    filtered = df[
        df["State"].astype(str).isin(selected_states)
        & df["Crop"].astype(str).isin(selected_crops)
        & df["Season"].astype(str).isin(selected_seasons)
    ].copy()

    if df["Year"].notna().any():
        available_years = sorted(
            df["Year"].dropna().astype(int).unique().tolist()
        )
        selected_years = st.sidebar.multiselect(
            "Select years",
            available_years,
            default=available_years
        )
        filtered = filtered[
            filtered["Year"].isin(selected_years)
        ]

    if filtered.empty:
        st.warning("No records match your filters. Select more options.")
        return

    # ---------------- DASHBOARD SUMMARY ----------------
    if page == "Dashboard":
        st.subheader("📊 Key Performance Indicators")

        total_production = safe_sum(filtered["Production"])
        total_area = safe_sum(filtered["Area"])
        average_yield = filtered["Yield"].mean()
        number_crops = filtered["Crop"].nunique()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Production", display_number(total_production))
        c2.metric("Total Cultivated Area", display_number(total_area))
        c3.metric(
            "Average Yield",
            display_number(average_yield)
            if pd.notna(average_yield) else "N/A"
        )
        c4.metric("Number of Crops", f"{number_crops:,}")

        st.divider()
        left, right = st.columns(2)

        production_by_crop = (
            filtered.groupby("Crop", as_index=False)["Production"]
            .sum()
            .sort_values("Production", ascending=False)
        )
        with left:
            st.subheader("Production by Crop")
            fig = px.bar(
                production_by_crop,
                x="Crop",
                y="Production",
                color="Crop",
                title="Total Production by Crop"
            )
            st.plotly_chart(fig, use_container_width=True)

        production_by_state = (
            filtered.groupby("State", as_index=False)["Production"]
            .sum()
            .sort_values("Production", ascending=False)
        )
        with right:
            st.subheader("State-wise Production Share")
            fig = px.pie(
                production_by_state,
                names="State",
                values="Production",
                hole=0.4,
                title="Production Distribution by State"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 Area vs Production")
        fig = px.scatter(
            filtered,
            x="Area",
            y="Production",
            color="Crop",
            hover_data=["State", "Season"],
            title="Cultivated Area Compared with Production"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest Records")
        st.dataframe(filtered.head(10), use_container_width=True)

    # ---------------- CROP ANALYSIS ----------------
    elif page == "Crop Analysis":
        st.header("🌱 Crop Analysis")

        left, right = st.columns(2)

        crop_production = (
            filtered.groupby("Crop", as_index=False)["Production"]
            .sum()
            .sort_values("Production", ascending=False)
        )
        with left:
            st.subheader("Production Comparison")
            fig = px.bar(
                crop_production,
                x="Production",
                y="Crop",
                orientation="h",
                color="Production",
                title="Crops Ranked by Production"
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Cultivated Area by Crop")
            area_data = (
                filtered.groupby("Crop", as_index=False)["Area"].sum()
            )
            fig = px.pie(
                area_data,
                names="Crop",
                values="Area",
                title="Area Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Yield Comparison")
        yield_data = (
            filtered.groupby("Crop", as_index=False)["Yield"]
            .mean()
            .dropna()
        )
        if not yield_data.empty:
            fig = px.bar(
                yield_data,
                x="Crop",
                y="Yield",
                color="Crop",
                title="Average Yield by Crop"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Yield data is not available for this selection.")

        st.subheader("Production Statistics")
        st.dataframe(
            filtered.groupby("Crop")[
                ["Area", "Production", "Yield"]
            ].agg(["count", "mean", "min", "max"]).round(2),
            use_container_width=True
        )

    # ---------------- TRENDS AND RAINFALL ----------------
    elif page == "Trends & Rainfall":
        st.header("🌦️ Production Trends and Rainfall")

        if filtered["Year"].notna().any():
            yearly = (
                filtered.dropna(subset=["Year"])
                .groupby("Year", as_index=False)
                .agg(
                    Production=("Production", "sum"),
                    Area=("Area", "sum"),
                    Yield=("Yield", "mean")
                )
                .sort_values("Year")
            )

            st.subheader("Production Trend Over the Years")
            fig = px.line(
                yearly,
                x="Year",
                y="Production",
                markers=True,
                title="Year-wise Total Crop Production"
            )
            st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Cultivated Area Trend")
                fig = px.area(
                    yearly,
                    x="Year",
                    y="Area",
                    title="Cultivated Area Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Yield Trend")
                fig = px.line(
                    yearly,
                    x="Year",
                    y="Yield",
                    markers=True,
                    title="Average Yield Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "No year column is available. Map your dataset's year "
                "column in the sidebar to view trends."
            )

        if "Rainfall" in filtered.columns:
            rainfall_data = filtered.dropna(subset=["Rainfall"])
            if not rainfall_data.empty:
                st.subheader("Rainfall Analysis")
                col1, col2 = st.columns(2)

                with col1:
                    fig = px.scatter(
                        rainfall_data,
                        x="Rainfall",
                        y="Production",
                        color="Crop",
                        title="Rainfall vs Production"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.bar(
                        rainfall_data.groupby(
                            "State", as_index=False
                        )["Rainfall"].mean(),
                        x="State",
                        y="Rainfall",
                        title="Average Rainfall by State"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Rainfall values are missing in the selected data.")
        else:
            st.info(
                "Rainfall analysis requires a numeric rainfall column. "
                "Map one in the sidebar to enable these charts."
            )

    # ---------------- DATA EXPLORER ----------------
    elif page == "Data Explorer":
        st.header("🔍 Data Explorer")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows after cleaning", f"{len(filtered):,}")
        c2.metric("Missing values before cleaning", f"{missing_before:,}")
        c3.metric("Duplicate rows before cleaning", f"{duplicates_before:,}")

        st.subheader("Filtered Dataset")
        st.dataframe(filtered, use_container_width=True)

        st.subheader("Descriptive Statistics")
        numeric_data = filtered.select_dtypes(include="number")
        if not numeric_data.empty:
            st.dataframe(
                numeric_data.describe().round(2),
                use_container_width=True
            )

            st.subheader("Distribution of Values")
            numeric_column = st.selectbox(
                "Choose a numeric column",
                numeric_data.columns.tolist()
            )
            fig = px.histogram(
                filtered,
                x=numeric_column,
                nbins=20,
                title=f"Distribution of {numeric_column}"
            )
            st.plotly_chart(fig, use_container_width=True)

            if len(numeric_data.columns) >= 2:
                st.subheader("Correlation Heatmap")
                correlation = numeric_data.corr()
                fig = px.imshow(
                    correlation,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="RdYlGn",
                    title="Correlation Between Numeric Variables"
                )
                st.plotly_chart(fig, use_container_width=True)

        csv_bytes = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Filtered Dataset (CSV)",
            data=csv_bytes,
            file_name="agriculture_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            filtered.to_excel(
                writer, index=False, sheet_name="Analysis"
            )

        st.download_button(
            "⬇️ Download Filtered Dataset (Excel)",
            data=excel_buffer.getvalue(),
            file_name="agriculture_analysis.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )

    # ---------------- PROJECT INFORMATION ----------------
    elif page == "Project Information":
        st.header("📘 About the Project")

        st.subheader("Abstract")
        st.write(
            "The Agriculture Crop Production Analysis System is a "
            "data analysis website developed to study crop production, "
            "cultivated area, yield, and agricultural trends. It uses "
            "Python, Pandas, NumPy, and Plotly to clean agricultural "
            "data, calculate summary statistics, and display interactive "
            "visualizations that help users understand crop performance."
        )

        st.subheader("Problem Statement")
        st.write(
            "Agricultural data can be difficult to compare when it is "
            "stored in large tables. This system organizes and visualizes "
            "crop data to make comparisons easier."
        )

        st.subheader("Objectives")
        st.markdown("""
        - Analyze crop production and cultivated area.
        - Compare crops and states or regions.
        - Explore yield and year-wise trends.
        - Study rainfall when rainfall data is provided.
        - Clean missing, duplicate, and inconsistent records.
        - Present results through charts, statistics, and downloads.
        """)

        st.subheader("Methodology")
        st.markdown("""
        1. Upload or load the dataset.
        2. Map the required dataset columns.
        3. Clean and preprocess the data.
        4. Apply state, crop, season, and year filters.
        5. Calculate descriptive statistics.
        6. Generate charts and interpret the results.
        7. Download the filtered analysis.
        """)

        st.subheader("Tools and Technologies")
        st.markdown("""
        - **Language:** Python
        - **Web framework:** Streamlit
        - **Data analysis:** Pandas and NumPy
        - **Visualization:** Plotly
        - **Dataset formats:** CSV and Excel
        """)

        st.subheader("Dataset Information")
        st.write(
            "Expected fields include crop name, cultivated area, "
            "production, and optional state, year, season, yield, "
            "and rainfall. Actual results depend on the uploaded dataset."
        )

# ---------------- APPLICATION ENTRY POINT ----------------
if not st.session_state.authenticated:
    authentication_page()
else:
    dashboard()
