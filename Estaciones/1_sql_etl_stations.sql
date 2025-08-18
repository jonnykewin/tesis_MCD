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
	ST_SetSRID(ST_MakePoint(replace(db.long, ',', '.')::numeric  , replace(db.lat, ',', '.')::numeric ), 4326) as numeric
from estaciones.dimar_barranquilla db 
union
select 
	'dimar' as fuente,
	'santa_marta' as ciudad,
	(db.fecha||' '||db.hora) ::timestamp as fecha_toma,
	db.codigo_estacion codigo_estacion,
	replace(db.temperatura, ',', '.')::numeric as medicion,
	ST_SetSRID(ST_MakePoint(replace(db.long, ',', '.')::numeric  , replace(db.lat, ',', '.')::numeric ), 4326) as numeric
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


--=======================================================
--Creación del dataset final de estaciones consolidadas
--=======================================================
create table estaciones.estaciones_consolidadas as 
select * from estaciones.estaciones_dimar ed 
union
select * from estaciones.estaciones_ideam id;