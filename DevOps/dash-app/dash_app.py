import os
import pandas as pd
from dash import Dash, html, Input, Output, dcc 
import dash_bootstrap_components as dbc

# Importe os módulos das suas páginas AQUI, no topo do arquivo
from pages import datalake #
from pages import spark    #
from pages import modelos  #
from pages import hadoop   #

# --- Definições da Sidebar (seu código original) ---
sidebar_bg = "#f8f9fa"
text_color = "#495057"
logo_home = '/assets/icons/data-lake.png'
logo_dados = '/assets/icons/rating.png' 
logo_modelos = '/assets/icons/bar-chart.png'
logo_config = '/assets/icons/develop.png' 

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
            "fontSize": "0.9rem", "color": text_color, "display": "flex",
            "alignItems": "center", "padding": "0.5rem 1rem", "userSelect": "none",
        },
        className="custom-nav-link" 
    )

sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(src='/assets/icons/ocean.gif', style={'width': '80px', 'marginBottom': '0.5rem'}),
                html.Hr(style={'borderTop': '3px solid #444444', 'margin': '0.5rem 1rem'})
            ],
            style={'textAlign': 'center'}
        ),
        navlink_with_logo("Datalake", "/", "home-link", logo_home),
        navlink_with_logo("Spark", "/spark", "dados-link", logo_dados),
        navlink_with_logo("Modelos", "/modelos", "modelos-link", logo_modelos),
        navlink_with_logo("Hadoop", "/hadoop", "config-link", logo_config),
        html.Div(
            [
                dbc.Button(
                    [
                        html.Img(
                            src="/assets/icons/refresh.png",
                            style={"height": "18px", "width": "18px", "marginRight": "8px"}
                        ),
                        "Refresh"
                    ],
                    id="refresh-button",
                    color="light", 
                    size="md",
                    className="refresh-button-custom",
                ),
                html.Hr(style={'borderTop': '3px solid #444444', 'margin': '0 1rem 0.5rem 1rem'}),
                html.Div(
                    [
                        # The icon that was here has been removed.
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
        "position": "fixed", "top": 0, "left": 0, "height": "100vh",
        "padding": "1rem 0.5rem", "width": "180px", "boxShadow": "2px 0 5px rgba(0,0,0,0.1)",
        "overflowX": "hidden", "backgroundColor": sidebar_bg, "display": "flex",
        "flexDirection": "column", "zIndex": 1000
    },
    className="bg-white",
)

# --- Inicialização do aplicativo Dash ---
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server 

# --- Layout principal do aplicativo ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), 
    sidebar,
    dcc.Loading( 
        id="loading-tab-content",
        type="circle", 
        children=html.Div(
            id='tab-content',
            style={
                'marginLeft': '180px', 'padding': '20px',
                'overflowY': 'auto', 'height': '100vh',   
            }
        ),
        style={'marginLeft': '180px', 'height': '100vh', 'overflowY': 'auto'}
    )
])

# --- REGISTRAR CALLBACKS DAS PÁGINAS ---
# Esta é a parte crucial que estava faltando ou precisava de ajuste
# Chame a função register_callbacks de cada módulo de página aqui
datalake.register_callbacks(app)
# Se as outras páginas também tiverem callbacks, registre-as:
# spark.register_callbacks(app)
# modelos.register_callbacks(app)
# hadoop.register_callbacks(app)


# --- Callbacks Globais do App ---

# Callback para atualizar o conteúdo da página com base na URL e no botão de refresh
@app.callback(
    Output('tab-content', 'children'),
    Input('url', 'pathname'),             
    Input('refresh-button', 'n_clicks') 
)
def update_page_content(pathname, refresh_clicks):
    # O callback_context não é mais necessário com a navegação por URL para esta lógica
    # ctx = callback_context
    # triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    current_path = pathname if pathname else '/'
    print(f"Navegando para: {current_path}") # Adicione um print para depurar a navegação

    if current_path == '/':
        # Não precisa mais do 'from ... import ...' aqui se já importou no topo
        return datalake.render()
    elif current_path == '/spark':
        return spark.render()
    elif current_path == '/modelos':
        return modelos.render()
    elif current_path == '/hadoop':
        return hadoop.render()
    else:
        return html.Div([
            html.H1("Página não encontrada (404)"),
            html.P(f"O caminho '{current_path}' não foi reconhecido.")
        ])

# Callback para atualizar o total de linhas (carrega no início e no refresh)
@app.callback(
    Output('total-rows-text', 'children'),
    Input('refresh-button', 'n_clicks') 
)
def update_total_rows(n_clicks_refresh):
    # print(f"Refresh button clicks: {n_clicks_refresh}") # Debug
    file_path = 'data/dadosCorretosPI.csv' #
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, sep=',', encoding='latin-1')
            return str(len(df))
        except Exception as e:
            print(f"Erro ao ler o CSV para contagem de linhas (dash_app.py): {e}")
            return "Erro" 
    else:
        return "0"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True) # app.run_server é mais comum para Dash > 2.0