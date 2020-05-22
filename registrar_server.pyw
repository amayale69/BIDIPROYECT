#-----------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                          #
# Programador: Luis Amaya                                                           #
# Analistas: Jose Astudillo / josmary Botaban                                       #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre    #
# Octubre (2018)                                                                    #
# Version 1.0                                                                       #
# Modulo: Registrar Server                                                          #
# Descripción: Rutina para crear y/o actualizar los datos de acceso a la base de    #
#              datos y generar las estructuras de tablas e indicas del sistema      #
#-----------------------------------------------------------------------------------#

# Importacion de librerias del sistema
import sys, re
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMainWindow, QAction, QPushButton, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QIODevice
from datetime import datetime, date, time, timedelta
import calendar
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib
import pprint
import hashlib
import random
import select
import ctypes #GetSystemMetrics
import os.path as path
class DialogoAcceso(QDialog):
	def __init__(self):

		QDialog.__init__(self)
		uic.loadUi("registrar_BD.ui", self)
		self.setEnabled(True)
		#Colocar titulo de la pantalla
		self.setWindowTitle("BIDIPROYECT - Registrar Base de Datos")
		self.lblTituloPantalla.setText("Registro de Base de Datos")
		#Operacion para centrar la ventana en la pantalla
		resolucion = ctypes.windll.user32
		resolucion_ancho = resolucion.GetSystemMetrics(0)
		resolucion_alto = resolucion.GetSystemMetrics(1)
		self.archivo_infosvr = ''
		self.infosvr = []
		self.lista = []
		self.BD_Name = ''
		self.BD_User = ''
		self.BD_Pass = ''
		left = (resolucion_ancho / 2) - (self.frameSize().width() / 2)
		top = (resolucion_alto / 2) - (self.frameSize().height() / 2)
		self.move(left, top)
		if path.exists('./regsvr.txt'):
			self.archivo_infosvr = open('regsvr.txt','r')
			self.infosvr = self.archivo_infosvr.readlines()
			self.BD_Name = self.infosvr[0]
			self.BD_Name = self.BD_Name.replace('\n', '').replace('\r', '') 
			self.BD_User = self.infosvr[1]
			self.BD_User = self.BD_User.replace('\n', '').replace('\r', '') 
			self.BD_Pass = self.infosvr[2]
			self.BD_Pass = self.BD_Pass.replace('\n', '').replace('\r', '') 
			self.archivo_infosvr.close
		else:
			self.BD_Name = ''
			self.BD_User = ''
			self.BD_Pass = ''
		self.txtDatabase.setText(self.BD_Name)
		self.txtUsuarioBD.setText(self.BD_User)
		self.txtClaveBD.setText(self.BD_Pass)

		self.btnRegistrar.clicked.connect(self.actualiza_server)


	def actualiza_server(self):
		self.BD_Name = self.txtDatabase.text()
		self.BD_User = self.txtUsuarioBD.text()
		self.BD_Pass = self.txtClaveBD.text()
		print(self.BD_Name + ", " + self.BD_User + ", " + self.BD_Pass)
		if self.txtDatabase.text() == '' or self.txtUsuarioBD.text() == '':
			QMessageBox.warning(self, "Error", "No ha cargado los datos de acceso a la Base de Datos, registre los datos o pulse salir", QMessageBox.Ok)
		else:
			#Establecer conexion a la Base de Datos
			cad_con = "dbname='%s' user='%s' password='%s' host='localhost'" % (self.BD_Name, self.BD_User, self.BD_Pass)

			try:
				self.db = psycopg2.connect(cad_con)
			except mysql.connector.Error as err:
				if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
					print("Algo esta equivocado en su usuario y/o clave")
				elif err.errno == errorcode.ER_BAD_DB_ERROR:
					print("Base de datos no existe...")
				else:
					print(err)
			else:
				self.archivo_infosvr = open('regsvr.txt','w')
				self.archivo_infosvr.write(self.BD_Name + '\n')
				self.archivo_infosvr.write(self.BD_User + '\n')
				self.archivo_infosvr.write(self.BD_Pass)
				self.archivo_infosvr.close
				print("Proceso Archivo de Registro Creado y/o Actualizado...")
				respuesta=QMessageBox.warning(self,"Adventencia", "Desea crear las tablas del sistema?: ", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.Yes:
					self.crear_tablas()
					self.db.close()
				self.close()

	# Rutina para crear las estructuras de datos en la Base de Datos
	def crear_tablas(self):
		print('Entro a Crear Tablas')
		self.db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
		cursor = self.db.cursor()

		hoy = datetime.today()
		formato_fecha2 = "%Y-%m-%d %H:%M:%S"
		lv_fechareg = hoy.strftime(formato_fecha2)
		crear_autoinc_trayecto = "CREATE SEQUENCE public.id_trayecto_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc_trayecto)

		crear_autoinc1 = "CREATE SEQUENCE public.id_periodo_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc1)

		crear_autoinc2 = "CREATE SEQUENCE public.id_proyecto_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc2)

		crear_autoinc3 = "CREATE SEQUENCE public.id_seccion_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc3)

		crear_autoinc4 = "CREATE SEQUENCE public.id_metodo_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc4)

		crear_autoinc5 = "CREATE SEQUENCE public.id_tipo_desarrollo_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc5)

		crear_autoinc6 = "CREATE SEQUENCE public.id_accede_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999 CACHE 1"
		cursor.execute(crear_autoinc6)
		print('Paso Definir Autoincrementadores')

		Crear_Tipo_Genero = "CREATE TYPE public.generos AS ENUM ('Masculino', 'Femenino')"
		Comm_Tipo_Genero = "COMMENT ON TYPE public.generos IS 'Tipo de Dato Enum para seleccionar sexo de las personas'"
		Crear_Tipo_Trayecto = "CREATE TYPE public.trayecto_tipo AS ENUM ('Regular', 'Prosecución')"
		Comm_Tipo_Trayecto = "COMMENT ON TYPE public.trayecto_tipo IS 'Tipo de Dato Enum para seleccionar el tipo de trayecto'"
		Crear_Trayecto = "CREATE TYPE public.ID_trayecto AS ENUM ('TRAYECTO I', 'TRAYECTO II', 'TRAYECTO III', 'TRAYECTO IV')"
		Comm_Trayecto = "COMMENT ON TYPE public.ID_trayecto IS 'Tipo de Dato Enum para seleccionar el trayecto a registrar'"
		Crear_ID_seccion = "CREATE TYPE public.ID_seccion AS ENUM ('IF-01', 'IF-02', 'IF-03', 'IF-04','IF-05', 'IF-06')"
		Comm_ID_seccion = "COMMENT ON TYPE public.ID_seccion IS 'Tipo de Dato Enum para seleccionar la seccion del grupo de desarrollo'"
		Crear_Estado_Registro = "CREATE TYPE public.Estado_Registro AS ENUM ('Activo', 'Inactivo')"
		Comm_Estado_Registro = "COMMENT ON TYPE public.Estado_Registro IS 'Tipo de Dato Enum indicar si un registro esta activo o inactivo'"
		Crear_Roles = "CREATE TYPE public.Roles AS ENUM ('Academico', 'Tecnico Metodologico', 'Comunitario')"
		Comm_Roles = "COMMENT ON TYPE public.Roles IS 'Tipo de Dato Enum indicar si un registro esta activo o inactivo'"

		cursor.execute(Crear_Tipo_Genero)
		cursor.execute(Comm_Tipo_Genero)
		cursor.execute(Crear_Tipo_Trayecto)
		cursor.execute(Comm_Tipo_Trayecto)
		cursor.execute(Crear_Trayecto)
		cursor.execute(Comm_Trayecto)
		cursor.execute(Crear_ID_seccion)
		cursor.execute(Comm_ID_seccion)
		cursor.execute(Crear_Estado_Registro)
		cursor.execute(Comm_Estado_Registro)
		cursor.execute(Crear_Roles)
		cursor.execute(Comm_Roles)
		print('Paso Definir Tipos Enums')

		lv_usuario = 'ADMIN'
		lv_padmin = 'ADMIN'
		lv_clave_admin = bytes(lv_padmin, 'utf-8')
		lv_password = hashlib.sha256(lv_clave_admin).hexdigest()

		crear_tb_usuarios 	= "CREATE TABLE public.usuarios (usuario character varying(15), responsable character varying(45), clave character varying(64), estado Estado_Registro DEFAULT 'Activo'::Estado_Registro, CONSTRAINT usuarios_pkey PRIMARY KEY (usuario)) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_usuarios 	= "COMMENT ON TABLE public.usuarios IS 'Registro de usuarios del sistema'"
		comm2_tb_usuarios 	= "COMMENT ON COLUMN public.usuarios.usuario IS 'Nombre de usuario no mayor de 15 caracteres'"
		comm3_tb_usuarios 	= "COMMENT ON COLUMN public.usuarios.responsable IS 'Nombre del responsable de usuario'"
		comm4_tb_usuarios 	= "COMMENT ON COLUMN public.usuarios.clave IS 'Clave de acceso del usuario'"
		comm5_tb_usuarios 	= "COMMENT ON COLUMN public.usuarios.estado IS 'Se utiliza para filtrar listas de registros Activos'"
		inserta_usuario_admin = "INSERT INTO usuarios VALUES('ADMIN', 'Administrador principal', '%s')" % (lv_password)

		cursor.execute(crear_tb_usuarios)
		cursor.execute(comm1_tb_usuarios)
		cursor.execute(comm2_tb_usuarios)
		cursor.execute(comm3_tb_usuarios)
		cursor.execute(comm4_tb_usuarios)
		cursor.execute(comm5_tb_usuarios)
		cursor.execute(inserta_usuario_admin)
		print('Paso Usuarios')

		crear_tb_metodologia = "CREATE TABLE public.metodologia (id_metodo integer NOT NULL DEFAULT nextval('id_metodo_seq'::regclass), descripcion character varying(40), CONSTRAINT id_metodo_pkey PRIMARY KEY (id_metodo)) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_metodologia = "COMMENT ON TABLE public.metodologia IS 'Registro de proyectos del periodo academico por trayecto y seccion'"
		comm2_tb_metodologia = "COMMENT ON COLUMN public.metodologia.id_metodo IS 'Campo serial y clave principal de los registros de los proyectos'"
		comm3_tb_metodologia = "COMMENT ON COLUMN public.metodologia.descripcion IS 'Descripcion de la metodologia'"
		insertar_metodologia = "INSERT INTO public.metodologia (descripcion) VALUES ('Metodología Ágil RUP'), ('Metodología Ágil XP'), ('Metodología James Seen'), ('Metodología WATCH'), ('Metodología SCRUM'), ('Metodología D-Mobile')"

		cursor.execute(crear_tb_metodologia)
		cursor.execute(comm1_tb_metodologia)
		cursor.execute(comm2_tb_metodologia)
		cursor.execute(comm3_tb_metodologia)
		cursor.execute(insertar_metodologia)

		print('Paso Metodologia')
		crear_tb_tipo_de_desarrollo = "CREATE TABLE public.tipo_de_desarrollo (id_tipo_desarrollo integer NOT NULL DEFAULT nextval('id_tipo_desarrollo_seq'::regclass), tipo_desarrollo character varying(40), CONSTRAINT id_tipo_desarrollo_pkey PRIMARY KEY (id_tipo_desarrollo)) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_tipo_de_desarrollo = "COMMENT ON TABLE public.tipo_de_desarrollo IS 'Registro de tipos de desarrollo'"
		comm2_tb_tipo_de_desarrollo = "COMMENT ON COLUMN public.tipo_de_desarrollo.id_tipo_desarrollo IS 'Campo serial y clave principal del tipo de desarrollo'"
		comm3_tb_tipo_de_desarrollo = "COMMENT ON COLUMN public.tipo_de_desarrollo.tipo_desarrollo IS 'Descripcion de los tipos de desarrollo'"
		insertar_tipo_de_desarrollo = "INSERT INTO public.tipo_de_desarrollo (tipo_desarrollo) VALUES ('Sistema de Información'), ('Desarrollo WEB'), ('Implementación de Redes'), ('Aplicaciones Móviles')"

		cursor.execute(crear_tb_tipo_de_desarrollo)
		cursor.execute(comm1_tb_tipo_de_desarrollo)
		cursor.execute(comm2_tb_tipo_de_desarrollo)
		cursor.execute(comm3_tb_tipo_de_desarrollo)
		cursor.execute(insertar_tipo_de_desarrollo)

		crear_tb_trayecto	= "CREATE TABLE public.trayecto (id_trayecto integer NOT NULL DEFAULT nextval('id_trayecto_seq'::regclass), nivel ID_trayecto DEFAULT 'TRAYECTO I'::ID_trayecto, periodo_academico integer, CONSTRAINT id_trayecto_pkey PRIMARY KEY (id_trayecto))"
		comm1_tb_trayecto	= "COMMENT ON TABLE public.trayecto IS 'Registro de trayecto'"
		comm2_tb_trayecto	= "COMMENT ON COLUMN public.trayecto.id_trayecto IS 'Campo serial y clave primaria del trayecto'"
		comm3_tb_trayecto	= "COMMENT ON COLUMN public.trayecto.nivel IS 'Identificador de nivel academico del trayecto'"
		comm4_tb_trayecto	= "COMMENT ON COLUMN public.trayecto.periodo_academico IS 'Año del periodo academico'"
		insertar_trayecto	= "INSERT INTO public.trayecto (nivel, periodo_academico) VALUES ('TRAYECTO III', 2018)"
		cursor.execute(crear_tb_trayecto)
		cursor.execute(comm1_tb_trayecto)
		cursor.execute(comm2_tb_trayecto)
		cursor.execute(comm3_tb_trayecto)
		cursor.execute(comm4_tb_trayecto)
		cursor.execute(insertar_trayecto)
		print('Paso Trayectos')

		crear_tb_secciones	= "CREATE TABLE public.secciones (id_seccion integer NOT NULL DEFAULT nextval('id_seccion_seq'::regclass), siglas ID_seccion DEFAULT 'IF-01'::ID_seccion, tipo_seccion trayecto_tipo DEFAULT 'Regular'::trayecto_tipo, ano_seccion numeric(4,0), nro_estudiantes integer, FK_id_trayecto integer, CONSTRAINT id_seccion_pkey PRIMARY KEY (id_seccion), CONSTRAINT FK_id_trayecto FOREIGN KEY (FK_id_trayecto) REFERENCES public.trayecto (id_trayecto) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE)"
		comm1_tb_secciones	= "COMMENT ON TABLE public.secciones IS 'Registro de secciones'"
		comm2_tb_secciones	= "COMMENT ON COLUMN public.secciones.id_seccion IS 'Campo serial y clave primaria de la seccion'"
		comm3_tb_secciones	= "COMMENT ON COLUMN public.secciones.siglas IS 'Identificador de nombre de seccion'"
		comm4_tb_secciones	= "COMMENT ON COLUMN public.secciones.tipo_seccion IS 'registro de tipo de seccion Regular/Prosecucion'"
		comm5_tb_secciones	= "COMMENT ON COLUMN public.secciones.ano_seccion IS 'Periodo academico de la seccion inscrita'"
		comm6_tb_secciones	= "COMMENT ON COLUMN public.secciones.nro_estudiantes IS 'Total de estudiantes en la seccion'"
		cursor.execute(crear_tb_secciones)
		cursor.execute(comm1_tb_secciones)
		cursor.execute(comm2_tb_secciones)
		cursor.execute(comm3_tb_secciones)
		cursor.execute(comm4_tb_secciones)
		cursor.execute(comm5_tb_secciones)
		cursor.execute(comm6_tb_secciones)
		print('Paso Secciones')

		crear_tb_proyecto = "CREATE TABLE public.proyectos (id_proyecto integer NOT NULL DEFAULT nextval('id_proyecto_seq'::regclass), codigo_proyecto character varying(28), numero_grupo_proyecto numeric(2,0), titulo_proyecto character varying(100), nombre_informe_codificado character varying(40), nombre_desarrollo_codificado character varying(40), nombre_manual_codificado character varying(40), FK_id_seccion integer, FK_id_metodo integer, FK_id_tipo_desarrollo integer, CONSTRAINT id_proyecto_pkey PRIMARY KEY (id_proyecto), CONSTRAINT FK_id_seccion FOREIGN KEY (FK_id_seccion) REFERENCES public.secciones (id_seccion) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE, CONSTRAINT FK_id_metodo FOREIGN KEY (FK_id_metodo) REFERENCES public.metodologia (id_metodo) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE, CONSTRAINT FK_id_tipo_desarrollo FOREIGN KEY (FK_id_tipo_desarrollo) REFERENCES public.tipo_de_desarrollo (id_tipo_desarrollo) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_proyecto	= "COMMENT ON TABLE public.proyectos IS 'Registro de proyectos del periodo academico por trayecto y seccion'"
		comm2_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.id_proyecto IS 'Campo serial y clave principal de los registros de los proyectos'"
		comm3_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.codigo_proyecto IS 'Codigo compuesto para catalogar los proyectos archivados'"
		comm4_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.numero_grupo_proyecto IS 'Numero del Grupo de Desarrollo del Proyecto asignado por el tutor'"
		comm5_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.titulo_proyecto IS 'Año de registro de las secciones de Prosecucion'"
		comm6_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.nombre_informe_codificado IS 'Nombre asignado por el sistema para ubicar el producto entregado por el estudiante'"
		comm7_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.nombre_desarrollo_codificado IS 'Nombre asignado por el sistema para ubicar el producto entregado por el estudiante'"
		comm8_tb_proyecto	= "COMMENT ON COLUMN public.proyectos.nombre_manual_codificado IS 'Nombre asignado por el sistema para ubicar el producto entregado por el estudiante'"

		cursor.execute(crear_tb_proyecto)
		cursor.execute(comm1_tb_proyecto)
		cursor.execute(comm2_tb_proyecto)
		cursor.execute(comm3_tb_proyecto)
		cursor.execute(comm4_tb_proyecto)
		cursor.execute(comm5_tb_proyecto)
		cursor.execute(comm6_tb_proyecto)
		cursor.execute(comm7_tb_proyecto)
		cursor.execute(comm8_tb_proyecto)
		print('Paso Proyectos')

		crear_tb_accede = "CREATE TABLE public.accede (id_accede integer NOT NULL DEFAULT nextval('id_accede_seq'::regclass), FK_usuario character varying(15), FK_id_proyecto integer, actividad character varying(10), fecha date, CONSTRAINT id_registra_pkey PRIMARY KEY (id_accede), CONSTRAINT FK_usuario FOREIGN KEY (FK_usuario) REFERENCES public.usuarios (usuario) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT FK_id_proyecto FOREIGN KEY (FK_id_proyecto) REFERENCES public.proyectos (id_proyecto) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_accede = "COMMENT ON TABLE public.accede IS 'Registro de proyectos del periodo academico por trayecto y seccion'"
		comm2_tb_accede = "COMMENT ON COLUMN public.accede.id_accede IS 'Campo serial y clave principal de los registros de los proyectos'"
		comm3_tb_accede = "COMMENT ON COLUMN public.accede.FK_usuario IS 'Clave foranea para establecer vinculo con entidad usuarios'"
		comm4_tb_accede = "COMMENT ON COLUMN public.accede.FK_id_proyecto IS 'Clave foranea para establecer vinculo con entidad proyectos'"
		cursor.execute(crear_tb_accede)
		cursor.execute(comm1_tb_accede)
		cursor.execute(comm2_tb_accede)
		cursor.execute(comm3_tb_accede)
		cursor.execute(comm4_tb_accede)
		print('Paso Accede')

		crear_tb_estudiante	= "CREATE TABLE public.estudiante (cedula_estudiante numeric(8,0), nombre_estudiante character varying(30), apellido_estudiante character varying(30), genero_estudiante generos DEFAULT 'Masculino'::generos, telefono_estudiante character varying(16), estado Estado_Registro DEFAULT 'Activo'::Estado_Registro, CONSTRAINT cedula_estudiante_pkey PRIMARY KEY (cedula_estudiante))"
		comm1_tb_estudiante	= "COMMENT ON TABLE public.estudiante IS 'Registro de estudiantes'"
		comm2_tb_estudiante	= "COMMENT ON COLUMN public.estudiante.cedula_estudiante IS 'Cedula del estudiante 8 caracteres numéricos'"
		comm3_tb_estudiante	= "COMMENT ON COLUMN public.estudiante.nombre_estudiante IS 'Nombre del estudiante 30 caracteres'"
		comm4_tb_estudiante	= "COMMENT ON COLUMN public.estudiante.apellido_estudiante IS 'Apellido del estudiante 30 caracteres'"
		comm5_tb_estudiante	= "COMMENT ON COLUMN public.estudiante.genero_estudiante IS 'Genero del estudiante del tipo Enum Genero valores: Femenino y Masculino'"
		comm6_tb_estudiante	= "COMMENT ON COLUMN public.estudiante.telefono_estudiante IS 'Telefono de contacto del estudiante 16 caracteres'"
		comm7_tb_estudiante	= "COMMENT ON COLUMN public.estudiante.estado IS 'estado del registro Activo/Inactivo'"
		cursor.execute(crear_tb_estudiante)
		cursor.execute(comm1_tb_estudiante)
		cursor.execute(comm2_tb_estudiante)
		cursor.execute(comm3_tb_estudiante)
		cursor.execute(comm4_tb_estudiante)
		cursor.execute(comm5_tb_estudiante)
		cursor.execute(comm6_tb_estudiante)
		cursor.execute(comm7_tb_estudiante)
		print('Paso Estudiante')

		crear_tb_tutores	= "CREATE TABLE public.tutores (cedula_tutor numeric(8,0), nombre_tutor character varying(30), apellido_tutor character varying(30), genero_tutor generos DEFAULT 'Masculino'::generos, telefono_tutor character varying(16), cantidad_alumnos integer, estado Estado_Registro DEFAULT 'Activo'::Estado_Registro, CONSTRAINT cedula_tutor_pkey PRIMARY KEY (cedula_tutor))"
		comm1_tb_tutores	= "COMMENT ON TABLE public.tutores IS 'Registro de tutores'"
		comm2_tb_tutores	= "COMMENT ON COLUMN public.tutores.cedula_tutor IS 'Cedula del tutor 8 caracteres numéricos'"
		comm3_tb_tutores	= "COMMENT ON COLUMN public.tutores.nombre_tutor IS 'Nombre del tutor 30 caracteres'"
		comm4_tb_tutores	= "COMMENT ON COLUMN public.tutores.apellido_tutor IS 'Apellido del tutor 30 caracteres'"
		comm5_tb_tutores	= "COMMENT ON COLUMN public.tutores.genero_tutor IS 'Genero del tutor del tipo Enum Genero valores: Femenino y Masculino'"
		comm6_tb_tutores	= "COMMENT ON COLUMN public.tutores.telefono_tutor IS 'Telefono de contacto del tutor 16 caracteres'"
		comm7_tb_tutores	= "COMMENT ON COLUMN public.tutores.estado IS 'estado del registro Activo/Inactivo'"
		comm8_tb_tutores	= "COMMENT ON COLUMN public.tutores.cantidad_alumnos IS 'Total de alumnos atendidos por el tutor'"
		cursor.execute(crear_tb_tutores)
		cursor.execute(comm1_tb_tutores)
		cursor.execute(comm2_tb_tutores)
		cursor.execute(comm3_tb_tutores)
		cursor.execute(comm4_tb_tutores)
		cursor.execute(comm5_tb_tutores)
		cursor.execute(comm6_tb_tutores)
		cursor.execute(comm7_tb_tutores)
		cursor.execute(comm8_tb_tutores)
		print('Paso Tutores')

		crear_tb_elaboran	= "CREATE TABLE public.elaboran (FK_id_proyecto integer, FK_cedula_estudiante numeric(8,0), CONSTRAINT FK_cedula_estudiante FOREIGN KEY (FK_cedula_estudiante) REFERENCES public.estudiante (cedula_estudiante) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT FK_id_proyecto FOREIGN KEY (FK_id_proyecto) REFERENCES public.proyectos (id_proyecto) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_elaboran	= "COMMENT ON TABLE public.elaboran IS 'Relacion entre Estudiante y Proyecto'"
		comm2_tb_elaboran	= "COMMENT ON COLUMN public.elaboran.FK_cedula_estudiante IS 'Referencia a la clave de la entidad Estudiante'"
		comm3_tb_elaboran	= "COMMENT ON COLUMN public.elaboran.FK_id_proyecto IS 'Referencia a la clave de la entidad proyecto'"
		cursor.execute(crear_tb_elaboran)
		cursor.execute(comm1_tb_elaboran)
		cursor.execute(comm2_tb_elaboran)
		cursor.execute(comm3_tb_elaboran)
		print('Paso Elaboran')

		crear_tb_asesora	= "CREATE TABLE public.es_asesorado (FK_id_proyecto integer, FK_cedula_tutor numeric(8,0), rol Roles DEFAULT 'Academico'::Roles, CONSTRAINT FK_id_proyecto FOREIGN KEY (FK_id_proyecto) REFERENCES public.proyectos (id_proyecto) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT FK_cedula_tutor FOREIGN KEY (FK_cedula_tutor) REFERENCES public.tutores (cedula_tutor) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION) WITH (OIDS = FALSE) TABLESPACE pg_default"
		comm1_tb_asesora	= "COMMENT ON TABLE public.es_asesorado IS 'Relacion entre Estudiante y Seccion'"
		comm2_tb_asesora	= "COMMENT ON COLUMN public.es_asesorado.FK_cedula_tutor IS 'Referencia a la clave de la entidad Tutores'"
		comm3_tb_asesora	= "COMMENT ON COLUMN public.es_asesorado.FK_id_proyecto IS 'Referencia a la clave de la entidad Proyectos'"
		comm4_tb_asesora	= "COMMENT ON COLUMN public.es_asesorado.rol IS 'Funcion que cumple el tutor hacia el estudiante'"
		cursor.execute(crear_tb_asesora)
		cursor.execute(comm1_tb_asesora)
		cursor.execute(comm2_tb_asesora)
		cursor.execute(comm3_tb_asesora)
		cursor.execute(comm4_tb_asesora)
		print('Paso Asesora')
		cursor.close()

# Constructor para ejecutar el programa, este modulo se ejecuta independiente del sistema y generalmente
# se usa una sola vez a menos que el administrador cambie la clave del usuario de la base de datos
# en cuyo caso debera ejecutar el modulo para acrualizar los datos al sistema.
# En caso de corrida posterior al uso del sistema no debe ejecutar la rutina de creacion de tablas
		
app = QApplication(sys.argv)
PRegserver = DialogoAcceso()
PRegserver.show()
app.exec_()
