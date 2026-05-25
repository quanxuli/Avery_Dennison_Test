import pandas as pd
import requests
import streamlit as st
import plotly.express as px

# ==========================================
# PHẦN 1: KẾT NỐI VÀ XỬ LÝ DỮ LIỆU (ETL)
# ==========================================
@st.cache_data
def load_data():
    # 1. Đọc Master Data
    try:
        master_df = pd.read_csv('RFID_Data-Analyst_Case-Study-Test/data/master_data.csv')
    except FileNotFoundError:
        master_df = pd.read_csv('master_data.csv')
    
    # 2. Gọi API lấy Defect Records
    api_url = "https://raw.githubusercontent.com/phongtdt/RFID_Data-Analyst_Case-Study-Test/main/mock-api/defect_records.json"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        defect_df = pd.DataFrame(response.json())
    else:
        st.error("Lỗi khi gọi API! Vui lòng kiểm tra lại kết nối mạng.")
        return None
        
    # 3. Merge dữ liệu
    df = pd.merge(defect_df, master_df, on='product_id', how='left')
    
    # 4. Làm sạch & Format dữ liệu
    df['defect_date'] = pd.to_datetime(df['defect_date'], format='mixed')
    
    # Sửa lỗi Heatmap: Chuẩn hóa cột severity (Gộp 'critical' và 'Critical', 'minor' và 'Minor')
    df['severity'] = df['severity'].str.title()
    
    df = df.sort_values('defect_date')
    return df

