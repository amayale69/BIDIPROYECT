CREATE SEQUENCE public.id_trayecto_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE SEQUENCE public.id_periodo_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE SEQUENCE public.id_proyecto_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE SEQUENCE public.id_seccion_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE SEQUENCE public.id_metodo_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE SEQUENCE public.id_tipo_desarrollo_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE SEQUENCE public.id_accede_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1;

CREATE TYPE public.generos AS ENUM ('Masculino', 'Femenino');
COMMENT ON TYPE public.generos IS 'Tipo de Dato Enum para seleccionar sexo de las personas';
CREATE TYPE public.trayecto_tipo AS ENUM ('Regular', 'Prosecución');
COMMENT ON TYPE public.trayecto_tipo IS 'Tipo de Dato Enum para seleccionar el tipo de trayecto';
CREATE TYPE public.ID_trayecto AS ENUM ('TRAYECTO I', 'TRAYECTO II', 'TRAYECTO III', 'TRAYECTO IV');
COMMENT ON TYPE public.ID_trayecto IS 'Tipo de Dato Enum para seleccionar el trayecto a registrar';
CREATE TYPE public.ID_seccion AS ENUM ('IF-01', 'IF-02', 'IF-03', 'IF-04','IF-05', 'IF-06');
COMMENT ON TYPE public.ID_seccion IS 'Tipo de Dato Enum para seleccionar la seccion del grupo de desarrollo';
CREATE TYPE public.Estado_Registro AS ENUM ('Activo', 'Inactivo');
COMMENT ON TYPE public.Estado_Registro IS 'Tipo de Dato Enum indicar si un registro esta activo o inactivo';
CREATE TYPE public.Roles AS ENUM ('Academico', 'Tecnico Metodologico', 'Comunitario');
COMMENT ON TYPE public.Roles IS 'Tipo de Dato Enum indicar si un registro esta activo o inactivo';

CREATE TABLE public.usuarios (
	usuario character varying(15), responsable character varying(45), 
	clave character varying(64), estado Estado_Registro DEFAULT 'Activo'::Estado_Registro, 
	CONSTRAINT usuarios_pkey PRIMARY KEY (usuario)) WITH (OIDS = FALSE) 
TABLESPACE pg_default;

CREATE TABLE public.metodologia (
	id_metodo integer NOT NULL DEFAULT nextval('id_metodo_seq'::regclass), 
	descripcion character varying(25), 
	CONSTRAINT id_metodo_pkey PRIMARY KEY (id_metodo)) 
WITH (OIDS = FALSE) TABLESPACE pg_default;

CREATE TABLE public.tipo_de_desarrollo (
	id_tipo_desarrollo integer NOT NULL DEFAULT nextval('id_tipo_desarrollo_seq'::regclass), 
	tipo_desarrollo character varying(25), 
	CONSTRAINT id_tipo_desarrollo_pkey PRIMARY KEY (id_tipo_desarrollo)) 
WITH (OIDS = FALSE) TABLESPACE pg_default;

CREATE TABLE public.trayecto (
	id_trayecto integer NOT NULL DEFAULT nextval('id_trayecto_seq'::regclass), 
	nivel ID_trayecto DEFAULT 'TRAYECTO I'::ID_trayecto, 
	periodo_academico integer, 
	CONSTRAINT id_trayecto_pkey PRIMARY KEY (id_trayecto));

CREATE TABLE public.secciones (
	id_seccion integer NOT NULL DEFAULT nextval('id_seccion_seq'::regclass), 
	siglas ID_seccion DEFAULT 'IF-01'::ID_seccion, 
	tipo_seccion trayecto_tipo DEFAULT 'Regular'::trayecto_tipo, 
	ano_seccion numeric(4,0), 
	nro_estudiantes integer, 
	FK_id_trayecto integer, 
	CONSTRAINT id_seccion_pkey PRIMARY KEY (id_seccion), 
	CONSTRAINT FK_id_trayecto FOREIGN KEY (FK_id_trayecto) REFERENCES public.trayecto (id_trayecto) 
	MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE);

