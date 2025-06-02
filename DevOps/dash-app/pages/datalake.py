import os
import sqlite3
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- Constantes e Caminhos ---
# Determina o diretório do script atual (pages/datalake.py)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível para o diretório pai (que deve ser a pasta dash-app/)
_APP_DIR = os.path.dirname(_SCRIPT_DIR)
# Define BASE_DATA_DIR relativo ao _APP_DIR
BASE_DATA_DIR = os.path.join(_APP_DIR, 'data')

CSV_PATH = os.path.join(BASE_DATA_DIR, 'dadosCorretosPI.csv')
DATALAKE_CSV_DIR = os.path.join(BASE_DATA_DIR, 'datalake')
DW_PATH = os.path.join(BASE_DATA_DIR, 'datawarehouse.db')

# --- Processo ETL Essencial ---
def etl_process():   
    try:
        os.makedirs(BASE_DATA_DIR, exist_ok=True)
        os.makedirs(DATALAKE_CSV_DIR, exist_ok=True)
        if os.path.dirname(DW_PATH) and not os.path.exists(os.path.dirname(DW_PATH)):
            os.makedirs(os.path.dirname(DW_PATH))
    except Exception as e_mkdir:
        print(f"AVISO ETL (datalake.py): Não foi possível criar diretórios: {e_mkdir}")

    if not os.path.exists(CSV_PATH):
        print(f"ERRO ETL (datalake.py): Arquivo de entrada {CSV_PATH} NÃO ENCONTRADO.")
        # (Lógica para criar DW vazio - omitida para focar no sucesso do ETL)
        print("--- PROCESSO ETL FALHOU (ARQUIVO DE ENTRADA NÃO ENCONTRADO) ---")
        return False

    df = None
    try:
        df = pd.read_csv(CSV_PATH, encoding='latin-1')
        if df.empty:
            print(f"AVISO ETL (datalake.py): Arquivo {CSV_PATH} está vazio.")
            # (Lógica para criar DW vazio)
            print("--- PROCESSO ETL FALHOU (ARQUIVO DE ENTRADA VAZIO) ---")
            return False
    except Exception as e_read_csv:
        print(f"ERRO ETL (datalake.py): Erro ao ler {CSV_PATH}: {e_read_csv}.")
        print("--- PROCESSO ETL FALHOU (ERRO DE LEITURA CSV) ---")
        return False
        
    if 'id' not in df.columns:
        print("ETL (datalake.py): Criando coluna 'id' a partir do índice.")
        df['id'] = df.index 
    else:
        # Se 'id' já existe, certifique-se de que é adequada para ser uma chave (ex: única, não nula)
        # Para este exemplo, vamos assumir que se existe, está ok, mas em produção, validaria.
        print("ETL (datalake.py): Usando coluna 'id' existente do CSV.")
    
    cols_dim_vazao = ['id', 'vazaoMedia', 'vazaoAtual']
    cols_fato = ['id', 'alagou']
    
    # Verifica se as colunas realmente existem no df ANTES de tentar selecioná-las
    actual_cols_dim_vazao = [col for col in cols_dim_vazao if col in df.columns]
    actual_cols_fato = [col for col in cols_fato if col in df.columns]

    if not all(col in actual_cols_dim_vazao for col in cols_dim_vazao):
        print(f"AVISO ETL (datalake.py): Nem todas as colunas esperadas para dim_vazao ({cols_dim_vazao}) existem em df. Usando: {actual_cols_dim_vazao}")
    if not all(col in actual_cols_fato for col in cols_fato):
        print(f"AVISO ETL (datalake.py): Nem todas as colunas esperadas para fato ({cols_fato}) existem em df. Usando: {actual_cols_fato}")

    dim_vazao_df = df[actual_cols_dim_vazao].copy()
    fato_df = df[actual_cols_fato].copy()

    conn = None
    try:
        conn = sqlite3.connect(DW_PATH)

        if 'id' in dim_vazao_df.columns and not dim_vazao_df.empty:
            dim_vazao_df.to_sql('dim_vazao', conn, if_exists='replace', index=False)
            print(f"ETL (datalake.py): Tabela 'dim_vazao' salva. Colunas no DB: {pd.read_sql_query('PRAGMA table_info(dim_vazao);', conn)['name'].tolist()}")
        else:
            print("ERRO ETL (datalake.py): 'dim_vazao_df' vazia ou sem 'id'. Não foi salva ou salva vazia.")
            pd.DataFrame(columns=cols_dim_vazao).to_sql('dim_vazao', conn, if_exists='replace', index=False) # Cria vazia

        if 'id' in fato_df.columns and not fato_df.empty:
            fato_df.to_sql('fato', conn, if_exists='replace', index=False)
            print(f"ETL (datalake.py): Tabela 'fato' salva. Colunas no DB: {pd.read_sql_query('PRAGMA table_info(fato);', conn)['name'].tolist()}")
        else:
            print("ERRO ETL (datalake.py): 'fato_df' vazia ou sem 'id'. Não foi salva ou salva vazia.")
            pd.DataFrame(columns=cols_fato).to_sql('fato', conn, if_exists='replace', index=False) # Cria vazia
            print("--- PROCESSO ETL FALHOU (CRIAÇÃO DA TABELA FATO) ---")
            if conn: conn.close()
            return False 
                 
    except Exception as e_sqlite_geral:
        print(f"ERRO ETL (datalake.py): Erro geral ao interagir com SQLite: {e_sqlite_geral}")
        if conn: conn.close()
        return False
    finally:
        if conn: conn.close()
    
    return True

