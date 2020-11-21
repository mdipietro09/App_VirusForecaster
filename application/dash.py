###############################################################################
#                                MAIN                                         #
###############################################################################

# Setup
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from settings import config, about
from python.data import Data
from python.model import Model
from python.result import Result



# Read data
data = Data()
data.get_data()



# App Instance
app = dash.Dash(name=config.name, assets_folder=config.root+"/application/static", external_stylesheets=[dbc.themes.LUX, config.fontawesome])
app.title = config.name



# Navbar
navbar = dbc.Nav(className="nav nav-pills", children=[
    ## logo/home
    dbc.NavItem(html.Img(src=app.get_asset_url("logo.PNG"), height="40px")),
    ## about
    dbc.NavItem(html.Div([
        dbc.NavLink("About", href="/", id="about-popover", active=False),
        dbc.Popover(id="about", is_open=False, target="about-popover", children=[
            dbc.PopoverHeader("How it works"), dbc.PopoverBody(about.txt)
        ])
    ])),
    ## links
    dbc.DropdownMenu(label="Links", nav=True, children=[
        dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"), "  Contacts"], href=config.contacts, target="_blank"), 
        dbc.DropdownMenuItem([html.I(className="fa fa-github"), "  Code"], href=config.code, target="_blank")
    ])
])



# Input
inputs = dbc.FormGroup([
    html.H4("Select Country"),
    dcc.Dropdown(id="country", options=[{"label":x,"value":x} for x in data.countrylist], value="World")
]) 



# App Layout
app.layout = dbc.Container(fluid=True, children=[
    ## Top
    html.H1(config.name, id="nav-pills"),
    navbar,
    html.Br(),html.Br(),html.Br(),

    ## Body
    dbc.Row([
        ### input + panel
        dbc.Col(md=3, children=[
            inputs, 
            html.Br(),html.Br(),html.Br(),
            html.Div(id="output-panel")
        ]),
        ### plots
        dbc.Col(md=9, children=[
            dbc.Col(html.H4("Forecast 30 days from today"), width={"size":6,"offset":3}), 
            dbc.Tabs(className="nav nav-pills", children=[
                dbc.Tab(dcc.Graph(id="plot-total"), label="Total cases"),
                dbc.Tab(dcc.Graph(id="plot-active"), label="Active cases")
            ])
        ])
    ])
])



# Python functions for about navitem-popover
@app.callback(output=Output("about","is_open"), inputs=[Input("about-popover","n_clicks")], state=[State("about","is_open")])
def about_popover(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(output=Output("about-popover","active"), inputs=[Input("about-popover","n_clicks")], state=[State("about-popover","active")])
def about_active(n, active):
    if n:
        return not active
    return active



# Python function to plot total cases
@app.callback(output=Output("plot-total","figure"), inputs=[Input("country","value")]) 
def plot_total_cases(country):
    data.process_data(country) 
    model = Model(data.dtf)
    model.forecast()
    model.add_deaths(data.mortality)
    result = Result(model.dtf)
    return result.plot_total(model.today)



# Python function to plot active cases
@app.callback(output=Output("plot-active","figure"), inputs=[Input("country","value")])
def plot_active_cases(country):
    data.process_data(country) 
    model = Model(data.dtf)
    model.forecast()
    model.add_deaths(data.mortality)
    result = Result(model.dtf)
    return result.plot_active(model.today)
    

    
# Python function to render output panel
@app.callback(output=Output("output-panel","children"), inputs=[Input("country","value")])
def render_output_panel(country):
    data.process_data(country) 
    model = Model(data.dtf)
    model.forecast()
    model.add_deaths(data.mortality)
    result = Result(model.dtf)
    peak_day, num_max, total_cases_until_today, total_cases_in_30days, active_cases_today, active_cases_in_30days = result.get_panel()
    peak_color = "white" if model.today > peak_day else "red"
    panel = html.Div([
        html.H4(country),
        dbc.Card(body=True, className="text-white bg-primary", children=[
            
            html.H6("Total cases until today:", style={"color":"white"}),
            html.H3("{:,.0f}".format(total_cases_until_today), style={"color":"white"}),
            
            html.H6("Total cases in 30 days:", className="text-danger"),
            html.H3("{:,.0f}".format(total_cases_in_30days), className="text-danger"),
            
            html.H6("Active cases today:", style={"color":"white"}),
            html.H3("{:,.0f}".format(active_cases_today), style={"color":"white"}),
            
            html.H6("Active cases in 30 days:", className="text-danger"),
            html.H3("{:,.0f}".format(active_cases_in_30days), className="text-danger"),
            
            html.H6("Peak day:", style={"color":peak_color}),
            html.H3(peak_day.strftime("%Y-%m-%d"), style={"color":peak_color}),
            html.H6("with {:,.0f} cases".format(num_max), style={"color":peak_color})
        
        ])
    ])
    return panel