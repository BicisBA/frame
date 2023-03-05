SELECT
    station_id,
    hour,
    dayofweek(make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0)) as dow,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    status,
    {% for i in minutes_to_eval %}
    minute(lead(make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0), {{i}}) over (
        partition by station_id
        order by make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) asc
    ) - make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0)) as minutes_bt_check_{{i}},
    (lead(num_bikes_available, {{i}}) over (
        partition by station_id
        order by make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) asc
    ) > 0)::int as bikes_available_{{i}},
    {% endfor %}
FROM
    {{ parquet_partitioned_table('status') }}
WHERE
	{{ filter_dates(start_date, end_date) }}
    AND status = 'IN_SERVICE'
