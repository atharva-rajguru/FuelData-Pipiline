WITH bronze_static_prices_data_all AS (
    SELECT * 
    FROM {{ source('nsw_fuel_raw', 'static_prices_data_all') }}
)

SELECT *
FROM bronze_static_prices_data_all