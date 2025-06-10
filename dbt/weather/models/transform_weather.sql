SELECT
  data:main.temp::FLOAT AS temperature,
  data:main.humidity::INT AS humidity,
  data:weather[0].description::STRING AS description,
  data:dt::TIMESTAMP AS timestamp
FROM raw_weather
