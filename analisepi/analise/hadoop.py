import pandas as pd

df = pd.read_csv('./dados/dadosCorretosPI.csv', sep=',', encoding='latin-1')

#--------------------------------------------------------------------#
#MapReduce: contar ocorrencias
#Nesta função os dados serão limpos tirando na's [ ] e ', alem de criar um append onde ficara o nome do solo e 1
def mapper(linhas):
  pares = []
  for linha in linhas:
    if pd.notna(linha):
      for solo in linha.replace("[","").replace("]","").replace("'","").split(","):
        solo = solo.strip()
        pares.append((solo, 1))
  return pares

#Nesta função
def shuffle(mapped_data):
  agrupado = {}
  for chave, valor in mapped_data:
    if chave not in agrupado:
      agrupado[chave] = []
    agrupado[chave].append(valor)
  return agrupado

#E por fim os valores de cada solo são agrupados e somados, basicamente contando quantos tipos de salo existem de cada tipo
def reducer(agrupado):
  return {chave:sum(valores) for chave, valores in agrupado.items()}

mapeado = mapper(df["solo"])
agrupado = shuffle(mapeado)
resultado = reducer(agrupado)
print("Map Reducer: Tipos de solo")
print(resultado)
#--------------------------------------------------------------------#

#Hive: SQL com pandas
print("HIVE:")
df_hive = df[["vazaoMedia","vazaoAtual","alagou"]]
#Cria um SQL na memoria e exibira onde a vazão é igual a 72741 (Vazão que foi colocada nos valores NA'S no tratamento de dados)
print(df_hive[(df_hive['vazaoAtual']) > df_hive['vazaoMedia']])

#--------------------------------------------------------------------#

from pickle import TRUE
#PIG: trasforma valores em tempo real
#Cria varios parametros para filtrar e transformar os dados
dados_pig = df[["vazaoMedia","vazaoAtual","alagou"]].dropna().head(100).values.tolist()
valor = 2
dados_pig[1] = [item * valor for item in dados_pig]
filtrado = [x for x in dados_pig if x[1] > x[0]]

  
print(f"Total filtrado: {len(filtrado)}")


trasformado = [(str(x[0]), str(x[1]), bool(x[2])) for x in filtrado]

print("PIG: Vazão atual acima de 2 vezes a média e houve alagamento")
for Alagou in trasformado:
  print(f"{Alagou }")

#--------------------------------------------------------------------#

#HBase: Banco NOSQL orientado a colunas
#Cria um banco SQL na memoria e estabeleçe o tipo das colunas
hbase = {
    f"Rio: {i}": {
        "info:vazaoMedia": int(row["vazaoMedia"]),
        "info:vazaoAtual": int(row["vazaoAtual"]),
        "info:alagou": bool(row["alagou"])
    }
    for i, row in df.iterrows()
}
print("HBase: Dados armazenados em colunas")
for chave, colunas in hbase.items():
  print(f"{chave} => Vazão Media: {colunas['info:vazaoMedia']}, Vazão Atual: {colunas['info:vazaoAtual']}, Alagou: {colunas['info:alagou']}")