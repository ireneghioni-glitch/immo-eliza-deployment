import streamlit as st
import pandas as pd
import requests
from pathlib import Path


# --- Initial configuration ---
st.set_page_config(page_title="immoEliza Properties Predictive Tool", layout="wide")


# --- Paths ------------------------------------------

# --- current dir ---
BASE_DIR = Path(__file__).resolve().parent

# absolute dynamic paths
MAP = BASE_DIR / "map_for_inv_app.csv"
PROV_STATS = BASE_DIR / "province_stats_for_inv_app.csv"

# --- sidebar configuration ---
# st.sidebar.imag("immoeliza_logo")
st.sidebar.title("🏠 ImmoEliza Hub")
st.sidebar.markdown("---")

# type of user choice
user = st.sidebar.radio(
    label="Select relatively to the objective of the analysis:",
    options=["Buyer", "Investor"]
)

st.sidebar.markdown("---")

# --- loading data ---
@st.cache_data
def load_data_for_buyer():
    df_stats = pd.read_csv(PROV_STATS)
    return df_stats

@st.cache_data
def load_data_for_investor():
    df_stats = pd.read_csv(PROV_STATS)
    df_map = pd.read_csv(MAP)
    return df_stats, df_map


# --- BUYER INTERFACE ---
def render_buyer_interface():
    st.header("Verify Market Value of a Property")
    st.subheader("Insert details about the property you are considering to buy")

    # default variables
    garden_area_mq = 0
    floor_number = 0
    floors_total = 0
    total_area_m2 = 0
    kitchen_equipped = "Not equipped"
    
    # organization of inputs in 2 columns
    col1, col2 = st.columns(2)

    # property characteristics
    with col1:
        property_type = st.radio("Kind of property", ["House", "Apartment"])
        if property_type == "Apartment":
            floor_number = st.number_input("Property Floor", min_value=0, max_value=50, help="Insert the floor number")
            floors_total = st.number_input("Total Floors", min_value=1, max_value=50, help="Insert total floors number of the building")
            if not floors_total:
                floors_total = floor_number
        living_area_m2 = st.number_input("Habitable floor area (m²)", min_value=1)
        bedrooms = st.slider("Number of bedrooms", min_value=1, max_value=10, value=1)
        bathrooms = st.slider("Number of bathrooms", min_value=1, max_value=5, value=1)
        has_terrace = st.checkbox("Has terrace")
        has_garden = st.checkbox("Has garden")
        if has_garden:
            garden_area_mq = st.number_input("Garden area (m²)", min_value=1)
        # calculate default total area for total_area_m2
        default_total_area = living_area_m2 + garden_area_mq if has_garden else living_area_m2
        total_area_m2 = st.number_input("Total area of property (m²)", min_value=living_area_m2, value=default_total_area)
        epc_score = st.selectbox("Select the EPC score", ['G', 'F', 'E-', 'E', 'E+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+', 'A++'])
        state_of_the_building = st.selectbox("Select the state of the property", ['New', 'under construction', 'Fully renovated', 'Normal', 'To renovate', 'To restore', 'To demolish'])
        building_year = st.number_input("Insert year of construction", min_value=1000, max_value=2099)
        facades = st.slider("Number of facades", min_value=1, max_value=4)
        kitchen_equipped = st.selectbox("Select level of kitchen equippment", ['Not equipped', 'Partially equipped', 'Fully equipped', 'Super equipped'])
        furnished = st.checkbox(f"{property_type} is furnished")

    with col2:
        region = st.selectbox("Select the region", ["Wallonia", "Flanders", "Brussels Capital Region"])
        province = st.selectbox("Select the province", ["Namur", "Antwerp", "Hainaut", "Limburg", "Brussels", "Walloon Brabant", "East Flanders", "Luxembourg", "West Flanders", "Liège", "Flemish Brabant"])
        postal_code = st.text_input("Post Code", "Insert a valid postal code")
    

    st.markdown("---")

    
    if province == "Brussels":
        region = "Brussels Capital Region"
    elif province in ["Antwerp", "Limburg", "East Flanders", "West Flanders", "Flemish Brabant"]:
        region = "Flanders"
    else:
        region = "Wallonia"
    
    # Button
    if st.button("Estimate the Price", use_container_width=True):

        payload= {
            "property_type": property_type.capitalize(),
            "living_area_m2": living_area_m2,
            "bedrooms": bedrooms,
            "epc_score": epc_score,
            "postal_code": postal_code,

            # optional
            "state_of_the_building": state_of_the_building,
            "facades": 4 if property_type == "House" else facades,
            "bathrooms": bathrooms if bathrooms else (2 if property_type == "House" else 1),
            "garden_area_m2": garden_area_mq,
            "furnished": furnished,
            "floor_number": floor_number if property_type == "Apartment" else 0,
            "floors_total": floors_total if floors_total != 0 else floor_number,
            "total_area_m2": int(total_area_m2),
            "kitchen_equipped": kitchen_equipped,
            "has_terrace": has_terrace,
            "has_garden": has_garden,
            "building_year": building_year if building_year else 2000,

            # province and region
            "province": province,
            "region": region
        }

        with st.spinner("We are querying the ImmoEliza servers..."):
            try:
                st.write("DEBUG PAYLOAD:", payload)
                response = requests.post("https://immo-eliza-api-n2lj.onrender.com", json=payload)
                if response.status_code == 200:
                    prediction = response.json().get("prediction", 0)
                    st.success(f"Estimated Market price for this property is {prediction:,.2f} €")
                else:
                    st.error(f"API error ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Network error: {e}")

