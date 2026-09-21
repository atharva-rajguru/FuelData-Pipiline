WITH bronze_updated_stations_data_all AS (
    SELECT * 
    FROM {{ source('nsw_fuel_raw', 'updated_stations_data_all') }}
)

SELECT *
FROM bronze_updated_stations_data_all