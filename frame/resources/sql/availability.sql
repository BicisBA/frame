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
	{% if not loop.last %}
		UNION
	{% endfor %}
SELECT
    station_id,
    hour,
    dayofweek(ts) as dow,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    minute(lead(ts, {}) over (
        order by ts asc
    ) - ts)  as minutes_bt_check,
    lead(num_bikes_available, {}) over (
        order by ts asc
    ) as bikes_available,
FROM
    base_status
{% endfor %}
