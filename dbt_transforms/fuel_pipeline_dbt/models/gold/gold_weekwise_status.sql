{{ config(
    materialized='table'
) }}

with categorized_prices as (
    select 
        lastupdated,
        fuel_type,
        price,
        case 
            when day_of_week(date_parse(lastupdated, '%d/%m/%Y %H:%i:%s')) in (6, 7) then 'Weekend (Sat-Sun)'
            else 'Weekday (Mon-Fri)'
        end as day_category,
        
        lag(price, 1) over (partition by station_code, fuel_type order by lastupdated) as prev_price
    from {{ ref('gold_historic_data') }}
    where lastupdated is not null
)


select 
    day_category,
    fuel_type,
    round(avg(price), 2) as avg_price,
    round(avg(price - prev_price), 2) as avg_price_change, -- Weekend ya Weekday par average kitna badha/ghata
    count(*) as total_price_points
from categorized_prices
group by 1, 2
order by fuel_type, day_category