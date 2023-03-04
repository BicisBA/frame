SELECT
    station_id,
    hour,
    dayofweek(make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0)) as dow,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    status,
{% for i in range(1, 7) %}
    (lead(num_bikes_available, {{i}}) over (
        partition by station_id
        order by make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) asc
    ) > 0)::int as bikes_available_{{i}},
{% endfor %}
{% for i in range(7,18,3) %}
    (lead(num_bikes_available, {{i}}) over (
        partition by station_id
        order by make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) asc
    ) > 0)::int as bikes_available_{{i}} {% if not loop.last %},{% endif %}
{% endfor %}
FROM
    {{ parquet_partitioned_table('status') }}
WHERE
	{{ filter_daterange(start_date, end_date) }}
    AND status = 'IN_SERVICE'
