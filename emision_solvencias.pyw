#---------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                        #
# Programador: Luis Amaya                                                         #
# Analistas: Jose Astudillo / josmary Botaban                                     #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre  #
# Octubre (2018)                                                                  #
# Version 1.0                                                                     #
# Modulo: Emision de Solvencias                                                   #
# Descripción: Consulta los estudiantes y sus proyectos para la emision de la     #
#              Solvencia Académica                                                # 
#---------------------------------------------------------------------------------#

import sys, os
from PyQt5.QtWidgets import QApplication, QPushButton, QAction, QMessageBox, QDialog, QTableWidget, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
import ctypes #GetSystemMetrics
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib, select
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import webbrowser as wb
from datetime import datetime, date, time, timedelta
import calendar
import os.path as path

# para mover archivos ejecutar shutil.move(archivo1, os.getcwd + "proyectos\\" + nombredestino)
class DialogoSolvencias(QDialog):
	#Método constructor de la clase
	def __init__(self):
		#Iniciar el objeto DialogoAcceso
		QDialog.__init__(self)
		uic.loadUi("consulta_solvencias.ui", self)
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

		#Iniciar valor de Estudiantes
		self.RegistroProyectos= []
		self.RegistroEstudiantes = []
		self.bdvacia = 0
		self.IdPeriodo = 0
		self.IdProyecto = 0
		self.TotalEstudiantes = 0 # Se utiliza para controlar la cantidad de Estudiantes Registrados en Sistema
		self.TotalProyectos = 0
		self.TotalProyectosPorEstudiantes = 0 # Se utiliza para controlar la cantidad de proyectos que tiene un estudiante
		self.encontrar=0
		self.Cedula = ''
		self.Nombre = ''
		self.Apellido = ''
		self.mensaje1.setText('')
		self.txtTotalProyectos.hide()
		self.txtProyectoActual.hide()
		# Configuracion Tabla Grupos de Proyecto
		self.tablaProyectos.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tablaProyectos.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tablaProyectos.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tablaProyectos.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tablaProyectos.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tablaProyectos.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tablaProyectos.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tablaProyectos.setSortingEnabled(True) # Habilitar clasificación
		self.tablaProyectos.setColumnCount(7) # Establecer el número de columnas
		self.tablaProyectos.setRowCount(0) # Establecer el número de filas
		self.tablaProyectos.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tablaProyectos.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tablaProyectos.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tablaProyectos.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tablaProyectos.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas
		nombreColumnasProyecto = ("Año", "Trayecto","Titulo del Proyecto", "Informe", "Desarrollo", "Manuales", "Seccion")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaProyectos.setHorizontalHeaderLabels(nombreColumnasProyecto)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((40, 80, 350, 75, 75, 75, 40), start=0):
			self.tablaProyectos.setColumnWidth(indice, ancho)

		self.tablaProyectos.setColumnHidden(6, True)

		#------------------------------------------------#
		# Botones y Disparadores Eventos Tab Principal   #
		#
		
		# Vincular eventos de click de los botones a las funciones correspondientes
		self.btnBuscar.clicked.connect(self.buscarEstudiante)
		self.btnSolvencia.clicked.connect(self.emitirSolvencia)
		self.btnLimpiar.clicked.connect(self.limpiarPantalla)
		self.btnCerrar.clicked.connect(self.cerrar)

		self.txtCedula.setFocus()

	# Ejecucion de consulta de la Base de Datos para crear matriz de consulta de datos de estudiantes
	def cargaEstudiantes(self):
		self.TotalEstudiantes = 0
		cursor_lista_estudiantes = "SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante FROM estudiante ORDER BY cedula_estudiante"
		self.cursor.execute(cursor_lista_estudiantes)
		self.RegistroEstudiantes = []
		rows = []
		index = 0
		for rows in self.cursor:
			#Abrir fila nueva
			self.RegistroEstudiantes.append([])
			#Crear columnas
			self.RegistroEstudiantes[index].append([])
			self.RegistroEstudiantes[index].append([])
			self.RegistroEstudiantes[index].append([])
			#Asignar Valor
			self.RegistroEstudiantes[index][0]=str(rows[0])
			self.RegistroEstudiantes[index][1]=str(rows[1])
			self.RegistroEstudiantes[index][2]=str(rows[2])
			index = index + 1
		self.TotalEstudiantes = index
		if rows == []:
			self.RegistroEstudiantes = []

	# Ejecucion de consulta de Base de Datos para crear matriz de consulta de datos de los proyectos por estudiantes
	def cargarProyectosEstudiantes(self):
		self.TotalProyectos = 0 
		cursor_lista_proyectos = (
			"""SELECT est.cedula_estudiante AS cedula, tray.periodo_academico, tray.nivel as trayecto, sec.siglas AS seccion, 
			sec.tipo_seccion, sec.ano_seccion, proy.titulo_proyecto, proy.nombre_informe_codificado, 
			proy.nombre_desarrollo_codificado, proy.nombre_manual_codificado
			FROM estudiante as est INNER JOIN elaboran AS ela ON est.cedula_estudiante = ela.FK_cedula_estudiante 
			INNER JOIN proyectos AS proy ON ela.FK_id_proyecto = proy.id_proyecto
			INNER JOIN secciones AS sec ON sec.id_seccion = proy.FK_id_seccion
			INNER JOIN trayecto AS tray ON tray.id_trayecto = sec.FK_id_trayecto 
			ORDER BY est.cedula_estudiante, tray.periodo_academico;
			 """
			 )
		self.cursor.execute(cursor_lista_proyectos)
		self.RegistroProyectos = []
		rows = []
		index = 0
		for rows in self.cursor:
			#Abrir fila nueva
			self.RegistroProyectos.append([])
			#Crear columnas
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			self.RegistroProyectos[index].append([])
			#Asignar Valor
			self.RegistroProyectos[index][0]=str(rows[0])
			self.RegistroProyectos[index][1]=str(rows[1])
			self.RegistroProyectos[index][2]=str(rows[2])
			self.RegistroProyectos[index][3]=str(rows[3])
			self.RegistroProyectos[index][4]=str(rows[4])
			self.RegistroProyectos[index][5]=str(rows[5])
			self.RegistroProyectos[index][6]=str(rows[6])
			self.RegistroProyectos[index][7]=str(rows[7])
			self.RegistroProyectos[index][8]=str(rows[8])
			self.RegistroProyectos[index][9]=str(rows[9])
			index = index + 1
		self.TotalProyectos = index
		if rows == []:
			self.RegistroProyectos = []

	#Ejecucion de busqueda de estudiantes en la matriz y cargar los valores en la pantalla de datos

	def consulta_estudiante(self,lvcedula):
		continuar = 0
		bdbuscar_estudiante = "SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante, estado from estudiante where cedula_estudiante = %i" % int(lvcedula)
		self.cursor.execute(bdbuscar_estudiante)
		rows=self.cursor.fetchone()
		if rows == None:
			self.encontrar = 0
		else:
			if str(rows[3]) == False:
				continuar = 0
				vestudiante = (str(rows[1]) + ' ' + str(rows[2]))
				respuesta = QMessageBox.warning(self,"Precaucion...", "El Estudiante " + vestudiante + " seleccionado esta inactivo\n Desea continuar?", QMessageBox.Yes | QMessageBox.No) 
				if respuesta == QMessageBox.Yes:
					continuar = 1
				else: 
					self.txtCedula.setText("")
			else:
				continuar = 1
			if continuar == 1:
				self.Nombre = str(rows[1])
				self.Apellido = str(rows[2])
				self.txtNombre.setText(self.Nombre)
				self.txtApellido.setText(self.Apellido)
				self.encontrar = 1

		if self.encontrar == 0:
			QMessageBox.warning(self,"Error...", "Cedula del Estudiante no esta registrado, dirijase al modulo de registro de estudiantes, verifique la informacion", QMessageBox.Ok)
			self.txtCedula.setText("")

	#Rutina para buscar los datos y proyectos de un estudiante luego de ingresar su cedula
	def buscarEstudiante(self):
		self.encontrar = 0
		if self.txtCedula.text()=='' or self.txtCedula.text()=='0':
			QMessageBox.information(self, "Base de Datos", "Debe indicar la cedula del Estudiante a consultar", QMessageBox.Ok)
		else:
			lv_cedula = int(self.txtCedula.text())
			self.consulta_estudiante(str(lv_cedula))
		if self.encontrar == 1:
			self.cargarProyectosEstudiantes()
			index = 0
			self.encontrar = 0
			self.Cedula = self.txtCedula.text()
			self.TotalProyectosPorEstudiantes = self.tablaProyectos.rowCount()
			self.tablaProyectos.setSortingEnabled(False)
			if self.tablaProyectos.rowCount() > 0:
				self.tablaProyectos.clearSelection()
				self.tablaProyectos.clearContents()
				index2 = self.tablaProyectos.rowCount()
				while index2 > 0:
					index = index2 - 1
					self.tablaProyectos.removeRow(index)
					index2 = index2 - 1
			self.LlenarTablaProyectos()
			if self.TotalProyectosPorEstudiantes > 0:
				self.btnSolvencia.setEnabled(True)
			else:
				self.btnSolvencia.setEnabled(False)

	# Procedimiento para cargar los valores de los proyectos de cada estudiante en la tabla de proyectos
	def LlenarTablaProyectos(self):
		lv_ano=''
		lv_trayecto=''
		lv_titulo=''
		lv_informe=''
		lv_desarrollo=''
		lv_manuales=''
		lv_seccion=''
		self.TotalProyectosPorEstudiantes = 0
		if self.TotalProyectos > 0:
			index = 0
			self.tablaProyectos.setRowCount(0)
			index2 = 0
			self.encontrar = 0
			while index < self.TotalProyectos:
				if str(self.RegistroProyectos[index][0]) == self.txtCedula.text():
					lv_ano = str(self.RegistroProyectos[index][1])
					lv_trayecto = str(self.RegistroProyectos[index][2])
					lv_seccion = str(self.RegistroProyectos[index][3])
					lv_tipo_seccion = str(self.RegistroProyectos[index][4])
					lv_ano_seccion = str(self.RegistroProyectos[index][5])
					lv_titulo = str(self.RegistroProyectos[index][6])
					lv_nombre_informe = str(self.RegistroProyectos[index][7])
					lv_nombre_desarrollo = str(self.RegistroProyectos[index][8])
					lv_nombre_manual = str(self.RegistroProyectos[index][9])
					if str(self.RegistroProyectos[index][7]) != 'None':
						lv_informe = 'RECIBIDO'
					else:
						lv_informe = 'PENDIENTE'
					if lv_trayecto == 'TRAYECTO III' or lv_trayecto == 'TRAYECTO IV':
						if str(self.RegistroProyectos[index][8]) != 'None':
							lv_desarrollo = 'RECIBIDO'
						else:
							lv_desarrollo = 'PENDIENTE'
						if str(self.RegistroProyectos[index][9]) != 'None':
							lv_manuales = 'RECIBIDO'
						else:
							lv_manuales = 'PENDIENTE'
					else:
						lv_desarrollo = 'NO REQUERIDO'
						lv_manuales = 'NO REQUERIDO'
					
					self.tablaProyectos.insertRow(index2)
					self.tablaProyectos.setItem(index2, 0, QTableWidgetItem(lv_ano))
					self.tablaProyectos.setItem(index2, 1, QTableWidgetItem(lv_trayecto))
					self.tablaProyectos.setItem(index2, 2, QTableWidgetItem(lv_titulo))
					self.tablaProyectos.setItem(index2, 3, QTableWidgetItem(lv_informe))
					self.tablaProyectos.setItem(index2, 4, QTableWidgetItem(lv_desarrollo))
					self.tablaProyectos.setItem(index2, 5, QTableWidgetItem(lv_manuales))
					self.tablaProyectos.setItem(index2, 6, QTableWidgetItem(lv_seccion))
					index2 = index2 + 1
				index = index + 1
			self.TotalProyectosPorEstudiantes = index2

	# Rutina para limpiar los datos presentados en pantalla
	def limpiarPantalla(self):
		self.txtCedula.setText('')
		self.txtNombre.setText('')
		self.txtApellido.setText('')
		self.btnSolvencia.setEnabled(False)
		index3 = 0
		if self.TotalProyectosPorEstudiantes > 0:
			self.tablaProyectos.clearSelection()
			self.tablaProyectos.clearContents()
			index2 = self.TotalProyectosPorEstudiantes
			while index2 > 0:
				index3 = index2 - 1
				self.tablaProyectos.removeRow(index3)
				index2 = index2 - 1
		self.txtCedula.setFocus()

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

	# Procedimiento para Generar Documento de Solvencia en PDF para impresión
	def emitirSolvencia(self):
		if self.tablaProyectos.currentRow() > -1:
			if self.TotalProyectosPorEstudiantes > 0:
				index =  self.tablaProyectos.currentRow()
				lv_cedula = self.txtCedula.text()
				lv_estudiante = self.Nombre + " " + self.Apellido
				lv_informe = self.tablaProyectos.item(index, 3).text()
				lv_desarrollo = self.tablaProyectos.item(index, 4).text()
				lv_manuales = self.tablaProyectos.item(index, 5).text()
				lv_seccion = self.tablaProyectos.item(index, 6).text()
				lv_ano_academico = self.tablaProyectos.item(index, 0).text()
				if lv_informe != 'PENDIENTE' and lv_desarrollo != 'PENDIENTE' and lv_manuales != 'PENDIENTE':
					hoy = datetime.today()
					formato_fecha1 = "%d días del mes de %B del año %Y"
					formato_fecha2 = "%d-%m-%Y"
					formato_fecha3 = "%m"
					formato_fecha4 = "%Y"
					lv_ano = hoy.strftime(formato_fecha4)
					lv_mes = self.meses(hoy.strftime(formato_fecha3))
					formato_fecha1 = "%d días del mes de " + lv_mes + " del año %Y"
					lv_fecha1 = hoy.strftime(formato_fecha2)
					lv_fecha2 = hoy.strftime(formato_fecha1)
					w, h = letter
					lv_archivo = './solvencias/Solvencia-'+lv_ano_academico+'-'+lv_cedula+'.pdf'
					lv_archivo2 = (r'.\solvencias\Solvencia-'+lv_ano_academico+'-'+lv_cedula+'.pdf')
					#Creando Documento PDF
					c = canvas.Canvas(lv_archivo, pagesize=letter)
					c.drawImage("./img/Membrete-UPTJAA.jpg", 50, h - 80, width=500, height=50)
					c.setLineWidth(.3)
					c.setFont("Times-Roman", 20, leading = None)
					c.drawString(200, h - 110, "SOLVENCIA ACADEMICA")
					c.setFont("Helvetica", 12, leading = None)
					c.drawString(50, h - 150, "FECHA: " + lv_fecha1)
					c.drawString(w-150, h - 150, "SECCION: " + lv_seccion)
					c.drawString(50, h - 200, "Quien suscribe, Coordinador del PNF de Informática de la U.P.T.J.A.A. por la presente hace")
					c.drawString(50, h - 220, "constar que el (la) estudiante: " + lv_estudiante)
					c.drawString(w - 150, h - 220,  ", C.I. Nro: ")
					c.line(210, h - 225, 455, h - 225)
					c.drawString(50, h - 240, "  " + lv_cedula + "     , está  solvente  ante  esta oficina dando cumplimiento con los requisitos")
					c.line(50, h - 245, 120, h - 245)
					c.drawString(50, h - 260, "necesarios para culminar el Periodo Académico "+lv_ano_academico+".")
					c.drawString(50, h - 300, "Constancia que se expide a los " + lv_fecha2)
					c.line(220, h - 380, 380, h - 380)
					c.drawString(240, h - 400, "Coordinador del PNFI")
					c.showPage()
					c.save()
					#Abriendo Archivo PDF
					wb.open_new(lv_archivo2)
				else:
					QMessageBox.warning(self, "Prohibicion", "No se puede emitir la solvencia del periodo " + lv_ano_academico + " del estudiante\n Aun tiene soportes de proyectos pendientes por entregar...", QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Prohibicion", "Estudiante no tiene proyectos registrados...", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Error", "Por favor seleccione el trayecto de cuya solvencia desea emitir al estudiante", QMessageBox.Ok)

	# Cerrar Modulo y retornar a pantalla principal
	def cerrar(self):
		self.close()

# Constructor para ejecutar el modulo independiente del programa principal, descarcar para hacer pruebas

#app = QApplication(sys.argv)
#PSolvencias = DialogoSolvencias()
#PSolvencias.show()
#app.exec_()
