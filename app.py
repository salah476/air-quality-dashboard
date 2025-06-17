import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Air Quality Dashboard - Milan")

# رفع الملف
uploaded_file = st.file_uploader("Upload your AirQualityUCI.xlsx file", type=["xlsx"])

# دالة لتقييم جودة الهواء حسب تركيز كل ملوث
def air_quality_status(value, pollutant):
    # تعاريف مبدئية لمستويات الخطورة (ممكن تضبط حسب المعايير المحلية)
    thresholds = {
        'CO(GT)': [4.5, 9.5, 12.5],            # مثال: قيم بالميكروغرام/م3 أو حسب المصدر
        'NMHC(GT)': [150, 300, 400],
        'C6H6(GT)': [5, 10, 15],
        'PT08.S2(NMHC)': [100, 200, 300],
        'NOx(GT)': [100, 200, 400],
        'PT08.S3(NOx)': [150, 300, 450],
        'NO2(GT)': [40, 80, 120],
        'PT08.S4(NO2)': [150, 300, 450],
        'PT08.S5(O3)': [100, 180, 240],
        'T': [0, 35, 50],                   # درجة الحرارة (ممكن نعتبر فوق 35 حار جداً)
        'RH': [30, 60, 90],                 # رطوبة نسبية (مثال)
        'AH': [5, 10, 15]                   # رطوبة مطلقة (مثال)
    }

    if pd.isna(value):
        return "No Data"
    if pollutant not in thresholds:
        return "Unknown"

    low, med, high = thresholds[pollutant]
    if value <= low:
        return "Good"
    elif value <= med:
        return "Moderate"
    elif value <= high:
        return "Unhealthy"
    else:
        return "Very Unhealthy"

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Raw Data Sample")
    st.dataframe(df.head())

    # نختار الأعمدة المهمة فقط
    columns_needed = ['CO(GT)', 'NMHC(GT)', 'C6H6(GT)', 'PT08.S2(NMHC)', 'NOx(GT)', 
                      'PT08.S3(NOx)', 'NO2(GT)', 'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH', 'PT08.S1(CO)']
    df = df[columns_needed]

    st.subheader("Air Quality Status per Pollutant")
    status_df = pd.DataFrame()
    for col in columns_needed[:-1]:  # نستثني الحساس PT08.S1(CO) لأنه توقع
        status_df[col] = df[col].apply(lambda x: air_quality_status(x, col))

    st.dataframe(status_df.head())

    st.subheader("Dashboard: Pollutants Levels")
    # رسم بياني لكل متغير
    cols = st.columns(3)
    for i, col_name in enumerate(columns_needed[:-1]):
        with cols[i % 3]:
            st.write(f"### {col_name}")
            fig, ax = plt.subplots()
            sns.histplot(df[col_name].dropna(), bins=30, kde=True, ax=ax)
            ax.set_xlabel(col_name)
            st.pyplot(fig)

    st.subheader("Correlation with PT08.S1(CO) Sensor (Predicted CO)")

    # نرسم العلاقة بين PT08.S1(CO) وكل ملوث تاني
    corr_df = df.dropna()
    corr = corr_df.corr()
    
    # عرض مصفوفة الارتباط (Correlation matrix)
    st.write(corr['PT08.S1(CO)'].sort_values(ascending=False))

    st.write("Scatter Plots with PT08.S1(CO)")

    for col in columns_needed[:-1]:
        fig, ax = plt.subplots()
        ax.scatter(corr_df['PT08.S1(CO)'], corr_df[col], alpha=0.5)
        ax.set_xlabel('PT08.S1(CO) Sensor')
        ax.set_ylabel(col)
        ax.set_title(f"{col} vs PT08.S1(CO)")
        st.pyplot(fig)
else:
    st.write("Please upload the AirQualityUCI.xlsx file to start the analysis.")
