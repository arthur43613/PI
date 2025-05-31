import pandas as pd
from dash import html, dcc
import plotly.express as px

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import col
from pyspark.sql.types import StringType


def run_spark_model():
    spark = SparkSession.builder.appName("ModeloAlagamento").master("local[*]").getOrCreate()

    df = spark.read.csv('data/dadosCorretosPI.csv', header=True, inferSchema=True)

    features = ['vazaoMedia', 'vazaoAtual', 'milimitroHora', 'milimitroDia',
                'milimitroSeteDias', 'temperatura', 'velocidadeVento']

    df_clf = df.select(*features, 'alagou')
    df_clf = VectorAssembler(inputCols=features, outputCol="features").transform(df_clf)
    df_clf = df_clf.withColumnRenamed("alagou", "label").withColumn("label", col("label").cast(StringType()))
    df_clf = StringIndexer(inputCol="label", outputCol="indexedLabel").fit(df_clf).transform(df_clf)

    model = DecisionTreeClassifier(labelCol="indexedLabel", featuresCol="features").fit(df_clf)
    predictions = model.transform(df_clf)

    accuracy = MulticlassClassificationEvaluator(
        labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy"
    ).evaluate(predictions)

    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": model.featureImportances.toArray()
    }).sort_values(by="Importance", ascending=True)

    sample_df = predictions.select("features", "indexedLabel", "prediction").limit(10).toPandas()
    sample_df["features"] = sample_df["features"].astype(str)

    spark.stop()
    return accuracy, importance_df, sample_df


def render():
    accuracy, fi_df, sample_pred = run_spark_model()

    fig = px.bar(fi_df, x="Importance", y="Feature", orientation='h',
                 title="Importância das Características no Modelo")

    return html.Div([
        html.H2("Classificação de Alagamentos com Spark"),
        html.P(f"Acurácia do modelo: {accuracy:.2%}"),

        dcc.Graph(figure=fig),

        html.H4("Exemplo de Previsões"),
        html.Table([
            html.Thead([
                html.Tr([html.Th(col) for col in sample_pred.columns])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(sample_pred.iloc[i][col]) for col in sample_pred.columns
                ]) for i in range(len(sample_pred))
            ])
        ], style={
            "width": "100%",
            "border": "1px solid black",
            "borderCollapse": "collapse",
            "marginTop": "20px"
        })
    ], style={"padding": "30px", "maxWidth": "1000px", "margin": "0 auto"}) 