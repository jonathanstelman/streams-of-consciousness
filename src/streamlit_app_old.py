from pathlib import Path
import streamlit as st
from streamlit_echarts import st_echarts

from data_loader import load_earnings_report
from data_processor import generate_reports
from plotting import generate_echarts_rates_plot_options


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
DEFAULT_RATE_GRAPH_TITLE = 'Sample Data'
DEFUALT_GRAPH_OPTIONS = {
    "title": {"text": DEFAULT_RATE_GRAPH_TITLE},
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

# Configure session state
if 'data' not in st.session_state:
    st.session_state.data = _sample_data

if 'rates_plot_title' not in st.session_state:
    st.session_state.rates_plot_title = DEFAULT_RATE_GRAPH_TITLE

if 'rates_plot_options' not in st.session_state:
    st.session_state.rates_plot_options = DEFUALT_GRAPH_OPTIONS

if 'earnings_data_file' not in st.session_state:
    st.session_state.earnings_data_file = None


# Processed outputs
if 'earnings_data' not in st.session_state:
    st.session_state.earnings_data = None

if 'rates_data' not in st.session_state:
    st.session_state.rates_data = None



def load_earnings_data(data_file_path, distributor):
    """Load the earnings report for a specified distributor"""
    partner_map_file = Path('data/partner_map_simplified.csv')
    data = load_earnings_report(data_file_path, distributor, partner_map_file)
    return data


def run_report():
    """Generate a report"""

    # Load the data
    distributor_map = {
        'CD Baby': 'cd_baby',
        'DistroKid (n/a)': 'distrokid'
    }
    distributor_code = distributor_map.get(st.session_state.distributor)

    transaction_map = {
        'Stream': 'stream',
        'Download': 'download',
        'Royalty': 'royalty',
        'YouTube Audio Tier': 'youtube_audio_tier'
    }
    transaction_codes = [transaction_map.get(t) for t in st.session_state.transactions]

    if st.session_state.earnings_data_file is None:
        st.session_state.earnings_data_file = 'data/sample_data/sample_data_cd_baby.txt'

    # TODO: try/ catch / exception handling
    earnings_data = load_earnings_data(st.session_state.earnings_data_file, distributor_code)

    # Generate summary report
    summary_reports = generate_reports(
        earnings_data,
        transaction_codes,
        adjust_for_inflation=st.session_state.adjust_for_inflation
    )

    # Display plot
    transactions_str = ', '.join(transactions).title()

    if st.session_state.adjust_for_inflation:
        st.session_state.rates_data = summary_reports['cpi_adjusted_rates']
        st.session_state.rates_plot_title = f'{transactions_str} Transactions - Adjusted for Inflation'

    else:
        st.session_state.rates_data = summary_reports['rates']
        st.session_state.rates_plot_title = f'{transactions_str} Transactions - Nominal Rates'

    graph_options = generate_echarts_rates_plot_options(
        st.session_state.rates_data,
        title_text=st.session_state.rates_plot_title
    )

    st.session_state.rates_plot_options = graph_options



st.write("""
    # Streams of Consciousness
    Welcome to *Streams of Conciousness*!  
    This app allows musicians to quickly view their own streaming
    pay-out rates for different streaming platforms, over time.
         
    Use the sidebar on the left to load your data and configure graph options
    
    ---
    """
)

with st.sidebar:
    st.session_state.earnings_data_file = st.file_uploader(
        label='**Step 1:** Upload your payout data file.',
        accept_multiple_files=False,
        type=['.csv', '.txt', 'xlsx']
    )

    distributor = st.selectbox(
        label='**Step 2:** Select your distributor.', 
        options=['CD Baby', 'DistroKid (n/a)'],
        key='distributor'
    )

    transactions = st.multiselect(
        label='**Step 3:** Which transaction types should be included in the report?',
        options=['Stream', 'Download', 'Royalty', 'YouTube Audio Tier'],
        default=['Stream'],
        key='transactions'
    )

    adjust_for_inflation = st.checkbox(
        label='**Step 4:** Adjust for inflation? (Adds about 1 minute)', 
        value=False,
        key='adjust_for_inflation'
    )

    st.button(
        label='Run Report!',
        on_click=run_report
    )

st_echarts(options=st.session_state.rates_plot_options, height="400px")
