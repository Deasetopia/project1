from dash import Dash, dcc, html, Input, Output
# import networkx as nx
from flask import Flask
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

# Initial App
server = Flask(__name__)
app = Dash(server=server)
app.title = "Product Affinity Dashboard"

# Overall Loading
df = pd.read_csv('./customer_segenv/1_Dash_BasketAffinity/data/5rules_M&S_Mar2022.csv')
pd.set_option('display.max_columns', None)
metric_columns = ['Combined_Baskets','confidence','lift']


#CURRENT HARD CODE SECTION
liftchoicevalue = 1
value_noitemstosee = 25

# Page Layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Product Affinity")],
            className= 'topsectionheader'
            ),
            
            html.Div(children = html.Div([dcc.Dropdown(
                    options = df['DESCRIPTION_item1'].unique(),
                    value = 'Salmon',
                    placeholder='Select an item',
                    id='dropdown_itemdescription'),
                    
                    dcc.Dropdown(
                    options = metric_columns,
                    value = 'confidence',
                    placeholder='Select a preferred metric',
                    id='dropdown_value_sortbycolumn')
                        ]),
                        ),

        html.Br(),

        dcc.Graph(id='indicator-graphic'),

        html.Div(
        html.Table([
        html.Tr([html.Td(''), html.Td(id='dropdown_value_sortbycolumn_OUT')]),
        html.Tr([html.Td(['']), html.Td(id='dropdown_value_sortbycolumn_next_OUT')]),
        html.Tr([html.Td(['']), html.Td(id='dropdown_value_sortbycolumn_last_OUT')])
        ])
    ),
    ])
])
# end of original div



# Do stuff sections    # Note: Inputs are IN ORDER of the functions below
# This app callback takes dropdown values to sort the (3) quick graphs of lift,confidence,etc
@app.callback(
    Output('dropdown_value_sortbycolumn_OUT', 'value'),
    Output('dropdown_value_sortbycolumn_next_OUT', 'value'),
    Output('dropdown_value_sortbycolumn_last_OUT', 'value'),
    Input('dropdown_value_sortbycolumn','value')
)
def getall_dropdown_value_sortbycolumn (someinput):
    metric_columns = ['Combined_Baskets','confidence','lift']
    if someinput == metric_columns[0]:
        someinput == metric_columns[0]
        next_value_sortbycolumn = metric_columns[1]
        last_value_sortbycolumn = metric_columns[2]
    elif someinput == metric_columns[1]:
        next_value_sortbycolumn = metric_columns[0]
        last_value_sortbycolumn = metric_columns[2]
    else:
        someinput = metric_columns[2]
        next_value_sortbycolumn = metric_columns[0]
        last_value_sortbycolumn = metric_columns[1]
    
    return someinput, next_value_sortbycolumn, last_value_sortbycolumn

# This callback will populate the datatable needed and create dashboard
@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('dropdown_itemdescription','value'),
    Input('dropdown_value_sortbycolumn','value'),
    Input('dropdown_value_sortbycolumn_next_OUT', 'value'),
    Input('dropdown_value_sortbycolumn_last_OUT', 'value'),
)

def create_everything(dditemdesc,dd_value_sort,dd_value_sortnext,dd_value_sortlast):
    metric_columns_to_percents = ['consequent support','confidence','rule_support']
    df_filter = df[
        (df['DESCRIPTION_item1'] == dditemdesc) & 
        (df['lift'] >= 1) #NEED THIS TO UPDATE EVENTUALLY
    ]

    df_show = df_filter.sort_values(by= dd_value_sort, ascending=False).head(value_noitemstosee)
    del df_filter
    for column in metric_columns_to_percents: df_show[column] = (df_show[column]*100).map('{:.2f}'.format)

    fig_height = 2
    fig_width = 3
    fig = make_subplots( # specs has to match the matrix shape of rows x columns
        rows=fig_height, cols=fig_width,
        shared_yaxes='rows',
        subplot_titles=(
            dd_value_sort.capitalize(),
            dd_value_sortnext.capitalize(),
            dd_value_sortlast.capitalize(),
            f'Table of All Metrics for {dditemdesc}'
            ), 
        specs= [[{'type':'xy'},{'type':'xy'},{'type':'xy'}],
        [{'type':'table','colspan': fig_width},{},{}]],
        row_heights= [200,300],
        vertical_spacing=0.1
        )
    
    df_show_temp = df_show.sort_values(by= dd_value_sort)
    fig.add_trace(
        go.Bar(
            name=dd_value_sort,
            x=df_show_temp[dd_value_sort],
            y=df_show_temp['DESCRIPTION_item2'],
            orientation='h',
            constraintext='outside'
            ),
            row=1, col=1
            )
        
    fig.add_trace(
        go.Bar(
            name=dd_value_sortnext,
            x=df_show_temp[dd_value_sortnext], 
            y=df_show_temp['DESCRIPTION_item2'],
            orientation='h', 
            constraintext='outside'
            ),
            row=1, col=2
            )
            
    fig.add_trace(
        go.Bar( 
            name=dd_value_sortlast, 
            x=df_show_temp[dd_value_sortlast], 
            y=df_show_temp['DESCRIPTION_item2'],
            orientation='h',
            constraintext='outside'
            ),
            row=1, col=3
            )

    del df_show_temp
    fig.add_trace(
        go.Table(
            header= dict(
                values=['Consequent <br> Item','Basket <br> Penetration (%)', 'Basket <br> Count',
                'Inclusion <br> Probability (%)','Relationship Strength <br> (higher = stronger)'],
                align="left"
                ),
                cells= dict(
                    values=[df_show.DESCRIPTION_item2,
                    df_show['consequent support'],
                    df_show['Combined_Baskets'],
                    df_show.confidence, df_show.lift],
                    align = "left"
                    )
                 ),
            row=2, col=1,
        )
        
    fig.update_layout(height=1500, width=1200, title= go.layout.Title(text=f'Product Affinity Dashboard <br><sup>{dditemdesc}</sup>', xref = 'paper',x = 0.5))
    
    return fig
    

if __name__ == '__main__':
    # app.run_server(debug=True,)
    app.run(host='0.0.0.0', port=8050, debug=False)