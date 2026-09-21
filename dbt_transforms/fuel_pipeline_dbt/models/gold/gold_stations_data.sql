{{ config(
    materialized='table',
    table_type='iceberg'
) }}

select distinct
    station_code,
    brand_name,
    latitude,
    longitude
from {{ ref('gold_historic_data') }}
where latitude is not null 
  and longitude is not null