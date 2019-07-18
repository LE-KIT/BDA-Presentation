import numpy as np
import pandas as pd
import os
import re
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category20
from bokeh.core.properties import value
from bokeh.models import HoverTool, BoxSelectTool, ResetTool, SaveTool
from bokeh.models import CustomJS
from bokeh.models import Button, DatePicker
from bokeh.models.widgets import CheckboxButtonGroup, MultiSelect, DateFormatter, TableColumn, DataTable
from bokeh.io import output_notebook, reset_output
from bokeh.layouts import column, row


def _create_datetime(row):
    date = row.Datum.strftime("%Y-%m-%d") + " " + row.Uhrzeit
    return date

def preprocessing(df):

    # Time Formatting
    df["Date"] = df.apply(lambda row: _create_datetime(row), axis=1)
    df["Date"] = pd.to_datetime(df.Date, format="%Y-%m-%d %H:%M")
    df = df.sort_values("Date").reset_index(drop=True)
    cols = list(df)
    cols.insert(0, cols.pop(cols.index("Date")))
    df = df.loc[:, cols]
    df.drop(["Datum", "Uhrzeit"], axis=1, inplace=True)

    # Rename columns
    countries = {
        "Niederlande": "NL",
        "Schweiz": "CHE",
        "Dänemark": "DNK",
        "Tschechien": "CZE",
        "Luxemburg": "LUX",
        "Schweden": "SWE",
        "Österreich": "AUT",
        "Frankreich": "FRA",
        "Polen": "PL",
    }

    types = {"Import": "IM", "Export": "EX"}

    type_pattern = r"\((.*?)\)"
    country_pattern = r"(.*?) "

    new_columns = [
        countries.get(re.search(country_pattern, col).group(1))
        + "_"
        + types.get(re.search(type_pattern, col).group(1))
        for col in df.columns[2::]
    ]

    new_columns.insert(0, "Date")
    new_columns.insert(1, "NX")
    df.columns = new_columns

    # Netto Exporte Füllen
    export_columns = [col for col in df.columns if col[-2::] == "EX"]
    import_columns = [col for col in df.columns if col[-2::] == "IM"]
    df["NX"] = df.loc[:, "NL_EX":"PL_IM"].sum(axis=1)

    # Fill Nones
    df = df.fillna(0)

    return df

def print_hi():
    return "hi!"

def import_data(dataPath="./pres_data/stromfluss"):
    import_files = os.listdir(dataPath)
    dateparse = lambda x: pd.datetime.strptime(x, '%d.%m.%Y')

    numberparse = lambda x: pd.np.float(x.replace(".", "")) if x != "-" else None
    convert_thousand = {num: numberparse for num in np.arange(2, 22)}

    for idx, file in enumerate(import_files):
        print("Import File: {} ".format(file))
        PATH = dataPath + "/" + file

        if idx > 0:
            df2 = pd.read_csv(PATH,
                              sep=r";",
                              decimal=r",",
                              thousands=r".",
                              converters=convert_thousand,
                              parse_dates=['Datum'],
                              date_parser=dateparse)
            df = df.append(df2)
        else:
            df = pd.read_csv(PATH,
                             sep=r";",
                             decimal=r",",
                             thousands=r".",
                             converters=convert_thousand,
                             parse_dates=['Datum'],
                             date_parser=dateparse)
    del df2
    return df

def show_bokeh(df):
    ## Setting up Bokeh
    reset_output()
    output_notebook()
    cds = ColumnDataSource(df)
    output_file("bda_bokeh.html")
    p = figure(x_axis_type="datetime", title="SMARD Data", x_axis_label="Date", y_axis_label="MWh",
               y_range=[-25000, +25000], plot_width=900, plot_height=300)
    ## Configure Tools
    hover_tool = HoverTool(
        tooltips=[
            ('date', '@Date{%F %T}'),
            ('value', '@$name MWh'),
        ],
        formatters={
            'Date': 'datetime',
        },
        mode='vline'
    )
    box_select_tool = BoxSelectTool(dimensions="width")
    save_tool = SaveTool()
    reset_tool = ResetTool()
    p.tools = [box_select_tool, hover_tool, save_tool, reset_tool]
    p.toolbar.active_inspect = []

    ## Adding glyphs
    ## Note: Step Function would be more appropriate, but does not support HoverTools atm, see https://github.com/bokeh/bokeh/issues/7419
    lines = []
    for col, color in zip(df.columns[1:], Category20[len(df.columns[1:])]):
        lines.append(p.line(x='Date', y=col, source=cds, legend=value(col), color=color, name=col, muted_color=color,
                            muted_alpha=0.0))

    ## customizing legend
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"

    ## Callbacks
    callback_datechange_from = CustomJS(args=dict(source=cds, p=p), code="""
    var date = cb_obj.value;
    p.x_range.start = Date.parse(date);
    """)

    callback_datechange_to = CustomJS(args=dict(source=cds, p=p), code="""
    var date = cb_obj.value;
    p.x_range.end = Date.parse(date);
    """)

    callback_col_change = CustomJS(args=dict(source=cds, lines=lines), code="""
    var data = source.data;
    for(var i = 0; i < lines.length; i++){
        lines[i].visible = cb_obj.active.includes(i);
    }
    """)

    datepicker_from = DatePicker(min_date = df['Date'].min(), max_date=df['Date'].max(), callback=callback_datechange_from)
    datepicker_to = DatePicker(min_date = df['Date'].min(), max_date=df['Date'].max(), callback=callback_datechange_to)
    checkbox_group_col1 = CheckboxButtonGroup(labels=[col for col in df.columns[1:10]], active=[], callback=callback_col_change)
    checkbox_group_col2 = CheckboxButtonGroup(labels=[col for col in df.columns[10:]], active=[], callback=callback_col_change)
    multi_select = MultiSelect(title="Option:", value=["NX"],
                           options=[(col,col) for col in df.columns[1:]], size=len(df.columns[1:]))

    # Data Table
    columns = [TableColumn(field="Date", title="Date", formatter=DateFormatter(format="%F %T"))] \
        + [TableColumn(field=col, title=col) for col in df.columns[1:]]

    #data_table = DataTable(source=cds, columns=columns, width=800, fit_columns=True, scroll_to_selection=True)



    r1 = row(datepicker_from, datepicker_to)
    r2 = row(checkbox_group_col1)
    r3 = row(checkbox_group_col2)
    layout = column(column(r1,r2,r3), p)

    show(layout)


