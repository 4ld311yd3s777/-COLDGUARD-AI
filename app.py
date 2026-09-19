import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# 1. CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="COLDGUARD AI - Cold Chain Risk Management",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CSS GIAO DIỆN
# =========================================================
st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }
    .title {
        font-size: 38px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .subtitle {
        font-size: 16px;
        color: #475569;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .info-box {
        padding: 16px 20px;
        border-radius: 10px;
        background-color: #ffffff;
        border-left: 5px solid #2563eb;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .risk-tag-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .risk-tag-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .risk-tag-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 3. TIÊU ĐỀ ỨNG DỤNG
# =========================================================
st.markdown('<div class="title">❄️ COLDGUARD AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'Mô hình AI dự báo và quản trị rủi ro chuỗi lạnh đối với nông sản & hàng hóa xuất khẩu'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# 4. HÀM TÍNH TOÁN RỦI RO (RISK ENGINE)
# =========================================================
def calculate_temperature_risk(temp):
    """
    Ngưỡng nhiệt độ mô phỏng cho chuỗi lạnh trái cây/xoài xuất khẩu:
    <= 6°C: Tối ưu (Rủi ro thấp)
    6 - 8°C: Ngưỡng cảnh báo (Rủi ro trung bình)
    > 8°C: Nguy cơ hư hỏng (Rủi ro cao)
    """
    try:
        val = float(temp)
    except:
        return 50.0
    if val <= 6.0:
        return 10.0
    elif val <= 8.0:
        return 45.0
    else:
        return 90.0

def calculate_humidity_risk(humidity):
    try:
        val = float(humidity)
    except:
        return 50.0
    if val <= 80.0:
        return 10.0
    elif val <= 88.0:
        return 45.0
    else:
        return 85.0

def calculate_waiting_risk(waiting_time):
    try:
        val = float(waiting_time)
    except:
        return 50.0
    if val <= 12.0:
        return 10.0
    elif val <= 24.0:
        return 45.0
    else:
        return 90.0

def calculate_transport_risk(transport_time):
    try:
        val = float(transport_time)
    except:
        return 50.0
    if val <= 28.0:
        return 10.0
    elif val <= 36.0:
        return 40.0
    else:
        return 80.0

def calculate_power_risk(power_status):
    status_str = str(power_status).strip().lower()
    abnormal_keywords = ["bất thường", "abnormal", "fault", "lỗi", "mất điện", "hong", "hỏng", "off", "0", "false"]
    if any(k in status_str for k in abnormal_keywords):
        return 90.0
    return 5.0

def classify_risk(score):
    if score >= 70.0:
        return "HIGH RISK"
    elif score >= 40.0:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"

def build_recommendation(row):
    actions = []
    if row["Nhiệt độ (°C)"] > 8.0:
        actions.append("Kiểm tra và hiệu chỉnh ngay hệ thống làm lạnh container")
    elif row["Nhiệt độ (°C)"] > 6.0:
        actions.append("Theo dõi sát xu hướng tăng nhiệt độ trong khoang lạnh")

    if row["Độ ẩm (%)"] > 88.0:
        actions.append("Tăng cường kiểm soát độ ẩm, thông gió tránh đọng sương")
    elif row["Độ ẩm (%)"] < 75.0:
        actions.append("Cảnh báo độ ẩm thấp có thể làm khô héo nông sản")

    if row["Thời gian chờ (giờ)"] > 24.0:
        actions.append("Ưu tiên luồng xanh / thủ tục hải quan rút ngắn thời gian chờ bãi")
    elif row["Thời gian chờ (giờ)"] > 12.0:
        actions.append("Chuẩn bị sẵn chứng từ xuất khẩu để thông quan nhanh")

    power_val = str(row["Tình trạng nguồn điện"]).strip().lower()
    if any(k in power_val for k in ["bất thường", "abnormal", "fault", "lỗi", "mất điện", "hỏng"]):
        actions.append("KHẨN CẤP: Kiểm tra giắc cắm nguồn reefer container và máy phát điện")

    if row["Thời gian vận chuyển (giờ)"] > 36.0:
        actions.append("Lộ trình vận chuyển kéo dài, kiểm tra tổng thể chất lượng hàng")

    if not actions:
        actions.append("Tiếp tục duy trì giám sát định kỳ điều kiện bảo quản")

    return " • " + "\n • ".join(actions)

# =========================================================
# 5. DỮ LIỆU MẪU BAN ĐẦU
# =========================================================
sample_data = {
    "Container": ["C01", "C02", "C03", "C04", "C05"],
    "Nhiệt độ (°C)": [5.2, 6.1, 7.4, 9.2, 5.8],
    "Độ ẩm (%)": [78.0, 82.0, 86.0, 92.0, 80.0],
    "Thời gian chờ (giờ)": [10.0, 18.0, 24.0, 38.0, 14.0],
    "Thời gian vận chuyển (giờ)": [26.0, 30.0, 34.0, 42.0, 28.0],
    "Tình trạng nguồn điện": ["Ổn định", "Ổn định", "Ổn định", "Bất thường", "Ổn định"]
}

# =========================================================
# 6. SIDEBAR: TẢI FILE & CẤU HÌNH
# =========================================================
st.sidebar.header("📁 Nguồn dữ liệu")

data_source = st.sidebar.radio(
    "Chọn phương thức nhập dữ liệu:",
    options=["Dữ liệu mẫu (Demo)", "Tải lên file CSV / Excel"],
    index=0
)

uploaded_df = None

# Hàm tìm cột thông minh
def auto_detect_column(columns, candidates):
    cols_lower = {str(c).strip().lower(): c for c in columns}
    for cand in candidates:
        cand_lower = cand.lower()
        for k, original_col in cols_lower.items():
            if cand_lower == k or cand_lower in k:
                return original_col
    return columns[0] if len(columns) > 0 else None

if data_source == "Tải lên file CSV / Excel":
    uploaded_file = st.sidebar.file_uploader(
        "Tải lên tệp dữ liệu container:",
        type=["csv", "xlsx", "xls"],
        help="Hỗ trợ file định dạng CSV hoặc Microsoft Excel (.xlsx, .xls)"
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                # Thử đọc với các bảng mã thông dụng
                try:
                    uploaded_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    uploaded_df = pd.read_csv(uploaded_file, encoding="latin1")
            else:
                uploaded_df = pd.read_excel(uploaded_file)
            
            st.sidebar.success(f"✅ Đã tải: `{uploaded_file.name}` ({len(uploaded_df)} dòng)")
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi khi đọc file: {e}")
    else:
        st.sidebar.info("💡 Chưa có file nào được tải lên. Đang sử dụng dữ liệu mẫu.")

# Nút tải file mẫu cho người dùng
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Mẫu dữ liệu chuẩn")
sample_df_template = pd.DataFrame(sample_data)
csv_template = sample_df_template.to_csv(index=False).encode("utf-8-sig")
st.sidebar.download_button(
    label="Tải file mẫu (CSV)",
    data=csv_template,
    file_name="mau_du_lieu_coldguard.csv",
    mime="text/csv",
    help="Tải file mẫu để xem định dạng các cột cần thiết"
)

# =========================================================
# 7. XỬ LÝ DỮ LIỆU & ÁNH XẠ CỘT (COLUMN MAPPING)
# =========================================================
if uploaded_df is not None and not uploaded_df.empty:
    raw_df = uploaded_df.copy()
    is_custom_data = True
else:
    raw_df = pd.DataFrame(sample_data)
    is_custom_data = False

cols = list(raw_df.columns)

with st.sidebar.expander("⚙️ Cấu hình ánh xạ cột", expanded=is_custom_data):
    st.caption("Khớp nối tên cột trong file của bạn với các biến rủi ro:")
    
    col_id = st.selectbox(
        "Cột Mã Container:",
        options=cols,
        index=cols.index(auto_detect_column(cols, ["container", "id", "mã", "code", "so_cont"])) if cols else 0
    )
    col_temp = st.selectbox(
        "Cột Nhiệt độ (°C):",
        options=cols,
        index=cols.index(auto_detect_column(cols, ["nhiệt độ", "nhiet do", "temp", "celsius"])) if cols else 0
    )
    col_hum = st.selectbox(
        "Cột Độ ẩm (%):",
        options=cols,
        index=cols.index(auto_detect_column(cols, ["độ ẩm", "do am", "humidity", "hum"])) if cols else 0
    )
    col_wait = st.selectbox(
        "Cột Thời gian chờ (giờ):",
        options=cols,
        index=cols.index(auto_detect_column(cols, ["thời gian chờ", "cho", "wait", "delay"])) if cols else 0
    )
    col_trans = st.selectbox(
        "Cột Thời gian vận chuyển (giờ):",
        options=cols,
        index=cols.index(auto_detect_column(cols, ["thời gian vận chuyển", "van chuyen", "transport", "transit"])) if cols else 0
    )
    col_power = st.selectbox(
        "Cột Tình trạng nguồn điện:",
        options=cols,
        index=cols.index(auto_detect_column(cols, ["nguồn điện", "nguon dien", "power", "dien"])) if cols else 0
    )

# Chuẩn hoá DataFrame về định dạng chuẩn của COLDGUARD
df = pd.DataFrame()
df["Container"] = raw_df[col_id].astype(str)
df["Nhiệt độ (°C)"] = pd.to_numeric(raw_df[col_temp], errors="coerce").fillna(6.0)
df["Độ ẩm (%)"] = pd.to_numeric(raw_df[col_hum], errors="coerce").fillna(80.0)
df["Thời gian chờ (giờ)"] = pd.to_numeric(raw_df[col_wait], errors="coerce").fillna(12.0)
df["Thời gian vận chuyển (giờ)"] = pd.to_numeric(raw_df[col_trans], errors="coerce").fillna(24.0)
df["Tình trạng nguồn điện"] = raw_df[col_power].fillna("Ổn định").astype(str)

# =========================================================
# 8. TÍNH TOÁN RISK SCORES
# =========================================================
df["Temperature Risk"] = df["Nhiệt độ (°C)"].apply(calculate_temperature_risk)
df["Humidity Risk"] = df["Độ ẩm (%)"].apply(calculate_humidity_risk)
df["Waiting Risk"] = df["Thời gian chờ (giờ)"].apply(calculate_waiting_risk)
df["Transport Risk"] = df["Thời gian vận chuyển (giờ)"].apply(calculate_transport_risk)
df["Power Risk"] = df["Tình trạng nguồn điện"].apply(calculate_power_risk)

# Trọng số mô hình Cold Chain Risk Score
df["Risk Score"] = (
    df["Temperature Risk"] * 0.35 +
    df["Humidity Risk"] * 0.15 +
    df["Waiting Risk"] * 0.25 +
    df["Transport Risk"] * 0.15 +
    df["Power Risk"] * 0.10
).round(1)

df["Risk Level"] = df["Risk Score"].apply(classify_risk)
df["Recommendation"] = df.apply(build_recommendation, axis=1)

# Thông báo trạng thái nguồn dữ liệu
if is_custom_data:
    st.success(f"📊 **Dữ liệu thực tế đang được phân tích:** Tổng cộng **{len(df)}** container từ tệp tải lên.")
else:
    st.info("ℹ️ **Chế độ Demo:** Đang hiển thị bộ dữ liệu mô phỏng 5 container xoài xuất khẩu. Hãy tải file CSV/Excel ở thanh bên trái để phân tích dữ liệu thực tế của bạn.")

# =========================================================
# 9. BỘ LỌC DỮ LIỆU SIDEBAR
# =========================================================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Bộ lọc hiển thị")

all_risk_levels = ["HIGH RISK", "MEDIUM RISK", "LOW RISK"]
selected_risk = st.sidebar.multiselect(
    "Mức độ rủi ro:",
    options=all_risk_levels,
    default=all_risk_levels
)

search_keyword = st.sidebar.text_input("Tìm kiếm mã container:", placeholder="Nhập mã container...")

filtered_df = df[df["Risk Level"].isin(selected_risk)]
if search_keyword.strip():
    filtered_df = filtered_df[filtered_df["Container"].str.contains(search_keyword.strip(), case=False, na=False)]

# =========================================================
# 10. KPI TỔNG QUAN
# =========================================================
total_c = len(df)
high_c = len(df[df["Risk Level"] == "HIGH RISK"])
med_c = len(df[df["Risk Level"] == "MEDIUM RISK"])
low_c = len(df[df["Risk Level"] == "LOW RISK"])
avg_score = round(df["Risk Score"].mean(), 1) if total_c > 0 else 0

st.markdown("### 📊 Tổng quan chỉ số rủi ro")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📦 Tổng container", total_c)
with col2:
    st.metric("🔴 High Risk", high_c, delta=f"{round(high_c/total_c*100, 1)}%" if total_c else None, delta_color="inverse")
with col3:
    st.metric("🟡 Medium Risk", med_c)
with col4:
    st.metric("🟢 Low Risk", low_c)
with col5:
    st.metric("📈 Risk Score TB", f"{avg_score}/100")

# Cảnh báo khẩn nếu có High Risk
if high_c > 0:
    high_cont_names = ", ".join(df[df["Risk Level"] == "HIGH RISK"]["Container"].tolist()[:5])
    suffix = "..." if high_c > 5 else ""
    st.error(f"🚨 **CẢNH BÁO:** Phát hiện **{high_c} container** ở mức độ rủi ro cao (**HIGH RISK**) cần can thiệp xử lý ngay: `{high_cont_names}{suffix}`")

# =========================================================
# 11. BẢNG DỮ LIỆU & PHÂN TÍCH CHI TIẾT
# =========================================================
st.markdown("---")
col_left, col_right = st.columns([6, 4])

with col_left:
    st.markdown("### 🚢 Danh sách xếp hạng rủi ro container")
    display_cols = [
        "Container", "Nhiệt độ (°C)", "Độ ẩm (%)",
        "Thời gian chờ (giờ)", "Thời gian vận chuyển (giờ)",
        "Tình trạng nguồn điện", "Risk Score", "Risk Level"
    ]
    sorted_df = filtered_df[display_cols].sort_values("Risk Score", ascending=False)
    
    def color_risk(val):
        if val == 'HIGH RISK':
            return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        elif val == 'MEDIUM RISK':
            return 'background-color: #fef3c7; color: #92400e; font-weight: bold;'
        elif val == 'LOW RISK':
            return 'background-color: #dcfce7; color: #166534; font-weight: bold;'
        return ''

    styler = sorted_df.style
    if hasattr(styler, 'map'):
        styled_df = styler.map(color_risk, subset=['Risk Level'])
    else:
        styled_df = styler.applymap(color_risk, subset=['Risk Level'])

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=380,
        hide_index=True
    )


with col_right:
    st.markdown("### 📈 Biểu đồ Cold Chain Risk Score")
    if not filtered_df.empty:
        # Giới hạn top 15 container nếu tập dữ liệu quá lớn
        chart_df = filtered_df.sort_values("Risk Score", ascending=False).head(15)
        fig_bar = px.bar(
            chart_df,
            x="Container",
            y="Risk Score",
            color="Risk Level",
            color_discrete_map={
                "HIGH RISK": "#ef4444",
                "MEDIUM RISK": "#f59e0b",
                "LOW RISK": "#10b981"
            },
            text="Risk Score",
            title=f"Top {len(chart_df)} Container có rủi ro cao nhất"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(yaxis=dict(range=[0, 105]), margin=dict(l=20, r=20, t=40, b=20), height=380)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Không có container nào phù hợp với bộ lọc hiện tại.")

# =========================================================
# 12. PHÂN TÍCH TƯƠNG QUAN & CÁC YẾU TỐ RỦI RO
# =========================================================
st.markdown("---")
st.markdown("### 🔍 Phân tích chuyên sâu các yếu tố chuỗi lạnh")

tab1, tab2 = st.tabs(["📊 Phân bố tương quan Nhiệt độ & Thời gian chờ", "⚖️ Trọng số thuật toán"])

with tab1:
    if not df.empty:
        fig_scatter = px.scatter(
            df,
            x="Thời gian chờ (giờ)",
            y="Nhiệt độ (°C)",
            color="Risk Level",
            size="Risk Score",
            hover_name="Container",
            color_discrete_map={
                "HIGH RISK": "#ef4444",
                "MEDIUM RISK": "#f59e0b",
                "LOW RISK": "#10b981"
            },
            title="Mối liên hệ giữa Thời gian chờ bãi và Nhiệt độ khoang lạnh"
        )
        # Thêm đường ngưỡng cảnh báo
        fig_scatter.add_hline(y=8.0, line_dash="dash", line_color="red", annotation_text="Ngưỡng nguy hiểm (8°C)")
        fig_scatter.add_vline(x=24.0, line_dash="dash", line_color="orange", annotation_text="Ngưỡng chờ tối đa (24h)")
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    factor_df = pd.DataFrame({
        "Yếu tố": ["Nhiệt độ khoang lạnh", "Thời gian chờ thông quan", "Thời gian vận chuyển", "Độ ẩm khoang", "Tình trạng nguồn điện"],
        "Trọng số (%)": [35, 25, 15, 15, 10]
    })
    fig_factor = px.pie(
        factor_df,
        values="Trọng số (%)",
        names="Yếu tố",
        title="Tỷ trọng ảnh hưởng của từng yếu tố tới Cold Chain Risk Score",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_factor.update_layout(height=400)
    st.plotly_chart(fig_factor, use_container_width=True)

# =========================================================
# 13. TRA CỨU CHI TIẾT & HỆ THỐNG KHUYẾN NGHỊ (RECOMMENDATION)
# =========================================================
st.markdown("---")
st.markdown("### 🔎 Kiểm tra chi tiết & Hệ thống khuyến nghị từng Container")

container_list = df["Container"].tolist()
if container_list:
    sel_col1, sel_col2 = st.columns([1, 2])
    with sel_col1:
        selected_container = st.selectbox("Chọn container cần tra cứu:", container_list)
    
    selected_row = df[df["Container"] == selected_container].iloc[0]

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.markdown(f"#### 📋 Thông số kỹ thuật Container `{selected_container}`")
        st.write(f"• **Nhiệt độ hiện tại:** `{selected_row['Nhiệt độ (°C)']} °C`")
        st.write(f"• **Độ ẩm khoang:** `{selected_row['Độ ẩm (%)']} %`")
        st.write(f"• **Thời gian chờ tại bãi/cửa khẩu:** `{selected_row['Thời gian chờ (giờ)']} giờ`")
        st.write(f"• **Thời gian vận chuyển trên đường:** `{selected_row['Thời gian vận chuyển (giờ)']} giờ`")
        st.write(f"• **Tình trạng nguồn điện làm lạnh:** `{selected_row['Tình trạng nguồn điện']}`")

    with detail_col2:
        st.markdown("#### 🧠 Đánh giá & Khuyến nghị hành động của AI")
        curr_score = selected_row["Risk Score"]
        curr_level = selected_row["Risk Level"]

        if curr_level == "HIGH RISK":
            st.markdown(f'<div class="risk-tag-high">🔴 {curr_level} ({curr_score}/100) - NGUY CƠ CAO</div>', unsafe_allow_html=True)
        elif curr_level == "MEDIUM RISK":
            st.markdown(f'<div class="risk-tag-medium">🟡 {curr_level} ({curr_score}/100) - CẦN THEO DÕI</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="risk-tag-low">🟢 {curr_level} ({curr_score}/100) - AN TOÀN</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="info-box" style="margin-top: 15px;">
                <b>Hành động đề xuất từ COLDGUARD AI:</b><br>
                {selected_row["Recommendation"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# 14. XUẤT BÁO CÁO (DOWNLOAD DATA)
# =========================================================
st.markdown("---")
st.markdown("### 📥 Xuất kết quả phân tích")

export_cols = [
    "Container", "Nhiệt độ (°C)", "Độ ẩm (%)", "Thời gian chờ (giờ)",
    "Thời gian vận chuyển (giờ)", "Tình trạng nguồn điện",
    "Risk Score", "Risk Level", "Recommendation"
]
export_df = df[export_cols]

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    export_df.to_excel(writer, index=False, sheet_name="ColdGuard_Analysis")
excel_data = buf.getvalue()

csv_data = export_df.to_csv(index=False).encode("utf-8-sig")

btn_col1, btn_col2, _ = st.columns([2, 2, 4])
with btn_col1:
    st.download_button(
        label="⬇️ Tải kết quả phân tích (CSV)",
        data=csv_data,
        file_name="coldguard_ket_qua_phan_tich.csv",
        mime="text/csv"
    )
with btn_col2:
    st.download_button(
        label="⬇️ Tải kết quả phân tích (Excel .xlsx)",
        data=excel_data,
        file_name="coldguard_ket_qua_phan_tich.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =========================================================
# 15. FOOTER
# =========================================================
st.markdown("---")
st.caption("❄️ COLDGUARD AI | Hệ thống dự báo và quản trị rủi ro chuỗi lạnh xuất khẩu | Hỗ trợ CSV, Excel & Phân tích tự động")
