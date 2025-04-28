import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, confusion_matrix)
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv('./dados/dadosCorretosPI.csv', sep=',', encoding='latin-1')

print(df.tail)

#--------------------------------------------------------------------#
# Criar uma figura
fig, ax = plt.subplots(figsize=(12, len(df.tail(20))*0.5))  # Ajuste a altura conforme o número de linhas
# Ocultar o eixo
ax.axis('off')
# Criar a tabela a partir do DataFrame
tabela = ax.table(cellText=df.tail(20).values,
                  colLabels=df.tail(20).columns,
                  cellLoc='center',
                  loc='center')
# Ajustar o tamanho da fonte
tabela.auto_set_font_size(False)
tabela.set_fontsize(10)
# Ajustar a largura das colunas automaticamente
tabela.scale(1.2, 1.2)
# Salvar como imagem
plt.savefig('analise/img/tabela_dados.png', bbox_inches='tight', dpi=300)
plt.close()

#--------------------------------------------------------------------#

# Pré-processamento dos Dados
# Separando features e target
X = df.drop(columns=['Unnamed: 0', 'alagou'], axis=1)
y = df['alagou']

#Identificando colunas numéricas e categóricas
numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
print(numeric_features)
categorical_features = X.select_dtypes(include=['object', 'category']).columns
print(categorical_features)

# Criando transformers para pré-processamento
numeric_transformer = Pipeline(steps=[
   ('imputer', SimpleImputer(strategy='median')),  # Imputação de valores faltantes
   ('scaler', StandardScaler())  # Escalonamento
])

categorical_transformer = Pipeline(steps=[
   ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),  # Imputação de valores faltantes
   ('onehot', OneHotEncoder(handle_unknown='ignore'))  # Codificação one-hot
])

# Combinando transformers em um ColumnTransformer
preprocessor = ColumnTransformer(
   transformers=[
       ('num', numeric_transformer, numeric_features),
       ('cat', categorical_transformer, categorical_features)
   ])

# Divisão dos Dados em Treino e Teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

# Seleção do Modelo
#MODELO DE CLASSIFICAÇÃO
model = RandomForestClassifier(n_estimators=100, random_state=69)

# Criando a Pipeline completa
pipeline = Pipeline(steps=[
   ('preprocessor', preprocessor),
   ('classifier', model)
])

#Treinamento do Modelo
pipeline.fit(X_train, y_train)

# Avaliação do Modelo
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1]  # Probabilidades para a classe positiva

# Métricas de Classificação
print('\n')
print(f'Acuracia: {accuracy_score(y_test, y_pred)}')
print(f'Precisao: {precision_score(y_test, y_pred, average="macro")}')
print(f'Recall: {recall_score(y_test, y_pred, average="macro")}')
print(f'F1-Score: {f1_score(y_test, y_pred, average="macro")}')

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average="macro")
rec = recall_score(y_test, y_pred, average="macro")
f1 = f1_score(y_test, y_pred, average="macro")

# Matriz de confusão
cm = confusion_matrix(y_test, y_pred)
classes = ['Classe 0', 'Classe 1']

# Plotando a matriz de confusão
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title('Matriz de Confusão')
plt.xlabel('Previsão')
plt.ylabel('Verdadeiro')

metricas_texto = (
    f'Acurácia: {acc:.2f}\n'
    f'Precisão: {prec:.2f}\n'
    f'Recall: {rec:.2f}\n'
    f'F1-Score: {f1:.2f}'
)

# Colocar o texto fora do gráfico (ou ajuste para onde preferir)
plt.gcf().text(1.02, 0.5, metricas_texto, fontsize=12, va='center')

plt.savefig('analise/img/matriz_confusao.png', bbox_inches='tight', dpi=300)
plt.show()

#--------------------------------------------------------------------#

#MODELO DE CLUSTERIZAÇÃO
k=2
model = KMeans(n_clusters=k, random_state=69)

# Criando a Pipeline completa
pipeline = Pipeline(steps=[
   ('preprocessor', preprocessor),
   ('classifier', model)
])

#Treinamento do Modelo
pipeline.fit(df)
labels = pipeline.predict(df)

# Transformação com o pré-processador
x_preprocessed = preprocessor.transform(X)

# Métricas
sil_score = silhouette_score(x_preprocessed, labels)
inertia = model.inertia_
db_score = davies_bouldin_score(x_preprocessed, labels)

print(f'Silhouette Score:{silhouette_score(x_preprocessed,labels)}')
print(f'Inércia:{model.inertia_}')
print(f'Coeficiente de Davies-Bouldin:{davies_bouldin_score(x_preprocessed,labels)}')

pca = PCA(n_components=2)
x_pca = pca.fit_transform(x_preprocessed)

plt.figure(figsize=(10,6))
scatter = plt.scatter(x_pca[:,0],x_pca[:,1],c=labels,
                      cmap='viridis',s=50,alpha=0.6)
centroids = pca.transform(model.cluster_centers_)
plt.scatter(centroids[:,0],centroids[:,1], c='red',marker='X',s=200, label='Centroids')

plt.colorbar(scatter, label='Cluster')
plt.xlabel('PCA1')
plt.ylabel('PCA2')
plt.title('Visualização dos Clusters do K-Means (2D)')
plt.legend()

metricas_texto = (
    f'Silhouette Score: {sil_score:.2f}\n'
    f'Inércia: {inertia:.2f}\n'
    f'Davies-Bouldin: {db_score:.2f}'
)

plt.gcf().text(1.02, 0.5, metricas_texto, fontsize=12, va='center')

plt.savefig('analise/img/grafico_cluster.png', bbox_inches='tight', dpi=300)
plt.show()

#--------------------------------------------------------------------#

#PIPE LINE COM MODELO DE REGRESSÃO
# Carregar os dados com mais exemplos para melhorar a generalização
df['texto'] = df['vazaoMedia'].astype(str) + ' ' + df['vazaoAtual'].astype(str) + ' ' + df['milimitroHora'].astype(str) + ' ' + df['milimitroDia'].astype(str)
data = pd.DataFrame({
    'texto': df['texto'],
    'rótulo': df['alagou']
})

x_train, x_test, y_train, y_test = train_test_split(df['texto'], df['alagou'], test_size=0.2, random_state=69, stratify=df['alagou']) #Separação dos dados de treino e teste
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2),max_df=0.8, min_df=1)),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=69))
])
pipeline.fit(x_train, y_train) #Treinamento do modelo

y_pred = pipeline.predict(x_test) #Predição dos dados de teste
relatorio = classification_report(y_test, y_pred)
acuracia = accuracy_score(y_test, y_pred)

# Criando a imagem
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')  # Oculta os eixos

# Monta o texto a ser exibido
texto = f'Relatório de Classificação:\n\n{relatorio}\nAcurácia: {acuracia:.2f}'

# Desenha o texto na imagem
plt.text(0, 1, texto, fontsize=12, va='top', ha='left', family='monospace')

# Salva a imagem
plt.savefig('analise/img/relatorio_regressao.png', bbox_inches='tight', dpi=300)
plt.show()

print('Relatorio de Classificacao:/n',classification_report(y_test, y_pred)) #Relatório de classificação
print('Acuracia:', accuracy_score(y_test, y_pred)) #Acurácia do modelo