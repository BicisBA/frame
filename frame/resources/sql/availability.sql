WITH base_status AS (
SELECT
    station_id,
    hour,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    status,
    make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) as ts,
FROM
    {{ parquet_partitioned_table('status') }}
WHERE
	status = 'IN_SERVICE'
	{% if station_id is defined and station_id is not none %}
	    AND station_id = {{station_id}}
	{% endif %}
	AND {{ filter_daterange(start_date, end_date) }}
)
{% for i in range(1,17, 3) %}
    {% if not loop.first %}
UNION
    {% endif %}
SELECT
    station_id,
    hour::int hod,
    dayofweek(ts) as dow,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    minute(lead(ts, {{i}}) over (
        order by ts asc
    ) - ts)  as minutes_bt_check,
    (lead(num_bikes_available, {{i}}) over (
        order by ts asc
    ) > 0)::int as bikes_available,
FROM
    base_status
{% endfor %}