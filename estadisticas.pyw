#---------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                        #
# Programador: Luis Amaya                                                         #
# Analistas: Jose Astudillo / josmary Botaban                                     #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre  #
# Octubre (2018)                                                                  #
# Version 1.0                                                                     #
# Modulo: Estadisticas del Sistema                                                #
# Descripción: Genera Estadisticas de los Proyectos Registrados en el Sistema     #
#---------------------------------------------------------------------------------#

# Importacion de librerias del sistema
import sys, os, shutil, functools, re
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
import ctypes #GetSystemMetrics
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib, select
import easygui as eg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
import webbrowser as wb
from datetime import datetime, date, time, timedelta
import calendar
import os.path as path

class DialogoEstadistica(QDialog):
	#Método constructor de la clase
	def __init__(self):
		#Iniciar el objeto DialogoAcceso
		QDialog.__init__(self)
		uic.loadUi("estadisticas.ui", self)
		#Habilitar Cuadro de Dialogo
		self.setEnabled(True)
		self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)

		#Operacion para centrar la ventana en la pantalla
		resolucion = ctypes.windll.user32
		resolucion_ancho = resolucion.GetSystemMetrics(0)
		resolucion_alto = resolucion.GetSystemMetrics(1)
		left = (resolucion_ancho / 2) - (self.frameSize().width() / 2)
		top = (resolucion_alto / 2) - (self.frameSize().height() / 2) - 40
		self.move(left, top)
		self.archivo_infosvr = ''
		self.infosvr = []
		self.lista = []
		self.BD_Name = ''
		self.BD_User = ''
		self.BD_Pass = ''
		self.archivo_infosvr = open('regsvr.txt','r')
		self.infosvr = self.archivo_infosvr.readlines()
		self.BD_Name = self.infosvr[0]
		self.BD_Name = self.BD_Name.replace('\n', '').replace('\r', '') 
		self.BD_User = self.infosvr[1]
		self.BD_User = self.BD_User.replace('\n', '').replace('\r', '') 
		self.BD_Pass = self.infosvr[2]
		self.BD_Pass = self.BD_Pass.replace('\n', '').replace('\r', '') 
		self.archivo_infosvr.close

		#Establecer conexion a la Base de Datos
		cad_con = "dbname='%s' user='%s' password='%s' host='localhost'" % (self.BD_Name, self.BD_User, self.BD_Pass)
		try:
			self.db = psycopg2.connect(cad_con)
		except:
			QMessageBox.warning(self, "Error de Base de Datos", "Ocurrio un error al intentar comunicarse con la Base de Datos", QMessageBox.Ok)
			self.quit()
		else:
			self.db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
			self.cursor = self.db.cursor()

		# Definicion de Variables
		self.hoy = datetime.today()
		self.formato_fecha1 = "%d días del mes de %B del año %Y"
		self.formato_fecha2 = "%d-%m-%Y"
		self.formato_fecha3 = "%m"
		self.formato_fecha4 = "%Y"
		self.formato_fecha5 = "%Y-%m-%d-%H%M%S"
		self.fechaarchivo = self.hoy.strftime(self.formato_fecha5)
		self.ano = self.hoy.strftime(self.formato_fecha4)
		self.mes = self.meses(self.hoy.strftime(self.formato_fecha3))
		self.formato_fecha1 = "%d días del mes de " + self.mes + " del año %Y"
		self.fecha1 = self.hoy.strftime(self.formato_fecha2)
		self.fecha2 = self.hoy.strftime(self.formato_fecha1)
		self.archivo = './Estadisticas/Estadistica '+self.fechaarchivo + '.pdf'
		self.archivo2 = (r'.\Estadisticas\Estadistica '+self.fechaarchivo + '.pdf')
		#Creando Documento PDF
		self.c = ""

		self.origen = ""
		self.destino = ""
		self.bdvacia = 0
		self.detallado = 0
		self.contlinea = 0
		self.IdProyecto = 0
		self.IdPeriodo = 0
		self.cedula = 0
		self.fechaini = 0
		self.fechafin = 0
		self.totalSecciones = 0
		self.imprimir_encabezado = 0
		self.cedula_tutor=""
		self.nombre_tutor=""
		self.cedula_anterior=""
		self.TotalRegistros = 0
		self.TotalTutores = 0
		self.TotalEstudiantes = 0
		self.TotalProyectos = 0
		self.TotalSInformacion = 0
		self.TotalDWeb = 0
		self.TotalRedes = 0
		self.TotalApps = 0
		self.TotalTutorEstudiantes = 0
		self.TotalTutorProyectos = 0
		self.TotalTutorSInformacion = 0
		self.TotalTutorDWeb = 0
		self.TotalTutorRedes = 0
		self.TotalTutorApps = 0
		self.TotalGeneralProyectos = 0
		self.TotalGeneralSInformacion = 0
		self.TotalGeneralDWeb = 0
		self.TotalGeneralRedes = 0
		self.TotalGeneralApps = 0
		self.RegistroActual = 0
		self.ano_periodo = ""
		self.trayecto = ""
		self.seccion = ""
		self.tipo_trayecto = ""
		self.ano_prosecucion = ""
		self.linea = 0
		self.hoy = datetime.today()
		self.formato_fecha = "%d-%m-%Y"
		self.formato_fecha2 = "%Y"
		self.AnoActual = self.hoy.strftime(self.formato_fecha2)
		self.FechaActual = self.hoy.strftime(self.formato_fecha)
		# Configuracion Tabla Grupos de Proyecto
		self.tablaEstadisticas.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tablaEstadisticas.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tablaEstadisticas.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tablaEstadisticas.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tablaEstadisticas.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tablaEstadisticas.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tablaEstadisticas.setWordWrap(True) # Establecer el ajuste de palabras del texto 
		self.tablaEstadisticas.setSortingEnabled(True) # Habilitar clasificación
		self.tablaEstadisticas.setColumnCount(13) # Establecer el número de columnas
		self.tablaEstadisticas.setRowCount(0) # Establecer el número de filas
		self.tablaEstadisticas.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tablaEstadisticas.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tablaEstadisticas.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tablaEstadisticas.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tablaEstadisticas.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas
		nombreColumnasProyecto = ("Cedula Tutor", "Nombre", "Periodo", "Trayecto", "Seccion", "Tipo de Trayecto", "Año Prosecucion", "Total Proyectos", "Total Estudiantes", "Total S. Informacion", "Total D. WEB", "Total Redes", "Total APP Móviles")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaEstadisticas.setHorizontalHeaderLabels(nombreColumnasProyecto)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((80, 150, 60, 60, 60, 100, 100, 100, 120, 120, 120, 120, 120 ), start=0):
			self.tablaEstadisticas.setColumnWidth(indice, ancho)

		# Ocultar campos iniciales
		self.txtCedula.setEnabled(False)
		self.txtCedula.setText("0")
		self.txtTutor.setText("")
		self.txtTutor.hide()
		self.lblTutor.hide()
		self.txtCedulaSeleccionada.hide()
		self.chkTutor.setChecked(False)
		self.chkPeriodo.setChecked(False)
		self.grpFechas.setEnabled(False)
		self.cmbFechaini.setEnabled(False)
		self.cmbFechafin.setEnabled(False)
		self.cmbFechaini.setCurrentIndex(int(self.AnoActual)-2013)
		self.cmbFechafin.setCurrentIndex(int(self.AnoActual)-2013)
		self.btnReset.setEnabled(False)
		self.btnBuscarTutor.setEnabled(False)

		# Ocultar Lista de Tutores
		self.grpTutores.hide()
		#------------------------------------------------#
		# Botones y Disparadores Eventos Tab Principal   #
		#
		
		# Vincular eventos de click de los botones a las funciones correspondientes
		self.btnGeneraEstadistica.clicked.connect(self.LlenarEstadistica)
		self.btnReset.clicked.connect(self.resetEstadistica)
		self.btnBuscarTutor.clicked.connect(self.AsignaTutor)
		self.btnSelTutor.clicked.connect(self.ElejirTutor)
		self.btnRetorno.clicked.connect(self.RetornoTutor)
		self.btnCerrar.clicked.connect(self.cerrar)
		self.chkTutor.clicked.connect(self.chequeoTutor)
		self.chkPeriodo.clicked.connect(self.chequeoPeriodo)
		self.optAnual.clicked.connect(self.chequeoGrpFechas)
		self.optRango.clicked.connect(self.chequeoGrpFechas)
		self.optDetallado.clicked.connect(self.chequeoTipoEstadistica)
		self.optConsolidado.clicked.connect(self.chequeoTipoEstadistica)
		self.btnImprime.clicked.connect(self.emitirEstadistica)
		self.ListaTutores.itemDoubleClicked.connect(self.ElejirTutor)
		self.ListaTutores.itemClicked.connect(self.actCedulaBuscar)
		self.optCedula.clicked.connect(self.ordenarTabla)
		self.optNombre.clicked.connect(self.ordenarTabla)
		self.optApellido.clicked.connect(self.ordenarTabla)
		self.txtFiltro.textChanged.connect(self.buscarDato)

	# Rutina para ordenar la lista de tutores
	def ordenarTabla(self):
		if self.optCedula.isChecked():
			self.ListaTutores.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		elif self.optNombre.isChecked():
			self.ListaTutores.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)
		else:
			self.ListaTutores.horizontalHeader().setSortIndicator(2, Qt.AscendingOrder)

	# Rutina para actualizar el campo de busqueda con la cedula del tutor al hacer click en 
	# un registro de la tabla
	def actCedulaBuscar(self):
		fila = self.ListaTutores.currentRow()
		totalregistros = self.ListaTutores.rowCount()
		cedula = self.ListaTutores.item(fila, 0).text().replace(" ", "")
		self.txtCedulaSeleccionada.setText(cedula)

	# Rutina para fijar el cursor de la tabla al ir introduciendo datos en el campo de busqueda de
	# acuerdo al ordenamiento de la tabla
	def buscarDato(self):
		lv_texto = self.txtFiltro.text().upper()
		if self.optCedula.isChecked()== True:
			validar = re.match('^[0-9\s]+$', lv_texto, re.I)
			columna = 0
		elif self.optNombre.isChecked()==True:	
			validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
			columna = 1
		else:
			validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
			columna = 2
		index = self.ListaTutores.rowCount()
		fila=0
		encontrar = 0
		while fila < index:
			lv_busqueda = self.ListaTutores.item(fila,columna).text()
			if lv_texto in lv_busqueda:
				encontrar = 1
				break;
			fila = fila + 1
		if encontrar == 1:
			posicion = self.ListaTutores.item(fila, columna)
			self.ListaTutores.scrollToItem(posicion)
			self.ListaTutores.setCurrentCell(fila, columna)
			self.txtCedulaSeleccionada.setText(self.ListaTutores.item(fila, 0).text().replace(" ", ""))
			return True
		else:
			return False


	# Rutina para activar los botones de seleccion de busqueda
	def activa_botones(self):
		self.grpTipo.setEnabled(True)
		self.btnReset.setEnabled(False)
		self.btnBuscarTutor.setEnabled(True)
		self.btnGeneraEstadistica.setEnabled(True)
		self.chkTutor.setEnabled(True)
		self.chkPeriodo.setEnabled(True)
		self.chkTutor.setChecked(False)
		self.chkPeriodo.setChecked(False)

	# Rutina para desactivar los botones de seleccion de busqueda
	def desactiva_botones(self):
		self.grpTipo.setEnabled(False)
		self.btnReset.setEnabled(True)
		self.btnBuscarTutor.setEnabled(False)
		self.btnGeneraEstadistica.setEnabled(False)
		self.chkTutor.setEnabled(False)
		self.chkPeriodo.setEnabled(False)
		self.txtCedula.setEnabled(False)
		self.grpFechas.setEnabled(False)
		self.cmbFechaini.setEnabled(False)
		self.cmbFechafin.setEnabled(False)
		

	# Rutina para vaciar la tabla para nueva busqueda
	def resetEstadistica(self):
		if self.TotalRegistros > 0:
			self.tablaEstadisticas.clearSelection()
			self.tablaEstadisticas.clearContents()
			index2 = self.TotalRegistros
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.tablaEstadisticas.removeRow(index3)
				index2 = index2 - 1
		self.optAnual.setChecked(True)
		self.chequeoGrpFechas()
		self.activa_botones()
		self.txtCedula.setText("")
		self.chkPeriodo.setChecked(False)
		self.chequeoTutor()

	# Rutina para activar o desactivar campos de acuerdo al tipo de estadistica
	def chequeoTipoEstadistica(self):
		if self.optDetallado.isChecked():
			self.tablaEstadisticas.setColumnHidden(3, False)
			self.tablaEstadisticas.setColumnHidden(4, False)
			self.tablaEstadisticas.setColumnHidden(5, False)
			self.tablaEstadisticas.setColumnHidden(6, False)	
		else:
			self.tablaEstadisticas.setColumnHidden(3, True)
			self.tablaEstadisticas.setColumnHidden(4, True)
			self.tablaEstadisticas.setColumnHidden(5, True)
			self.tablaEstadisticas.setColumnHidden(6, True)

	# Rutina para activar o desactivar campos de tutor acuerdo seleccion de tutor unico o general
	def chequeoTutor(self):
		if self.chkTutor.isChecked():
			self.txtCedula.setText("0")
			self.txtCedula.setEnabled(True)
			self.lblTutor.show()
			self.txtTutor.show()
			self.txtTutor.setText("")
			self.tablaEstadisticas.setColumnHidden(0, True)
			self.tablaEstadisticas.setColumnHidden(1, True)
			self.btnBuscarTutor.setEnabled(True)
		else:
			self.txtCedula.setText("0")
			self.txtCedula.setEnabled(False)
			self.lblTutor.hide()
			self.txtTutor.hide()
			self.txtTutor.setText("")
			self.tablaEstadisticas.setColumnHidden(0, False)
			self.tablaEstadisticas.setColumnHidden(1, False)
			self.btnBuscarTutor.setEnabled(False)

	# Rutina para hailitar o deshabilitar busqueda por periodo 
	def chequeoPeriodo(self):
		if self.chkPeriodo.isChecked():
			self.grpFechas.setEnabled(True)
			self.optAnual.setChecked(True)
			self.cmbFechaini.setEnabled(True)
			self.cmbFechafin.setEnabled(False)
			self.cmbFechaini.setCurrentIndex(int(self.AnoActual)-2013)
			self.cmbFechafin.setCurrentIndex(int(self.AnoActual)-2013)
		else:
			self.grpFechas.setEnabled(False)
			self.optAnual.setChecked(True)
			self.cmbFechaini.setEnabled(False)
			self.cmbFechafin.setEnabled(False)
			self.cmbFechaini.setCurrentIndex(int(self.AnoActual)-2013)
			self.cmbFechafin.setCurrentIndex(int(self.AnoActual)-2013)

	# Rutina para habilitar busqueda por fecha simple o rango de fechas
	def chequeoGrpFechas(self):
		if self.optAnual.isChecked():
			self.cmbFechafin.setEnabled(False)
			self.cmbFechaini.setCurrentIndex(int(self.AnoActual)-2013)
			self.cmbFechafin.setCurrentIndex(int(self.AnoActual)-2013)
		else:
			self.cmbFechafin.setEnabled(True)
			self.cmbFechaini.setCurrentIndex(0)
			self.cmbFechafin.setCurrentIndex(int(self.AnoActual)-2013)

	# Rutina para cargar la tabla de tutores 
	def cargaTutores(self):
		index2 = self.ListaTutores.rowCount()
		if index2 > 0:
			self.ListaTutores.clearSelection()
			self.ListaTutores.clearContents()
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.ListaTutores.removeRow(index3)
				index2 = index2 - 1
		cursor_lista_tutores = "SELECT cedula_tutor, nombre_tutor, apellido_tutor FROM tutores WHERE estado = 'Activo' order by cedula_tutor"
		self.cursor.execute(cursor_lista_tutores)
		index = 0
		for rows in self.cursor:
			self.ListaTutores.insertRow(index)
			lvcedula = str(rows[0])
			lvnombre = str(rows[1])
			lvapellido = str(rows[2])
			self.ListaTutores.setItem(index, 0, QTableWidgetItem((' '+lvcedula)[-8:]))
			self.ListaTutores.setItem(index, 1, QTableWidgetItem(lvnombre))
			self.ListaTutores.setItem(index, 2, QTableWidgetItem(lvapellido))
			index = index + 1

	# Rutina para extraer los datos de un tutor de la base de datos
	def consulta_tutor(self,lvcedula):
		if lvcedula == '0' or lvcedula == '':
			self.txtTutor=''
		else:
			bdbuscar_tutor = "SELECT cedula_tutor, nombre_tutor, apellido_tutor, estado from tutores where cedula_tutor = %i" % int(lvcedula)
			self.cursor.execute(bdbuscar_tutor)
			rows=self.cursor.fetchone()
			if rows == None:
				self.encontrar = 0
				self.txtTutor.setText('')
			else:
				if str(rows[3]) == 'Inactivo':
					continuar = 0
					vtutor = (str(rows[1]) + ' ' + str(rows[2]))
					respuesta = QMessageBox.warning(self,"Precaucion...", "El Tutor " + vtutor + " seleccionado esta inactivo\n Desea continuar?", QMessageBox.Yes | QMessageBox.No) 
					if respuesta == QMessageBox.Yes:
						continuar = 1
					else: 
						self.txtTutor.setText("")
						self.txtCedula.setText("0")
				else:
					continuar = 1
				if continuar == 1:
					self.txtTutor.setText(str(rows[1]) + ' ' + str(rows[2]))
					self.encontrar = 1
			if self.encontrar == 0:
				respuesta = QMessageBox.warning(self,"Error...", "Cedula del Tutor no esta registrado, dirijase al modulo de registro de tutores y añada nuevo tutor o seleccione uno de la lista\n Desea acceder a la lista?", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.Yes:
					self.txtCedula.setText("0")
					self.AsignaTutor()
				else:
					self.txtCedula.setText("0")
					self.txtTutor.setText('')

	# Rutina para asignar tutor a la busqueda de estadisticas
	def AsignaTutor(self):
		#self.cargaTutores()
		if self.txtCedula.text()=='' or self.txtCedula.text()=='0':
			self.txtCedula.setText("0")
			self.cargaTutores()
			self.grpTutores.show()
		else:
			lv_cedula_tutor = int(self.txtCedula.text())
			self.consulta_tutor(str(lv_cedula_tutor))

	# Rutina para elejir un tutor de la lista de busqueda
	def ElejirTutor(self):
		if self.ListaTutores.currentRow() == -1:
			QMessageBox.information(self,"Base de Datos", "Debe seleccionar un tutor de la lista", QMessageBox.Ok)
		else:
			row = self.ListaTutores.currentRow()
			self.txtCedula.setText(self.txtCedulaSeleccionada.text())
			self.txtTutor.setText(self.ListaTutores.item(row, 1).text() + " " + self.ListaTutores.item(row, 2).text())
		self.grpTutores.hide()

	# Rutina para retornar sin elejir tutor de la lista de busqueda
	def RetornoTutor(self):
		respuesta = QMessageBox.warning(self,"Base de Datos", "Esta seguro de no elejir ningun tutor?", QMessageBox.Yes | QMessageBox.No)
		if respuesta == QMessageBox.Yes:
			self.txtCedula.setText("0")
			self.txtTutor.setText("")
		self.grpTutores.hide()

	# Rutina para cargar los datos en la tabla de estadistica de acuerdo a la seleccion del usuario
	def LlenarEstadistica(self):
		self.desactiva_botones()
		self.tablaEstadisticas.setRowCount(0)
		self.cedula = int(self.txtCedula.text())
		self.fechaini = int(self.cmbFechaini.currentText())
		self.fechafin = int(self.cmbFechafin.currentText())
		if self.chkTutor.isChecked():
			if self.chkPeriodo.isChecked():
				if self.optAnual.isChecked():
					cursor_consulta = """SELECT tray.periodo_academico, tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, tray.nivel as trayecto, sec.siglas as seccion, sec.tipo_seccion, 
									sec.ano_seccion, proy.codigo_proyecto, proy.numero_grupo_proyecto, proy.titulo_proyecto, 
									met.descripcion as metodo, tdes.tipo_desarrollo, est.cedula_estudiante,  
									tray.id_trayecto,  sec.id_seccion, met.id_metodo, tdes.id_tipo_desarrollo 
									FROM proyectos as proy INNER JOIN secciones as sec ON proy.FK_id_seccion = sec.id_seccion
									INNER JOIN trayecto as tray ON sec.FK_id_trayecto = tray.id_trayecto
									INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
									INNER JOIN tipo_de_desarrollo AS tdes ON proy.FK_id_tipo_desarrollo = tdes.id_tipo_desarrollo
									INNER JOIN es_asesorado as esa ON proy.id_proyecto = esa.FK_id_proyecto and esa.rol = 'Tecnico Metodologico'
									INNER JOIN tutores as tut ON tut.cedula_tutor = esa.FK_cedula_tutor
									INNER JOIN elaboran as ela ON ela.FK_id_proyecto = proy.id_proyecto
									INNER JOIN estudiante as est ON est.cedula_estudiante = ela.FK_cedula_estudiante
									WHERE tut.cedula_tutor='%i' AND sec.ano_seccion = '%i' 
									ORDER BY tut.cedula_tutor, sec.ano_seccion, tray.nivel, sec.siglas, 
									met.descripcion, tdes.tipo_desarrollo;""" % (self.cedula, self.fechaini)
				else:
					cursor_consulta = """SELECT tray.periodo_academico, tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, tray.nivel as trayecto, sec.siglas as seccion, sec.tipo_seccion, 
									sec.ano_seccion, proy.codigo_proyecto, proy.numero_grupo_proyecto, proy.titulo_proyecto, 
									met.descripcion as metodo, tdes.tipo_desarrollo, est.cedula_estudiante,  
									tray.id_trayecto,  sec.id_seccion, met.id_metodo, tdes.id_tipo_desarrollo 
									FROM proyectos as proy INNER JOIN secciones as sec ON proy.FK_id_seccion = sec.id_seccion
									INNER JOIN trayecto as tray ON sec.FK_id_trayecto = tray.id_trayecto
									INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
									INNER JOIN tipo_de_desarrollo AS tdes ON proy.FK_id_tipo_desarrollo = tdes.id_tipo_desarrollo
									INNER JOIN es_asesorado as esa ON proy.id_proyecto = esa.FK_id_proyecto and esa.rol = 'Tecnico Metodologico'
									INNER JOIN tutores as tut ON tut.cedula_tutor = esa.FK_cedula_tutor
									INNER JOIN elaboran as ela ON ela.FK_id_proyecto = proy.id_proyecto
									INNER JOIN estudiante as est ON est.cedula_estudiante = ela.FK_cedula_estudiante
									WHERE tut.cedula_tutor='%i' AND tray.periodo_academico >= %i AND tray.periodo_academico <= %i  
									ORDER BY tut.cedula_tutor, sec.ano_seccion, tray.nivel, sec.siglas, 
									met.descripcion, tdes.tipo_desarrollo;""" % (self.cedula, self.fechaini, self.fechafin)
			else:
				cursor_consulta = """SELECT tray.periodo_academico, tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, tray.nivel as trayecto, sec.siglas as seccion, sec.tipo_seccion, 
									sec.ano_seccion, proy.codigo_proyecto, proy.numero_grupo_proyecto, proy.titulo_proyecto, 
									met.descripcion as metodo, tdes.tipo_desarrollo, est.cedula_estudiante,  
									tray.id_trayecto,  sec.id_seccion, met.id_metodo, tdes.id_tipo_desarrollo 
									FROM proyectos as proy INNER JOIN secciones as sec ON proy.FK_id_seccion = sec.id_seccion
									INNER JOIN trayecto as tray ON sec.FK_id_trayecto = tray.id_trayecto
									INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
									INNER JOIN tipo_de_desarrollo AS tdes ON proy.FK_id_tipo_desarrollo = tdes.id_tipo_desarrollo
									INNER JOIN es_asesorado as esa ON proy.id_proyecto = esa.FK_id_proyecto and esa.rol = 'Tecnico Metodologico'
									INNER JOIN tutores as tut ON tut.cedula_tutor = esa.FK_cedula_tutor
									INNER JOIN elaboran as ela ON ela.FK_id_proyecto = proy.id_proyecto
									INNER JOIN estudiante as est ON est.cedula_estudiante = ela.FK_cedula_estudiante
									WHERE tut.cedula_tutor='%i'
									ORDER BY tut.cedula_tutor, sec.ano_seccion, tray.nivel, sec.siglas, 
									met.descripcion, tdes.tipo_desarrollo;""" % (self.cedula)
		else:
			if self.chkPeriodo.isChecked():
				if self.optAnual.isChecked():
					cursor_consulta = """SELECT tray.periodo_academico, tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, tray.nivel as trayecto, sec.siglas as seccion, sec.tipo_seccion, 
									sec.ano_seccion, proy.codigo_proyecto, proy.numero_grupo_proyecto, proy.titulo_proyecto, 
									met.descripcion as metodo, tdes.tipo_desarrollo, est.cedula_estudiante,  
									tray.id_trayecto,  sec.id_seccion, met.id_metodo, tdes.id_tipo_desarrollo 
									FROM proyectos as proy INNER JOIN secciones as sec ON proy.FK_id_seccion = sec.id_seccion
									INNER JOIN trayecto as tray ON sec.FK_id_trayecto = tray.id_trayecto
									INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
									INNER JOIN tipo_de_desarrollo AS tdes ON proy.FK_id_tipo_desarrollo = tdes.id_tipo_desarrollo
									INNER JOIN es_asesorado as esa ON proy.id_proyecto = esa.FK_id_proyecto and esa.rol = 'Tecnico Metodologico'
									INNER JOIN tutores as tut ON tut.cedula_tutor = esa.FK_cedula_tutor
									INNER JOIN elaboran as ela ON ela.FK_id_proyecto = proy.id_proyecto
									INNER JOIN estudiante as est ON est.cedula_estudiante = ela.FK_cedula_estudiante
									WHERE tray.periodo_academico ='%i'
									ORDER BY tut.cedula_tutor, sec.ano_seccion, tray.nivel, sec.siglas, 
									met.descripcion, tdes.tipo_desarrollo;""" % (self.fechaini)
				else:
					cursor_consulta = """SELECT tray.periodo_academico, tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, tray.nivel as trayecto, sec.siglas as seccion, sec.tipo_seccion, 
									sec.ano_seccion, proy.codigo_proyecto, proy.numero_grupo_proyecto, proy.titulo_proyecto, 
									met.descripcion as metodo, tdes.tipo_desarrollo, est.cedula_estudiante,  
									tray.id_trayecto,  sec.id_seccion, met.id_metodo, tdes.id_tipo_desarrollo 
									FROM proyectos as proy INNER JOIN secciones as sec ON proy.FK_id_seccion = sec.id_seccion
									INNER JOIN trayecto as tray ON sec.FK_id_trayecto = tray.id_trayecto
									INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
									INNER JOIN tipo_de_desarrollo AS tdes ON proy.FK_id_tipo_desarrollo = tdes.id_tipo_desarrollo
									INNER JOIN es_asesorado as esa ON proy.id_proyecto = esa.FK_id_proyecto and esa.rol = 'Tecnico Metodologico'
									INNER JOIN tutores as tut ON tut.cedula_tutor = esa.FK_cedula_tutor
									INNER JOIN elaboran as ela ON ela.FK_id_proyecto = proy.id_proyecto
									INNER JOIN estudiante as est ON est.cedula_estudiante = ela.FK_cedula_estudiante
									WHERE tray.periodo_academico >= %i AND tray.periodo_academico <= %i  
									ORDER BY tut.cedula_tutor, sec.ano_seccion, tray.nivel, sec.siglas, 
									met.descripcion, tdes.tipo_desarrollo;""" % (self.fechaini, self.fechafin)
			else:
				cursor_consulta = """SELECT tray.periodo_academico, tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, tray.nivel as trayecto, sec.siglas as seccion, sec.tipo_seccion, 
									sec.ano_seccion, proy.codigo_proyecto, proy.numero_grupo_proyecto, proy.titulo_proyecto, 
									met.descripcion as metodo, tdes.tipo_desarrollo, est.cedula_estudiante,  
									tray.id_trayecto,  sec.id_seccion, met.id_metodo, tdes.id_tipo_desarrollo 
									FROM proyectos as proy INNER JOIN secciones as sec ON proy.FK_id_seccion = sec.id_seccion
									INNER JOIN trayecto as tray ON sec.FK_id_trayecto = tray.id_trayecto
									INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
									INNER JOIN tipo_de_desarrollo AS tdes ON proy.FK_id_tipo_desarrollo = tdes.id_tipo_desarrollo
									INNER JOIN es_asesorado as esa ON proy.id_proyecto = esa.FK_id_proyecto and esa.rol = 'Tecnico Metodologico'
									INNER JOIN tutores as tut ON tut.cedula_tutor = esa.FK_cedula_tutor
									INNER JOIN elaboran as ela ON ela.FK_id_proyecto = proy.id_proyecto
									INNER JOIN estudiante as est ON est.cedula_estudiante = ela.FK_cedula_estudiante
									ORDER BY tut.cedula_tutor, sec.ano_seccion, tray.nivel, sec.siglas, 
									met.descripcion, tdes.tipo_desarrollo;"""
		self.cursor.execute(cursor_consulta)
		rows = []
		index = -1
		self.IdProyecto = 0
		self.TotalRegistros = 0
		self.TotalTutores = 0
		self.TotalEstudiantes = 0
		self.TotalProyectosTutor = 0
		self.TotalSInformacion = 0
		self.TotalDWeb = 0
		self.TotalRedes = 0
		self.TotalApps = 0
		self.TotalGeneralProyectos = 0
		self.TotalGeneralEstudiantes = 0
		self.TotalGeneralSInformacion = 0
		self.TotalGeneralDWeb = 0
		self.TotalGeneralRedes = 0
		self.TotalGeneralApps = 0
		lv_cedula = ""
		lv_cedula_anterior = ""
		lv_ano = ""
		lv_ano_anterior = ""
		lv_trayecto = ""
		lv_trayecto_anterior = ""
		lv_seccion = ""
		lv_seccion_anterior = ""
		lv_tipo_trayecto = ""
		lv_tipo_trayecto_anterior = ""
		lv_ano_prosecucion = ""
		lv_ano_prosecucion_anterior = ""
		lv_codigo_proyecto = ""
		lv_codigo_proyecto_anterior = ""
		agregar = 0
		for rows in self.cursor:
			if rows==[]:
				self.bdvacia = 1
			else:
				lv_cedula = str(rows[1])
				lv_nombre = str(rows[2]) + " " + str(rows[3])
				lv_ano = str(rows[0])
				lv_trayecto = str(rows[4])
				lv_seccion = str(rows[5])
				lv_tipo_trayecto = str(rows[6])
				lv_ano_prosecucion = str(rows[7])
				lv_codigo_proyecto = str(rows[8])
				self.TotalGeneralEstudiantes = self.TotalGeneralEstudiantes + 1
				if self.optDetallado.isChecked():
					if lv_cedula != lv_cedula_anterior or lv_ano != lv_ano_anterior or lv_trayecto != lv_trayecto_anterior or lv_seccion != lv_seccion_anterior or lv_tipo_trayecto != lv_tipo_trayecto_anterior or  lv_ano_prosecucion != lv_ano_prosecucion_anterior:
						self.TotalProyectosTutor = 1
						self.TotalGeneralProyectos = self.TotalGeneralProyectos + 1
						self.TotalEstudiantes = 1
						lv_cedula_anterior = lv_cedula 
						lv_ano_anterior = lv_ano 
						lv_trayecto_anterior = lv_trayecto
						lv_seccion_anterior = lv_seccion
						lv_tipo_trayecto_anterior = lv_tipo_trayecto
						lv_ano_prosecucion_anterior = lv_ano_prosecucion 
						agregar = 1
					else:
						self.TotalEstudiantes = self.TotalEstudiantes + 1
						agregar = 0
						if lv_codigo_proyecto != lv_codigo_proyecto_anterior:
							self.TotalProyectosTutor = self.TotalProyectosTutor + 1
				else:
					if lv_cedula != lv_cedula_anterior or lv_ano != lv_ano_anterior:
						self.TotalProyectosTutor = 1
						self.TotalEstudiantes = 1
						agregar = 1
						lv_cedula_anterior = lv_cedula
						lv_ano_anterior = lv_ano
					else:
						self.TotalEstudiantes = self.TotalEstudiantes + 1
						agregar = 0
						if lv_codigo_proyecto != lv_codigo_proyecto_anterior:
							self.TotalProyectosTutor = self.TotalProyectosTutor + 1
				if str(rows[12]) == "Sistema de Información":
					lv_SInformacion = 1
					lv_DWeb = 0
					lv_Redes = 0
					lv_Apps = 0
				elif str(rows[12]) == "Desarrollo WEB":
					lv_SInformacion = 0
					lv_DWeb = 1
					lv_Redes = 0
					lv_Apps = 0
				elif str(rows[12]) == "Implementación de Redes":
					lv_SInformacion = 0
					lv_DWeb = 0
					lv_Redes = 1
					lv_Apps = 0
				else:
					lv_SInformacion = 0
					lv_DWeb = 0
					lv_Redes = 0
					lv_Apps = 1

				if lv_codigo_proyecto != lv_codigo_proyecto_anterior:
					self.TotalGeneralProyectos = self.TotalGeneralProyectos + 1
					lv_codigo_proyecto_anterior = lv_codigo_proyecto
					if str(rows[12]) == "Sistema de Información":
						self.TotalGeneralSInformacion = self.TotalGeneralSInformacion + 1
					elif str(rows[12]) == "Desarrollo WEB":
						self.TotalGeneralDWeb = self.TotalGeneralDWeb + 1
					elif str(rows[12]) == "Implementación de Redes":
						self.TotalGeneralRedes = self.TotalGeneralRedes + 1
					else:
						self.TotalGeneralApps = self.TotalGeneralApps + 1
				else:
					lv_SInformacion = 0
					lv_DWeb = 0
					lv_Redes = 0
					lv_Apps = 0

				if agregar == 1:
					index = index + 1
					self.TotalRegistros = self.TotalRegistros  + 1
					self.tablaEstadisticas.insertRow(index)
					self.tablaEstadisticas.setItem(index, 0, QTableWidgetItem(lv_cedula))
					self.tablaEstadisticas.setItem(index, 1, QTableWidgetItem(lv_nombre))
					self.tablaEstadisticas.setItem(index, 2, QTableWidgetItem(lv_ano))
					self.tablaEstadisticas.setItem(index, 3, QTableWidgetItem(lv_trayecto))
					self.tablaEstadisticas.setItem(index, 4, QTableWidgetItem(lv_seccion))
					self.tablaEstadisticas.setItem(index, 5, QTableWidgetItem(lv_tipo_trayecto))
					self.tablaEstadisticas.setItem(index, 6, QTableWidgetItem(lv_ano_prosecucion))
					self.TotalSInformacion = lv_SInformacion
					self.TotalDWeb = lv_DWeb
					self.TotalRedes = lv_Redes
					self.TotalApps = lv_Apps
				else:
					self.TotalSInformacion = self.TotalSInformacion + lv_SInformacion
					self.TotalDWeb = self.TotalDWeb + lv_DWeb
					self.TotalRedes = self.TotalRedes + lv_Redes
					self.TotalApps = self.TotalApps + lv_Apps

				self.tablaEstadisticas.setItem(index, 7, QTableWidgetItem(str(self.TotalProyectosTutor)))
				self.tablaEstadisticas.setItem(index, 8, QTableWidgetItem(str(self.TotalEstudiantes)))
				self.tablaEstadisticas.setItem(index, 9, QTableWidgetItem(str(self.TotalSInformacion)))
				self.tablaEstadisticas.setItem(index, 10, QTableWidgetItem(str(self.TotalDWeb)))
				self.tablaEstadisticas.setItem(index, 11, QTableWidgetItem(str(self.TotalRedes)))
				self.tablaEstadisticas.setItem(index, 12, QTableWidgetItem(str(self.TotalApps)))
			self.TotalGeneralProyectos = self.TotalGeneralProyectos + 1


	# Rutina para generar el mes esctrito en el sistema dato que la funcion de 
	# fecha retorna el mes en idioma ingles
	def meses(self, mes):
		if mes=='01':
			mes_escrito = 'Enero'
		elif mes=='02':
			mes_escrito = 'Febrero'
		elif mes=='03':
			mes_escrito = 'Marzo'
		elif mes=='04':
			mes_escrito = 'Abril'
		elif mes=='05':
			mes_escrito = 'Mayo'
		elif mes=='06':
			mes_escrito = 'Junio'
		elif mes=='07':
			mes_escrito = 'Julio'
		elif mes=='08':
			mes_escrito = 'Agosto'
		elif mes=='09':
			mes_escrito = 'Septiembre'
		elif mes=='10':
			mes_escrito = 'Octubre'
		elif mes=='11':
			mes_escrito = 'Noviembre'
		else:
			mes_escrito = 'Diciembre'
		return mes_escrito

	# Rutina para generar el acumulado de la estadistica a imprimir
	def actualizaTotalesGenerales(self):
		self.TotalGeneralEstudiantes = self.TotalGeneralEstudiantes + self.TotalEstudiantes
		self.TotalGeneralProyectos = self.TotalGeneralProyectos + self.TotalProyectos
		self.TotalGeneralSInformacion = self.TotalGeneralSInformacion + self.TotalSInformacion
		self.TotalGeneralDWeb = self.TotalGeneralDWeb + self.TotalDWeb
		self.TotalGeneralRedes = self.TotalGeneralRedes + self.TotalRedes
		self.TotalGeneralApps = self.TotalGeneralApps + self.TotalApps

	# Rutina para imprimir linea impresa en el reporte de un registro
	def imprimeLineaRegistros(self):
		w, h = letter
		if self.detallado == 1:
			if self.cedula_tutor != self.cedula_anterior:
				if self.cedula_anterior != "":
					self.cnv.line(30, h - self.linea, 760, h - self.linea)
					self.linea = self.linea + 15
					self.cnv.drawString(35, h - self.linea, "Totales del Tutor: ")
					self.cnv.drawString(260, h - self.linea, str(self.TotalTutorEstudiantes))
					self.cnv.drawString(315, h - self.linea, str(self.TotalTutorProyectos))
					self.cnv.drawString(375, h - self.linea, str(self.TotalTutorSInformacion))
					self.cnv.drawString(440, h - self.linea, str(self.TotalTutorDWeb))
					self.cnv.drawString(500, h - self.linea, str(self.TotalTutorRedes))
					self.cnv.drawString(550, h - self.linea, str(self.TotalTutorApps))
					self.cnv.drawString(260, h - self.linea, str(self.TotalTutorEstudiantes))
					self.cnv.drawString(315, h - self.linea, str(self.TotalTutorProyectos))
					self.cnv.drawString(375, h - self.linea, str(self.TotalTutorSInformacion))
					self.cnv.drawString(440, h - self.linea, str(self.TotalTutorDWeb))
					self.cnv.drawString(500, h - self.linea, str(self.TotalTutorRedes))
					self.cnv.drawString(550, h - self.linea, str(self.TotalTutorApps))
					self.linea = self.linea + 20
					self.contlinea = self.contlinea + 1
				self.cnv.drawString(50, h - self.linea, self.nombre_tutor)
				self.linea = self.linea + 20
				self.contlinea = self.contlinea + 1
			self.cnv.drawString(35, h - self.linea, str(self.totalSecciones))
			self.cnv.drawString(60, h - self.linea, self.ano_periodo)
			self.cnv.drawString(90, h - self.linea, self.trayecto)
			self.cnv.drawString(180, h - self.linea, self.seccion)
			self.cnv.drawString(260, h - self.linea, str(self.TotalEstudiantes))
			self.cnv.drawString(315, h - self.linea, str(self.TotalProyectos))
			self.cnv.drawString(375, h - self.linea, str(self.TotalSInformacion))
			self.cnv.drawString(440, h - self.linea, str(self.TotalDWeb))
			self.cnv.drawString(500, h - self.linea, str(self.TotalRedes))
			self.cnv.drawString(550, h - self.linea, str(self.TotalApps))
			self.totalSecciones = self.totalSecciones + 1
		else:
			self.cnv.drawString(35, h - self.linea, self.nombre_tutor)
			self.cnv.drawString(150, h - self.linea, str(self.totalSecciones))
			self.cnv.drawString(180, h - self.linea, self.ano_periodo)
			self.cnv.drawString(260, h - self.linea, str(self.TotalEstudiantes))
			self.cnv.drawString(315, h - self.linea, str(self.TotalProyectos))
			self.cnv.drawString(375, h - self.linea, str(self.TotalSInformacion))
			self.cnv.drawString(440, h - self.linea, str(self.TotalDWeb))
			self.cnv.drawString(500, h - self.linea, str(self.TotalRedes))
			self.cnv.drawString(550, h - self.linea, str(self.TotalApps))
			self.totalSecciones = self.totalSecciones + 1

	# Procedimiento para Generar Documento de Solvencia en PDF para impresión
	def emitirEstadistica(self):
		w, h = letter
		lv_pagina = 1
		self.cnv = canvas.Canvas(self.archivo, pagesize=landscape(letter))
		if self.optDetallado.isChecked():
			self.detallado = 1
		else:
			self.detallado = 0
		self.imprimir_encabezado = 1
		self.cedula_tutor=""
		self.nombre_tutor=""
		self.cedula_anterior=""
		self.TotalRegistros = 0
		self.TotalTutores = 0
		self.TotalEstudiantes = 0
		self.TotalProyectos = 0
		self.TotalProyectosTutor = 0
		self.TotalRUP = 0
		self.TotalXP = 0
		self.TotalDMovil = 0
		self.TotalOtrosMetodos = 0
		self.TotalSInformacion = 0
		self.TotalDWeb = 0
		self.TotalRedes = 0
		self.TotalApps = 0
		self.TotalTutorEstudiantes = 0
		self.TotalTutorProyectos = 0
		self.TotalTutorRUP = 0
		self.TotalTutorXP = 0
		self.TotalTutorDMovil = 0
		self.TotalTutorOtrosMetodos = 0
		self.TotalTutorSInformacion = 0
		self.TotalTutorDWeb = 0
		self.TotalTutorRedes = 0
		self.TotalTutorApps = 0
		self.TotalGeneralEstudiantes = 0
		self.TotalGeneralProyectos = 0
		self.TotalGeneralRUP = 0
		self.TotalGeneralXP = 0
		self.TotalGeneralDMovil = 0
		self.TotalGeneralOtrosMetodos = 0
		self.TotalGeneralSInformacion = 0
		self.TotalGeneralDWeb = 0
		self.TotalGeneralRedes = 0
		self.TotalGeneralApps = 0
		self.RegistroActual = 0
		
		self.ano_periodo = ""
		self.trayecto = ""
		self.seccion = ""
		self.tipo_trayecto = ""
		self.ano_prosecucion = ""

		index = self.tablaEstadisticas.rowCount()
		while self.RegistroActual < index:
			self.cedula_tutor = self.tablaEstadisticas.item(self.RegistroActual, 0).text()
			self.nombre_tutor = self.tablaEstadisticas.item(self.RegistroActual, 1).text()
			self.ano_periodo = self.tablaEstadisticas.item(self.RegistroActual, 2).text()
			self.trayecto = self.tablaEstadisticas.item(self.RegistroActual, 3).text()
			self.seccion = self.tablaEstadisticas.item(self.RegistroActual, 4).text()
			self.tipo_trayecto = self.tablaEstadisticas.item(self.RegistroActual, 5).text()
			self.ano_prosecucion = self.tablaEstadisticas.item(self.RegistroActual, 6).text()
			self.TotalProyectos = int(self.tablaEstadisticas.item(self.RegistroActual, 7).text())
			self.TotalEstudiantes = int(self.tablaEstadisticas.item(self.RegistroActual, 8).text())
			self.TotalSInformacion = int(self.tablaEstadisticas.item(self.RegistroActual, 9).text())
			self.TotalDWeb = int(self.tablaEstadisticas.item(self.RegistroActual, 10).text())
			self.TotalRedes = int(self.tablaEstadisticas.item(self.RegistroActual, 11).text())
			self.TotalApps = int(self.tablaEstadisticas.item(self.RegistroActual, 12).text())
			if self.imprimir_encabezado == 1:
				self.cnv.drawImage("./img/Membrete-UPTJAA.jpg", 50, h - 280, width=700, height=60)
				self.cnv.setLineWidth(.3)
				self.cnv.setFont("Helvetica", 10, leading = None)
				self.cnv.drawString(50, h - 300, "FECHA: " + self.fecha1)
				self.cnv.drawString(680, h - 300, "PAGINA: " + str(lv_pagina))
				self.cnv.setFont("Times-Roman", 14, leading = None)
				self.cnv.drawString(200, h - 320, "ESTADISTICAS DE PROYECTOS DEL PNF DE INFORMATICA")
				self.cnv.setFont("Helvetica", 10, leading = None)
				if self.detallado == 1:
					self.cnv.drawString(60, h - 340, "Periodo")
					self.cnv.drawString(235, h - 340, "Cantidad")
					self.cnv.drawString(295, h - 340, "Proyectos")
					self.cnv.drawString(355, h - 340, "Total")
					self.cnv.drawString(430, h - 340, "Total")
					self.cnv.drawString(490, h - 340, "Total")
					self.cnv.drawString(540, h - 340, "Total")
					self.cnv.drawString(35, h - 350, "#")
					self.cnv.drawString(50, h - 350, "Academico")
					self.cnv.drawString(110, h - 350, "Trayecto")
					self.cnv.drawString(175, h - 350, "Seccion")
					self.cnv.drawString(235, h - 350, "Estudiantes")
					self.cnv.drawString(295, h - 350, "Recibidos")
					self.cnv.drawString(355, h - 350, "S.Informacion")
					self.cnv.drawString(430, h - 350, "Des. Web")
					self.cnv.drawString(490, h - 350, "Redes")
					self.cnv.drawString(540, h - 350, "APPS")
					self.cnv.setLineWidth(.3)
					self.cnv.line(30,h - 352,760,h - 352)
					self.cnv.line(30,h - 354,760,h - 354)
					self.TotalTutores = self.TotalTutores + 1
					self.totalSecciones = 1
					self.linea = 370
					self.contlinea = 1
				else:
					#c.drawString(50, h - 360, "Cedula:  " + lv_cedula_tutor)
					self.cnv.drawString(185, h - 340, "Periodo")
					self.cnv.drawString(235, h - 340, "Cantidad")
					self.cnv.drawString(290, h - 340, "Proyectos")
					self.cnv.drawString(350, h - 340, "Total")
					self.cnv.drawString(425, h - 340, "Total")
					self.cnv.drawString(488, h - 340, "Total")
					self.cnv.drawString(535, h - 340, "Total")
					self.cnv.drawString(35, h - 350, "Tutor Academico")   
					self.cnv.drawString(120, h - 350, "Secciones")
					self.cnv.drawString(175, h - 350, "Academico")
					self.cnv.drawString(230, h - 350, "Estudiantes")
					self.cnv.drawString(290, h - 350, "Recibidos")
					self.cnv.drawString(350, h - 350, "S.Informacion")
					self.cnv.drawString(425, h - 350, "Des. Web")
					self.cnv.drawString(488, h - 350, "Redes")
					self.cnv.drawString(535, h - 350, "APPS")
					self.cnv.setLineWidth(.3)
					self.cnv.line(30,h - 352,760,h - 352)
					self.cnv.line(30,h - 354,760,h - 354)
					self.TotalTutores = self.TotalTutores + 1
					self.totalSecciones = 1
					self.linea = 370
					self.contlinea = 1
				self.imprimir_encabezado = 0
			if self.cedula_tutor != self.cedula_anterior:
				self.totalSecciones=1
				if self.detallado == 1:
					self.imprimeLineaRegistros()
					self.cedula_anterior = self.cedula_tutor
					self.TotalTutorEstudiantes = self.TotalEstudiantes
					self.TotalTutorProyectos = self.TotalProyectos
					self.TotalTutorSInformacion = self.TotalSInformacion
					self.TotalTutorDWeb = self.TotalDWeb
					self.TotalTutorRedes = self.TotalRedes
					self.TotalTutorApps = self.TotalApps
					self.actualizaTotalesGenerales()
					self.contlinea = self.contlinea + 1
					self.linea = self.linea + 20
					self.RegistroActual = self.RegistroActual + 1
				else:
					self.imprimeLineaRegistros()
					self.actualizaTotalesGenerales()
					self.contlinea = self.contlinea + 1
					self.linea = self.linea + 20
					self.RegistroActual = self.RegistroActual + 1
			else:
				if self.detallado == 1:
					self.imprimeLineaRegistros()
					self.TotalTutorEstudiantes = self.TotalTutorEstudiantes + self.TotalEstudiantes
					self.TotalTutorProyectos = self.TotalTutorProyectos + self.TotalProyectos
					self.TotalTutorSInformacion = self.TotalTutorSInformacion + self.TotalSInformacion
					self.TotalTutorDWeb = self.TotalTutorDWeb + self.TotalDWeb
					self.TotalTutorRedes = self.TotalTutorRedes + self.TotalRedes
					self.TotalTutorApps = self.TotalTutorApps + self.TotalApps
					self.actualizaTotalesGenerales()
					self.contlinea = self.contlinea + 1
					self.linea = self.linea + 20
					self.RegistroActual = self.RegistroActual + 1
				else:
					self.imprimeLineaRegistros()
					self.actualizaTotalesGenerales()
					self.contlinea = self.contlinea + 1
					self.linea = self.linea + 20
					self.RegistroActual = self.RegistroActual + 1
			
			if self.contlinea >= 14:
				lv_pagina = lv_pagina + 1
				c.showPage()
				self.contlinea = 1
				self.imprimir_encabezado = 1
		if self.detallado == 1:
			self.cnv.line(30, h - self.linea, 760, h - self.linea)
			self.linea = self.linea + 15
			self.cnv.drawString(35, h - self.linea, "Totales del Tutor: ")
			self.cnv.drawString(260, h - self.linea, str(self.TotalTutorEstudiantes))
			self.cnv.drawString(315, h - self.linea, str(self.TotalTutorProyectos))
			self.cnv.drawString(375, h - self.linea, str(self.TotalTutorSInformacion))
			self.cnv.drawString(440, h - self.linea, str(self.TotalTutorDWeb))
			self.cnv.drawString(500, h - self.linea, str(self.TotalTutorRedes))
			self.cnv.drawString(550, h - self.linea, str(self.TotalTutorApps))
			self.cnv.drawString(260, h - self.linea, str(self.TotalTutorEstudiantes))
			self.cnv.drawString(315, h - self.linea, str(self.TotalTutorProyectos))
			self.cnv.drawString(375, h - self.linea, str(self.TotalTutorSInformacion))
			self.cnv.drawString(440, h - self.linea, str(self.TotalTutorDWeb))
			self.cnv.drawString(500, h - self.linea, str(self.TotalTutorRedes))
			self.cnv.drawString(550, h - self.linea, str(self.TotalTutorApps))
			self.linea = self.linea + 20
		self.cnv.line(30, h - self.linea, 760, h - self.linea)
		self.linea = self.linea + 2
		self.cnv.line(30, h - self.linea, 760, h - self.linea)
		self.linea = self.linea + 20
		self.cnv.drawString(35, h - self.linea, "Totales General PNF: ")
		self.cnv.drawString(260, h - self.linea, str(self.TotalGeneralEstudiantes))
		self.cnv.drawString(315, h - self.linea, str(self.TotalGeneralProyectos))
		self.cnv.drawString(375, h - self.linea, str(self.TotalGeneralSInformacion))
		self.cnv.drawString(440, h - self.linea, str(self.TotalGeneralDWeb))
		self.cnv.drawString(500, h - self.linea, str(self.TotalGeneralRedes))
		self.cnv.drawString(550, h - self.linea, str(self.TotalGeneralApps))
		self.cnv.drawString(260, h - self.linea, str(self.TotalGeneralEstudiantes))
		self.cnv.drawString(315, h - self.linea, str(self.TotalGeneralProyectos))
		self.cnv.drawString(375, h - self.linea, str(self.TotalGeneralSInformacion))
		self.cnv.drawString(440, h - self.linea, str(self.TotalGeneralDWeb))
		self.cnv.drawString(500, h - self.linea, str(self.TotalGeneralRedes))
		self.cnv.drawString(550, h - self.linea, str(self.TotalGeneralApps))

		self.cnv.showPage()
		self.cnv.save()
		#Abriendo Archivo PDF
		wb.open_new(self.archivo2)

	def cerrar(self):
		self.close()


# Constructor para ejecutar el modulo independiente del programa principal, descarcar para hacer pruebas

#app = QApplication(sys.argv)
#PEstadistica = DialogoEstadistica()
#PEstadistica.show()
#app.exec_()
