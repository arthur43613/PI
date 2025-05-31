import os
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sqlite3

# Constants
CSV_PATH = 'data/dadosCorretosPI.csv'
DW_PATH = 'data/datawarehouse.db'

# OLAP function to query the data
olap_dimensoes = {
    'vazaoMedia': 't."vazaoMedia"',
    'vazaoAtual': 't."vazaoAtual"',
    'alagou': 'f."alagou"',
}

def run_olap_query(dim1, dim2):
    conn = sqlite3.connect(DW_PATH)
    col1 = olap_dimensoes[dim1]
    col2 = olap_dimensoes[dim2] if dim2 != 'Nenhuma' else None

    select_clause = f"{col1} AS dim1"
    group_clause = "dim1"

    if col2:
        select_clause += f", {col2} AS dim2"
        group_clause += ", dim2"

    query = f"""
        SELECT {select_clause}, AVG(t."vazaoMedia") AS media
        FROM fato f
        JOIN dim_vazao t ON f."Unnamed: 0" = t."Unnamed: 0"
        GROUP BY {group_clause}
        ORDER BY f."alagou" DESC
        LIMIT 100
    """
    df_result = pd.read_sql_query(query, conn)
    conn.close()
    return df_result

# Function to generate clustering plot
def cluster_plot():
    df = pd.read_csv(CSV_PATH, encoding='latin-1')
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[['vazaoMedia', 'vazaoAtual']])
    kmeans = KMeans(n_clusters=2, random_state=42)
    df['Cluster'] = kmeans.fit_predict(scaled_data)

    fig = px.scatter(df, x='vazaoMedia', y='vazaoAtual', color='Cluster',
                     title='Clusters de Alagamentos', labels={'vazaoMedia': 'Vazão Média', 'vazaoAtual': 'Vazão Atual'})
    return fig

# Function to generate distribution plot
def distribution_plot():
    df = pd.read_csv(CSV_PATH, encoding='latin-1')
    fig = px.histogram(df, x='vazaoMedia', nbins=30, title='Distribuição da Vazão Média', marginal="box", color_discrete_sequence=['skyblue'])
    fig.update_layout(xaxis_title='Vazão Média', yaxis_title='Frequência')
    return fig

# Home page layout
def render():
    return html.Div([
        html.H2("Painel de Análise - OLAP & Clustering"),
        dbc.Row([
            dbc.Col([
                html.Label("Dimensão 1"),
                dcc.Dropdown(id='dim1', options=[{'label': k, 'value': k} for k in olap_dimensoes.keys()], value='vazaoMedia')
            ], width=6),
            dbc.Col([
                html.Label("Dimensão 2 (opcional)"),
                dcc.Dropdown(id='dim2', options=[{'label': 'Nenhuma', 'value': 'Nenhuma'}] + [{'label': k, 'value': k} for k in olap_dimensoes.keys()],
                             value='Nenhuma')
            ], width=6),
        ], className='my-3'),

        dcc.Graph(id='olap-graph'),

        html.Hr(),

        html.H4("Clusters de Alagamento"),
        dcc.Graph(figure=cluster_plot()),

        html.Hr(),

        html.H4("Distribuição da Vazão Média"),
        dcc.Graph(figure=distribution_plot()),
    ])