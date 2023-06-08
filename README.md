### data pipeline for taiko testnet a3


<p align="center">
    <img src="https://github.com/hatark/hosted_files/blob/504310f9ff09ce835ef59b5ec617bc1856c69d8e/taiko_a3_dashboard.png"  />
</p>



**Please write an issue if you have improving suggestions about the dashboard!**

This is the data processing code base behind [taiko a3 dashboard](https://data.zkpool.io/public/dashboards/Aebs8y0nZ9w20wokJeFlIjWsi9DQcTVOzmBDpQXe?org_slug=default). The code's entry point is in `dags` dir. All files in `dags` dir are intended for Apache Airflow. In our team we use Apache Airflow heavily for scheduled tasks, but you can make only small changes to files in `dags` dir to migrate to crontab.

The dashboard itself is made using [redash](https://github.com/getredash/redash) and ran in our server.