import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# 1. CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="COLDGUARD AI",
    page_icon="❄️",
    layout="wide"
)

# =========================================================
# 2. CSS GIAO DIỆN
# =========================================================
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 18px;
        color: #64748b;
        margin-bottom: 25px;
    }
    .risk-high {
        background-color: #fee2e2;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    .risk-medium {
        background-color: #fef3c7;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    .risk-low {
        background-color: #dcfce7;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    .info-box {
        padding: 18px;
        border-radius: 12px;
        background-color: white;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .small-text {
        color: #64748b;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 3. TIÊU ĐỀ
# =========================================================
st.markdown(
    '<div class="title">❄️ COLDGUARD AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Mô hình dự báo và quản trị rủi ro chuỗi lạnh đối với hàng hóa xuất khẩu
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "Prototype mô phỏng: dự báo rủi ro chuỗi lạnh cho các container "
    "xoài xuất khẩu đang chờ thông quan."
)

# =========================================================
# 4. DỮ LIỆU MÔ PHỎNG
# =========================================================
data = {
    "Container": [
        "C01", "C02", "C03", "C04", "C05"
    ],
    "Nhiệt độ (°C)": [
        5.2, 6.1, 7.4, 9.2, 5.8
    ],
    "Độ ẩm (%)": [
        78, 82, 86, 92, 80
    ],
    "Thời gian chờ (giờ)": [
        10, 18, 24, 38, 14
    ],
    "Thời gian vận chuyển (giờ)": [
        26, 30, 34, 42, 28
    ],
    "Tình trạng nguồn điện": [
        "Ổn định", "Ổn định", "Ổn định", "Bất thường", "Ổn định"
    ]
}

df = pd.DataFrame(data)

# =========================================================
# 5. HÀM TÍNH RISK SCORE
# =========================================================
def calculate_temperature_risk(temp):
    """
    Nhiệt độ mô phỏng:
    2 - 6°C: rủi ro thấp
    6 - 8°C: rủi ro trung bình
    > 8°C: rủi ro cao
    """
    if temp <= 6:
        return 10
    elif temp <= 8:
        return 45
    else:
        return 90

def calculate_humidity_risk(humidity):
    if humidity <= 80:
        return 10
    elif humidity <= 88:
        return 45
    else:
        return 85

def calculate_waiting_risk(waiting_time):
    if waiting_time <= 12:
        return 10
    elif waiting_time <= 24:
        return 45
    else:
        return 90

def calculate_transport_risk(transport_time):
    if transport_time <= 28:
        return 10
    elif transport_time <= 36:
        return 40
    else:
        return 80

def calculate_power_risk(power_status):
    if power_status == "Ổn định":
        return 5
    else:
        return 90

# =========================================================
# 6. TÍNH RISK SCORE
# =========================================================
df["Temperature Risk"] = df["Nhiệt độ (°C)"].apply(
    calculate_temperature_risk
)
df["Humidity Risk"] = df["Độ ẩm (%)"].apply(
    calculate_humidity_risk
)
df["Waiting Risk"] = df["Thời gian chờ (giờ)"].apply(
    calculate_waiting_risk
)
df["Transport Risk"] = df["Thời gian vận chuyển (giờ)"].apply(
    calculate_transport_risk
)
df["Power Risk"] = df["Tình trạng nguồn điện"].apply(
    calculate_power_risk
)

# =========================================================
# 7. COLD CHAIN RISK SCORE
# =========================================================
df["Risk Score"] = (
    df["Temperature Risk"] * 0.35 +
    df["Humidity Risk"] * 0.15 +
    df["Waiting Risk"] * 0.25 +
    df["Transport Risk"] * 0.15 +
    df["Power Risk"] * 0.10
)

# Làm tròn
df["Risk Score"] = df["Risk Score"].round(1)

# =========================================================
# 8. PHÂN LOẠI RỦI RO
# =========================================================
def classify_risk(score):
    if score >= 70:
        return "HIGH RISK"
    elif score >= 40:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"

df["Risk Level"] = df["Risk Score"].apply(classify_risk)

# =========================================================
# 9. HÀM ĐỀ XUẤT HÀNH ĐỘNG
# =========================================================
def recommendation(row):
    actions = []
    if row["Nhiệt độ (°C)"] > 8:
        actions.append(
            "Kiểm tra và điều chỉnh hệ thống làm lạnh"
        )
    if row["Độ ẩm (%)"] > 88:
        actions.append(
            "Tăng cường kiểm soát độ ẩm"
        )
    if row["Thời gian chờ (giờ)"] > 24:
        actions.append(
            "Ưu tiên xử lý và rút ngắn thời gian chờ"
        )
    if row["Tình trạng nguồn điện"] == "Bất thường":
        actions.append(
            "Kiểm tra nguồn điện và thiết bị bảo quản"
        )
    if not actions:
        actions.append(
            "Tiếp tục theo dõi điều kiện bảo quản"
        )
    return "; ".join(actions)

df["Recommendation"] = df.apply(
    recommendation, axis=1
)

# =========================================================
# 10. SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Bộ lọc")

selected_risk = st.sidebar.multiselect(
    "Mức độ rủi ro",
    options=[
        "HIGH RISK",
        "MEDIUM RISK",
        "LOW RISK"
    ],
    default=[
        "HIGH RISK",
        "MEDIUM RISK",
        "LOW RISK"
    ]
)

filtered_df = df[
    df["Risk Level"].isin(selected_risk)
]

# =========================================================
# 11. KPI
# =========================================================
total_containers = len(df)
high_risk = len(
    df[df["Risk Level"] == "HIGH RISK"]
)
medium_risk = len(
    df[df["Risk Level"] == "MEDIUM RISK"]
)
low_risk = len(
    df[df["Risk Level"] == "LOW RISK"]
)
average_risk = round(
    df["Risk Score"].mean(), 1
)

st.markdown("## 📊 Tổng quan")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Tổng container",
        total_containers
    )
with col2:
    st.metric(
        "🔴 High Risk",
        high_risk
    )
with col3:
    st.metric(
        "🟡 Medium Risk",
        medium_risk
    )
with col4:
    st.metric(
        "🟢 Low Risk",
        low_risk
    )
with col5:
    st.metric(
        "Risk Score TB",
        average_risk
    )

# =========================================================
# 12. CẢNH BÁO
# =========================================================
high_risk_df = df[
    df["Risk Level"] == "HIGH RISK"
]
if len(high_risk_df) > 0:
    st.warning(
        f"⚠️ Phát hiện {len(high_risk_df)} container "
        "có mức rủi ro cao cần ưu tiên xử lý."
    )

# =========================================================
# 13. BẢNG XẾP HẠNG CONTAINER
# =========================================================
st.markdown("## 🚢 Phân tích rủi ro container")

display_df = filtered_df[
    [
        "Container",
        "Nhiệt độ (°C)",
        "Độ ẩm (%)",
        "Thời gian chờ (giờ)",
        "Thời gian vận chuyển (giờ)",
        "Tình trạng nguồn điện",
        "Risk Score",
        "Risk Level"
    ]
].sort_values(
    "Risk Score", ascending=False
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# 14. BIỂU ĐỒ RISK SCORE
# =========================================================
st.markdown("## 📈 Xếp hạng rủi ro")

fig_risk = px.bar(
    filtered_df.sort_values(
        "Risk Score", ascending=False
    ),
    x="Container",
    y="Risk Score",
    text="Risk Score",
    title="Cold Chain Risk Score theo container",
    labels={
        "Container": "Container",
        "Risk Score": "Risk Score"
    }
)

fig_risk.update_traces(
    textposition="outside"
)
fig_risk.update_layout(
    yaxis=dict(
        range=[0, 100]
    )
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)

# =========================================================
# 15. PHÂN TÍCH CÁC YẾU TỐ RỦI RO
# =========================================================
st.markdown("## 🔍 Phân tích yếu tố rủi ro")

factor_df = pd.DataFrame({
    "Yếu tố": [
        "Nhiệt độ",
        "Độ ẩm",
        "Thời gian chờ",
        "Thời gian vận chuyển",
        "Nguồn điện"
    ],
    "Mức độ ảnh hưởng": [
        35, 15, 25, 15, 10
    ]
})

fig_factor = px.bar(
    factor_df,
    x="Yếu tố",
    y="Mức độ ảnh hưởng",
    text="Mức độ ảnh hưởng",
    title="Trọng số các yếu tố trong Risk Score",
    labels={
        "Yếu tố": "Yếu tố",
        "Mức độ ảnh hưởng": "Trọng số (%)"
    }
)

fig_factor.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_factor,
    use_container_width=True
)

# =========================================================
# 16. CHI TIẾT CONTAINER
# =========================================================
st.markdown("## 🔎 Chi tiết container")

selected_container = st.selectbox(
    "Chọn container để phân tích",
    df["Container"].tolist()
)

selected_row = df[
    df["Container"] == selected_container
].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Điều kiện hiện tại")
    st.write(
        f"**Nhiệt độ:** "
        f"{selected_row['Nhiệt độ (°C)']} °C"
    )
    st.write(
        f"**Độ ẩm:** "
        f"{selected_row['Độ ẩm (%)']} %"
    )
    st.write(
        f"**Thời gian chờ:** "
        f"{selected_row['Thời gian chờ (giờ)']} giờ"
    )
    st.write(
        f"**Thời gian vận chuyển:** "
        f"{selected_row['Thời gian vận chuyển (giờ)']} giờ"
    )
    st.write(
        f"**Nguồn điện:** "
        f"{selected_row['Tình trạng nguồn điện']}"
    )

with col2:
    st.markdown("### Kết quả AI")
    score = selected_row["Risk Score"]
    st.metric(
        "Cold Chain Risk Score",
        f"{score}/100"
    )

    risk_level = selected_row["Risk Level"]
    if risk_level == "HIGH RISK":
        st.error(
            f"🔴 {risk_level}"
        )
    elif risk_level == "MEDIUM RISK":
        st.warning(
            f"🟡 {risk_level}"
        )
    else:
        st.success(
            f"🟢 {risk_level}"
        )

# =========================================================
# 17. GIẢI THÍCH NGUYÊN NHÂN
# =========================================================
st.markdown("### 🧠 Nguyên nhân rủi ro")

causes = []

if selected_row["Nhiệt độ (°C)"] > 8:
    causes.append(
        "Nhiệt độ bảo quản đang cao."
    )
if selected_row["Độ ẩm (%)"] > 88:
    causes.append(
        "Độ ẩm cao làm gia tăng rủi ro ảnh hưởng chất lượng."
    )
if selected_row["Thời gian chờ (giờ)"] > 24:
    causes.append(
        "Thời gian chờ thông quan kéo dài."
    )
if selected_row["Thời gian vận chuyển (giờ)"] > 36:
    causes.append(
        "Thời gian vận chuyển dài."
    )
if selected_row["Tình trạng nguồn điện"] == "Bất thường":
    causes.append(
        "Nguồn điện của hệ thống bảo quản có dấu hiệu bất thường."
    )

if not causes:
    causes.append(
        "Các điều kiện hiện tại nằm trong ngưỡng kiểm soát."
    )

for cause in causes:
    st.write("• " + cause)

# =========================================================
# 18. RECOMMENDATION SYSTEM
# =========================================================
st.markdown("## 🚨 Recommendation System")

if selected_row["Risk Level"] == "HIGH RISK":
    st.error(
        "ƯU TIÊN XỬ LÝ NGAY"
    )
elif selected_row["Risk Level"] == "MEDIUM RISK":
    st.warning(
        "CẦN THEO DÕI VÀ CAN THIỆP"
    )
else:
    st.success(
        "TIẾP TỤC THEO DÕI"
    )

st.markdown(
    f"""
    <div class="info-box">
    <b>Khuyến nghị:</b><br><br>
    {selected_row["Recommendation"]}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 19. CASE STUDY
# =========================================================
st.markdown("## 🥭 Case Study – Xuất khẩu xoài")

st.markdown(
    """
    **Bối cảnh mô phỏng**
    Một lô hàng gồm 5 container xoài xuất khẩu đang chờ thông quan tại cửa khẩu quốc tế.
    Hệ thống COLDGUARD AI tiếp nhận dữ liệu từ nhiều nguồn như điều kiện nhiệt độ, độ ẩm, thời gian chờ và tình trạng nguồn điện.
    Hệ thống tính toán Cold Chain Risk Score để nhận diện container có nguy cơ ảnh hưởng chất lượng và hỗ trợ doanh nghiệp ưu tiên xử lý.
    """
)

st.markdown(
    """
    **Quy trình**
    Dữ liệu logistics + dữ liệu môi trường
    ↓
    Phân tích dữ liệu
    ↓
    Cold Chain Risk Score
    ↓
    Phân loại mức độ rủi ro
    ↓
    Cảnh báo container nguy cơ cao
    ↓
    Đề xuất hành động
    """
)

# =========================================================
# 20. DOWNLOAD DATA
# =========================================================
st.markdown("## 📥 Xuất dữ liệu")

csv = df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Tải dữ liệu COLDGUARD",
    data=csv,
    file_name="coldguard_risk_analysis.csv",
    mime="text/csv"
)

# =========================================================
# 21. FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "COLDGUARD AI | Prototype mô phỏng phục vụ nghiên cứu và trình diễn đề án"
)
