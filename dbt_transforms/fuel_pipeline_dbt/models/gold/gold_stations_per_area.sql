{{
    config(
    materialized='table',
    table_type='iceberg')
}}

select 
    suburb_name, 
    count(distinct station_code) as unique_stations_count
from {{ ref('gold_historic_data') }}
group by suburb_name