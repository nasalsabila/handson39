import streamlit as st
import pandas as pd 
import numpy as np 
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Portofolio Kim Sejeong",
    page_icon="👩‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# fungsi untuk load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/data_dummy_retail_store.csv")


# load data retail 
df_sales = load_data()
df_sales.columns = df_sales.columns.str.lower().str.replace(' ', '_')
df_sales['tanggal_pesanan'] = pd.to_datetime(df_sales['tanggal_pesanan']) 

# sidebar 
st.sidebar.header("Pengaturan & Navigasi")

pilihan_halaman = st.sidebar.radio(
    "Pilih Halaman:",
    ("Profil", "Dashboard Penjualan", "Prediksi Penjualan")
)

if pilihan_halaman == "Profil":
    st.title("Tentang Saya")
    st.markdown("*Siapa Kim Sejeong?*")

    st.write("Halo! Saya adalah **Kim Sejong**. Aspirasi saya menjadi *data analyst & scientist*.")
    st.image("assets/Kim_Se-Jeong-Gugudan-p1.jpeg", width=200, caption="Saya yang cantik rupawan")

    st.header("Skills:")
    st.markdown("""
        * Pemrograman
            * Python 
            * PostgreSQL
            * MySQL
        * Softskills
            * Problem Solving
            * Critical Thinking
    """)

    st.write("Butuh saya untuk jadi DA/DS? Kontak saya di kimsejeong@gmail.com")

elif pilihan_halaman == "Dashboard Penjualan":
    st.title("Dashboard Penjualan Toko Kim")
    st.markdown("---")

    st.sidebar.markdown("### Filter Data Dashboard")

    min_date = df_sales['tanggal_pesanan'].min().date()
    max_date = df_sales["tanggal_pesanan"].max().date()

    # filter tanggal
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date_filter = pd.to_datetime(date_range[0])
        end_date_filter = pd.to_datetime(date_range[1])
        filtered_df = df_sales[(df_sales['tanggal_pesanan'] >= start_date_filter) &
                               (df_sales['tanggal_pesanan'] <= end_date_filter)]
    else: 
        filtered_df = df_sales


    # filter wilayah
    selected_regions = st.sidebar.multiselect(
        "Pilih Wilayah:",
        options=df_sales['wilayah'].unique().tolist(),
        default=df_sales['wilayah'].unique().tolist()
    )
    filtered_df = filtered_df[filtered_df['wilayah'].isin(selected_regions)]

    col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

    total_sales = filtered_df['total_penjualan'].sum()
    total_orders = filtered_df['orderid'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    total_products_sold = filtered_df['jumlah'].sum()

    with col1:
        st.metric(label="Total Penjualan", value=f"Rp {total_sales:,.2f}")
    with col2:
        st.metric(label="Jumlah Pesanan", value=f"{total_orders:,}")
    with col3:
        st.metric(label="Rata-rata Nilai Pesanan", value=f"Rp {avg_order_value:,.2f}")
    with col4:
        st.metric(label="Jumlah Produk Terjual", value=f"{total_products_sold:,}")

    st.markdown("---")

    # monthly sales (line chart)
    st.subheader("Tren Penjualan Bulanan")
    sales_by_month = filtered_df.groupby('bulan')['total_penjualan'].sum().reset_index()

    sales_by_month['bulan'] = pd.to_datetime(sales_by_month['bulan']).dt.to_period('M')
    sales_by_month = sales_by_month.sort_values('bulan') # memastikan urutan bulannya benar
    sales_by_month['bulan'] = sales_by_month['bulan'].astype(str) # balikin untuk string untuk plotly

    fig_monthly_sales = px.line(
        sales_by_month,
        x='bulan',
        y='total_penjualan',
        title='Monthly Sales'
    )
    st.plotly_chart(fig_monthly_sales, use_container_width=True)

    st.subheader("Performa Penjualan Lebih Detail")
    tab1, tab2 = st.tabs(["Metode Pembayaran", "Penjualan per Wilayah"])

    with tab1:
        st.write("#### Penjualan Berdasarkan Metode Pembayaran")

        sales_by_payment = (
            filtered_df.groupby('metode_pembayaran')['total_penjualan']
            .sum()
            .reset_index()
        )

        fig_payment = px.bar(
            sales_by_payment,
            x='metode_pembayaran',
            y='total_penjualan',
            title='Total Penjualan per Metode Pembayaran',
            color='metode_pembayaran',
            color_discrete_sequence=px.colors.qualitative.Vivid  # Skema warna cerah
        )

        st.plotly_chart(fig_payment, use_container_width=True)
    
    with tab2:
        st.write("#### Penjualan Berdasarkan Wilayah")
        sales_by_region = (
            filtered_df.groupby('wilayah')['total_penjualan']
            .sum()
            .reset_index()
        )

        fig_region = px.bar(
            sales_by_region,
            x='wilayah',
            y='total_penjualan',
            title='Total Penjualan per Wilayah',
            color='wilayah',
            color_discrete_sequence=px.colors.qualitative.Safe  # Warna yang lebih lembut
        )

        st.plotly_chart(fig_region, use_container_width=True)

    st.subheader("Eksplorasi Raw Data")

    with st.expander("Klik untuk melihat data"):
        st.write("Berikut adalah sebagian kecil dari data transaksi yang digunakan untuk dashboard ini.")

        num_rows_to_display = st.slider(
            "Jumlah baris yang ditampilkan",
            min_value = 10,
            max_value = 200,
            value = 50, 
            step = 10
        )

        st.dataframe(filtered_df.head(num_rows_to_display))

        st.write("Statistik Deskriptif")
        st.dataframe(filtered_df.describe())
    


        


