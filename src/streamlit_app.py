from datetime import datetime
from pathlib import Path
import streamlit as st
from streamlit_echarts import st_echarts

from data_loader import load_earnings_report
from data_processor import generate_reports
from plotting import generate_echarts_rates_plot_options
from utils import convert_df_to_csv

st.set_page_config(layout="wide")


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
DEFAULT_RATE_PLOT_TITLE = 'Sample Data'
DEFAULT_PLOT_OPTIONS = {
    "title": {"text": DEFAULT_RATE_PLOT_TITLE},
    "tooltip": {
        "trigger": "axis",
        "confine": True
    },
    "color": ['red', 'blue'],
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
    st.session_state.rates_plot_title = DEFAULT_RATE_PLOT_TITLE

if 'rates_plot_options' not in st.session_state:
    st.session_state.rates_plot_options = DEFAULT_PLOT_OPTIONS

if 'earnings_plot_options' not in st.session_state:
    st.session_state.earnings_plot_options = None

if 'counts_plot_options' not in st.session_state:
    st.session_state.counts_plot_options = None

# widgets
if 'distributor' not in st.session_state:
    st.session_state.distributor = 'CD Baby'

if 'earnings_data_file' not in st.session_state:
    st.session_state.earnings_data_file = None

if 'raw_earnings_data' not in st.session_state:
    st.session_state.raw_earnings_data = None

if 'transactions' not in st.session_state:
    st.session_state.transactions = ['Stream']


# Processed outputs
if 'earnings_data' not in st.session_state:
    st.session_state.earnings_data = None

if 'rates_data' not in st.session_state:
    st.session_state.rates_data = None

if 'counts_data' not in st.session_state:
    st.session_state.counts_data = None


def load_earnings_data() -> None:
    """Load earnings data"""
    distributor_map = {
        'CD Baby': 'cd_baby', # TODO: add 'DistroKid': 'distrokid'
    }
    distributor_code = distributor_map.get(st.session_state.distributor)
    service_map_file = Path('data/partner_map_simplified.csv')

    if st.session_state.earnings_data_file:
        _file = st.session_state.earnings_data_file
    else:
        _file = 'data/sample_data/sample_data_cd_baby.txt'

    st.session_state.raw_earnings_data = load_earnings_report(
        _file, distributor_code, service_map_file
    )


available_transactions = {
    'CD Baby': ['Stream', 'Download', 'Royalty', 'YouTube Audio Tier'],
    # TODO: 'DistroKid': ['Stream', 'Download']
}


def run_report():
    """Run report generator"""

    transaction_map = {
        'Stream': 'stream',
        'Download': 'download',
        'Royalty': 'royalty',
        'YouTube Audio Tier': 'youtube_audio_tier'
    }
    transaction_codes = [transaction_map.get(t) for t in st.session_state.transactions]

    # TODO: load this by default in the sample data
    if st.session_state.earnings_data_file is None:
        st.session_state.earnings_data_file = 'data/sample_data/sample_data_cd_baby.txt'


    # Generate summary report
    summary_reports = generate_reports(
        st.session_state.raw_earnings_data,
        transaction_codes,
        adjust_for_inflation=st.session_state.adjust_for_inflation
    )

    # Display plot
    transactions_str = ', '.join(st.session_state.transactions).title()

    if st.session_state.adjust_for_inflation:
        inflation_str = ' - Adjusted for Inflation'
        st.session_state.rates_data = summary_reports['cpi_adjusted_rates']
        st.session_state.earnings_data = summary_reports['cpi_adjusted_earnings']
    else:
        inflation_str = ''
        st.session_state.rates_data = summary_reports['rates']
        st.session_state.earnings_data = summary_reports['earnings']

    # rates
    st.session_state.rates_plot_options = generate_echarts_rates_plot_options(
        st.session_state.rates_data,
        title_text=f'{transactions_str} Transactions - Rates{inflation_str}'
    )

    # earnings
    st.session_state.earnings_plot_options = generate_echarts_rates_plot_options(
        st.session_state.earnings_data,
        title_text=f'{transactions_str} Transactions - Earnings{inflation_str}'
    )

    # counts
    st.session_state.counts_data = summary_reports['counts']
    st.session_state.counts_plot_options = generate_echarts_rates_plot_options(
        st.session_state.counts_data,
        title_text=f'{transactions_str} Transactions - Counts'
    )

    return


# Page Layout

def display_sidebar():
    """Display the sidebar"""
    with st.sidebar:

        distributor = st.selectbox(
            label='**Step 1:** Select your distributor.', 
            options=['CD Baby'], # TODO: add 'DistroKid'
            key='distributor'
        )

        earnings_data_file = st.session_state.earnings_data_file = st.file_uploader(
            label='**Step 2:** Upload your payout data file.',
            accept_multiple_files=False,
            type=['.csv', '.txt', 'xlsx']
        )
        load_earnings_data()

        transactions = st.multiselect(
            label='**Step 3:** Which transaction types should be included in the report?',
            options=available_transactions.get(distributor),
            key='transactions'
        )

        adjust_for_inflation = st.checkbox(
            label='**Step 4:** Adjust for inflation? ',
            value=False,
            key='adjust_for_inflation'
        )

        run_report_button = st.button(
            label='Run Report!',
            on_click=run_report
        )

    return


def display_page() -> None:
    """Display the main page"""
    st.markdown("""
    # Streams of Consciousness
    Welcome to *Streams of Conciousness*!  
    This app allows musicians to quickly view their own streaming
    pay-out rates for different streaming platforms, over time.
        
    Use the left sidebar to load your data and configure graph options.

    ---
    """
    )
    # Downloader filename
    adjusted = '_adjusted' if st.session_state.adjust_for_inflation else ''
    timestamp = datetime.now().strftime("%Y%m%d")

    st_echarts(
        options=st.session_state.rates_plot_options,
        height="400px",
        key='rates_plot'
    )
    if 'rates_data' in st.session_state and st.session_state.rates_data is not None:
        rates_csv = convert_df_to_csv(st.session_state.rates_data)
        st.download_button(
            label="Download CSV",
            data=rates_csv,
            file_name=f'soc_streaming_rates{adjusted}_{timestamp}.csv',
            mime='text/csv',
        )

    st_echarts(
        options=st.session_state.earnings_plot_options,
        height="400px",
        key='earnings_plot'
    )
    if 'earnings_data' in st.session_state and st.session_state.earnings_data is not None:
        earnings_csv = convert_df_to_csv(st.session_state.earnings_data)
        st.download_button(
            label="Download CSV",
            data=earnings_csv,
            file_name=f'soc_streaming_earnings{adjusted}_{timestamp}.csv',
            mime='text/csv',
        )

    st_echarts(
        options=st.session_state.counts_plot_options,
        height="400px",
        key='counts_plot'
    )
    if 'counts_data' in st.session_state and st.session_state.counts_data is not None:
        counts_csv = convert_df_to_csv(st.session_state.counts_data)
        st.download_button(
            label="Download CSV",
            data=counts_csv,
            file_name=f'soc_streaming_counts_{timestamp}.csv',
            mime='text/csv',
        )
    return


def main():
    """Render Streamlit App"""
    display_sidebar()
    display_page()


if __name__ == "__main__":
    main()