CREATE TABLE public.proyectos (
	id_proyecto integer NOT NULL DEFAULT nextval('id_proyecto_seq'::regclass), 
	codigo_proyecto character varying(28), 
	numero_grupo_proyecto numeric(2,0), 
	titulo_proyecto character varying(100), 
	nombre_informe_codificado character varying(40), 
	nombre_desarrollo_codificado character varying(40), 
	nombre_manual_codificado character varying(40), 
	FK_id_seccion integer, 
	FK_id_metodo integer, 
	FK_id_tipo_desarrollo integer, 
	CONSTRAINT id_proyecto_pkey PRIMARY KEY (id_proyecto), 
	CONSTRAINT FK_id_seccion FOREIGN KEY (FK_id_seccion) REFERENCES public.secciones (id_seccion) 
	MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE, 
	CONSTRAINT FK_id_metodo FOREIGN KEY (FK_id_metodo) REFERENCES public.metodologia (id_metodo) 
	MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE, 
	CONSTRAINT FK_id_tipo_desarrollo FOREIGN KEY (FK_id_tipo_desarrollo) REFERENCES public.tipo_de_desarrollo (id_tipo_desarrollo) 
	MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE) 
WITH (OIDS = FALSE) TABLESPACE pg_default;

CREATE TABLE public.accede (
	id_accede integer NOT NULL DEFAULT nextval('id_accede_seq'::regclass), 
	FK_usuario character varying(15), 
	FK_id_proyecto integer, 
	actividad character varying(10), 
	fecha date, 
	CONSTRAINT id_registra_pkey PRIMARY KEY (id_accede), 
	CONSTRAINT FK_usuario FOREIGN KEY (FK_usuario) REFERENCES public.usuarios (usuario) 
	MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION, 
	CONSTRAINT FK_id_proyecto FOREIGN KEY (FK_id_proyecto) REFERENCES public.proyectos (id_proyecto) 
	MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION) 
WITH (OIDS = FALSE) TABLESPACE pg_default;

CREATE TABLE public.estudiante (
	cedula_estudiante numeric(8,0), 
	nombre_estudiante character varying(30), 
	apellido_estudiante character varying(30), 
	genero_estudiante generos DEFAULT 'Masculino'::generos, 
	telefono_estudiante character varying(16), 
	estado Estado_Registro DEFAULT 'Activo'::Estado_Registro, 
	CONSTRAINT cedula_estudiante_pkey PRIMARY KEY (cedula_estudiante));

CREATE TABLE public.tutores (
	cedula_tutor numeric(8,0), 
	nombre_tutor character varying(30), 
	apellido_tutor character varying(30), 
	genero_tutor generos DEFAULT 'Masculino'::generos, 
	telefono_tutor character varying(16), 
	cantidad_alumnos integer, 
	estado Estado_Registro DEFAULT 'Activo'::Estado_Registro, 
	CONSTRAINT cedula_tutor_pkey PRIMARY KEY (cedula_tutor));

CREATE TABLE public.elaboran (
	FK_id_proyecto integer, 
	FK_cedula_estudiante numeric(8,0), 
	CONSTRAINT FK_cedula_estudiante FOREIGN KEY (FK_cedula_estudiante) 
	REFERENCES public.estudiante (cedula_estudiante) 
	MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION, 
	CONSTRAINT FK_id_proyecto FOREIGN KEY (FK_id_proyecto) 
	REFERENCES public.proyectos (id_proyecto) 
	MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION) 
WITH (OIDS = FALSE) TABLESPACE pg_default;

CREATE TABLE public.es_asesorado (
	FK_id_proyecto integer, 
	FK_cedula_tutor numeric(8,0), 
	rol Roles DEFAULT 'Academico'::Roles, 
	CONSTRAINT FK_id_proyecto FOREIGN KEY (FK_id_proyecto) 
	REFERENCES public.proyectos (id_proyecto) 
	MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION, 
	CONSTRAINT FK_cedula_tutor FOREIGN KEY (FK_cedula_tutor) 
	REFERENCES public.tutores (cedula_tutor) 
	MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION) 
WITH (OIDS = FALSE) TABLESPACE pg_default;