# --- Executa o ETL ao carregar o módulo ---
ETL_SUCESSO_NA_IMPORTACAO = etl_process()

# --- Lógica OLAP e Plots ---
olap_dimensoes = {
    'vazaoMedia': 'dv."vazaoMedia"',
    'vazaoAtual': 'dv."vazaoAtual"',
    'alagou': 'f."alagou"',
}

def run_olap_query(dim1_key, dim2_key):
    print(f"--- run_olap_query (datalake.py) chamada com dim1='{dim1_key}', dim2='{dim2_key}' ---")
    
    if not os.path.exists(DW_PATH):
        print(f"AVISO run_olap_query (datalake.py): DW NÃO ENCONTRADO: {DW_PATH}. Retornando DataFrame vazio.")
        return pd.DataFrame()

    conn = None
    df_result = pd.DataFrame() 
    try:
        conn = sqlite3.connect(DW_PATH)
        
        count_fato = pd.read_sql_query("SELECT COUNT(*) as count FROM fato", conn).iloc[0]['count']
        count_dim_vazao = pd.read_sql_query("SELECT COUNT(*) as count FROM dim_vazao", conn).iloc[0]['count']
        print(f"DEBUG run_olap_query: Contagem em DB: fato={count_fato}, dim_vazao={count_dim_vazao}")

        df_join_test = pd.read_sql_query("SELECT f.id as f_id, dv.id as dv_id, f.alagou, dv.vazaoMedia FROM fato f JOIN dim_vazao dv ON f.id = dv.id LIMIT 5", conn)
        print(f"DEBUG run_olap_query: Teste de JOIN (head 5 linhas):\n{df_join_test}")
        if df_join_test.empty and count_fato > 0 and count_dim_vazao > 0 : # Adicionado para checar se o join falha mesmo com dados
            print("ALERTA run_olap_query: Teste de JOIN retornou DataFrame vazio, mas tabelas têm dados! Verifique a coluna 'id'.")

        col1_sql = olap_dimensoes.get(dim1_key)
        col2_sql = olap_dimensoes.get(dim2_key) if dim2_key != 'Nenhuma' else None

        if not col1_sql:
            print(f"AVISO run_olap_query (datalake.py): Chave dim1 '{dim1_key}' inválida.")
            return df_result
        
        alias_fato = "f"
        alias_dim_vazao = "dv"
        alias_dim_mililitro = "dm" # Se for usar

        select_clause_parts = [f"{col1_sql} AS dim1_val"]
        group_clause_parts = ["dim1_val"]
        
        # CORREÇÃO AQUI:
        query_base = f"""
            FROM fato {alias_fato} 
            JOIN dim_vazao {alias_dim_vazao} ON {alias_fato}.id = {alias_dim_vazao}.id 
        """
        
        needs_join_dim_mililitro = (col1_sql and f'{alias_dim_mililitro}."' in col1_sql) or \
                                   (col2_sql and f'{alias_dim_mililitro}."' in col2_sql)
        if needs_join_dim_mililitro:
             query_base += f"LEFT JOIN dim_mililitro {alias_dim_mililitro} ON {alias_fato}.id = {alias_dim_mililitro}.id "

        if col2_sql:
            if not olap_dimensoes.get(dim2_key):
                 print(f"AVISO run_olap_query (datalake.py): Chave dim2 '{dim2_key}' inválida, ignorando.")
                 col2_sql = None 
            else:
                select_clause_parts.append(f"{col2_sql} AS dim2_val")
                group_clause_parts.append("dim2_val")
        
        select_clause = ", ".join(select_clause_parts)
        group_clause = ", ".join(group_clause_parts)
        
        metric_to_aggregate = f'{alias_dim_vazao}."vazaoMedia"' 
        metric_alias = 'media_calculada'

        query = f"""
            SELECT {select_clause}, AVG({metric_to_aggregate}) AS {metric_alias}
            {query_base}
            WHERE dim1_val IS NOT NULL {f"AND dim2_val IS NOT NULL" if col2_sql and 'dim2_val' in select_clause else ""}
            GROUP BY {group_clause}
            ORDER BY {metric_alias} DESC NULLS LAST 
            LIMIT 100
        """       
        
        df_result = pd.read_sql_query(query, conn)

    except sqlite3.OperationalError as e_sql_op:
        print(f"ERRO OPERACIONAL SQL run_olap_query (datalake.py): {e_sql_op}")
        df_result = pd.DataFrame() 
    except Exception as e:
        print(f"ERRO GERAL run_olap_query (datalake.py): {e}")
        df_result = pd.DataFrame()
    finally:
        if conn:
            conn.close()
    return df_result

