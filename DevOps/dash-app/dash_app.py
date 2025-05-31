import os
import pandas as pd
from dash import Dash, html, Input, Output, dcc 
import dash_bootstrap_components as dbc

# Sidebar colors and icons
sidebar_bg = "#f8f9fa"
text_color = "#495057"

logo_home = '/assets/icons/data-lake.png'
logo_dados = '/assets/icons/rating.png' 
logo_modelos = '/assets/icons/bar-chart.png'
logo_config = '/assets/icons/develop.png' 

# Função para criar NavLinks com ícones
def navlink_with_logo(text, href, id_name, logo_path):
    return dbc.NavLink(
        [
            html.Img(src=logo_path, style={'width': '20px', 'marginRight': '8px'}),
            text
        ],
        href=href,     
        id=id_name,
        active="exact", 
        style={
            "fontSize": "0.9rem",
            "color": text_color,
            "display": "flex",
            "alignItems": "center",
            "padding": "0.5rem 1rem",
            "userSelect": "none",
        },
        className="custom-nav-link" 
    )

# Definição da Sidebar
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(src='/assets/icons/ocean.gif', style={'width': '80px', 'marginBottom': '0.5rem'}),
                html.Hr(style={'borderTop': '3px solid #444444', 'margin': '0.5rem 1rem'})
            ],
            style={'textAlign': 'center'}
        ),

        # NavLinks atualizados para usar caminhos de URL
        navlink_with_logo("Datalake", "/", "home-link", logo_home),
        navlink_with_logo("Spark", "/spark", "dados-link", logo_dados),
        navlink_with_logo("Modelos", "/modelos", "modelos-link", logo_modelos),
        navlink_with_logo("Hadoop", "/hadoop", "config-link", logo_config),

        # Seção inferior da sidebar (Refresh e Total de Linhas)
        html.Div(
            [
                dbc.Button(
                    [
                        html.Img(
                            src="/assets/icons/refresh.png",
                            style={ 
                                "height": "18px",
                                "width": "18px",
                                "marginRight": "8px"
                            }
                        ),
                        "Refresh"
                    ],
                    id="refresh-button",
                    color="light", 
                    size="md",
                    className="refresh-button-custom", #
                ),

                html.Hr(style={'borderTop': '3px solid #444444', 'margin': '0 1rem 0.5rem 1rem'}),

                html.Div(
                    [
                        html.Img(src='/assets/icons/table.png', style={'width': '40px', 'height': '40px', 'marginRight': '5px'}),
                        html.Span(id='total-rows-text', style={
                            'fontWeight': 'bold', 'fontSize': '1.8rem', 'color': text_color,
                        }),
                    ],
                    style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '7px'}
                )
            ],
            style={'padding': '1rem', 'marginTop': 'auto', 'userSelect': 'none'}
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "height": "100vh",
        "padding": "1rem 0.5rem",
        "width": "180px",
        "boxShadow": "2px 0 5px rgba(0,0,0,0.1)",
        "overflowX": "hidden",
        "backgroundColor": sidebar_bg,
        "display": "flex",
        "flexDirection": "column",
        "zIndex": 1000
    },
    className="bg-white",
)

# Inicialização do aplicativo Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server 

# Layout principal do aplicativo
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), 
    sidebar,
    dcc.Loading( 
        id="loading-tab-content",
        type="circle", 
        children=html.Div(
            id='tab-content',
            style={
                'marginLeft': '180px', 
                'padding': '20px',
                'overflowY': 'auto',
                'height': '100vh',   
            }
        ),
 
        style={'marginLeft': '180px', 'height': '100vh', 'overflowY': 'auto'}
    )
])

# Callback para atualizar o conteúdo da página com base na URL e no botão de refresh
@app.callback(
    Output('tab-content', 'children'),
    Input('url', 'pathname'),             
    Input('refresh-button', 'n_clicks') 
)
def update_page_content(pathname, refresh_clicks):
    current_path = pathname if pathname else '/'

    if current_path == '/':
        from pages.datalake import render as render_home
        content = render_home()
    elif current_path == '/spark':
        from pages.spark import render as render_spark
        content = render_spark()
    elif current_path == '/modelos':
        from pages.modelos import render as render_modelos
        content = render_modelos()
    elif current_path == '/hadoop':
        from pages.hadoop import render as render_hadoop
        content = render_hadoop()
    else:
        content = html.Div([
            html.H1("Página não encontrada (404)"),
            html.P(f"O caminho '{current_path}' não foi reconhecido.")
        ])
    
    return content

# Callback para atualizar o total de linhas (carrega no início e no refresh)
@app.callback(
    Output('total-rows-text', 'children'),
    Input('refresh-button', 'n_clicks') 
)
def update_total_rows(n_clicks_refresh):
    file_path = 'data/dadosCorretosPI.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, sep=',', encoding='latin-1')
            return str(len(df))
        except Exception as e:
            print(f"Erro ao ler o CSV para contagem de linhas: {e}")
            return "Erro" 
    else:
        return "0"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)