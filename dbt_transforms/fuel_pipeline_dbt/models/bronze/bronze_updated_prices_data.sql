WITH bronze_updated_prices_data AS (
    SELECT * 
    FROM {{ source('nsw_fuel_raw', 'updated_prices_data') }}
)

SELECT *
FROM bronze_updated_prices_data