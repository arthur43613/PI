from dash import html, dcc, dash_table
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    classification_report
)

def render():
    # Load data fresh each render
    df = pd.read_csv('data/dadosCorretosPI.csv', sep=',', encoding='latin-1')

    # Prepare features and target
    X = df.drop(columns=['Unnamed: 0', 'alagou'], errors='ignore')
    y = df['alagou']

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns

    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer([
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

    # Data Table component
    table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.tail(20).to_dict("records"),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
    )

    # Confusion matrix and metrics
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=69))
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro")
    rec = recall_score(y_test, y_pred, average="macro")
    f1 = f1_score(y_test, y_pred, average="macro")

    conf_fig = px.imshow(cm, text_auto=True,
                        x=['Pred: 0', 'Pred: 1'],
                        y=['True: 0', 'True: 1'],
                        color_continuous_scale='Blues',
                        title="Matriz de Confusão")
    conf_fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
    conf_metrics = f"Acurácia: {acc:.2f} | Precisão: {prec:.2f} | Recall: {rec:.2f} | F1-Score: {f1:.2f}"

    conf_graph = dcc.Graph(figure=conf_fig)

    # Cluster plot using PCA + KMeans
    x_preprocessed = preprocessor.fit_transform(X)
    kmeans = KMeans(n_clusters=2, random_state=69).fit(x_preprocessed)
    labels = kmeans.predict(x_preprocessed)
    pca = PCA(n_components=2)
    x_pca = pca.fit_transform(x_preprocessed)

    df_pca = pd.DataFrame(x_pca, columns=['PCA1', 'PCA2'])
    df_pca['Cluster'] = labels.astype(str)

    cluster_fig = px.scatter(df_pca, x='PCA1', y='PCA2', color='Cluster',
                             title='Clusterização com PCA (KMeans)')
    cluster_fig.update_traces(marker=dict(size=8, opacity=0.6))
    cluster_graph = dcc.Graph(figure=cluster_fig)

    # Text report for TF-IDF classification
    df_text = df.copy()
    df_text['texto'] = (
        df_text['vazaoMedia'].astype(str) + ' ' +
        df_text['vazaoAtual'].astype(str) + ' ' +
        df_text['milimitroHora'].astype(str) + ' ' +
        df_text['milimitroDia'].astype(str)
    )

    x_train, x_test, y_train, y_test = train_test_split(
        df_text['texto'], df_text['alagou'], test_size=0.2, random_state=69, stratify=df_text['alagou'])

    pipeline_text = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_df=0.8, min_df=1)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=69))
    ])
    pipeline_text.fit(x_train, y_train)
    y_pred_text = pipeline_text.predict(x_test)

    report = classification_report(y_test, y_pred_text)
    acc_text = accuracy_score(y_test, y_pred_text)

    text_report = html.Pre(
        f"Relatório de Classificação\n\n{report}\nAcurácia: {acc_text:.2f}",
        style={'whiteSpace': 'pre-wrap', 'fontFamily': 'monospace'}
    )

    # Helper to create nicely styled sections
    def render_section(title, description, content_component):
        return html.Div([
            html.H3(title, style={'marginBottom': '10px'}),
            html.P(description, style={'marginBottom': '20px'}),
            content_component
        ], style={
            'backgroundColor': '#f9f9f9',
            'padding': '30px',
            'marginBottom': '40px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
            'textAlign': 'center',
            'maxWidth': '1000px',
            'marginLeft': 'auto',
            'marginRight': 'auto'
        })

    return html.Div([
        render_section("Tabela de Dados", "Visualização das últimas 20 linhas.", table),
        render_section("Matriz de Confusão", conf_metrics, conf_graph),
        render_section("Gráfico de Clusters", "Visualização dos clusters gerados pelo algoritmo.", cluster_graph),
        render_section("Relatório de Texto", "Relatório do modelo de classificação baseado em TF-IDF.", text_report)
    ], style={'padding': '60px', 'maxWidth': '1200px', 'margin': '0 auto'})