# ==========================================
# PHẦN 2: GIAO DIỆN CHÍNH (MAIN APP)
# ==========================================
def main():
    st.set_page_config(page_title="Factory Defect Dashboard", layout="wide", page_icon="🏭")
    
    st.title("🏭 Dashboard Phân Tích Lỗi Sản Xuất")
    st.markdown("Phục vụ giám sát chất lượng cho 4 dây chuyền sản xuất [Phiên bản: Avery Dennison - Internal]")
    st.markdown("---")
    
    # 1. LẤY DỮ LIỆU THÔ (Chứa cả rác 2026 để làm Validation)
    df_raw = load_data()
    if df_raw is None:
        return

    # 2. LỌC DỮ LIỆU CHUẨN KINH DOANH (Chỉ lấy Jan-Jun 2024 để vẽ Biểu đồ & Insight)
    mask = (df_raw['defect_date'] >= '2024-01-01') & (df_raw['defect_date'] <= '2024-06-30')
    df_filtered = df_raw.loc[mask]

    # KHỞI TẠO 3 TABS CHÍNH
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard Phân Tích", 
        "🛡️ Báo cáo Chất lượng Dữ liệu", 
        "🤖 AI Tự động Phân tích (Insights)"
    ])

    # ------------------------------------------
    # TAB 1: DASHBOARD (Dùng df_filtered)
    # ------------------------------------------
    with tab1:
        st.subheader("1. Tổng quan chỉ số chất lượng (KPIs - Nửa đầu năm 2024)")
        col1, col2, col3, col4 = st.columns(4)
        
        total_defects = len(df_filtered)
        total_cost = df_filtered['repair_cost'].sum()
        worst_line = df_filtered['production_line'].value_counts().idxmax()
        critical_defects = len(df_filtered[df_filtered['severity'] == 'Critical'])

        col1.metric("Tổng số lỗi phát sinh", f"{total_defects:,}")
        col2.metric("Tổng chi phí sửa chữa", f"${total_cost:,.2f}")
        col3.metric("Dây chuyền lỗi nhiều nhất", worst_line)
        col4.metric("Số lỗi mức độ Critical", f"{critical_defects:,}")
        st.markdown("---")

        st.subheader("2. Biến động số lượng lỗi theo thời gian")
        daily_defects = df_filtered.groupby(df_filtered['defect_date'].dt.date).size().reset_index(name='defect_count')
        fig_trend = px.line(
            daily_defects, x='defect_date', y='defect_count', 
            markers=True, labels={'defect_date': 'Ngày', 'defect_count': 'Số lượng lỗi'}
        )
        fig_trend.add_hline(y=daily_defects['defect_count'].mean(), line_dash="dot", 
                            annotation_text="Trung bình lỗi/ngày", annotation_position="bottom right")
        st.plotly_chart(fig_trend, use_container_width=True)

        st.subheader("3. Phân bổ lỗi theo Dây chuyền & Danh mục")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_line = px.bar(df_filtered['production_line'].value_counts().reset_index(name='count'), 
                              x='production_line', y='count', color='production_line', text_auto=True)
            st.plotly_chart(fig_line, use_container_width=True)
        with col_chart2:
            fig_category = px.bar(df_filtered['category'].value_counts().reset_index(name='count'), 
                                  x='category', y='count', color='category', text_auto=True)
            st.plotly_chart(fig_category, use_container_width=True)

        st.subheader("4. Ma trận Vị trí và Độ nghiêm trọng (Heatmap)")
        location_severity = pd.crosstab(df_filtered['defect_location'], df_filtered['severity'])
        fig_heatmap = px.imshow(
            location_severity, text_auto=True, aspect="auto", color_continuous_scale="Reds",
            labels=dict(x="Độ nghiêm trọng", y="Vị trí lỗi", color="Số lượng")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("5. Xuất Dữ liệu Báo cáo")
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Tải xuống Dữ liệu sạch (CSV)", data=csv, file_name='consolidated_defect_records.csv', mime='text/csv')

    # ------------------------------------------
    # TAB 2: DATA VALIDATION (Dùng df_raw gốc để bẫy lỗi)
    # ------------------------------------------
    with tab2:
        st.subheader("Kiểm tra Tính toàn vẹn của Dữ liệu (Data Validation)")
        st.markdown("Hệ thống tự động kiểm tra các bất thường trong tập dữ liệu trước khi đưa lên báo cáo để đảm bảo độ chính xác của Insights.")

        missing_master = df_raw['category'].isnull().sum()
        if missing_master == 0:
            st.success("✅ 1. Toàn vẹn kết nối: 100% mã lỗi từ xưởng đều khớp với Master Data.")
        else:
            st.error(f"❌ 1. Cảnh báo: Có {missing_master} dòng lỗi không khớp Master Data!")

        negative_cost = len(df_raw[df_raw['repair_cost'] < 0])
        if negative_cost == 0:
            st.success("✅ 2. Logic chi phí: Không phát hiện chi phí sửa chữa âm.")
        else:
            st.error(f"❌ 2. Cảnh báo: Phát hiện {negative_cost} dòng có chi phí sửa chữa âm!")

        st.markdown("---")
        st.markdown("### 🔍 Kiểm tra Bẫy Dữ liệu (Business Time-frame Trap)")
        
        # Bắt các dòng dữ liệu không nằm trong khoảng Tháng 1 - Tháng 6 / 2024
        outliers_df = df_raw[~df_raw.index.isin(df_filtered.index)]
        outliers_count = len(outliers_df)
        
        if outliers_count == 0:
            st.success("✅ 100% dữ liệu nằm chuẩn trong phạm vi yêu cầu.")
        else:
            st.warning(f"⚠️ **PHÁT HIỆN DỮ LIỆU RÁC (OUTLIERS):** Hệ thống API trả về **{outliers_count} bản ghi** nằm ngoài mốc thời gian kinh doanh yêu cầu (Jan - Jun 2024).")
            st.write("Chi tiết các dòng dữ liệu vi phạm (Năm 2026):")
            st.dataframe(outliers_df[['defect_date', 'production_line', 'category', 'severity']], use_container_width=True)
            st.info("💡 **Hành động của hệ thống:** Các dữ liệu nhiễu này đã được tự động cách ly khỏi các thuật toán tính toán ở Tab 1 và Tab 3 để đảm bảo KPI và đồ thị không bị bóp méo.")

    # ------------------------------------------
    # TAB 3: AUTO-INSIGHTS (Dùng df_filtered)
    # ------------------------------------------
    with tab3:
        st.subheader("🤖 Hệ thống Tự động Phân tích Dữ liệu")
        st.markdown("Thuật toán tự động quét qua tập dữ liệu sạch để trích xuất các quy luật bất thường.")
        st.markdown("---")
        
        # 1. ĐÁNH GIÁ XU HƯỚNG
        st.markdown("### 📈 1. Phân tích Xu hướng (Jan-Jun 2024)")
        df_filtered_copy = df_filtered.copy()
        df_filtered_copy['month'] = df_filtered_copy['defect_date'].dt.to_period('M')
        monthly_trend = df_filtered_copy.groupby('month').size().reset_index(name='count')
        
        first_m = monthly_trend.iloc[0]
        last_m = monthly_trend.iloc[-1]
        
        if last_m['count'] < first_m['count']:
            st.success(f"**📉 Đánh giá tự động: GIẢM (Tín hiệu Tích cực)**\nHệ thống sản xuất có cải thiện. Tháng cuối kỳ giảm {first_m['count'] - last_m['count']} lỗi so với đầu kỳ.")
        else:
            st.error(f"**📈 Đánh giá tự động: TĂNG (Tín hiệu Tiêu cực)**\nHệ thống ghi nhận sự gia tăng lỗi ở cuối kỳ so với đầu kỳ. Số lượng lỗi đang có sự dao động mạnh, liên tục xuất hiện các đỉnh (spike) vượt mức trung bình. Cần rà soát lại quy trình bảo trì.")

        # 2. VỊ TRÍ & ĐỘ NGHIÊM TRỌNG
        st.markdown("### 🔍 2. Phân tích Vị trí & Cấp độ rủi ro")
        critical_df = df_filtered[df_filtered['severity'] == 'Critical']
        if not critical_df.empty:
            worst_location = critical_df['defect_location'].value_counts().idxmax()
            worst_loc_count = critical_df['defect_location'].value_counts().max()
            
            st.warning(f"**Điểm nóng nghiêm trọng (Hotspot):** Vị trí **'{worst_location}'** đang ghi nhận tần suất xuất hiện lỗi cấp độ 'Critical' cao nhất toàn nhà máy với **{worst_loc_count} trường hợp**.")
            st.info(f"**💡 Đề xuất:** Chuyển dịch nguồn lực QC, áp dụng phương pháp đo đạc kỹ thuật bằng thiết bị/AI vào khâu lắp ráp '{worst_location}' thay vì chỉ kiểm tra ngoại quan (Visual).")

        # 3. QUY LUẬT NÚT THẮT
        st.markdown("### 🧩 3. Nhận diện Quy luật Nút thắt (Bottlenecks)")
        pattern_df = df_filtered.groupby(['production_line', 'category']).size().reset_index(name='count')
        worst_pattern = pattern_df.loc[pattern_df['count'].idxmax()]
        
        worst_line = worst_pattern['production_line']
        worst_cat = worst_pattern['category']
        bottleneck_cost = df_filtered[(df_filtered['production_line'] == worst_line) & (df_filtered['category'] == worst_cat)]['repair_cost'].sum()
        
        st.error(f"**Nút thắt hệ thống:** Tổ hợp giữa **{worst_line}** và **{worst_cat}** đang tạo ra lượng lỗi lớn nhất (**{worst_pattern['count']} lỗi**).")
        st.markdown(f"> **Tác động tài chính:** Riêng quy luật bất thường này đã làm tiêu hao **${bottleneck_cost:,.2f}** chi phí sửa chữa.")
        st.info("**💡 Đề xuất:** Tiến hành Audit ngay lập tức tính tương thích kỹ thuật giữa máy móc của dây chuyền này với đặc tính thiết kế của nhóm sản phẩm trên.")

if __name__ == "__main__":
    main()