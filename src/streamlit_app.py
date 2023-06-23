from pathlib import Path
import streamlit as st
from data_loader import load_earnings_report
from data_processor import generate_reports
from plotting import generate_bokeh_plot


@st.cache_data
def load_earnings_data(data_file_path, distributor):
    partner_map_file = Path('data/streaming_services/partner_map_simplified.csv')
    data = load_earnings_report(data_file_path, distributor, partner_map_file)
    return data


st.write("""
    # Streams of Consciousness
    Welcome to *Streams of Conciousness*!  
    This tool allows musicians to quickly view their own stremaing
    pay-out rates for different streaming platforms, over time.
    
    ---
    """
)


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
    label='**Step 3:** Should we adjust for inflation?', 
    value=True
)


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
    summary_reports = generate_reports(earnings_data, transaction_codes, adjust_for_inflation=True)

    # Display plot
    transactions_str = ', '.join(transactions).title()
    
    if adjust_for_inflation:
        rates = summary_reports['cpi_adjusted_rates']
        title = f'{transactions_str} Transactions - Adjusted for inflation'
    
    else:
        rates = summary_reports['rates']
        title = f'{transactions_str} Transactions - Nominal rates'
         
    plot = generate_bokeh_plot(rates, title_text=title)
    st.bokeh_chart(plot)


st.button(
    label='Run Report!',
    on_click=run_report
)