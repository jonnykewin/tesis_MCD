/***************************************************************************
           Query de limpieza y preparación de estaciones metereologicas
           para las ciudades de Barranquilla, Santa Marta y Cartagena
              -------------------------------------------------------

***************************************************************************/

--=========================================
--Consolidación estacion DIMAR
--=========================================

create table estaciones.estaciones_dimar as 
select 
	'dimar' as fuente,
	'barranquilla' as ciudad,
	(db.fecha||' '||db.hora) ::timestamp as fecha_toma,
	db.codigo_estacion codigo_estacion,
	replace(db.temperatura, ',', '.')::numeric as medicion,
	ST_SetSRID(ST_MakePoint(replace(db.long, ',', '.')::numeric  , replace(db.lat, ',', '.')::numeric ), 4326) as geometria
from estaciones.dimar_barranquilla db 
union
select 
	'dimar' as fuente,
	'santa_marta' as ciudad,
	(db.fecha||' '||db.hora) ::timestamp as fecha_toma,
	db.codigo_estacion codigo_estacion,
	replace(db.temperatura, ',', '.')::numeric as medicion,
	ST_SetSRID(ST_MakePoint(replace(db.long, ',', '.')::numeric  , replace(db.lat, ',', '.')::numeric ), 4326) as geometria
from estaciones.dimar_santa_marta db 

--Limpieza de valores atipicios de mediciones estaciones DIMAR
delete from estaciones.estaciones_dimar where medicion = -99999;

--=====================================================
--Consolidación estacion IDEAM
--=====================================================
create table estaciones.estaciones_ideam as 
select 
	'ideam' as fuente,
	lower(id."Municipio") as ciudad,
	id."FechaObservacion" ::timestamp as fecha_toma,
	id."CodigoEstacion" as codigo_estacion,
	id."ValorObservado" ::numeric as medicion,
	ST_SetSRID(ST_MakePoint(id."Longitud" ::numeric, id."Latitud" ::numeric),4326) as geometria
from estaciones.ideam id
where id."FechaObservacion" :: date in (
  DATE '2015-04-01',
  DATE '2016-01-14',
  DATE '2017-01-16',
  DATE '2018-02-04',
  DATE '2019-01-06',
  DATE '2020-03-29',
  DATE '2021-02-12',
  DATE '2022-02-23',
  DATE '2023-01-17',
  DATE '2024-01-20'
);

--=====================================================
--Consolidación estaciones ERA5 LAND
--=====================================================
create table estaciones.estaciones_era5 as 
select 
	'era5_land' as fuente,
	case 
		when el.ciudad like 'santa marta' then 'santa_marta'
		else el.ciudad
	end as ciudad,
	(el.date||' '||'10:00:00.000') ::timestamp as fecha_toma,
	el.codigo_estacion as codigo_estacion,
	el."first" ::numeric as medicion,
	ST_SetSRID(ST_MakePoint(el.lon ::numeric ,el.lat ::numeric),4326) as geometria
from estaciones.era5land el 
where el."first" != '';

--=====================================================
--Consolidación estacion ERA5 hourly
--=====================================================
create table estaciones.estaciones_era5_hourly as 
select 
	'era5_hourly' as fuente,
	case 
		when erm.ciudad like 'santa marta' then 'santa_marta'
		else erm.ciudad
	end as ciudad,
	(erm.date||' '||'10:00:00.000') ::timestamp as fecha_toma,
	erm.codigo_estacion as codigo_estacion,
	erm."first" ::numeric as medicion,
	ST_SetSRID(ST_MakePoint(erm.lon ::numeric ,erm.lat ::numeric),4326) as geometria
from estaciones.eramar erm
where erm."first" != '';


--=======================================================
--Creación del dataset final de estaciones consolidadas
--=======================================================
create table estaciones.estaciones_consolidadas as 
select * from estaciones.estaciones_dimar ed 
union
select * from estaciones.estaciones_ideam id
union
select * from estaciones.estaciones_era5
union 
select * from estaciones.estaciones_era5_hourly;


update  estaciones.estaciones_consolidadas set
ciudad = 'santa_marta'
where ciudad = 'santa marta';
