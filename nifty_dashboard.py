
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from nsepy import get_history
from datetime import date

st.set_page_config(page_title="Nifty June-July Analysis", layout="wide")

june_start = date(2025, 6, 1)
june_end = date(2025, 6, 30)
july_start = date(2025, 7, 1)
today = date.today()

nifty_indices = [
    ("NIFTY 50", "NIFTY"),
    ("NIFTY BANK", "BANKNIFTY"),
    ("NIFTY IT", "NIFTYIT"),
    ("NIFTY FMCG", "NIFTYFMCG"),
    ("NIFTY PHARMA", "NIFTYPHARMA"),
    ("NIFTY AUTO", "NIFTYAUTO"),
    ("NIFTY METAL", "NIFTYMETAL"),
    ("NIFTY FINANCIAL SERVICES", "NIFTYFIN"),
    ("NIFTY ENERGY", "NIFTYENERGY"),
    ("NIFTY REALTY", "NIFTYREALTY")
]

@st.cache_data
def get_index_data():
    results = []
    for index_symbol, display_name in nifty_indices:
        try:
            june_data = get_history(symbol=display_name, index=True, index_symbol=index_symbol,
                                    start=june_start, end=june_end)
            if june_data.empty:
                continue
            june_high = june_data['High'].max()
            june_low = june_data['Low'].min()

            july_open_data = get_history(symbol=display_name, index=True, index_symbol=index_symbol,
                                         start=july_start, end=july_start)
            july_open = july_open_data['Open'].iloc[0] if not july_open_data.empty else None

            if july_open is None:
                open_status = "Data Missing"
            elif july_open > june_high:
                open_status = "Above June High"
            elif july_open < june_low:
                open_status = "Below June Low"
            else:
                open_status = "Within Range"

            july_data = get_history(symbol=display_name, index=True, index_symbol=index_symbol,
                                    start=july_start, end=today)
            trigger_high = any(july_data['High'] >= june_high) if not july_data.empty else False
            trigger_low = any(july_data['Low'] <= june_low) if not july_data.empty else False

            results.append({
                "Index": display_name,
                "June High": june_high,
                "June Low": june_low,
                "July Open": july_open,
                "Open Status": open_status,
                "Touched June High": "Yes" if trigger_high else "No",
                "Touched June Low": "Yes" if trigger_low else "No"
            })

        except Exception as e:
            results.append({"Index": display_name, "Error": str(e)})
    return pd.DataFrame(results)

df = get_index_data()

st.title("📊 Nifty Indices June-July Analysis Dashboard")
st.dataframe(df, use_container_width=True)

st.subheader("📈 Comparison: June High, June Low, July Open")
fig = go.Figure()
fig.add_trace(go.Bar(x=df["Index"], y=df["June High"], name="June High", marker_color='skyblue'))
fig.add_trace(go.Bar(x=df["Index"], y=df["June Low"], name="June Low", marker_color='orange'))
fig.add_trace(go.Bar(x=df["Index"], y=df["July Open"], name="July Open", marker_color='green'))

fig.update_layout(barmode='group', xaxis_title="Index", yaxis_title="Value", height=500)
st.plotly_chart(fig, use_container_width=True)

st.subheader("🚨 Trigger Summary (Touched June High/Low)")
col1, col2 = st.columns(2)
with col1:
    st.write("📌 Touched June High")
    st.write(df[df["Touched June High"] == "Yes"][["Index"]])
with col2:
    st.write("📌 Touched June Low")
    st.write(df[df["Touched June Low"] == "Yes"][["Index"]])

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV Report", data=csv, file_name="nifty_june_july_analysis.csv", mime='text/csv')
