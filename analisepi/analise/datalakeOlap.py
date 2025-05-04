import pandas as pd
import sqlite3
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import networkx as nx
from ipywidgets import interact, widgets

CSV_PATH = './dados/dadosCorretosPI.csv'
DATALAKE_PATH = 'datalake'
DW_PATH = 'datawarehouse.db'

#--------------------------------------------------------------------#
#ETAPA 1 - Extract
df = pd.read_csv(CSV_PATH, encoding='latin-1')

#ETAPA 2 - Transform
dim_vazao = df[['Unnamed: 0','vazaoMedia', 'vazaoAtual']]
dim_mililitro = df[['Unnamed: 0','milimitroHora', 'milimitroDia', 'milimitroSeteDias']]
fato = df[['Unnamed: 0','alagou']]

#ETAPA 3 - Load
#DataLake
os.makedirs(DATALAKE_PATH, exist_ok=True)
dim_vazao.to_csv(f'{DATALAKE_PATH}/dim_vazao.csv',index=True)
dim_mililitro.to_csv(f'{DATALAKE_PATH}/dim_mililitro.csv',index=True)
fato.to_csv(f'{DATALAKE_PATH}/fato.csv',index=True)

#DataWarehouse (SQLite)
conn = sqlite3.connect(DW_PATH)
dim_vazao.to_sql('dim_vazao', conn, if_exists='replace', index=True)
dim_mililitro.to_sql('dim_mililitro', conn, if_exists='replace', index=True)
fato.to_sql('fato', conn, if_exists='replace', index=True)

#Criar Estrela (Grafo)
G = nx.DiGraph()
G.add_node('fato', label='fato', color='blue')
dimensoes = ['dim_vazao','dim_mililitro']
for dim in dimensoes:
    G.add_node(dim, label=dim, color='green')
    G.add_edge(dim, 'fato')

colors = [G.nodes[n]['color'] for n in G.nodes]
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color=colors, node_size=2000, font_size=10, font_weight='bold')
plt.title('Modelo Estrela')
plt.savefig('analise/img/img_estrela.png', format='png', dpi=300)
plt.show()

#--------------------------------------------------------------------#

olap_dimensoes = {
    'vazaoMedia': 't."vazaoMedia"',
    'vazaoAtual': 't."vazaoAtual"',
    'alagou': 'f."alagou"',
}

dim1_dropdown = widgets.Dropdown(options=olap_dimensoes.keys(), description='Dimensão 1:')
dim2_dropdown = widgets.Dropdown(options=['Nenhuma'] + list(olap_dimensoes.keys()), description='Dimensão 2:')

def gerar_consulta(dim1, dim2):
    col1 = olap_dimensoes[dim1]
    col2 = olap_dimensoes[dim2] if dim2 != 'Nenhuma' else None

    select_clause = f"{col1} AS dim1"
    group_clause = "dim1"

    if col2:
        select_clause += f", {col2} AS dim2"
        group_clause += ", dim2"

    query = f"""
        SELECT {select_clause}, AVG("vazaoMedia") AS media
        FROM fato f
        JOIN dim_vazao t ON f."Unnamed: 0" = t."Unnamed: 0"
        GROUP BY {group_clause}
        ORDER BY 'f."alagou"' DESC
        LIMIT 100
    """

    df_resultado = pd.read_sql_query(query, conn)

    plt.figure(figsize=(10, 5))

    if col2:
        sns.barplot(data=df_resultado, x='dim1', y='media', hue='dim2')
        plt.legend(title=dim2, bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        sns.barplot(data=df_resultado, x='dim1', y='media')

    plt.title(f' {dim1}' + (f' e {dim2}' if col2 else ''))
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig('analise/img/sql_img.png', format='png', dpi=300)
    plt.show()

#--------------------------------------------------------------------#

interact(gerar_consulta, dim1=dim1_dropdown, dim2=dim2_dropdown)

#Data Minig
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df[['vazaoMedia', 'vazaoAtual']])
kmeans = KMeans(n_clusters=2, random_state=42)
df['Cluster'] = kmeans.fit_predict(scaled_data)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='vazaoMedia', y='vazaoAtual', hue='Cluster', palette='viridis', s=100, alpha=0.7)
plt.title('Clusters de Alagamentos')
plt.xlabel('Vazão Média')
plt.ylabel('Vazão Atual')
plt.legend(title='Cluster')
plt.savefig('analise/img/data_minig.png', format='png', dpi=300)
plt.show()

#--------------------------------------------------------------------#

# Distribuição da Vazão media
plt.figure(figsize=(10, 5))
sns.histplot(df['vazaoMedia'], kde=True, color='skyblue')
plt.title('Distribuição da Vazão media')
plt.xlabel('Vazão')
plt.ylabel('Rios com tal vazão')
plt.tight_layout()
plt.savefig('analise/img/distribuicao.png', format='png', dpi=300)
plt.show()