def cluster_plot():
    if not os.path.exists(CSV_PATH): return px.bar(title=f"Arquivo {os.path.basename(CSV_PATH)} não encontrado.")
    # ... (resto da função cluster_plot)
    try:
        df = pd.read_csv(CSV_PATH, encoding='latin-1')
        if df.empty or 'vazaoMedia' not in df.columns or 'vazaoAtual' not in df.columns:
            return px.bar(title="Dados insuficientes para cluster plot.")
        df_cluster = df[['vazaoMedia', 'vazaoAtual']].copy()
        df_cluster.dropna(inplace=True)
        if len(df_cluster) < 2:
             return px.bar(title="Poucos dados para clusterizar após remover NaNs.")
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_cluster)
        kmeans = KMeans(n_clusters=min(2, len(df_cluster)), random_state=42, n_init='auto') 
        df_cluster['Cluster'] = kmeans.fit_predict(scaled_data)
        fig = px.scatter(df_cluster, x='vazaoMedia', y='vazaoAtual', color='Cluster',
                         title='Clusters de Alagamentos', labels={'vazaoMedia': 'Vazão Média', 'vazaoAtual': 'Vazão Atual'})
    except Exception as e:
        print(f"ERRO cluster_plot (pages/datalake.py): {e}")
        fig = px.bar(title=f"Erro ao gerar cluster plot: {e}")
    return fig


