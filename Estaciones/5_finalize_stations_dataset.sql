-- =========================================================
-- 1) consolidado de gpkg finales → estaciones_nuevas.estaciones_datos
-- =========================================================

drop table if exists estaciones_nuevas.estaciones_datos;


create table estaciones_nuevas.estaciones_datos as
select
	fuente,
	ciudad,
	fecha_toma,
	codigo_estacion,
	medicion,
	lst1 as lst,
	sea_water1 as sea_water,
	fresh_water1 as fresh_water,
	builds1 as builds,
	clouds1 as clouds,
	bare1 as bare_ground,
	veg1 as veg,
	ndbi1 as ndbi,
	ndwi1 as ndwi,
	ndvi1 as ndVi,
	st_emissivity1  as st_emissivity, 
	geometry
from 
(select *
from estaciones_meteorologicas_final_barranquilla_2015
union 
select *
from estaciones_meteorologicas_final_barranquilla_2016
union 
select *
from estaciones_meteorologicas_final_barranquilla_2017
union 
select *
from estaciones_meteorologicas_final_barranquilla_2018
union 
select *
from estaciones_meteorologicas_final_barranquilla_2019
union 
select *
from estaciones_meteorologicas_final_barranquilla_2020
union 
select *
from estaciones_meteorologicas_final_barranquilla_2021
union 
select *
from estaciones_meteorologicas_final_barranquilla_2022
union 
select *
from estaciones_meteorologicas_final_barranquilla_2023
union
select *
from estaciones_meteorologicas_final_barranquilla_2024
union 
select *
from estaciones_meteorologicas_final_cartagena_2015
union 
select *
from estaciones_meteorologicas_final_cartagena_2016
union 
select *
from estaciones_meteorologicas_final_cartagena_2017
union 
select *
from estaciones_meteorologicas_final_cartagena_2018
union 
select *
from estaciones_meteorologicas_final_cartagena_2019
union 
select *
from estaciones_meteorologicas_final_cartagena_2020
union 
select *
from estaciones_meteorologicas_final_cartagena_2021
union 
select *
from estaciones_meteorologicas_final_cartagena_2022
union 
select *
from estaciones_meteorologicas_final_cartagena_2023
union 
select *
from estaciones_meteorologicas_final_cartagena_2024
union 
select *
from estaciones_meteorologicas_final_santa_marta_2015
union 
select *
from estaciones_meteorologicas_final_santa_marta_2016
union 
select *
from estaciones_meteorologicas_final_santa_marta_2017
union 
select *
from estaciones_meteorologicas_final_santa_marta_2018
union 
select *
from estaciones_meteorologicas_final_santa_marta_2019
union 
select *
from estaciones_meteorologicas_final_santa_marta_2020
union 
select *
from estaciones_meteorologicas_final_santa_marta_2021
union 
select *
from estaciones_meteorologicas_final_santa_marta_2022
union 
select *
from estaciones_meteorologicas_final_santa_marta_2023
union 
select *
from estaciones_meteorologicas_final_santa_marta_2024);


-- =========================================================
-- 2) Limpieza: eliminar registros sin ningún valor raster
-- =========================================================
delete from estaciones_datos ef 
where ef.lst is null and
ef.sea_water is null and
ef.fresh_water is null and
ef.builds is null and
ef.clouds is null and
ef.bare_ground is null and
ef.veg is null and
ef.ndbi is null and
ef.ndwi is null and
ef.ndvi is null and
ef.st_emissivity is null;


-- =========================================================
-- 3) filtro: medición más cercana a las 10:00 (UTCpor fuente, ciudad, estación y día
-- =========================================================

create table estaciones_final as 
WITH base AS (
  SELECT
    ef.*,
    date_trunc('day', ef.fecha_toma) + interval '10 hour'        AS target_10am,
    abs(extract(epoch from (ef.fecha_toma - (date_trunc('day', ef.fecha_toma) + interval '10 hour')))) AS diff_sec,
    ef.fecha_toma::date AS fecha_dia
  FROM estaciones_nuevas.estaciones_datos AS ef
),
ranked AS (
  SELECT
    b.*,
    row_number() OVER (
      PARTITION BY b.fuente, b.ciudad, b.codigo_estacion, b.fecha_dia
      ORDER BY
        b.diff_sec ASC,                                              -- más cerca a las 10:00
        CASE WHEN b.fecha_toma >= b.target_10am THEN 0 ELSE 1 END,  -- si empata, prefiero justo después de las 10
        b.fecha_toma                                                -- y el más temprano
    ) AS rn
  FROM base b
)
SELECT *
FROM ranked
WHERE rn = 1
ORDER BY fuente, ciudad, codigo_estacion, fecha_dia;


--===============================================
-- 4) Limpieza: eliminar registros sin ningún valor raster
--===============================================
delete from estaciones_final ef 
where ef.lst is null or
ef.sea_water is null or
ef.fresh_water is null or
ef.builds is null or
ef.clouds is null or
ef.bare_ground is null or
ef.veg is null or
ef.ndbi is null or
ef.ndwi is null or
ef.ndvi is null or
ef.st_emissivity is null;


--Cuando la diferencia entre la medición y el LST es mayor a 25
delete 
from estaciones_final as ef
where abs(ef.lst::numeric -ef.medicion::numeric) > 25;

--===============================================
-- 4) Dataset: Final para entrada del modelo
--===============================================
create table estaciones_nuevas.estaciones_estudio as
select 
	ef.fuente,
	ef.ciudad,
	ef.codigo_estacion,
	ef.fecha_toma,
	extract (year from ef.fecha_toma) as anio,
	extract (month from ef.fecha_toma) as mes,
	extract (day from ef.fecha_toma) as dia,
	round(ef.medicion::numeric,3) medicion,
	ef.sea_water,
	ef.fresh_water,
	ef.builds,
	ef.clouds,
	ef.bare_ground,
	ef.veg,
	ef.lst,
	ef.ndbi,
	ef.ndvi,
	ef.ndwi,
	ef.st_emissivity,
	round(st_y(ST_Transform(ef.geometry,9377))::numeric,4) as norte,
	round(st_x(ST_Transform(ef.geometry,9377))::numeric,4) as este
from estaciones_nuevas.estaciones_final ef ;


create table estaciones_nuevas.estaciones_estudio_geo as
select 
	ef.fuente,
	ef.ciudad,
	ef.codigo_estacion,
	ef.fecha_toma,
	extract (year from ef.fecha_toma) as anio,
	extract (month from ef.fecha_toma) as mes,
	extract (day from ef.fecha_toma) as dia,
	round(ef.medicion::numeric,3) medicion,
	ef.sea_water,
	ef.fresh_water,
	ef.builds,
	ef.clouds,
	ef.bare_ground,
	ef.veg,
	ef.lst,
	ef.ndbi,
	ef.ndvi,
	ef.ndwi,
	ef.st_emissivity,
	round(st_y(ST_Transform(ef.geometry,9377))::numeric,4) as norte,
	round(st_x(ST_Transform(ef.geometry,9377))::numeric,4) as este,
	ST_Transform(ef.geometry,9377) as geom
from estaciones_nuevas.estaciones_final ef ;