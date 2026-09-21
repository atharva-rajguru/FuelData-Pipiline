{{ config(
    materialized='table',
    table_type='iceberg'
) }}

select 
    brand_name,
    fuel_type,
    is_adblue_available,
    sum(distinct station_code) as total_stations_offering,
    round(avg(price), 2) as average_price,
    min(price) as lowest_price,
    max(price) as highest_price
from {{ ref('gold_historic_data') }}
group by 
    brand_name, 
    fuel_type, 
    is_adblue_available