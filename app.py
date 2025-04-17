import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Nhóm bài tập: 200_Trực quan hóa dữ liệu_17-04_2025
# Lê Bật Huy Hùng _ 2121051339
# Hoàng Nguyên _ 2221050010

# ========================================
# CẤU HÌNH TRANG
# ========================================
st.set_page_config(
    page_title="Phân Tích Điện Ảnh",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thiết lập style cho biểu đồ
try:
    plt.style.use('seaborn-v0_8')  # Sử dụng style mới
except:
    sns.set_theme()  # Fallback nếu style không tồn tại

# ========================================
# TIÊU ĐỀ ỨNG DỤNG
# ========================================
st.title("Phân Tích Dữ Liệu Điện Ảnh 🎬")
st.markdown("""
Cho ta cái nhìn tổng quan về dữ liệu phim gồm: rating, ngân sách, bảng so sánh...
""")

# ========================================
# HÀM TẢI VÀ XỬ LÝ DỮ LIỆU
# ========================================
@st.cache_data
def load_data():
    # Tải dữ liệu từ URL
    url = "https://raw.githubusercontent.com/nv-thang/Data-Visualization-Course/main/Dataset%20for%20Practice/movies.csv"
    data = pd.read_csv(url)
    
    # Tiền xử lý dữ liệu
    data = data.dropna()
    
    # Xử lý cột năm
    data['year'] = pd.to_datetime(data['year'], format='%Y', errors='coerce').dt.year
    data = data.dropna(subset=['year'])
    data['year'] = data['year'].astype(int)
    
    # Tính toán các chỉ số mới
    data['profit'] = data['gross'] - data['budget']
    data['roi'] = (data['profit'] / data['budget']) * 100  # ROI tính bằng %
    
    # Chuyển đổi đơn vị tiền tệ về triệu USD
    for col in ['budget', 'gross', 'profit']:
        data[col] = data[col] / 1_000_000
    
    return data

movies_data = load_data()

# ========================================
# SIDEBAR - BỘ LỌC DỮ LIỆU
# ========================================
st.sidebar.header("Bộ Lọc Dữ Liệu")

# Lọc theo năm
min_year = int(movies_data['year'].min())
max_year = int(movies_data['year'].max())
selected_years = st.sidebar.slider(
    "Chọn khoảng năm",
    min_year,
    max_year,
    (min_year, max_year)
)

# Lọc theo thể loại
all_genres = sorted(set([genre for sublist in movies_data['genre'].str.split(', ') for genre in sublist if pd.notna(genre)]))
selected_genres = st.sidebar.multiselect(
    "Chọn thể loại phim",
    all_genres,
    default=all_genres[:3]  # Mặc định chọn 3 thể loại đầu tiên
)

# Lọc theo rating
min_rating, max_rating = st.sidebar.slider(
    "Chọn khoảng rating",
    float(movies_data['score'].min()),
    float(movies_data['score'].max()),
    (0.0, 10.0)
)

# ========================================
# ÁP DỤNG BỘ LỌC
# ========================================
filtered_data = movies_data[
    (movies_data['year'] >= selected_years[0]) & 
    (movies_data['year'] <= selected_years[1]) & 
    (movies_data['genre'].str.contains('|'.join(selected_genres), na=False)) & 
    (movies_data['score'] >= min_rating) & 
    (movies_data['score'] <= max_rating)
]

# ========================================
# HIỂN THỊ THÔNG TIN TỔNG QUAN
# ========================================
st.header("📊 Thông Tin Tổng Quan")

# Tạo 4 cột thông tin
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số phim", f"{len(filtered_data):,}")
col2.metric("Ngân sách trung bình", f"${filtered_data['budget'].mean():.2f} triệu")
col3.metric("Doanh thu trung bình", f"${filtered_data['gross'].mean():.2f} triệu")
col4.metric("Rating trung bình", f"{filtered_data['score'].mean():.1f}/10")

# ========================================
# BIỂU ĐỒ 1: PHÂN BỐ RATING
# ========================================
st.header("Bảng Phân Bố Rating Phim")
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.histplot(
    data=filtered_data,
    x='score',
    bins=20,
    kde=True,
    color='#1f77b4',
    edgecolor='white',
    linewidth=0.5,
    ax=ax1
)
ax1.set_xlabel('Rating', fontsize=12)
ax1.set_ylabel('Số lượng phim', fontsize=12)
ax1.set_title('Phân Phối Rating Của Các Bộ Phim', fontsize=14, pad=20)
ax1.grid(axis='y', alpha=0.3)
st.pyplot(fig1)

# ========================================
# BIỂU ĐỒ 2: TOP 10 PHIM RATING CAO
# ========================================
st.header("Top 10 Phim Có Rating Cao Nhất")
top_movies = filtered_data.sort_values('score', ascending=False).head(10)

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=top_movies,
    x='score',
    y='name',
    palette='viridis',
    ax=ax2
)
ax2.set_xlabel('Rating', fontsize=12)
ax2.set_ylabel('', fontsize=12)
ax2.set_title('Top 10 Phim Có Rating Cao Nhất', fontsize=14, pad=20)
ax2.grid(axis='x', alpha=0.3)

