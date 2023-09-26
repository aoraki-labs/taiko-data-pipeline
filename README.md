# data pipeline for taiko testnet a3

<p align="center">
    <img src="https://raw.githubusercontent.com/hatark/hosted_files/main/taiko-icon-blk-md.svg" />
</p>



**Please write an issue if you have improving suggestions about the dashboard!**

This is the data processing code base behind [taiko a5 dashboard](https://data.zkpool.io/public/dashboards/tB19TP9i8MicP2MAzQSlB6IQ27M5JKPkUg7HN2Kz?org_slug=default). The code's entry point is in `dags` dir. All files in `dags` dir are intended for Apache Airflow. In our team we use Apache Airflow heavily for scheduled tasks, but you can make only small changes to files in `dags` dir to migrate to crontab.

The dashboard itself is made using [redash](https://github.com/getredash/redash) and ran in our server.