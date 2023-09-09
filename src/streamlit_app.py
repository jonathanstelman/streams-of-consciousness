from pathlib import Path
import streamlit as st
from streamlit_echarts import st_echarts

from data_loader import load_earnings_report
from data_processor import generate_reports
#from plotting import generate_bokeh_plot
from plotting import generate_echarts_rates_graph_options


_sample_companies = ['Company A', 'Company B']
_sample_data = []
for i, company in enumerate(_sample_companies):
    values = [0.03,0.025,0.02,0.01] if i == 0 else [0.025,0.035,0.03,0.032]
    _sample_data.append({
        'name': company,
        'type': 'line',
        'symbol': 'circle',
        'symbolSize': 4,
        'data': values
    })
_default_rate_graph_title = 'Sample Data'
_default_graph_options = {
    "title": {"text": _default_rate_graph_title},
    "tooltip": {
        "trigger": "axis",
        "confine": True
    },
    "color": ['red', 'blue'], #colors,
    "emphasis": {"focus": "series"},
    "legend": {
        "orient": "vertical",
        "right": 10,
        "top": "center", 
        "data": _sample_companies
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "toolbox": {"feature": {"saveAsImage": {}}},
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "data": ['2020', '2021', '2022', '2023']
    },
    "yAxis": {"type": "value"},
    "series": _sample_data
}

if 'data' not in st.session_state:
    st.session_state.data = _sample_data
if 'rates_plot_title' not in st.session_state:
    st.session_state.rates_plot_title = _default_rate_graph_title
if 'rates_plot_options' not in st.session_state:
    st.session_state.rates_plot_options = _default_graph_options


def load_earnings_data(data_file_path, distributor):
    partner_map_file = Path('data/partner_map_simplified.csv')
    data = load_earnings_report(data_file_path, distributor, partner_map_file)
    return data


def run_report():

    # Load the data
    distributor_map = {
        'CD Baby': 'cd_baby',
        'DistroKid (n/a)': 'distrokid'
    }
    distributor_code = distributor_map.get(distributor)

    transaction_map = {
        'Stream': 'stream',
        'Download': 'download',
        'Royalty': 'royalty',
        'YouTube Audio Tier': 'youtube_audio_tier'
    }
    transaction_codes = [transaction_map.get(t) for t in transactions]

    if uploaded_file is None:
        pass

    # TODO: try/ catch / exception handling
    earnings_data = load_earnings_data(uploaded_file, distributor_code)

    # Generate summary report
    summary_reports = generate_reports(
        earnings_data, 
        transaction_codes, 
        adjust_for_inflation=adjust_for_inflation
    )

    # Display plot
    transactions_str = ', '.join(transactions).title()
    
    if adjust_for_inflation:
        rates = summary_reports['cpi_adjusted_rates']
        title = f'{transactions_str} Transactions - Adjusted for Inflation'
    
    else:
        rates = summary_reports['rates']
        title = f'{transactions_str} Transactions - Nominal Rates'

    
         
    # plot = generate_bokeh_plot(rates, title_text=title)
    # st.bokeh_chart(plot)

    graph_options = generate_echarts_rates_graph_options(rates, title_text=title)

    #st_echarts(options=graph_options, height="400px")
    st.session_state.rates_plot_options = graph_options
    



st.write("""
    # Streams of Consciousness
    Welcome to *Streams of Conciousness*!  
    This app allows musicians to quickly view their own stremaing
    pay-out rates for different streaming platforms, over time.
         
    Use the sidebar on the left to load your data and configure graph options
    
    ---
    """
)

with st.sidebar:
    uploaded_file = st.file_uploader(
        label='**Step 1:** Upload your payout data file.',
        accept_multiple_files=False,
        type=['.csv', '.txt', 'xlsx']
    )

    distributor = st.selectbox(
        label='**Step 2:** Select your distributor.', 
        options=['CD Baby', 'DistroKid (n/a)']
    )

    transactions = st.multiselect(
        label='**Step 3:** Which transaction types should be included in the report?',
        options=['Stream', 'Download', 'Royalty', 'YouTube Audio Tier'],
        default=['Stream'])

    adjust_for_inflation = st.checkbox(
        label='**Step 4:** Adjust for inflation? (Adds about 1 minute)', 
        value=False
    )

    st.button(
        label='Run Report!',
        on_click=run_report
    )

#st.header('Streaming Rates over Time', divider='rainbow')
st_echarts(options=st.session_state.rates_plot_options, height="400px")