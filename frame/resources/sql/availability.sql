SELECT
    station_id,
    hour::utinyint as hod,
    dayofweek(make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0))::utinyint as dow,
    num_bikes_available::utinyint as num_bikes_available,
    num_bikes_disabled::utinyint as num_bikes_disabled,
    num_docks_available::utinyint as num_docks_available,
    num_docks_disabled::utinyint as num_docks_disabled,
	make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) as 'ts',
    {% for i in minutes_to_eval %}
    minute(
		lead(
			make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0),
			{{i}}
		) over (
        	partition by station_id
        	order by make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0)
			asc
    	) - make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0)
	) as minutes_bt_check_{{i}},
    lead(num_bikes_available, {{i}}) over (
        partition by station_id
        order by make_timestamp(year::int, month::int, day::int, hour::int, minute::int, 0.0) asc
    ) > 0 as bikes_available_{{i}},
    {% endfor %}
FROM
    {{ parquet_partitioned_table('status') }}
WHERE
	status = 'IN_SERVICE'
	{% if station_id is defined and station_id is not none %}
	    AND station_id = {{station_id}}
	{% endif %}
	AND {{ filter_daterange(start_date, end_date) }}
