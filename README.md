### data pipeline for taiko dashboard

This is the code base for [taiko a3 dashboard](https://data.zkpool.io/public/dashboards/Aebs8y0nZ9w20wokJeFlIjWsi9DQcTVOzmBDpQXe?org_slug=default). The code's entry point is in `dags` dir. All files in `dags` dir are intended for Apache Airflow. In our team we use Apache Airflow heavily for scheduled tasks, but you can make only small changes to files in `dags` dir to migrate to crontab.