# Thêm giá trị rating vào mỗi thanh
for i, (score, name) in enumerate(zip(top_movies['score'], top_movies['name'])):
    ax2.text(score, i, f' {score:.1f}', va='center', ha='left', fontsize=10)

st.pyplot(fig2)

# ========================================
# BIỂU ĐỒ 3: TƯƠNG QUAN NGÂN SÁCH - DOANH THU
# ========================================
st.header("Mối Quan Hệ Giữa Ngân Sách và Doanh Thu")
fig3, ax3 = plt.subplots(figsize=(10, 6))
scatter = sns.scatterplot(
    data=filtered_data,
    x='budget',
    y='gross',
    hue='score',
    size='score',
    sizes=(20, 200),
    palette='coolwarm',
    alpha=0.7,
    ax=ax3
)
ax3.set_xlabel('Ngân sách (triệu USD)', fontsize=12)
ax3.set_ylabel('Doanh thu (triệu USD)', fontsize=12)
ax3.set_title('Mối Quan Hệ Giữa Ngân Sách và Doanh Thu', fontsize=14, pad=20)
ax3.grid(alpha=0.3)

# Điều chỉnh legend
plt.legend(
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    title='Rating',
    borderaxespad=0.
)

st.pyplot(fig3)

# ========================================
# BIỂU ĐỒ 4: XU HƯỚNG NGÂN SÁCH QUA CÁC NĂM
# ========================================
st.header("Xu Hướng Ngân Sách Phim Qua Các Năm")

# Tính toán dữ liệu theo năm
budget_trend = filtered_data.groupby('year')['budget'].mean().reset_index()

fig4, ax4 = plt.subplots(figsize=(10, 6))
sns.lineplot(
    data=budget_trend,
    x='year',
    y='budget',
    marker='o',
    color='purple',
    linewidth=2.5,
    markersize=8,
    ax=ax4
)
ax4.set_xlabel('Năm', fontsize=12)
ax4.set_ylabel('Ngân sách trung bình (triệu USD)', fontsize=12)
ax4.set_title('Xu Hướng Ngân Sách Phim Qua Các Năm', fontsize=14, pad=20)
ax4.grid(True, alpha=0.3)

# Định dạng trục y
ax4.yaxis.set_major_formatter('${x:,.0f}M')

st.pyplot(fig4)

# ========================================
# HIỂN THỊ DỮ LIỆU THÔ
# ========================================
st.header("📋 Bản Dữ Liệu Thô")
with st.expander("Xem toàn bộ dữ liệu đã lọc", expanded=False):
    st.dataframe(
        filtered_data,
        column_config={
            "budget": st.column_config.NumberColumn("Ngân sách", format="$%.2f M"),
            "gross": st.column_config.NumberColumn("Doanh thu", format="$%.2f M"),
            "profit": st.column_config.NumberColumn("Lợi nhuận", format="$%.2f M"),
            "roi": st.column_config.NumberColumn("ROI", format="%.2f%%")
        },
        hide_index=True,
        use_container_width=True
    )

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
**Ghi chú:**
- Dữ liệu được làm sạch bằng cách loại bỏ các bản ghi có giá trị thiếu
- Tất cả giá trị tiền tệ được tính bằng triệu USD
- ROI (Return on Investment) = (Lợi nhuận/Ngân sách) × 100%
- Dữ liệu được lấy từ nguồn công khai trên GitHub
""")
st.caption(f"© {datetime.now().year} - Phân tích Điện Ảnh | Cập nhật lần cuối: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")