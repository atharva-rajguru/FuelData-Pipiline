{{ config(
    materialized='view' 
) }}

WITH silver_static_stations_data_all as (
    select 
        brand,
        code,
        name,
        address,
        CAST(json_extract_scalar(location, '$.latitude') AS DOUBLE) AS latitude,
        CAST(json_extract_scalar(location, '$.longitude') AS DOUBLE) AS longitude,
        isadblueavailable as is_adblue_available
    
    FROM {{ ref('bronze_static_stations_data_all') }}
)

select * from silver_static_stations_data_all
