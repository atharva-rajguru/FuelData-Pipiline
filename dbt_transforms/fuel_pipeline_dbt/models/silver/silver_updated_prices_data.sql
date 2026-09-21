{{ config(
    materialized='view' 
) }}

WITH silver_updated_prices_data as (
    select 
        stationcode as station_code, 
        fueltype as fuel_type,
        price, 
        lastupdated
    FROM {{ ref('bronze_updated_prices_data') }}
)

select * from silver_updated_prices_data
