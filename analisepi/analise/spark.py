import numpy as np
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer
from pyspark.sql.types import StringType
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("ModeloAlagamento").master("local[*]").getOrCreate()

df = spark.read.csv('./dados/dadosCorretosPI.csv', header=True, inferSchema=True)
df.createOrReplaceTempView("dadosCorretosPI")

print("Consultando rios que alagaram")
df_sql = spark.sql("SELECT * FROM dadosCorretosPI WHERE `alagou` = TRUE").show(5)

colunas_features = ['vazaoMedia', 'vazaoAtual', 'milimitroHora', 'milimitroDia', 'milimitroSeteDias', 'temperatura', 'velocidadeVento']

df_clf = df.select(*colunas_features, 'alagou')
assember_clf = VectorAssembler(inputCols=colunas_features, outputCol="features")
df_clf = assember_clf.transform(df_clf).withColumnRenamed("alagou", "label")

df_clf = df_clf.withColumn("label", col("label").cast(StringType()))
labelIndexer = StringIndexer(inputCol="label", outputCol="indexedLabel")
df_clf = labelIndexer.fit(df_clf).transform(df_clf)
clf = DecisionTreeClassifier(labelCol="indexedLabel", featuresCol="features")
modelo_clf = clf.fit(df_clf)

previsoes_clf = modelo_clf.transform(df_clf)

avaliador_clf= MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy_clf = avaliador_clf.evaluate(previsoes_clf)
print(f"Acurácia do modelo de classificação:, {accuracy_clf: .2%}")

print("Exemplo de previsoes do modelo:")
previsoes_clf.select("Features", "indexedLabel", "prediction").show(15)

plt.figure(figsize=(10, 6))
plt.barh(colunas_features, modelo_clf.featureImportances.toArray())
plt.xlabel('Importância da característica')
plt.ylabel('Características')
plt.title('Importância das características no modelo de classificação')
plt.show()

#--------------------------------------------------------------------#

train_data, test_data = df_clf.randomSplit([0.8, 0.2], seed=69)

modelo_clf = clf.fit(train_data)

previsoes_teste = modelo_clf.transform(test_data)
acuracia_teste = avaliador_clf.evaluate(previsoes_teste)
print(f"Acurácia do modelo de classificação nos dados de teste:, {accuracy_clf: .2%}")

modelo_clf.save("modelo_clf_alagamento")

from pyspark.ml.classification import DecisionTreeClassificationModel
modelo_carregado = DecisionTreeClassificationModel.load("modelo_clf_alagamento")

previsoes_carregadas = modelo_carregado.transform(df_clf)

acuracia_carregada = avaliador_clf.evaluate(previsoes_carregadas)
print(f"Acurácia do modelo carregado: {acuracia_carregada:.2%}")

spark.stop()
