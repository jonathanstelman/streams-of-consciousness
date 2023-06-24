import click
import logging
from pathlib import Path
from bokeh.plotting import show

from data_processor import generate_reports, load_earnings_report
import enums
import plotting


logging.basicConfig(
    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
    level=logging.INFO
)

allowed_distributors = [d.value for d in enums.Distributor]
allowed_transactions = [t.value for t in enums.Transaction]


@click.command()
@click.argument('file_name', type=click.Path(exists=True), nargs=1)
@click.argument('distributor', type=click.Choice(allowed_distributors), default='cd_baby', nargs=1)
@click.argument('transactions', type=click.Choice(allowed_transactions), nargs=-1)
def main(file_name, distributor, transactions) -> None:
    
    source_data_path = Path(file_name)
    partner_map_path = Path('data/partner_map_simplified.csv')
    
    logging.info(f'Loading data from file: {source_data_path.name}...')
    earnings_report = load_earnings_report(source_data_path, distributor, partner_map_path)

    # TODO: separate reports into different functions
    # TODO: move the reports into a dataclass
    logging.info('Generating summary reports...')
    summary_reports = generate_reports(earnings_report, transactions, adjust_for_inflation=True)

    logging.info('Generating interactive graph...')
    transactions_str = ', '.join(transactions).title() + ' Transactions - '
    plot_1 = plotting.generate_bokeh_plot(summary_reports['rates'], title_text=f'{transactions_str} Nominal')
    plot_2 = plotting.generate_bokeh_plot(summary_reports['cpi_adjusted_rates'], title_text=f'{transactions_str} Adjusted for inflation')

    show(plot_1)
    show(plot_2)
    
if __name__ == '__main__':
    main()