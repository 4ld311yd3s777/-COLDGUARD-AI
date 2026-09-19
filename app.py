import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# 1. CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="COLDGUARD AI",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CSS GIAO DIỆN CHUẨN PIXEL-PERFECT
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 95%;
    }

    /* Banner chính */
    .hero-banner {
        background-color: #0b2545;
        border-radius: 14px;
        padding: 32px 36px;
        color: #ffffff;
        margin-bottom: 24px;
    }

    .hero-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    .hero-title-icon {
        color: #38bdf8;
        font-size: 32px;
    }

    .hero-tag {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.2px;
        color: #93c5fd;
        margin-bottom: 14px;
    }

    .hero-desc {
        font-size: 16px;
        color: #f1f5f9;
        font-weight: 400;
    }

    /* Tabs tùy biến */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 700;
        color: #64748b;
        padding: 10px 4px 14px 4px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        color: #ef4444 !important;
        border-bottom: 3px solid #ef4444 !important;
    }

    /* Metric cards */
    .metric-col {
        display: flex;
        flex-direction: column;
        padding: 4px 8px;
    }

    .metric-label {
        font-size: 14px;
        color: #475569;
        font-weight: 500;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .metric-val {
        font-size: 34px;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.1;
    }

    /* Bảng xếp hạng HTML */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        font-size: 14px;
        border: 1px solid #edf2f7;
        border-radius: 8px;
        overflow: hidden;
    }

    .custom-table th {
        background-color: #f8fafc;
        color: #475569;
        font-weight: 600;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid #e2e8f0;
    }

    .custom-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #f1f5f9;
        color: #1e293b;
    }

    .custom-table tr:hover {
        background-color: #f8fafc;
    }

    /* Cảnh báo vàng */
    .alert-warning-box {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-radius: 8px;
        padding: 14px 18px;
        color: #78350f;
        font-size: 14.5px;
        font-weight: 500;
        margin-top: 20px;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    /* Footer */
    .footer-text {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #f1f5f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 3. DỮ LIỆU MẪU BAN ĐẦU (ĐÚNG THEO GIAO DIỆN HÌNH ẢNH)
# =========================================================
default_demo_data = {
    "Container": ["MG001", "MG002", "MG003", "MG004", "MG005"],
    "Nhiệt độ (°C)": [4.2, 5.1, 6.3, 4.8, 8.9],
    "Độ ẩm (%)": [82, 85, 88, 80, 94],
    "Thời gian chờ (giờ)": [18, 24, 31, 20, 52],
    "Làm lạnh": ["Bình thường", "Bình thường", "Bình thường", "Bình thường", "Bất thường"]
}

# =========================================================
# 4. HÀM TÍNH TOÁN RISK SCORE & PHÂN LOẠI
# =========================================================
def compute_risk_score(temp, hum, wait_time, cooling_status):
    """
    Tính toán Cold Chain Risk Score (0 - 100):
    - Nhiệt độ: <= 6°C: 0đ | 6 - 8°C: 25đ | > 8°C: 40đ
    - Độ ẩm: <= 85%: 0đ | 85 - 90%: 10đ | > 90%: 15đ
    - Thời gian chờ: <= 24h: 0đ | 24 - 36h: 15đ | > 36h: 25đ
    - Làm lạnh: Bất thường -> 20đ | Bình thường -> 0đ
    """
    # Nhiệt độ
    try:
        t = float(temp)
    except:
        t = 5.0
    if t <= 6.0:
        score_t = 0
    elif t <= 8.0:
        score_t = 25
    else:
        score_t = 40

    # Độ ẩm
    try:
        h = float(hum)
    except:
        h = 80.0
    if h <= 85.0:
        score_h = 0
    elif h <= 90.0:
        score_h = 10
    else:
        score_h = 15

    # Thời gian chờ
    try:
        w = float(wait_time)
    except:
        w = 12.0
    if w <= 24.0:
        score_w = 0
    elif w <= 36.0:
        score_w = 15
    else:
        score_w = 25

    # Làm lạnh / Nguồn điện
    status_str = str(cooling_status).strip().lower()
    abnormal_kws = ["bất thường", "abnormal", "fault", "lỗi", "mất điện", "hỏng", "off", "0"]
    if any(k in status_str for k in abnormal_kws):
        score_c = 20
    else:
        score_c = 0

    total_score = score_t + score_h + score_w + score_c
    return total_score

def classify_risk_level(score):
    """
    Theo mục 3.1.4 tài liệu LogiPro:
    - 0-39: Low / Normal
    - 40-69: Medium / Warning
    - 70-100: High Risk
    """
    if score >= 70:
        return "High Risk"
    elif score >= 40:
        return "Warning"
    else:
        return "Normal"

def classify_priority(score):
    """
    Theo mục 3.1.5 tài liệu LogiPro (Cold Chain Priority):
    - 70-100 (High Risk) -> P1: Ưu tiên xử lý + kho lạnh
    - 40-69 (Medium)    -> P2: Tăng giám sát + bố trí bảo quản
    - 0-39 (Low)        -> P3: Xử lý bình thường
    """
    if score >= 70:
        return "P1"
    elif score >= 40:
        return "P2"
    else:
        return "P3"

def determine_primary_cause(row):
    """
    Theo mục 3.1.5 & 3.1.6 tài liệu LogiPro:
    Xác định nguyên nhân rủi ro (Risk Cause) phân biệt 'nguy hiểm vì cái gì':
    Nhiệt độ lệch / Thời gian chờ / Nguồn điện làm lạnh
    """
    causes = []
    if "bất thường" in str(row.get("Làm lạnh", "")).lower():
        causes.append("Sự cố hệ thống làm lạnh")
    if float(row.get("Nhiệt độ (°C)", 0)) > 6.0:
        causes.append("Nhiệt độ lệch cao")
    if float(row.get("Thời gian chờ (giờ)", 0)) > 24.0:
        causes.append("Thời gian chờ kéo dài")
    if float(row.get("Độ ẩm (%)", 0)) > 88.0:
        causes.append("Độ ẩm khoang cao")

    if not causes:
        return "Điều kiện bảo quản đạt chuẩn"
    return " & ".join(causes[:2])

def get_recommendation(row):
    """
    Theo mục 3.1.6 tài liệu LogiPro:
    Khuyến nghị hành động kết hợp giữa Priority Level và Risk Cause
    """
    p = classify_priority(row.get("Risk Score", 0))
    recs = []
    
    if p == "P1":
        recs.append("ƯU TIÊN P1: Đưa ngay vào khu vực bảo quản lạnh và làm thủ tục thông quan luồng ưu tiên")
    elif p == "P2":
        recs.append("CẢNH BÁO P2: Tăng cường tần suất giám sát nhiệt độ và sẵn sàng bố trí bảo quản bổ sung")
    else:
        recs.append("TIÊU CHUẨN P3: Duy trì chế độ giám sát định kỳ theo quy trình chuẩn")

    if "bất thường" in str(row.get("Làm lạnh", "")).lower():
        recs.append("Khẩn cấp: Kiểm tra giắc cắm nguồn điện reefer container và máy phát điện")
    if float(row.get("Nhiệt độ (°C)", 0)) > 8.0:
        recs.append("Nhiệt độ vượt ngưỡng cho phép: Hiệu chỉnh công suất làm mát tức thì")
    elif float(row.get("Nhiệt độ (°C)", 0)) > 6.0:
        recs.append("Nhiệt độ có xu hướng tăng: Kiểm tra kín gió và luồng khí đối lưu")

    if float(row.get("Thời gian chờ (giờ)", 0)) > 36.0:
        recs.append("Thời gian lưu bãi quá giới hạn khuyến nghị: Rút ngắn thời gian thông quan")

    return " • " + "\n • ".join(recs)


# =========================================================
# 5. SIDEBAR: TẢI FILE VÀ NGUỒN DỮ LIỆU
# =========================================================
with st.sidebar:
    st.markdown("### 📁 DỮ LIỆU")
    st.caption("Tải dữ liệu Excel hoặc CSV")

    uploaded_file = st.file_uploader(
        "Tải dữ liệu Excel hoặc CSV",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
        help="Hỗ trợ file CSV hoặc Microsoft Excel (.xlsx, .xls)"
    )

    uploaded_df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                try:
                    uploaded_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    uploaded_df = pd.read_csv(uploaded_file, encoding="latin1")
            else:
                uploaded_df = pd.read_excel(uploaded_file)
            
            st.markdown(
                f"""
                <div style="background-color: #dcfce7; color: #166534; padding: 12px 14px; border-radius: 8px; font-size: 13.5px; font-weight: 500; line-height: 1.4; margin-top: 14px;">
                    ✅ Đã tải tệp: <b>{uploaded_file.name}</b> ({len(uploaded_df)} dòng).
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as err:
            st.error(f"Lỗi khi đọc file: {err}")
    else:
        st.markdown(
            """
            <div style="background-color: #eaf4fd; color: #0369a1; padding: 12px 14px; border-radius: 8px; font-size: 13.5px; font-weight: 500; line-height: 1.4; margin-top: 14px;">
                Đang sử dụng dữ liệu mô phỏng COLDGUARD AI.
            </div>
            """,
            unsafe_allow_html=True
        )

    # Nút tải file mẫu
    st.markdown("---")
    st.caption("Mẫu file dữ liệu chuẩn:")
    sample_csv_data = pd.DataFrame(default_demo_data).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Tải file mẫu (CSV)",
        data=sample_csv_data,
        file_name="mau_coldguard_containers.csv",
        mime="text/csv",
        use_container_width=True
    )

# =========================================================
# 6. XỬ LÝ VÀ CHUẨN HOÁ DỮ LIỆU
# =========================================================
def auto_match_col(columns, candidates):
    cols_dict = {str(c).strip().lower(): c for c in columns}
    for cand in candidates:
        for k, original in cols_dict.items():
            if cand in k:
                return original
    return columns[0] if len(columns) > 0 else None

if uploaded_df is not None and not uploaded_df.empty:
    raw_df = uploaded_df.copy()
    c_list = list(raw_df.columns)
    
    col_id = auto_match_col(c_list, ["container", "id", "mã", "code"])
    col_temp = auto_match_col(c_list, ["nhiệt độ", "nhiet do", "temp", "celsius"])
    col_hum = auto_match_col(c_list, ["độ ẩm", "do am", "hum", "humidity"])
    col_wait = auto_match_col(c_list, ["thời gian chờ", "chờ", "wait", "delay"])
    col_cool = auto_match_col(c_list, ["làm lạnh", "nguồn điện", "power", "cooling", "trạng thái"])

    df = pd.DataFrame()
    df["Container"] = raw_df[col_id].astype(str)
    df["Nhiệt độ (°C)"] = pd.to_numeric(raw_df[col_temp], errors="coerce").fillna(5.0)
    df["Độ ẩm (%)"] = pd.to_numeric(raw_df[col_hum], errors="coerce").fillna(80.0).astype(int)
    df["Thời gian chờ (giờ)"] = pd.to_numeric(raw_df[col_wait], errors="coerce").fillna(12.0).astype(int)
    df["Làm lạnh"] = raw_df[col_cool].fillna("Bình thường").astype(str)
else:
    df = pd.DataFrame(default_demo_data)

# Tính toán điểm rủi ro và các trường chuẩn theo tài liệu LogiPro
df["Risk Score"] = df.apply(
    lambda r: compute_risk_score(r["Nhiệt độ (°C)"], r["Độ ẩm (%)"], r["Thời gian chờ (giờ)"], r["Làm lạnh"]),
    axis=1
)
df["Phân loại"] = df["Risk Score"].apply(classify_risk_level)
df["Priority"] = df["Risk Score"].apply(classify_priority)
df["Nguyên nhân chính"] = df.apply(determine_primary_cause, axis=1)
df["Recommendation"] = df.apply(get_recommendation, axis=1)

# =========================================================
# 7. HERO BANNER CHÍNH
# =========================================================
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">
            <span class="hero-title-icon">❄️</span>
            <span>COLDGUARD AI</span>
        </div>
        <div class="hero-tag">
            AI-POWERED COLD CHAIN RISK MANAGEMENT
        </div>
        <div class="hero-desc">
            Giám sát và dự báo rủi ro chuỗi lạnh hàng hóa xuất khẩu
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 8. NAVIGATION TABS
# =========================================================
tab_dash, tab_case = st.tabs(["📊 DASHBOARD", "🥭 CASE STUDY"])

with tab_dash:
    # -----------------------------------------------------
    # 8.1. TỔNG QUAN RỦI RO CHUỖI LẠNH (METRICS)
    # -----------------------------------------------------
    st.markdown("### 📊 Tổng quan rủi ro chuỗi lạnh")

    total_count = len(df)
    normal_count = len(df[df["Phân loại"] == "Normal"])
    warning_count = len(df[df["Phân loại"] == "Warning"])
    high_count = len(df[df["Phân loại"] == "High Risk"])
    avg_score = round(df["Risk Score"].mean(), 1) if total_count > 0 else 0.0

    m1, m2, m3, m4, m5 = st.columns(5)

    def render_metric(col, label, val):
        html_str = f"<div class='metric-col'><div class='metric-label'>{label}</div><div class='metric-val'>{val}</div></div>"
        with col:
            if hasattr(st, "html"):
                st.html(html_str)
            else:
                st.markdown(html_str, unsafe_allow_html=True)

    render_metric(m1, "📦 Tổng Container", total_count)
    render_metric(m2, "🟢 Normal", normal_count)
    render_metric(m3, "🟡 Warning", warning_count)
    render_metric(m4, "🔴 High Risk", high_count)
    render_metric(m5, "⚠️ Risk Score TB", avg_score)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # 8.2. BIỂU ĐỒ 2 CỘT (BAR CHART & DONUT CHART)
    # -----------------------------------------------------
    c_left, c_right = st.columns([5.5, 4.5])

    with c_left:
        bar_df = df.sort_values(by="Risk Score", ascending=False).head(15) if len(df) > 15 else df
        subtitle_text = f"Top 15/{len(df)} Container rủi ro cao nhất" if len(df) > 15 else "Mức độ rủi ro"
        st.caption(subtitle_text)

        fig_bar = px.bar(
            bar_df,
            x="Container",
            y="Risk Score",
            text="Risk Score"
        )
        fig_bar.update_traces(
            marker_color="#0068c9",
            textposition="outside",
            textfont=dict(size=12, color="#475569")
        )
        fig_bar.update_layout(
            yaxis=dict(
                range=[0, 115],
                tickvals=[0, 20, 40, 60, 80, 100],
                gridcolor="#f1f5f9",
                zeroline=True,
                zerolinecolor="#e2e8f0"
            ),
            xaxis=dict(
                showgrid=False
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            height=340
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_right:
        st.markdown("#### 📊 Phân loại rủi ro")
        st.caption("<span style='opacity:0'>.</span>", unsafe_allow_html=True)

        # Tính tỷ lệ phần trăm
        risk_dist = df["Phân loại"].value_counts().reset_index()
        risk_dist.columns = ["Phân loại", "Số lượng"]

        # Thứ tự chuẩn
        color_order = {
            "Normal": "#0068c9",
            "Warning": "#70bbf9",
            "High Risk": "#ef4444"
        }

        fig_donut = px.pie(
            risk_dist,
            names="Phân loại",
            values="Số lượng",
            hole=0.48,
            color="Phân loại",
            color_discrete_map=color_order
        )
        fig_donut.update_traces(
            textinfo="percent",
            textfont_size=13,
            textposition="inside",
            sort=False
        )
        fig_donut.update_layout(
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.9,
                xanchor="left",
                x=1.02
            ),
            margin=dict(l=10, r=80, t=20, b=20),
            height=340,
            paper_bgcolor="white"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # 8.3. BẢNG XẾP HẠNG CONTAINER THEO MỨC ĐỘ RỦI RO
    # -----------------------------------------------------
    st.markdown("### 🏆 Xếp hạng Container theo mức độ rủi ro")

    # Sắp xếp giảm dần theo Risk Score
    sorted_df = df.sort_values(by="Risk Score", ascending=False).reset_index(drop=True)
    sorted_df.index = sorted_df.index + 1  # 1-indexed

    # Tạo bảng HTML đẹp mắt y hệt ảnh 3
    rows_html = "".join([
        f"<tr>"
        f"<td style='color: #64748b; font-weight: 500;'>{idx}</td>"
        f"<td style='font-weight: 600;'>{row['Container']}</td>"
        f"<td>{row['Nhiệt độ (°C)']}</td>"
        f"<td>{row['Độ ẩm (%)']}</td>"
        f"<td>{row['Thời gian chờ (giờ)']}</td>"
        f"<td>{row['Làm lạnh']}</td>"
        f"<td style='font-weight: 600;'>{row['Risk Score']}</td>"
        f"<td>{row['Phân loại']}</td>"
        f"</tr>"
        for idx, row in sorted_df.iterrows()
    ])

    table_html = (
        "<table class='custom-table'>"
        "<thead><tr>"
        "<th style='width: 50px;'></th>"
        "<th>Container</th>"
        "<th>Nhiệt độ (°C)</th>"
        "<th>Độ ẩm (%)</th>"
        "<th>Thời gian chờ (giờ)</th>"
        "<th>Làm lạnh</th>"
        "<th>Risk Score</th>"
        "<th>Phân loại</th>"
        "</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )

    table_wrapper = (
        f"<div style='max-height: 480px; overflow-y: auto; border: 1px solid #edf2f7; border-radius: 8px;'>{table_html}</div>"
        if len(sorted_df) > 10 else table_html
    )
    if hasattr(st, "html"):
        st.html(table_wrapper)
    else:
        st.markdown(table_wrapper, unsafe_allow_html=True)

    # Cảnh báo vàng bên dưới bảng - Hiển thị đầy đủ tất cả container cần ưu tiên xử lý
    high_risk_rows = sorted_df[sorted_df["Phân loại"] == "High Risk"]
    if not high_risk_rows.empty:
        if len(high_risk_rows) == 1:
            r = high_risk_rows.iloc[0]
            alert_html = (
                f"<div class='alert-warning-box'>"
                f"⚠️ <b>Container cần ưu tiên xử lý:</b> {r['Container']} — Risk Score <b>{r['Risk Score']}</b> — High Risk"
                f"</div>"
            )
        else:
            items_html = "".join([
                f"<div style='margin-top: 6px; padding-left: 8px; font-size: 14px;'>"
                f"• <b>{r['Container']}</b> — Risk Score: <b>{r['Risk Score']}</b> — <b>{r['Phân loại']}</b> "
                f"<span style='color: #b45309;'>({r['Nguyên nhân chính']})</span>"
                f"</div>"
                for _, r in high_risk_rows.iterrows()
            ])
            scroll_style = "max-height: 250px; overflow-y: auto; margin-top: 8px;" if len(high_risk_rows) > 5 else "margin-top: 8px;"
            alert_html = (
                f"<div class='alert-warning-box'>"
                f"<div style='font-size: 15px; font-weight: 700;'>"
                f"⚠️ Danh sách container cần ưu tiên xử lý ({len(high_risk_rows)} container High Risk / P1):"
                f"</div>"
                f"<div style='{scroll_style}'>{items_html}</div>"
                f"</div>"
            )
    else:
        alert_html = (
            f"<div class='alert-warning-box' style='background-color: #f0fdf4; border-color: #bbf7d0; color: #166534;'>"
            f"✅ <b>Tất cả container đều nằm trong ngưỡng an toàn</b> (Không có container High Risk cần can thiệp khẩn cấp)."
            f"</div>"
        )

    if hasattr(st, "html"):
        st.html(alert_html)
    else:
        st.markdown(alert_html, unsafe_allow_html=True)

# =========================================================
# 9. TAB 2: CASE STUDY & CHI TIẾT
# =========================================================
with tab_case:
    st.markdown("### 🥭 Case Study – Xuất khẩu xoài Cát Chu")
    st.markdown(
        """
        **Bối cảnh thực tế**  
        Một lô hàng gồm 5 container xoài xuất khẩu đang chờ làm thủ tục thông quan tại cửa khẩu quốc tế.  
        Hệ thống **COLDGUARD AI** liên tục tiếp nhận dữ liệu thời gian thực từ các cảm biến IoT gắn trong container:  
        - **Nhiệt độ bảo quản (°C):** Ngưỡng an toàn 4 - 6°C.  
        - **Độ ẩm không khí (%):** Ngưỡng tối ưu 80 - 85%.  
        - **Thời gian chờ tại bãi (giờ):** Giới hạn tối đa khuyến nghị 24 giờ.  
        - **Tình trạng hệ thống làm lạnh:** Nguồn điện cấp ổn định hoặc bất thường.
        """
    )

    st.markdown("---")
    st.markdown("#### 🔍 Kiểm tra chi tiết & Đề xuất hành động theo từng Container")

    cont_choice = st.selectbox("Chọn container để phân tích chuyên sâu:", df["Container"].tolist())
    selected_row = df[df["Container"] == cont_choice].iloc[0]

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown(f"**Thông số Container {cont_choice}:**")
        st.write(f"• Nhiệt độ: **{selected_row['Nhiệt độ (°C)']} °C**")
        st.write(f"• Độ ẩm: **{selected_row['Độ ẩm (%)']} %**")
        st.write(f"• Thời gian chờ: **{selected_row['Thời gian chờ (giờ)']} giờ**")
        st.write(f"• Trạng thái làm lạnh: **{selected_row['Làm lạnh']}**")
        st.write(f"• Nguyên nhân rủi ro (*Risk Cause*): **{selected_row['Nguyên nhân chính']}**")

    with d_col2:
        st.markdown(f"**Đánh giá AI & Phân luồng ưu tiên (*Cold Chain Priority*):**")
        score_val = selected_row["Risk Score"]
        level_val = selected_row["Phân loại"]
        priority_val = selected_row["Priority"]
        
        if level_val == "High Risk":
            st.error(f"🔴 {level_val} ({score_val}/100) — Mức ưu tiên: **{priority_val} (Ưu tiên xử lý + kho lạnh)**")
        elif level_val == "Warning":
            st.warning(f"🟡 {level_val} ({score_val}/100) — Mức ưu tiên: **{priority_val} (Tăng giám sát + bố trí bảo quản)**")
        else:
            st.success(f"🟢 {level_val} ({score_val}/100) — Mức ưu tiên: **{priority_val} (Quy trình tiêu chuẩn)**")

        st.info(f"💡 **Hành động đề xuất:**\n\n{selected_row['Recommendation']}")

    st.markdown("---")
    st.markdown("#### 📥 Xuất báo cáo dữ liệu phân tích")
    
    export_df = df.copy()
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="COLDGUARD_Analysis")
    excel_bytes = buf.getvalue()

    b1, b2, _ = st.columns([2, 2, 4])
    with b1:
        st.download_button(
            label="⬇️ Tải kết quả (Excel .xlsx)",
            data=excel_bytes,
            file_name="coldguard_ket_qua.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with b2:
        st.download_button(
            label="⬇️ Tải kết quả (CSV)",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="coldguard_ket_qua.csv",
            mime="text/csv"
        )

# =========================================================
# 10. FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer-text">
        COLDGUARD AI | Prototype mô phỏng quản trị rủi ro chuỗi lạnh | Dữ liệu phục vụ mục đích nghiên cứu và trình diễn.
    </div>
    """,
    unsafe_allow_html=True
)
