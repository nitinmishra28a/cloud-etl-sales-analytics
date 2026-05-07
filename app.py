import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import time
from auth.auth_system import create_user, login_user
from sqlalchemy import create_engine

# =========================================
# 1. PAGE CONFIGURATION
# =========================================
st.set_page_config(
    page_title="Cloud ETL Sales Analytics",
    page_icon="📊",
    layout="wide"
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""
# =========================================
# 2. UTILITY & CACHED FUNCTIONS
# =========================================

def load_css():
    """Loads the external CSS file for global styling."""
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("styles.css not found. Dashboard UI may look basic.")

@st.cache_data
def cached_load_csv(file):
    """Improvement: Cache the raw data loading to prevent redundant I/O."""
    return pd.read_csv(file)

def get_mysql_engine():
    """Improvement: Centralized engine creation using secure secrets."""
    try:
        user = st.secrets["DB_USER"]
        pw = st.secrets["DB_PASS"]
        host = st.secrets["DB_HOST"]
        db = st.secrets["DB_NAME"]
        return create_engine(f"mysql+mysqlconnector://{user}:{pw}@{host}/{db}")
    except KeyError as e:
        st.error(f"Secret Key Missing: {e}. Check .streamlit/secrets.toml")
        return None

# Load Global Styles
load_css()

# =========================================
# 3. SIDEBAR NAVIGATION & CONSTANTS
# =========================================
st.sidebar.title("📊 Analytics Portal")
st.sidebar.markdown("Cloud ETL Analytics System v2.0")

st.sidebar.divider()
st.sidebar.header("⚙️ Data Management")

uploaded_file = st.sidebar.file_uploader(
    "Upload Sales CSV File",
    type=["csv"]
)

# =========================================
# AUTHENTICATION SCREEN
# =========================================

if not st.session_state.logged_in:

    st.title("🔐 Cloud ETL Analytics Login")

    auth_option = st.radio(
        "Select Option",
        ["Login", "Signup"],
        horizontal=True
    )

    # =====================================
    # LOGIN
    # =====================================

    if auth_option == "Login":

        st.subheader("Login to Continue")

        login_username = st.text_input("Username")

        login_password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login_user(
                login_username,
                login_password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.username = login_username

                st.success("✅ Login Successful")

                st.rerun()

            else:

                st.error("❌ Invalid Username or Password")

    # =====================================
    # SIGNUP
    # =====================================

    else:

        st.subheader("Create New Account")

        new_username = st.text_input("Create Username")

        new_email = st.text_input("Email")

        new_password = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Signup"):

            success = create_user(
                new_username,
                new_email,
                new_password
            )

            if success:

                st.success("✅ Account Created Successfully")

            else:

                st.error("❌ Signup Failed")

    st.stop()

# =========================================
# 4. MAIN APPLICATION LOGIC
# =========================================
if uploaded_file:
    # --- STEP 1: CACHED DATA LOADING ---
    df_raw = cached_load_csv(uploaded_file)
    df = df_raw.copy()  # Use copy to keep the cache pure

    # --- STEP 2: ETL PROCESSING WITH PROGRESS BAR ---
    st.subheader("🛠️ ETL Processing Pipeline")
    progress_bar = st.progress(0)
    status_msg = st.empty()

    # ETL Stages
    status_msg.info("Running ETL: Cleaning duplicates...")
    df.drop_duplicates(inplace=True)
    progress_bar.progress(30)
    time.sleep(0.3)

    status_msg.info("Running ETL: Handling null values and formatting dates...")
    df.fillna(0, inplace=True)
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
    progress_bar.progress(60)
    time.sleep(0.3)

    status_msg.info("Running ETL: Calculating financial metrics...")
    if 'sales' in df.columns and 'cost' in df.columns:
        df['profit'] = df['sales'] - df['cost']
        df['profit_margin'] = (df['profit'] / df['sales'].replace(0, 1)) * 100
    progress_bar.progress(100)
    status_msg.success("✅ ETL Process Completed Successfully")

    # --- STEP 3: SIDEBAR FILTERS (Improved Date Filter) ---
    st.sidebar.divider()
    st.sidebar.header("📌 Global Filters")
    st.sidebar.divider()

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()

    # Real Date Range Filter
    if 'order_date' in df.columns:
        min_date = df['order_date'].min().date()
        max_date = df['order_date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['order_date'].dt.date >= start_date) & (df['order_date'].dt.date <= end_date)]

    # Categorical Filters
    if 'region' in df.columns:
        selected_regions = st.sidebar.multiselect("Select Region", options=df['region'].unique(), default=df['region'].unique())
        df = df[df['region'].isin(selected_regions)]

    if 'product' in df.columns:
        selected_products = st.sidebar.multiselect("Select Product", options=df['product'].unique(), default=df['product'].unique())
        df = df[df['product'].isin(selected_products)]

    # --- STEP 4: CALCULATE METRICS ---
    total_revenue = df['sales'].sum() if 'sales' in df.columns else 0
    total_profit = df['profit'].sum() if 'profit' in df.columns else 0
    total_orders = len(df)
    avg_margin = df['profit_margin'].mean() if 'profit_margin' in df.columns else 0

    # SIDEBAR METRICS (Improvement 6)
    st.sidebar.divider()
    st.sidebar.subheader("Quick Insights")
    st.sidebar.metric("Filtered Revenue", f"₹ {total_revenue:,.0f}")
    st.sidebar.metric("Filtered Orders", f"{total_orders:,}")
    st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

    # --- STEP 5: DASHBOARD UI ---
    st.title("📊 Sales Analytics Dashboard")
    st.subheader("📈 Business Performance Overview")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Total Revenue", f"₹ {total_revenue:,.0f}")
    kpi2.metric("📊 Total Profit", f"₹ {total_profit:,.0f}")
    kpi3.metric("🛒 Total Orders", f"{total_orders:,}")
    kpi4.metric("📌 Avg Margin", f"{avg_margin:.2f}%")

    st.divider()

    # --- STEP 6: DATA PREVIEW & MYSQL SYNC ---
    with st.expander("🔍 Inspect Processed Data"):
        st.dataframe(df.head(50), use_container_width=True)

    if st.sidebar.button("🚀 Load Data into MySQL"):
        engine = get_mysql_engine()
        if engine:
            try:
                # Improvement: Using 'replace' for clean testing, can be changed to 'append'
                df.to_sql("sales_data", con=engine, if_exists="replace", index=False)
                st.sidebar.success("✅ MySQL Data Sync Complete!")
            except Exception as e:
                st.sidebar.error(f"❌ Database Sync Failed: {e}")

    # --- STEP 7: CHARTS (Improved Professional Themes) ---
    st.subheader("📊 Visual Analytics")
    
    # Monthly Sales Trend (Using pd.Grouper)
    if 'order_date' in df.columns:
        st.write("#### 📅 Monthly Revenue Trend")
        monthly_sales = df.groupby(pd.Grouper(key='order_date', freq='M'))['sales'].sum().reset_index()
        fig_line = px.line(monthly_sales, x='order_date', y='sales', markers=True)
        fig_line.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_line, use_container_width=True)

    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if 'region' in df.columns:
            st.write("#### 🌍 Sales by Region")
            region_sales = df.groupby('region')['sales'].sum().reset_index()
            fig_region = px.bar(region_sales, x='region', y='sales', color='sales', color_continuous_scale='Blues')
            fig_region.update_layout(template="plotly_dark")
            st.plotly_chart(fig_region, use_container_width=True)

    with chart_col2:
        if 'product' in df.columns:
            st.write("#### 🏆 Top 10 Products")
            product_sales = df.groupby('product')['sales'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_product = px.bar(product_sales, x='product', y='sales', color='product')
            fig_product.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig_product, use_container_width=True)
            
        # =====================================
    # LIVE DATABASE VIEWER
    # =====================================

    st.divider()

    st.subheader("🗄️ Live Database Viewer")

    engine = get_mysql_engine()

    if engine:

        try:

            # Load Database Data
            db_query = """
            SELECT *
            FROM sales_data
            """

            db_df = pd.read_sql(
                db_query,
                engine
            )

            # Database Stats
            db_col1, db_col2, db_col3 = st.columns(3)

            db_col1.metric(
                "Total Database Rows",
                f"{len(db_df):,}"
            )

            db_col2.metric(
                "Total Columns",
                f"{len(db_df.columns)}"
            )

            db_col3.metric(
                "Database Status",
                "Connected"
            )

            st.markdown("---")

            # Search Box
            search_term = st.text_input(
                "🔍 Search Product"
            )

            if search_term:

                if 'product' in db_df.columns:

                    db_df = db_df[
                        db_df['product']
                        .astype(str)
                        .str.contains(
                            search_term,
                            case=False
                        )
                    ]

            # Region Filter
            if 'region' in db_df.columns:

                selected_region_db = st.selectbox(
                    "Filter by Region",
                    ["All"] + list(
                        db_df['region']
                        .unique()
                    )
                )

                if selected_region_db != "All":

                    db_df = db_df[
                        db_df['region']
                        == selected_region_db
                    ]

            # Show Database Table
            st.dataframe(
                db_df,
                use_container_width=True,
                height=400
            )

            # Row Count
            st.success(
                f"Showing {len(db_df):,} records"
            )

        except Exception as e:

            st.error(
                f"Database Viewer Error: {e}"
            )
            
        # =====================================
    # SALES FORECASTING MODULE
    # =====================================

    st.divider()

    st.subheader("🔮 Sales Forecasting")

    try:

        from prophet import Prophet

        # Prepare Monthly Data
        forecast_df = (
            df.groupby(
                pd.Grouper(
                    key='order_date',
                    freq='M'
                )
            )['sales']
            .sum()
            .reset_index()
        )

        # Prophet Format
        forecast_df.columns = ['ds', 'y']

        # Create Model
        model = Prophet()

        model.fit(forecast_df)

        # Future Dates
        future = model.make_future_dataframe(
            periods=6,
            freq='M'
        )

        # Predictions
        forecast = model.predict(future)

        # Show Forecast Data
        st.write("### 📈 Future Sales Forecast")

        forecast_chart = px.line(
            forecast,
            x='ds',
            y='yhat',
            title='Predicted Future Revenue'
        )

        forecast_chart.update_layout(
            template='plotly_dark',
            height=500
        )

        st.plotly_chart(
            forecast_chart,
            use_container_width=True
        )

        # Show Forecast Table
        with st.expander("📋 Forecast Data"):

            st.dataframe(
                forecast[
                    ['ds', 'yhat']
                ].tail(6),
                use_container_width=True
            )

        st.success(
            "✅ Forecast generated successfully"
        )

    except Exception as e:

        st.error(
            f"Forecasting Error: {e}"
        )

    # --- STEP 8: DOWNLOAD & STATUS ---
    st.divider()
    st.subheader("⬇️ Export & System Health")
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Processed Report",
        data=csv_data,
        file_name='processed_sales_data.csv',
        mime='text/csv'
    )

    st.markdown("### ⚙️ System Status")
    status_c1, status_c2, status_c3 = st.columns(3)
    status_c1.success("✅ ETL Pipeline Active")
    status_c2.success("✅ MySQL Secrets Secure")
    status_c3.success("✅ Data Cache Enabled")

# =========================================
# 5. DEFAULT SCREEN
# =========================================
else:
    st.info("""
    👋 Welcome! Please upload a Sales CSV file in the sidebar to begin.
    
    The system will automatically:
    - Perform ETL Cleaning & Deduplication
    - Calculate Profits & Margins
    - Visualize Regional & Product Trends
    - Allow MySQL Cloud Sync
    """)

# =========================================
# 6. FOOTER
# =========================================
st.markdown("---")
st.caption("Cloud ETL Sales Analytics System | Python • MySQL • Streamlit • Plotly")