from datetime import timedelta
from pyspark.mllib.evaluation import BinaryClassificationMetrics


def get_dates(chartshow_date):
    results = {}
    results["end_date"] = "{0} 20:00:00".format(chartshow_date.strftime("%Y-%m-%d"))
    start_date = chartshow_date - timedelta(days=7)
    results["start_date"] = "{0} 00:00:00".format(start_date.strftime("%Y-%m-%d"))
    results["current_weekofyear"] = chartshow_date.isocalendar()[1] -1
    results["next_weekofyear"] = chartshow_date.isocalendar()[1]
    results["last_year"] = chartshow_date.year
    return results


def get_training_data(spark, chartshow_date):
    dates = get_dates(chartshow_date)

    df = spark.sql(
    """
    SELECT
        p.*,
        CASE WHEN next.rank IS NULL THEN 0 ELSE next.rank END AS nextrank,
        CASE WHEN current.rank IS NULL THEN 0 ELSE current.rank END AS currentrank,
        CASE WHEN next.rank IS NOT NULL THEN 1 ELSE 0 END AS label
    FROM
    (
        SELECT
            artist,
            title,
            year,
            month,
            week,
            COUNT(*) AS weekly_play_count
        FROM playlist
        GROUP BY
            artist,
            title,
            year,
            month,
            week
    ) p
    LEFT OUTER JOIN
    (
        SELECT
            artist,
            title,
            rank
        FROM
            chartshow
        WHERE
            YEAR(date) = {year}
            AND WEEKOFYEAR(date) = {next_weekofyear}
    )
    next ON p.artist = next.artist AND p.title = next.title
    LEFT OUTER JOIN
    (
        SELECT
            artist,
            title,
            rank
        FROM
            chartshow
        WHERE
            YEAR(date) = {year}
            AND WEEKOFYEAR(date) = {current_weekofyear}
    )
    current ON p.artist = current.artist AND p.title = current.title
    WHERE
    year = '{year}' AND week >={current_weekofyear} AND week <= '{next_weekofyear}'
    ORDER BY year, week, weekly_play_count DESC
    """.format(year=dates["last_year"], current_weekofyear=dates['current_weekofyear'], next_weekofyear=dates["next_weekofyear"], start=dates["start_date"], end=dates["end_date"]))
    return df.dropna()


def get_data(spark, chartshow_date):
    dates = get_dates(chartshow_date)

    df = spark.sql(
    """
    SELECT
        p.*,
        CASE WHEN current.rank IS NULL THEN 0 ELSE current.rank END AS currentrank
    FROM playlist p
    LEFT OUTER JOIN
    (
        SELECT
            artist,
            title,
            rank
        FROM
            chartshow
        WHERE 
            YEAR(date) = {year}
            AND WEEKOFYEAR(date) = {current_weekofyear}
    )
    current ON p.artist = current.artist AND p.title = current.title
    WHERE
    datetime >= '{start}' AND datetime <= '{end}'
    ORDER BY p.datetime DESC
    """.format(year=dates["last_year"], current_weekofyear=dates['current_weekofyear'], start=dates["start_date"], end=dates["end_date"]))
    return df.dropna()


def predict(model, data):

    results = model.transform(data)
    predictionsAndLabels = results.select("prediction", "label") \
                                  .rdd.map(lambda r: (float(r["prediction"]), float(r["label"])))
    metrics = BinaryClassificationMetrics(predictionsAndLabels)
    print "AUC: {0}".format(metrics.areaUnderROC)
    print "AUP: {0}".format(metrics.areaUnderPR)

    return results


def load(sqlContext, spark):
    sqlContext.read.format('com.databricks.spark.csv') \
        .option("header", True) \
        .option("inferSchema", True) \
        .load('output/csv/chartshow/*/*.csv') \
        .selectExpr("rank", "date", "LOWER(LTRIM(RTRIM(artist))) AS artist", "LOWER(LTRIM(RTRIM(title))) AS title") \
        .createOrReplaceTempView("chartshow")

    sqlContext.read.format('com.databricks.spark.csv') \
        .option("header", True) \
        .option("inferSchema", True) \
        .load('output/csv/*.csv') \
        .selectExpr("id", "datetime", "LOWER(LTRIM(RTRIM(artist))) AS artist", "LOWER(LTRIM(RTRIM(title))) AS title", "year", "month", "day", "day_of_week", "week", "hour") \
        .createOrReplaceTempView("playlist")

    spark.sql("""
    SELECT
        YEAR(date) AS year,
        WEEKOFYEAR(date) AS weekofyear
    FROM chartshow
    GROUP BY YEAR(date), WEEKOFYEAR(date)
    ORDER BY
        year ASC, weekofyear ASC
    """).createOrReplaceTempView("weeks")