def distribution_plot():
    if not os.path.exists(CSV_PATH): return px.bar(title=f"Arquivo {os.path.basename(CSV_PATH)} não encontrado.")
    # ... (resto da função distribution_plot)
    try:
        df = pd.read_csv(CSV_PATH, encoding='latin-1')
        if df.empty or 'vazaoMedia' not in df.columns:
            return px.bar(title="Dados insuficientes para gráfico de distribuição.")
        df_dist = df[['vazaoMedia']].copy(); df_dist.dropna(inplace=True)
        if df_dist.empty: return px.bar(title="Sem dados de 'vazaoMedia' após NaNs.")
        fig = px.histogram(df_dist, x='vazaoMedia', nbins=30, title='Distribuição da Vazão Média', marginal="box", color_discrete_sequence=['skyblue'])
        fig.update_layout(xaxis_title='Vazão Média', yaxis_title='Frequência')
    except Exception as e:
        print(f"ERRO distribution_plot (pages/datalake.py): {e}")
        fig = px.bar(title=f"Erro ao gerar gráfico de distribuição: {e}")
    return fig

# --- Layout da Página Datalake ---
def render():
    print("Renderizando layout da página Datalake (pages/datalake.py)...")
    fig_cluster = cluster_plot()
    fig_distribution = distribution_plot()
    return html.Div([
        html.H2("Painel de Análise Datalake - OLAP & Clustering"),
        dbc.Row([
            dbc.Col([
                html.Label("Dimensão 1 (OLAP)"),
                dcc.Dropdown(id='datalake-dim1-dropdown', 
                             options=[{'label': k, 'value': k} for k in olap_dimensoes.keys()], 
                             value='vazaoMedia', clearable=False)
            ], width=6),
            dbc.Col([
                html.Label("Dimensão 2 (OLAP - opcional)"),
                dcc.Dropdown(id='datalake-dim2-dropdown', 
                             options=[{'label': 'Nenhuma', 'value': 'Nenhuma'}] + [{'label': k, 'value': k} for k in olap_dimensoes.keys()],
                             value='Nenhuma', clearable=False)
            ], width=6),
        ], className='my-3'),
        dcc.Loading(dcc.Graph(id='datalake-olap-graph')),
        html.Hr(),
        html.H4("Clusters de Alagamento"),
        dcc.Graph(id='datalake-cluster-plot', figure=fig_cluster),
        html.Hr(),
        html.H4("Distribuição da Vazão Média"),
        dcc.Graph(id='datalake-distribution-plot', figure=fig_distribution),
    ], style={'padding': '20px'})

# --- Callbacks específicos para a página Datalake ---
def register_callbacks(app_instance): 
    @app_instance.callback(
        Output('datalake-olap-graph', 'figure'),
        Input('datalake-dim1-dropdown', 'value'),
        Input('datalake-dim2-dropdown', 'value')
    )
    def update_olap_graph_page_callback(dim1, dim2):
        # Não chamamos mais o ETL aqui, pois ele roda na importação do módulo.
        # Se o ETL_SUCESSO_NA_IMPORTACAO for False, run_olap_query já retorna df vazio.
        df_result = run_olap_query(dim1, dim2)
        
        if df_result.empty:
            return px.bar(title=f"Nenhum dado OLAP para ({dim1}, {dim2}). Verifique os logs do ETL e da query.")
        
        y_col = 'media_calculada' 
        x_col = 'dim1_val'
        color_col = 'dim2_val' if dim2 != 'Nenhuma' and 'dim2_val' in df_result.columns else None
        
        title_text = f'OLAP: Média Vazão Média por {dim1}'
        if color_col: title_text += f' e {dim2}'
            
        try:
            if color_col: fig = px.bar(df_result, x=x_col, y=y_col, color=color_col, barmode='group', title=title_text)
            else: fig = px.bar(df_result, x=x_col, y=y_col, title=title_text)
            fig.update_layout(xaxis_title=dim1, yaxis_title='Média Calculada (Vazão Média)')
        except Exception as e:
            print(f"Erro ao gerar gráfico OLAP Plotly (datalake.py): {e}")
            fig = px.bar(title=f"Erro ao gerar gráfico OLAP: {e}")
        
        return fig