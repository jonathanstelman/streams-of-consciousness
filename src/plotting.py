from math import floor
import bokeh
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Legend, NumeralTickFormatter, Title, Range1d
import pandas as pd

def generate_bokeh_plot(
            rates: pd.DataFrame,
            size=(1000, 500),
            title_text='Nominal rates (unadjusted)'
        ):
    """generate a bokeh plot of transation rates over time
    """
    years = rates.columns.values
    companies = rates.index.values
    palette = bokeh.palettes.all_palettes['Turbo'][256][32:]
    skip = floor(len(palette) / len(companies))
    colors = [palette[i*skip] for i in range(len(companies))]
    
    TOOLS = 'pan,wheel_zoom,reset,save,box_select'
    TOOLTIPS = [('Company', '@Company'), 
                ('Year', '@Year'),
                ('Rate', '@Rate{$0.0000}')]
    p = figure(
            width=size[0], 
            height=size[1],
            tools=TOOLS,
            tooltips=TOOLTIPS
        )
    
    legend_it = []
    for i, company in enumerate(rates.index.values):
        source = ColumnDataSource(
            data = {
                'Year': years,
                'Rate': rates.iloc[i].values,
                'Company': [company]*len(years)
            }
        )
        c = p.circle('Year', 'Rate', source=source, color=colors[i], size=2)
        l = p.line('Year', 'Rate', source=source, color=colors[i])
        legend_it.append((company, [c, l]))
    
    p.add_layout(
        Title(
            text='Single artist report - do not use for general market trends'.upper(), 
            text_font_style='italic'), 'above'
    )

    p.add_layout(
        Title(
            text=title_text,
            text_font_size='10pt'), 'above'
    )

    p.add_layout(
        Title(
            text='Royalty Transaction Rates over Time',
            text_font_size='16pt'), 'above'
    )

    p.background_fill_color = 'black'
    p.ygrid.grid_line_color = '#333'
    p.xgrid.grid_line_color = None

    p.x_range = Range1d(2009.9, 2022.1, bounds=(2000, 2030))
    p.y_range = Range1d(0, 0.04, bounds=(0, .2))
    p.yaxis[0].formatter = NumeralTickFormatter(format='$ 0.000')

    legend = Legend(items=legend_it, click_policy='hide')
    p.add_layout(legend, 'right')

    # TODO: figure out how to make the wheel zoom default scroll
    # p.toolbar.active_inspect = [pan, wheel_zoom]
    
    return p




def generate_echarts_graph(
            rates: pd.DataFrame,
            #size=(1000, 500),
            title_text='Nominal rates (unadjusted)'
        ):

    years = [str(y) for y  in rates.columns.values] + \
        [str(max(rates.columns.values)+1), str(max(rates.columns.values)+2)]
    companies = [str(c) for c in rates.index.values]
    
    def convert_rate(value, precision=4):
        if pd.isnull(value): return None
        return round(value, precision)

    series = []
    for i, company in enumerate(companies):
        values = [convert_rate(v) for v in rates.iloc[i].values]
        series.append({
            'name': company,
            'type': 'line',
            'data': values
        })

    palette = bokeh.palettes.all_palettes['Turbo'][256][32:]
    skip = floor(len(palette) / len(companies))
    colors = [palette[i*skip] for i in range(len(companies))]

    options = {
        "title": {"text": title_text},
        "tooltip": {"trigger": "axis"},
        "color": colors,
        "legend": {
            "orient": "vetical",
            "right": 10, 
            "top": "center", 
            "data": companies,
            #"backgroundColor": '#eee',
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": years
        },
        "yAxis": {"type": "value"},
        "series": series
    }
    return options