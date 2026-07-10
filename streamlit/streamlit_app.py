import streamlit as st
import pandas as pd
import requests
from pathlib import Path


# --- Initial configuration ---
st.set_page_config(page_title="immoEliza Properties Predictive Tool", layout="wide")



# --- Paths and Constants ---------------------------------

# --- current dir ---
BASE_DIR = Path(__file__).resolve().parent

# absolute dynamic paths
MAP = BASE_DIR / "map_for_inv_app.csv"
PROV_STATS = BASE_DIR / "province_stats_for_inv_app.csv"

LOGO_PATH = BASE_DIR / "immoeliza_logo.png"


PROVINCE_POSTAL_CODES = {
        "Brussels": "1000",
        "Antwerp": "2000",
        "East Flanders": "9000",
        "Flemish Brabant": "3000",
        "Limburg": "3500",
        "West Flanders": "8000",
        "Hainaut": "7000",
        "Liège": "4000",
        "Luxembourg": "6700",
        "Namur": "5000",
        "Walloon Brabant": "1300"
    }


# --- sidebar configuration ---
st.sidebar.image(str(LOGO_PATH), use_container_width=True)
st.sidebar.title("🏠 ImmoEliza Hub")


page = st.sidebar.radio(
    "Naviga nel portale:",
    ["Buyer Analytics", "Investor Simulator"]
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
        building_year = st.number_input("Insert year of construction", min_value=1000, max_value=2099, help="A default value will be used if no value is given")
        facades = st.slider("Number of facades", min_value=1, max_value=4)
        kitchen_equipped = st.selectbox("Select level of kitchen equippment", ['Not equipped', 'Partially equipped', 'Fully equipped', 'Super equipped'])
        furnished = st.checkbox(f"{property_type} is furnished")

    with col2:
        region = st.selectbox("Select the region", ["Wallonia", "Flanders", "Brussels Capital Region"])
        province = st.selectbox("Select the province", ["Namur", "Antwerp", "Hainaut", "Limburg", "Brussels", "Walloon Brabant", "East Flanders", "Luxembourg", "West Flanders", "Liège", "Flemish Brabant"])
        postal_code = st.text_input("Post Code", value="1000", help="Insert a valid postal code")
    

    st.markdown("---")

    
    if province == "Brussels":
        region = "Brussels Capital Region"
    elif province in ["Antwerp", "Limburg", "East Flanders", "West Flanders", "Flemish Brabant"]:
        region = "Flanders"
    else:
        region = "Wallonia"
    
    # Button
    if st.button("Estimate the Price"):

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
                    st.markdown("---")
                    res_col1, res_col2 = st.columns(2)
                    res_col1.metric("Estimated Market Price", f"{prediction:,.2f} €")
                    st.success("The price estimation has been generated successfully based on local market parameters.")
                else:
                    st.error(f"API error ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Network error: {e}")

# --- INVESTOR INTERFACE ---
def render_investor_interface():
    st.header("Investments and ROI Simulator")

    df_stats, df_map = load_data_for_investor()
    
    # province selection for viewing statistics
    selected_province = st.selectbox(
        "Select the province where you intend to build or invest:",
        df_stats["province"].unique()
    )
    api_province = "Brussels" if selected_province == "Brussels Capital Region" else selected_province

    # default postal code for picked province
    selected_postal_code = PROVINCE_POSTAL_CODES.get(selected_province, "1000")

    if not selected_province:
        st.info("Select at least one province from the menu to visualize valuable market indicators.")
    else:
        # extracting data
        prov_data = df_stats[df_stats['province'] == selected_province]

        # dynamic Belgium map: filtering of df_map
        filtered_map = df_map[df_map['province'] == selected_province]

        # dynamic statistics per province: calculate data before passing them to UI
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

        # DYNAMIC BELGIUM MAP
        st.subheader(f"Real estate density map in {selected_province}")
        st.map(filtered_map)

        st.markdown("---")

        # default variables
        kitchen_equipped = "Not equipped"
        has_terrace = False
        floor_number = 0
        floors_total = 1
        garden_area_m2 = 0

        st.subheader("Configure Your Hypothetical Construction Project")

        # widgets for simulating future construction
        c1, c2 = st.columns(2)
        with c1:
            building_year = st.number_input("Expected year for construction", min_value=2026, value=2026)
            proj_type = st.radio("Select the kind of proeprty you want to build", ["House", "Apartment"])
            proj_area = st.number_input("Expected Total Project Area (m²)", min_value=50, value=200)
            has_garden = st.checkbox(f"{proj_type} has a garden")
            if has_garden:
                garden_area_m2 = st.number_input("Insert expected surface area for garden (m²)", min_value=1, max_value=1000)
            facades = st.slider("Insert number of facades", min_value=1, max_value=4, help="A default value will be used if no value is given")
            
            if proj_type == "Apartment":
                has_terrace = st.checkbox("Has terrace")
                floor_number = st.number_input("Insert number of floor", min_value=0, max_value=50, help="A default value will be used if no value is given")
                floors_total = st.number_input("Insert total floors of the building", min_value=floor_number, max_value=50, help="A default value will be used if no value is given")
                if not floors_total:
                    floors_total = floor_number
            else:
                floors_total = st.number_input("Insert total floors of the building", min_value=0, max_value=50, help="A default value will be used if no value is given")
            
            proj_type_rooms = st.slider("The number of bedrooms expected for property (a default value will be used in case no value is given)", min_value=1, max_value=10, value=1)
            final_epc_score = st.selectbox("Select the desired EPC score for the new properties", ['G', 'F', 'E-', 'E', 'E+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+', 'A++'])
        
        with c2:
            estimated_cost = st.number_input("Insert the estimated construction cost (€)", min_value=10000, value= 250000, step=5000)

        if st.button("estimate the Financial Sustainability and ROI"):
            payload = {
                "property_type": proj_type.capitalize(),
                "bedrooms": int(proj_type_rooms),
                "living_area_m2": int(proj_area),
                "total_area_m2": int(proj_area + garden_area_m2),
                "province": api_province,
                "epc_score": final_epc_score,

                # default values for API mandatory info
                "postal_code": selected_postal_code,  # default value given by selected province 1000 as fallback value

                # optional
                "state_of_the_building": "New",
                "facades": int(facades),
                "bathrooms": int(2 if proj_type == "House" else 1),
                "garden_area_m2": int(garden_area_m2),
                "total_area_m2": int(proj_area + garden_area_m2),
                "furnished": False,
                "floor_number": int(floor_number),
                "floors_total": int(floors_total),
                "kitchen_equipped": kitchen_equipped,
                "has_terrace": bool(has_terrace),
                "building_year": int(building_year),

                # region
                "region": "Brussels Capital Region" if api_province == "Brussels" else (
                    "Flanders" if api_province in ["Antwerp", "Limburg", "East Flanders", "West Flanders", "Flemish Brabant"] else "Wallonia"
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
                        st.error(f"API error ({response.status_code}): {response.text}")
                        # st.error("Unable to generate an estimate for this combination.")
                except Exception as e:
                    st.error(f"Error: {e}")


# Execute fuction associated to the selected page
if page == "Buyer Analytics":
    render_buyer_interface()
else:
    render_investor_interface()