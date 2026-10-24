
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Agriculture Crop Analysis",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Agriculture Crop Production Analysis System")
st.write(
    "Explore crop production, cultivated area, "
    "yield, and yearly agricultural trends."
)

st.sidebar.header("Dataset")
uploaded_file = st.sidebar.file_uploader(
    "Upload your agriculture CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip().lower() for c in df.columns]

    aliases = {
        "state/region": "state",
        "region": "state",
        "crop name": "crop",
        "crop_name": "crop",
        "year": "year",
        "area cultivated": "area",
        "area cultivated (ha)": "area",
        "area": "area",
        "production": "production",
        "yield": "yield",
        "season": "season"
    }

    df = df.rename(
        columns={c: aliases[c] for c in df.columns if c in aliases}
    )

    required = ["state", "crop", "year", "area", "production"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(
            "Missing columns: " + ", ".join(missing)
            + ". Please check your CSV column names."
        )
        st.stop()

    for col in ["year", "area", "production"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required).copy()
    if "season" not in df.columns:
        df["season"] = "Not specified"

    if "yield" not in df.columns:
        df["yield"] = (
            df["production"] / df["area"].replace(0, float("nan"))
        )

    df = df.dropna(subset=["year", "area", "production"])
    st.success("Your uploaded dataset is loaded.")

else:
    # Illustrative demo data, not official statistics
    states = ["Andhra Pradesh", "Telangana", "Karnataka",
              "Tamil Nadu"]
    crops = ["Rice", "Wheat", "Maize", "Cotton"]
    records = []

    for si, state in enumerate(states):
        for ci, crop in enumerate(crops):
            for year in range(2020, 2026):
                area = 1000 + si * 180 + ci * 120 + (year - 2020) * 25
                production = area * (
                    2.0 + ci * 0.35 + si * 0.12
                    + (year - 2020) * 0.04
                )
                records.append({
                    "state": state,
                    "crop": crop,
                    "year": year,
                    "area": area,
                    "production": round(production, 2),
                    "yield": round(production / area, 2),
                    "season": "Demo"
                })

    df = pd.DataFrame(records)
    st.info(
        "You are viewing illustrative sample data. "
        "Upload your actual dataset for real project results."
    )

df["state"] = df["state"].astype(str)
df["crop"] = df["crop"].astype(str)

st.sidebar.header("Filters")
state_options = sorted(df["state"].unique())
crop_options = sorted(df["crop"].unique())

selected_states = st.sidebar.multiselect(
    "Select states", state_options, default=state_options
)
selected_crops = st.sidebar.multiselect(
    "Select crops", crop_options, default=crop_options
)

years = sorted(df["year"].dropna().astype(int).unique())
selected_years = st.sidebar.multiselect(
    "Select years", years, default=years
)

filtered = df[
    df["state"].isin(selected_states)
    & df["crop"].isin(selected_crops)
    & df["year"].isin(selected_years)
]

if filtered.empty:
    st.warning("No records match these filters. Please change them.")
    st.stop()

total_area = filtered["area"].sum()
total_production = filtered["production"].sum()
average_yield = (
    total_production / total_area if total_area else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Production", f"{total_production:,.2f}")
c2.metric("Cultivated Area", f"{total_area:,.2f}")
c3.metric("Average Yield", f"{average_yield:,.2f}")
c4.metric("Crop Types", filtered["crop"].nunique())

st.subheader("Yearly Production Trend")
yearly = filtered.groupby("year", as_index=False)["production"].sum()
fig1 = px.line(
    yearly, x="year", y="production", markers=True,
    title="Total Crop Production by Year"
)
st.plotly_chart(fig1, use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("Production by Crop")
    crop_data = filtered.groupby(
        "crop", as_index=False
    )["production"].sum()
    fig2 = px.bar(
        crop_data, x="crop", y="production",
        color="crop", title="Crop-wise Production"
    )
    st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader("Production by State")
    state_data = filtered.groupby(
        "state", as_index=False
    )["production"].sum()
    fig3 = px.bar(
        state_data, x="state", y="production",
        title="State-wise Production"
    )
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Agriculture Dataset")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "Download Filtered Data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_agriculture_data.csv",
    mime="text/csv"
)

st.caption(
    "Note: Results depend on the dataset uploaded. "
    "Check units and data sources before interpreting results."
)
