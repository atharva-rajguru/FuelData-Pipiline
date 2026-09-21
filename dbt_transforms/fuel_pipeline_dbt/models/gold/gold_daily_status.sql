{{ config(
    materialized='table',
    incremental_strategy='append'
) }}

select *
from {{ref('gold_historic_data')}}
where date(date_parse(lastupdated, '%d/%m/%Y %H:%i:%s')) = current_date


