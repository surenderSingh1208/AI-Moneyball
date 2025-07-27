import streamlit as st
import pandas as pd
import io

# ---- Custom CSS ----
st.markdown("""
    <style>
    /* Background and font */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f8f9fa;
    }
    /* Title */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    /* Subtext */
    .sub-text {
        text-align: center;
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 30px;
    }
    /* Card styling */
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        background: #fff;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
    /* Button customization */
    div.stDownloadButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 1rem;
        transition: background-color 0.3s;
    }
    div.stDownloadButton > button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown('<div class="main-title">Referral Commission Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Upload referral and transaction Excel files to calculate commissions</div>', unsafe_allow_html=True)

# ---- File Upload Section in two columns ----
col1, col2 = st.columns(2)
with col1:
    referral_file = st.file_uploader("Upload Referral Excel", type=["xlsx", "xls"])
with col2:
    transaction_file = st.file_uploader("Upload Transaction Excel", type=["xlsx", "xls"])

# ---- Processing Logic ----
if referral_file and transaction_file:
    try:
        # Load files
        referral_df = pd.read_excel(referral_file)
        txn_df = pd.read_excel(transaction_file)

        # Standardize columns
        referral_df.columns = referral_df.columns.str.strip().str.lower()
        txn_df.columns = txn_df.columns.str.strip().str.lower()

        # Merge on client code + payment mode
        merged_df = pd.merge(
            txn_df,
            referral_df,
            left_on=["client_code", "payment_mode"],
            right_on=["client", "payment mode"],
            how="left"
        )

        # Commission calculation
        def calculate_commission(row):
            if pd.isna(row["rates types"]) or pd.isna(row["rates"]):
                return 0

            rate_type = str(row["rates types"]).strip().lower()
            rate = row["rates"]

            if rate_type == "percentage":
                rate_factor = rate / 100 if rate > 1 else rate
                return round(row["payee_amount"] * rate_factor, 4)
            elif rate_type == "fixed":
                return round(rate, 4)
            else:
                return 0

        merged_df["Referral_Commission"] = merged_df.apply(calculate_commission, axis=1)

        # ---- Display Result ----
        st.subheader("Preview of Calculated Commissions")
        st.dataframe(merged_df.head(20))

        # ---- Download Button ----
        output = io.BytesIO()
        merged_df.to_excel(output, index=False)
        st.download_button(
            label="Download Processed Excel",
            data=output.getvalue(),
            file_name="referral_commission_calculated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error processing files: {e}")
