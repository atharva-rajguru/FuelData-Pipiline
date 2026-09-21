{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

with incoming_data as (
    {% if not is_incremental() %}
        select * from {{ ref('silver_static_combined') }}
        union all
        select * from {{ ref('silver_updated_combined') }} where status = 'New'
    {% else %}
        -- Baad mein sirf naye live updates aayenge
        select * from {{ ref('silver_updated_combined') }} where status = 'New'
    {% endif %}
),

ranked_data as (
    select *,
        row_number() over (
            partition by station_code, fuel_type 
            order by lastupdated desc
        ) as rn
    from incoming_data
)

select 
    brand_name, 
    station_code, 
    brand_name_and_loc,
    address,
    street_address,
    suburb_name,
    postcode,
    latitude,
    longitude,
    is_adblue_available,
    fuel_type,
    price,
    lastupdated
from ranked_data
where rn = 1