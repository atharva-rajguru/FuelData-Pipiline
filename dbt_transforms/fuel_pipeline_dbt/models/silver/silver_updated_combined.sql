{{ config(
    materialized='view',
) }}

with a as (select distinct * from {{ref ('silver_updated_stations_data_all')}}),
b as (select distinct * from {{ref ('silver_updated_prices_data')}}),
silver_data_all_updated as (select * from a left join b on a.code = b.station_code)

select
        brand as brand_name, 
        station_code,
        name as brand_name_and_loc,
        address,
        trim(split_part(address, ',', 1)) as street_address,
        trim(regexp_extract(trim(split_part(address, ',', 2)),'^(.+)\s+NSW\s+[0-9]{4}$',1)) AS suburb_name,
        regexp_extract(address, '(\d{4})', 1) as postcode,
        latitude,
        longitude,
        is_adblue_available,
        fuel_type,
        price,
        lastupdated,
        'New' as status
        
     from silver_data_all_updated

