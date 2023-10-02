from flask import Flask, render_template, request, jsonify
import asyncio
import plotly.graph_objs as go
import dash
from dash import dcc, html
from nfl_data import *
from dataManager import DataManager
from scraper import *

options = [
    {'label': 'Receptions', 'value': 'rec'},
    {'label': 'Targets', 'value': 'Tgt'},
    {'label': 'Receiving Yards', 'value': 'rec yards'},
    {'label': 'Receiving TDs', 'value':'rec tds'},
    {'label': 'Rush attempts', 'value':'att'},
    {'label': 'Rushing yards', 'value':'rush yards'},
    {'label': 'Rushing TDs', 'value':'rush tds'},
    {'label': 'Fantasy Points', 'value':'Points'},
]

data_manager = DataManager()

def get_stat_display(stat):
    return next(item['label'] for item in options if item['value'] == stat)

def update_graph(fig, players, stat):
    fig.data = []
    stat_display = get_stat_display(stat)[:-1]+"(s)"
    for player, player_data in data_manager.get_data(players, stat):
        fig.add_trace(
            go.Scatter(
                x=list(range(1, 19)), 
                y=player_data, 
                name=player,
                hovertemplate="%{y} "+stat_display
            )
        )
    return fig

def generate_line_plot(players, stat):
    layout = go.Layout(
        height=650
    )
    fig = go.Figure(layout=layout)
    fig.update_xaxes(
        range=[0, 19]
    )
    fig.update_layout(
        xaxis_title='Week',
        yaxis_title=get_stat_display(stat),
        showlegend=True
    )
    return update_graph(fig, players, stat)

app = Flask(__name__)

@app.route('/')
def home():
    data_manager.clear()
    return render_template('index.html')

@app.route('/stats')
def display_stats():
    data_manager.clear()
    return render_template('stats.html')

@app.route('/teams')
def compare_teams():
    data_manager.clear()
    return render_template('chart.html')

@app.route('/projections')
def display_projections():
    data_manager.clear()
    return render_template('projections.html')

@app.route('/data', methods=['POST'])
async def get_data():
    request_type = request.data.decode('utf-8')
    if request_type == "names":
        names = await asyncio.to_thread(get_all_names)
        return jsonify(array=names)
    elif request_type == "names-fp":
        names = await asyncio.to_thread(get_fantasy_pros_names)
        return jsonify(array=names)
    elif request_type.startswith("projections"):
        rows = await asyncio.to_thread(get_mass_z_predictions)
        return jsonify(rows=rows)
    elif request_type.startswith("projection:"):
        player = [request_type[11:]]
        row = await asyncio.to_thread(get_mass_z_predictions, player)
        return jsonify(rows=row)
    elif request_type=="offense_comparison":
        data = await asyncio.to_thread(team_stats)
        return jsonify(data=data)
    else:
        player_stats = await asyncio.to_thread(get_player_stats, request_type)
        return jsonify(player_stats)

fig = generate_line_plot([], "rec")

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/graph/')

dash_app.title = "Graphing App"
dash_app.layout = html.Div([
    html.A(
        "Back to Home", 
        href="/", 
        style=  {
            'display': 'inline-block',
            'padding': '5px 10px',  
            'margin-bottom': '10px', 
            'background-color': '#007BFF', 
            'color': 'white',
            'border': 'none',
            'border-radius': '5px',
            'cursor': 'pointer',
            'text-decoration': 'none',
            'font-size': '12px',  
        }
    ),
    html.Br(),
    dcc.Dropdown(
        id='player-selector',
        options=[{'label': column, 'value': column} for column in get_fantasy_pros_names()],
        value=[],
        multi=True
    ),
    dcc.Dropdown(
        id='stat-dropdown',
        options=options,
        value='rec',
        style={
            'width': '250px',
            'font-size': '15px'
        }
    ),
    dcc.Graph(
        id='graph',
        figure=fig
    )
])

@dash_app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('player-selector', 'value'),
     dash.dependencies.Input('stat-dropdown', 'value')])
def update_output(selected_players, stat):
    fig.update_layout(
        yaxis_title=get_stat_display(stat)
    )
    return update_graph(fig, selected_players, stat)

if __name__ == '__main__':
    app.run()