# --- INVESTOR INTERFACE ---
def render_investor_interface():
    st.header("Investments and ROI Simulator")

    # default variables
    facades = 1
    floor_number = 0
    floors_total = 0
    garden_area_m2 = 0.0

    df_stats, df_map = load_data_for_investor()
    
    # province selection for viewing statistics
    selected_province = st.selectbox(
        "Select the province where you intend to build or invest:",
        df_stats["province"].unique()
    )

    if not selected_province:
        st.info("Select at least one province from the menu to visualize valuable market indicators.")
    else:
        # extracting data
        prov_data = df_stats[df_stats['province'] == selected_province]

        # Scalar Aggregation: calculate data before passing them to UI
        avg_price = float(prov_data['mean_price_mq'].mean())
        avg_density = float(prov_data['mean_urban_density'].mean())
        total_properties = int(prov_data['properties_total'].sum())
        avg_green = float(prov_data['green_properties_ratio'].mean())

        # metrics viz
        st.subheader(f"Current Market Indicators for {selected_province}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            label="Mean Price per m²", 
            value=f"{avg_price:.2f} €/m²"
            )
        m2.metric(
            label="Urban Density Index (Mean)", 
            value=f"{avg_density:.1f}"
        )
        m3.metric(
            label="Active Listing Volume",
            value=f"{total_properties:,}".replace(",", ".")
        )
        m4.metric(
            label="Green Real Estate Share (A/B)",
            value=f"{avg_green:.1f} %",
            help="Percentage of properties in the province with an energy efficiency rating between A++ and B-"
        )
    
        st.markdown("---")

        # MAP
        st.subheader(f"Real estate density map in {selected_province}")
        st.map(df_map)

        st.markdown("---")

        st.subheader("Configure Your Hypothetical Construction Project")

        # widgets for simulating future construction
        c1, c2 = st.columns(2)
        with c1:
            proj_type = st.radio("Select the kind of proeprty you want to build", ["House", "Apartment"])
            proj_area = st.number_input("Expected Total Project Area (m²)", min_value=50, value=200)
            if proj_type == "Apartment":
                facades = st.slider("Insert number of facades (a default value will be used if no value is given)", min_value=1, max_value=4)
                floor_number = st.number_input("Insert number of floor (a default value will be used if no value is given)", min_value=0, max_value=50)
                floors_total = st.number_input("Insert number of floor (a default value will be used if no value is given)", min_value=0, max_value=50)
                if not floors_total:
                    floors_total = floor_number
            else:
                has_garden = st.checkbox(f"{proj_type} has a garden")
                if has_garden:
                    garden_area_m2 = st.number_input("Insert expected surface area for garden (m²)", min_value=1, max_value=1000)
            proj_type_rooms = st.slider("The number of bedrooms expected for property (a default value will be used in case no value is given)", min_value=1, max_value=10, value=1)
            if not proj_type_rooms:
                proj_type_rooms = 3 if proj_type == "House" else 2
            final_epc_score = st.selectbox("Select the desired EPC score for the new properties", ['G', 'F', 'E-', 'E', 'E+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+', 'A++'])
        with c2:
            estimated_cost = st.number_input("Insert the estimated construction cost (€)", min_value=10000, value= 250000, step=5000)

        if st.button("estimate the Financial Sustainability and ROI", use_container_width=True):
            payload = {
                "property_type": proj_type.capitalize(),
                "bedrooms": proj_type_rooms,
                "living_area_m2": int(proj_area),
                "province": selected_province,
                "epc_score": final_epc_score,

                # default values for API mandatory info
                "postal_code": "1000",  # fallback value

                # optional
                "state_of_the_building": "New",
                "facades": 4 if proj_type == "House" else facades,
                "bathrooms": 2 if proj_type == "House" else 1,
                "garden_area_m2": garden_area_m2,
                "living_area_m2": int(proj_area + garden_area_m2),
                "furnished": False,
                "floor_number": 1 if proj_type == "Apartment" else None,

                # region
                "region": "Brussels Capital Region" if selected_province == "Brussels" else (
                "Flanders" if selected_province in ["Antwerp", "Limburg", "East Flanders", "West Flanders", "Flemish Brabant"] else "Wallonia"
                )

            }

            with st.spinner("We are calculating the future resale value..."):
                try:
                    response = requests.post("https://immo-eliza-api-n2lj.onrender.com", json=payload)
                    if response.status_code == 200:
                        predicted_revenue = response.json().get("prediction", 0)
                        net_profit = predicted_revenue - estimated_cost
                        roi = (net_profit / estimated_cost) * 100

                        st.markdown("---")
                        res_col1, res_col2 = st.columns(2)
                        res_col1.metric("Estimated Sale Value (Revenue)", f"{predicted_revenue:,.2f} €")
                        if net_profit > 0:
                            st.success(f"Estimated Profit: {net_profit:,.2f} € (ROI: {roi:.1f}%)")
                        else:
                            st.error(f"Financial Loss Risk: {net_profit:,.2f} € (ROI: {roi:.1f}%)")
                    else:
                        st.error("Unable to generate an estimate for this combination.")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- Interface Routing Activation ---
if "Buyer" in user:
    render_buyer_interface()
else:
    render_investor_interface()