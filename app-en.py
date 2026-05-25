import pandas as pd
import requests
import streamlit as st
import plotly.express as px

# ==========================================
# PART 1: DATA EXTRACTION & TRANSFORMATION (ETL)
# ==========================================
@st.cache_data
def load_data():
    # 1. Read Master Data
    try:
        master_df = pd.read_csv('RFID_Data-Analyst_Case-Study-Test/data/master_data.csv')
    except FileNotFoundError:
        master_df = pd.read_csv('master_data.csv')
    
    # 2. Fetch Defect Records via API
    api_url = "https://raw.githubusercontent.com/phongtdt/RFID_Data-Analyst_Case-Study-Test/main/mock-api/defect_records.json"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        defect_df = pd.DataFrame(response.json())
    else:
        st.error("API Connection Failed! Please check your network.")
        return None
        
    # 3. Merge DataFrames
    df = pd.merge(defect_df, master_df, on='product_id', how='left')
    
    # 4. Data Cleansing & Formatting
    df['defect_date'] = pd.to_datetime(df['defect_date'], format='mixed')
    
    # Standardize 'severity' column to Title Case to fix heatmap duplicates
    df['severity'] = df['severity'].str.title()
    
    df = df.sort_values('defect_date')
    return df

# ==========================================
# PART 2: MAIN DASHBOARD APPLICATION
# ==========================================
def main():
    st.set_page_config(page_title="Factory Defect Dashboard", layout="wide", page_icon="🏭")
    
    st.title("🏭 Production Defect Analysis Dashboard")
    st.markdown("Quality monitoring for 4 production lines [Classification: Avery Dennison - Internal]")
    st.markdown("---")
    
    # 1. FETCH RAW DATA (Includes 2026 outliers for Validation purposes)
    df_raw = load_data()
    if df_raw is None:
        return

    # 2. FILTER BUSINESS TIMEFRAME (Jan-Jun 2024 for Charts & Insights)
    mask = (df_raw['defect_date'] >= '2024-01-01') & (df_raw['defect_date'] <= '2024-06-30')
    df_filtered = df_raw.loc[mask]

    # INITIALIZE 3 MAIN TABS
    tab1, tab2, tab3 = st.tabs([
        "📊 Analytics Dashboard", 
        "🛡️ Data Quality Validation", 
        "🤖 AI Auto-Insights"
    ])

    # ------------------------------------------
    # TAB 1: DASHBOARD (Uses df_filtered)
    # ------------------------------------------
    with tab1:
        st.subheader("1. Quality Overview (KPIs - H1 2024)")
        col1, col2, col3, col4 = st.columns(4)
        
        total_defects = len(df_filtered)
        total_cost = df_filtered['repair_cost'].sum()
        worst_line = df_filtered['production_line'].value_counts().idxmax()
        critical_defects = len(df_filtered[df_filtered['severity'] == 'Critical'])

        col1.metric("Total Defects", f"{total_defects:,}")
        col2.metric("Total Repair Cost", f"${total_cost:,.2f}")
        col3.metric("Worst Performing Line", worst_line)
        col4.metric("Critical Defects", f"{critical_defects:,}")
        st.markdown("---")

        st.subheader("2. Defect Volume Trend over Time")
        daily_defects = df_filtered.groupby(df_filtered['defect_date'].dt.date).size().reset_index(name='defect_count')
        fig_trend = px.line(
            daily_defects, x='defect_date', y='defect_count', 
            markers=True, labels={'defect_date': 'Date', 'defect_count': 'Defect Count'}
        )
        fig_trend.add_hline(y=daily_defects['defect_count'].mean(), line_dash="dot", 
                            annotation_text="Avg Defects/Day", annotation_position="bottom right")
        st.plotly_chart(fig_trend, use_container_width=True)

        st.subheader("3. Defect Distribution by Line & Category")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_line = px.bar(df_filtered['production_line'].value_counts().reset_index(name='count'), 
                              x='production_line', y='count', color='production_line', text_auto=True,
                              title="By Production Line")
            st.plotly_chart(fig_line, use_container_width=True)
        with col_chart2:
            fig_category = px.bar(df_filtered['category'].value_counts().reset_index(name='count'), 
                                  x='category', y='count', color='category', text_auto=True,
                                  title="By Product Category")
            st.plotly_chart(fig_category, use_container_width=True)

        st.subheader("4. Defect Location vs. Severity (Heatmap)")
        location_severity = pd.crosstab(df_filtered['defect_location'], df_filtered['severity'])
        fig_heatmap = px.imshow(
            location_severity, text_auto=True, aspect="auto", color_continuous_scale="Reds",
            labels=dict(x="Severity Level", y="Defect Location", color="Defect Count")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("5. Export Consolidated Data")
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Clean Data (CSV)", data=csv, file_name='consolidated_defect_records.csv', mime='text/csv')

    # ------------------------------------------
    # TAB 2: DATA VALIDATION (Uses df_raw to catch errors)
    # ------------------------------------------
    with tab2:
        st.subheader("Data Integrity & Validation Report")
        st.markdown("The automated system verifies data integrity and isolates anomalies before extracting insights.")

        missing_master = df_raw['category'].isnull().sum()
        if missing_master == 0:
            st.success("✅ 1. Join Integrity: 100% of API defect records successfully mapped to Master Data.")
        else:
            st.error(f"❌ 1. Warning: {missing_master} defect records are missing Master Data references!")

        negative_cost = len(df_raw[df_raw['repair_cost'] < 0])
        if negative_cost == 0:
            st.success("✅ 2. Cost Logic: No negative repair costs detected in the dataset.")
        else:
            st.error(f"❌ 2. Warning: Detected {negative_cost} records with negative repair costs!")

        st.markdown("---")
        st.markdown("### 🔍 Business Time-frame Trap Validation")
        
        # Catch records outside the Jan-Jun 2024 requirement
        outliers_df = df_raw[~df_raw.index.isin(df_filtered.index)]
        outliers_count = len(outliers_df)
        
        if outliers_count == 0:
            st.success("✅ 100% of data falls strictly within the requested timeframe (Jan-Jun 2024).")
        else:
            st.warning(f"⚠️ **OUTLIERS DETECTED:** The API returned **{outliers_count} records** outside the requested business timeframe (Jan - Jun 2024).")
            st.write("Details of the out-of-bounds records (Year 2026):")
            st.dataframe(outliers_df[['defect_date', 'production_line', 'category', 'severity']], use_container_width=True)
            st.info("💡 **System Action:** These noisy records have been automatically isolated from Tab 1 and Tab 3 calculations to prevent KPI distortion.")

    # ------------------------------------------
    # TAB 3: AUTO-INSIGHTS (Uses df_filtered)
    # ------------------------------------------
    with tab3:
        st.subheader("🤖 Automated Data Analysis System")
        st.markdown("Algorithmic extraction of operational bottlenecks and hotspot patterns.")
        st.markdown("---")
        
        # 1. TREND ANALYSIS
        st.markdown("### 📈 1. Trend Analysis (Jan-Jun 2024)")
        df_filtered_copy = df_filtered.copy()
        df_filtered_copy['month'] = df_filtered_copy['defect_date'].dt.to_period('M')
        monthly_trend = df_filtered_copy.groupby('month').size().reset_index(name='count')
        
        first_m = monthly_trend.iloc[0]
        last_m = monthly_trend.iloc[-1]
        
        if last_m['count'] < first_m['count']:
            st.success(f"**📉 Auto-evaluation: DECREASING (Positive Signal)**\nProduction is stabilizing. The final month saw a reduction of {first_m['count'] - last_m['count']} defects compared to the start of the period.")
        else:
            st.error(f"**📈 Auto-evaluation: INCREASING (Negative Signal)**\nThe system recorded an overall increase and high volatility in defect volume towards the end of H1. Frequent spikes exceeding the daily average suggest equipment wear or process deviations.")

        # 2. LOCATION & SEVERITY
        st.markdown("### 🔍 2. Defect Location & Severity Risk")
        critical_df = df_filtered[df_filtered['severity'] == 'Critical']
        if not critical_df.empty:
            worst_location = critical_df['defect_location'].value_counts().idxmax()
            worst_loc_count = critical_df['defect_location'].value_counts().max()
            
            st.warning(f"**Critical Hotspot:** The **'{worst_location}'** location is recording the highest frequency of 'Critical' defects across the factory with **{worst_loc_count} cases**.")
            st.info(f"**💡 Recommendation:** Shift QC resources and apply technical measurement methods (e.g., deep learning-based automated visual inspection) to the '{worst_location}' assembly stage instead of relying purely on visual surface checks.")

        # 3. BOTTLENECKS
        st.markdown("### 🧩 3. Bottleneck Pattern Recognition")
        pattern_df = df_filtered.groupby(['production_line', 'category']).size().reset_index(name='count')
        worst_pattern = pattern_df.loc[pattern_df['count'].idxmax()]
        
        worst_line = worst_pattern['production_line']
        worst_cat = worst_pattern['category']
        bottleneck_cost = df_filtered[(df_filtered['production_line'] == worst_line) & (df_filtered['category'] == worst_cat)]['repair_cost'].sum()
        
        st.error(f"**System Bottleneck:** The combination of **{worst_line}** running **{worst_cat}** generates the highest defect volume (**{worst_pattern['count']} defects**).")
        st.markdown(f"> **Financial Impact:** This specific vulnerability alone accounts for **${bottleneck_cost:,.2f}** in repair costs.")
        st.info("**💡 Recommendation:** Immediately audit the technical compatibility and equipment calibration on this line when processing this specific product category.")

if __name__ == "__main__":
    main()