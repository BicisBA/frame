SELECT
    station_id::usmallint as station_id,
    num_bikes_available::utinyint as num_bikes_available,
    num_bikes_disabled::utinyint as num_bikes_disabled,
    num_docks_available::utinyint as num_docks_available,
    num_docks_disabled::utinyint as num_docks_disabled,
    hour::int as hod,
    dayofweek(make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0))::utinyint as dow,
    date_diff(
        'minute',
        make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0),
        MIN(CASE WHEN num_bikes_available > prev_num_bikes_available THEN make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) END) OVER (
            PARTITION BY station_id ORDER BY make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0)
            ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING
        )
    ) AS minutes_until_next_bike_arrival
FROM (
    SELECT
        *,
        LAG(num_bikes_available) OVER (
            PARTITION BY station_id ORDER BY last_reported, year, month, day, hour, minute
        ) AS prev_num_bikes_available
    FROM {{ parquet_partitioned_table('status') }}
    WHERE status = 'IN_SERVICE'
    {% if station_id is defined and station_id is not none %}
	    AND station_id = {{station_id}}
	{% endif %}
    AND {{ filter_daterange(start_date, end_date) }}
) subquery
