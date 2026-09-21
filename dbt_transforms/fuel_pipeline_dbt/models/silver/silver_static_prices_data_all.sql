{{ config(
    materialized='view' 
) }}

WITH silver_static_prices_data_all as (
    select 
        stationcode as station_code, 
        fueltype as fuel_type,
        price, 
        lastupdated
    FROM {{ ref('bronze_static_prices_data_all') }}

)


select * from silver_static_prices_data_all