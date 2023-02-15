WITH base_status AS (SELECT
    station_id,
    hour,
    num_bikes_available,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    status,
    make_timestamp(year, month, day, hour, minute, 0.0) as ts,
FROM
    status
WHERE
    station_id = {} and
    status = 'IN_SERVICE'),
status_by_minute AS (
	{% for i in range(1, 16) %}
		{% if not loop.last %}
	UNION
		{% endif %}
	SELECT
    	station_id,
    	hour,
    	dayofweek(ts) as dow,
    	num_bikes_available,
    	num_bikes_disabled,
    	num_docks_available,
    	num_docks_disabled,
    	minute(lead(ts, {i}) over (
    	    order by ts asc
    	) - ts)  as minutes_bt_check,
    	lead(num_bikes_available, {i}) over (
    	    order by ts asc
    	) as bikes_available,
	FROM
    	base_status
	{% endfor %}
)
SELECT station_id,
    hour,
    dow,
    num_bikes_disabled,
    num_docks_available,
    num_docks_disabled,
    minutes_bt_check
FROM status_by_minute
WHERE num_bikes_available = 0
AND bikes_available > 0
