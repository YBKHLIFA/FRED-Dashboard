import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Initialisation de l'application
app = dash.Dash(__name__)

# Configuration
FRED_DATA_FILE = 'fred_data.csv'
UPDATE_INTERVAL = 5 * 60 * 1000  # 5 minutes en millisecondes

# Styles CSS personnalisés
styles = {
    'header': {
        'backgroundColor': '#1f77b4',
        'color': 'white',
        'padding': '20px',
        'borderRadius': '5px',
        'marginBottom': '20px'
    },
    'graph-container': {
        'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
        'borderRadius': '5px',
        'padding': '15px',
        'marginBottom': '20px',
        'backgroundColor': 'white'
    },
    'table-container': {
        'maxHeight': '400px',
        'overflowY': 'scroll',
        'marginBottom': '20px'
    }
}

def load_fred_data():
    """Charge et formate les données FRED"""
    try:
        df = pd.read_csv(FRED_DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Conversion des valeurs numériques
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        
        # Formatage des unités
        df['Formatted_Value'] = df.apply(
            lambda x: f"{x['Value']:.1f}%" if x['Unit'] == 'Percent' else f"{x['Value']:,.1f} {x['Unit']}",
            axis=1
        )
        
        return df
    except Exception as e:
        print(f"Erreur de chargement FRED: {str(e)}")
        return pd.DataFrame()

def create_timeseries_chart(df):
    """Crée le graphique temporel"""
    if df.empty:
        return px.scatter(title='Aucune donnée disponible')
    
    return px.line(
        df,
        x='Date',
        y='Value',
        color='Title',
        title='Évolution des Indicateurs Économiques',
        labels={'Value': 'Valeur', 'Date': 'Date'},
        hover_data={'Title': True, 'Value': ':.2f', 'Unit': True},
        template='plotly_white'
    ).update_layout(
        hovermode='x unified',
        yaxis_title=None,
        xaxis_title=None
    )

def create_latest_values_table(df):
    """Crée le tableau des dernières valeurs"""
    if df.empty:
        return dash_table.DataTable()
    
    # Filtre les dernières valeurs par série
    latest = df.sort_values('Date', ascending=False).groupby('Series ID').first().reset_index()
    
    return dash_table.DataTable(
        columns=[
            {'name': 'Indicateur', 'id': 'Title'},
            {'name': 'Date', 'id': 'Date'},
            {'name': 'Valeur', 'id': 'Formatted_Value'},
            {'name': 'Tendance', 'id': 'Series ID'}
        ],
        data=latest.to_dict('records'),
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'whiteSpace': 'normal'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Series ID} = "UNRATE"',
                    'column_id': 'Tendance'
                },
                'backgroundColor': '#ffcccc',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{Series ID} = "GDP"',
                    'column_id': 'Tendance'
                },
                'backgroundColor': '#ccffcc',
                'color': 'black'
            }
        ]
    )

# Layout de l'application
app.layout = html.Div([
    html.Div([
        html.H1("Tableau de Bord Économique FRED", style={'marginBottom': '0px'}),
        html.Div(id='last-update', style={'fontStyle': 'italic'})
    ], style=styles['header']),
    
    dcc.Interval(
        id='interval-component',
        interval=UPDATE_INTERVAL,
        n_intervals=0
    ),
    
    html.Div([
        html.Div([
            dcc.Graph(
                id='fred-timeseries',
                style=styles['graph-container']
            )
        ], className='six columns'),
        
        html.Div([
            html.H3("Dernières Valeurs", style={'marginTop': '0px'}),
            html.Div(
                id='fred-values-table',
                style=styles['table-container']
            )
        ], className='six columns')
    ], className='row'),
    
    html.Div([
        html.H3("Données Brutes"),
        html.Div(
            id='raw-data-table',
            style=styles['table-container']
        )
    ])
], style={'padding': '20px', 'backgroundColor': '#f5f5f5'})

# Callbacks
@app.callback(
    [Output('fred-timeseries', 'figure'),
     Output('fred-values-table', 'children'),
     Output('raw-data-table', 'children'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # Chargement des données
    df = load_fred_data()
    
    # Dernière mise à jour
    last_update = f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Création des composants
    fig = create_timeseries_chart(df)
    values_table = create_latest_values_table(df)
    
    # Tableau des données brutes
    raw_table = dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'}
    ) if not df.empty else html.P("Aucune donnée disponible")
    
    return fig, values_table, raw_table, last_update

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
