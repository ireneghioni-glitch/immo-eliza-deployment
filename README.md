# 🏡 Immo-Eliza Predictive Tool & Market Analytics Hub Deployment 🚀

![Python](https://img.shields.io/badge/Python-3.14.5-blue)
![Sprint](https://img.shields.io/badge/Sprint-4%20🏁-brightgreen)
![Status](https://img.shields.io/badge/Status-ongoing-brightgreen)
[![BeCode](https://img.shields.io/badge/Training-BeCode-brilliantgreen?logo=becode&logoColor=white)](https://becode.org/)

- Repository: `immo-eliza-deployment`
- Type: `Learning`
- Duration: `5 days`
- Deadline: `10/07/2024 at 4:00 PM`
- Team: Solo


A production-ready, interactive Streamlit intelligence portal powered by an enterprise-grade Machine Learning backend. This application translates complex real estate data pipeline models into actionable insights, tailored for two distinct market players: **Home Buyers** and **Property Investors**.

---

## 🎯 Target Audience & Value Proposition

### 1. The Regular Home Buyer
* **The Problem:** Buying a home is one of the largest financial choices an individual makes. Buyers often struggle with information asymmetry, overpaying for properties, or failing to understand if a listed price reflects fair market value.
* **Why this portal is compelling:** It democratizes data science. By providing an intuitive, streamlined form interface, non-technical buyers can input a few property traits and instantly get a data-backed market valuation. It gives regular consumers immediate leverage during price negotiations.

### 2. The Professional Property Investor
* **The Problem:** Investors need to run quick feasibility studies across multiple provinces, assess financial viability, estimate renovation costs, and calculate exact Return on Investment (ROI) without wading through messy spreadsheets.
* **Why this portal is compelling:** It includes an advanced simulation engine. Beyond mere price prediction, it incorporates localized sub-market stats and geographical heatmaps. It automatically computes potential resale revenues, net profit margins, and ROI percentages, acting as an instantaneous automated financial analyst.

---

## ⭐ Case Study: Project Development

### Situation
The Belgian real estate market features highly fragmented data across different provinces and regions, making accurate property valuation and investment benchmarking difficult for individuals and professionals alike. The goal was to deploy a live, user-facing intelligence application that could interface with a remote machine learning model to bridge this gap.

### Task
My task was to engineer a robust, fast-loading frontend architecture using Streamlit. The application needed to support dual-mode analytics workflows (Buyer vs. Investor), dynamically render geospatial map data, handle API state management (including cold starts on deployment servers like Render), and reflect a clean, unified brand identity matching the corporate logo assets.

### Action
1.  **Engineered Dual Interfaces:** Built dedicated UI routing branches (`render_buyer_interface` and `render_investor_interface`) to separate the consumer-facing valuation form from the heavy analytical investor dashboard.
2.  **Optimized Performance & State:** Implemented Streamlit caching routines (`@st.cache_data`) to parse and load regional statistics (`province_stats_for_inv_app.csv`) and geographical coordinates (`map_for_inv_app.csv`) efficiently, cutting intra-app latency down to zero.
3.  **Custom Brand Integration:** Injected targeted CSS styling to align the application’s design system directly with the corporate brand guidelines—applying a high-contrast dark theme, custom lilla button components (`#B9A6E8`), and layout-optimized asset rendering (`use_container_width=True` for wordmarks).
4.  **Resilience Engineering:** Integrated error handles and informational logs to guide users gracefully during API cold starts (Render's 15-minute container spin-downs).

### Result
* Successfully delivered a multi-tiered, responsive data product that generates accurate market valuations in real-time.
* Achieved instantaneous sub-second prediction rendering for active server sessions.
* Maintained 100% decoupling between the visualization layer, the local geographical datasets, and the hosted predictive machine learning backend.

---

## 🛠️ Tech Stack & Architecture

* **Frontend Framework:** Streamlit (Python-native web execution)
* **Data Processing:** Pandas, Pathlib
* **Asset Management:** Pillow (PIL)
* **API Interfacing:** Requests (Communicating with a remote FastAPI/XGBoost backend)

---

## 📁 Repository Structure

```text
immo-eliza-deployment/
│
├── api/                                 # Backend Production API (FastAPI application)
│   ├── utils/                           # Data pipelines, validation, and transformations
│   │   ├── __init__.py
│   │   ├── preprocessing.py             # Feature cleaning and handling of missing inputs
│   │   ├── split_data.py                # Train/test split utility functions
│   │   └── validation.py                # Pydantic payloads type check controls
│   ├── __init__.py
│   ├── app.py                           # Core API server entrypoint orchestration
│   ├── bins_density.joblib              # Quantile threshold mappings for urban index
│   ├── density_mapping.joblib
│   ├── geo_mapping.joblib               # Geographic spatial lookup serialization
│   ├── global_medians.joblib            # Fallback values for incomplete property inputs
│   ├── ohe.joblib                       # One-Hot Encoder weights for categorical data
│   ├── ordinal.joblib                   # Ordinal encoding scales for structural states
│   ├── predict.py                       # Extracted ML scoring logic routing functions
│   ├── scaler.joblib                    # Normalization scalar arrays for numerical inputs
│   └── xgboost_model.joblib             # Core trained XGBoost regression model object
│
├── streamlit/                           # Frontend UI Application Layer
│   ├── .streamlit/                      # Native framework configuration hub
│   │   └── config.toml                  # Application theme specs (Light/Dark mode)
│   ├── immoeliza_logo.png               # High-resolution brand logo asset
│   ├── map_for_inv_app.csv              # Coordinate data for investor heatmaps
│   ├── province_stats_for_inv_app.csv   # Aggregated regional baseline statistics
│   └── streamlit_app.py                 # Main portal execution engine & UI layout
│
├── .gitignore                           # Excluded files tracking patterns list
├── Dockerfile                           # Container building assembly instructions script
├── main.py                              # Master structural framework pipeline root hook
├── README.md                            # Comprehensive project overview documentation
└── requirements.txt                     # Explicit platform-wide Python dependencies list