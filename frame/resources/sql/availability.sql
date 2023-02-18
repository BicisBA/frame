WITH base_status AS (select
    station_id,
    hour,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    status,
    make_timestamp(year, month, day, hour, minute, 0.0) as ts,
from
    status
where
    station_id = {} and
    status = 'IN_SERVICE'
)
{% for i in range(1,17, 3) %}

{% endfor %}
