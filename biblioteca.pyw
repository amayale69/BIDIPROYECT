import sys, os, shutil, functools, re
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QFileDialog, QAction, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
import ctypes #GetSystemMetrics
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib, select
import webbrowser as wb
import easygui as eg
import os.path as path

# para mover archivos ejecutar shutil.move(archivo1, os.getcwd + "proyectos\\" + nombredestino)
class DialogoBiblioteca(QDialog):
	#Método constructor de la clase
	def __init__(self):
		#Iniciar el objeto DialogoAcceso
		QDialog.__init__(self)
		uic.loadUi("biblioteca.ui", self)
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
		self.origen = ""
		self.destino = ""
		self.TotalRegistrosTabla = 0

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
		self.tablaProyectos.setColumnCount(12) # Establecer el número de columnas
		self.tablaProyectos.setRowCount(0) # Establecer el número de filas
		self.tablaProyectos.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tablaProyectos.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tablaProyectos.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tablaProyectos.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tablaProyectos.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas

		nombreColumnasProyecto = ("Titulo del Proyecto", "Año", "Trayecto", "Tutor/Asesor", "Metodologia", "Tipo Desarrollo", "Informe", "Desarrollo", "Manuales", "NInforme", "NDesarrollo", "NManuales")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaProyectos.setHorizontalHeaderLabels(nombreColumnasProyecto)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((450, 40, 100, 150, 180, 180, 60, 60, 60, 80, 80, 80 ), start=0):
			self.tablaProyectos.setColumnWidth(indice, ancho)
		# Ocultar Campos de Codigo del los Documentos
		self.tablaProyectos.setColumnHidden(9, True)
		self.tablaProyectos.setColumnHidden(10, True)
		self.tablaProyectos.setColumnHidden(11, True)
		self.tablaProyectos.setSortingEnabled(True)

		#------------------------------------------------#
		# Botones y Disparadores Eventos Tab Principal   #
		#
		
		self.optTitulo.clicked.connect(self.ordenarTabla)
		self.optTrayecto.clicked.connect(self.ordenarTabla)
		self.optTutor.clicked.connect(self.ordenarTabla)
		self.optMetodo.clicked.connect(self.ordenarTabla)
		self.optTDesarrollo.clicked.connect(self.ordenarTabla)
		self.tablaProyectos.itemClicked.connect(self.actSeleccion)


		# Vincular eventos de click de los botones a las funciones correspondientes
		self.btnCargaProyectos.clicked.connect(self.LlenarTablaProyectosBiblioteca)
		self.btnVerProyecto.clicked.connect(self.VerProyecto)
		self.btnInforme.clicked.connect(self.descargaInforme)
		self.btnDesarrollo.clicked.connect(self.descargaDesarrollo)
		self.btnManuales.clicked.connect(self.descargaManual)
		self.btnCerrar.clicked.connect(self.cerrar)
		self.txtFiltro.textChanged.connect(self.buscarDato)


	#Funcion para Ejecutar consultas a BD para llenar Tabla de datos
	def LlenarTablaProyectosBiblioteca(self):
		self.tablaProyectos.setSortingEnabled(False)
		if self.tablaProyectos.rowCount() > 0:
			self.tablaProyectos.clearSelection()
			#self.tabla_personas.disconnect()
			self.tablaProyectos.clearContents()
			#self.tabla_personas.setRowCount(0)
			index2 = self.tablaProyectos.rowCount()
			while index2 > 0:
				index = index2 - 1
				self.tablaProyectos.removeRow(index)
				index2 = index2 - 1

		self.tablaProyectos.setRowCount(0)

		cursor_lista_proyectos = ("""SELECT proy.titulo_proyecto, tray.periodo_academico, tray.nivel as trayecto, 
		tut.nombre_tutor as nombre, tut.apellido_tutor as apellido, 
		met.descripcion as metodo, tdesa.tipo_desarrollo, proy.nombre_informe_codificado as informe, 
		proy.nombre_desarrollo_codificado as desarrollo, proy.nombre_manual_codificado as manuales 
		FROM proyectos AS proy LEFT JOIN es_asesorado AS ase ON ase.fk_id_proyecto = proy.id_proyecto
		INNER JOIN tutores as tut ON tut.cedula_tutor = ase.fk_cedula_tutor
		INNER JOIN metodologia AS met ON proy.fk_id_metodo = met.id_metodo
		INNER JOIN tipo_de_desarrollo AS tdesa ON proy.fk_id_tipo_desarrollo = tdesa.id_tipo_desarrollo 
		INNER JOIN secciones AS sec ON proy.fk_id_seccion = sec.id_seccion
		INNER JOIN trayecto AS tray ON sec.fk_id_trayecto = tray.id_trayecto
		WHERE ase.rol = 'Tecnico Metodologico'
		ORDER BY tray.periodo_academico,  tray.nivel, met.descripcion, tdesa.tipo_desarrollo, proy.titulo_proyecto;"""
		)

		self.cursor.execute(cursor_lista_proyectos)
		rows = []
		index = 0
		for rows in self.cursor:
			lv_titulo = str(rows[0])
			lv_ano = str(rows[1])
			lv_trayecto = str(rows[2])
			lv_tutor = str(rows[3]) + " " + str(rows[4])
			lv_metodo = str(rows[5])
			lv_tipo_desarrollo = str(rows[6])
			if str(rows[7]) != 'None':
				lv_informe = 'SI'
			else:
				lv_informe = 'NO'
			if str(rows[8]) != 'None':
				lv_desarrollo = 'SI'
			else:
				lv_desarrollo = 'NO'
			if str(rows[9]) != 'None':
				lv_manuales = 'SI'
			else:
				lv_manuales = 'NO'
			lv_NInforme = str(rows[7])
			lv_NDesarrollo = str(rows[8])
			lv_NManual = str(rows[9])
			self.tablaProyectos.insertRow(index)
			self.tablaProyectos.setItem(index, 0, QTableWidgetItem(lv_titulo))
			self.tablaProyectos.setItem(index, 1, QTableWidgetItem(lv_ano))
			self.tablaProyectos.setItem(index, 2, QTableWidgetItem(lv_trayecto))
			self.tablaProyectos.setItem(index, 3, QTableWidgetItem(lv_tutor))
			self.tablaProyectos.setItem(index, 4, QTableWidgetItem(lv_metodo))
			self.tablaProyectos.setItem(index, 5, QTableWidgetItem(lv_tipo_desarrollo))
			self.tablaProyectos.setItem(index, 6, QTableWidgetItem(lv_informe))
			self.tablaProyectos.setItem(index, 7, QTableWidgetItem(lv_desarrollo))
			self.tablaProyectos.setItem(index, 8, QTableWidgetItem(lv_manuales))
			self.tablaProyectos.setItem(index, 9, QTableWidgetItem(lv_NInforme))
			self.tablaProyectos.setItem(index, 10, QTableWidgetItem(lv_NDesarrollo))
			self.tablaProyectos.setItem(index, 11, QTableWidgetItem(lv_NManual))
			index = index + 1
		self.TotalRegistrosTabla = index
		self.tablaProyectos.setSortingEnabled(True)

	def VerProyecto(self):
		if self.TotalRegistrosTabla > 0:
			if self.tablaProyectos.currentRow() > -1:
				index = self.tablaProyectos.currentRow()
				lv_informe = self.tablaProyectos.item(index, 6).text()
				lv_NInforme = self.tablaProyectos.item(index, 9).text()
				if lv_informe == 'SI':
					lv_archivo = (r'.\proyectos\%s') % lv_NInforme
					#Abriendo Archivo PDF
					wb.open_new(lv_archivo)
				else:
					QMessageBox.warning(self, "Base de Datos", "El proyecto no tiene el documento/archivo solicitado", QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Error", "Por favor seleccione el proyecto para visualizar", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Error", "La tabla esta vacía, por favor pulse el boton 'Cargar Tabla Proyectos' y seleccione el proyecto a visualizar", QMessageBox.Ok)

	def descargaInforme(self):
		if self.TotalRegistrosTabla > 0:
			if self.tablaProyectos.currentRow() > -1:
				index = self.tablaProyectos.currentRow()
				lv_informe = self.tablaProyectos.item(index, 6).text()
				lv_NInforme = self.tablaProyectos.item(index, 9).text()
				directorio = ""
				if lv_informe == "SI":
					directorio = eg.diropenbox(msg="Seleccione Directorio a Guardar Archivo:", title="Control: diropenbox", default='/home')
					if directorio != None:
						self.origen = ('./proyectos/' + lv_NInforme)  
						self.destino = directorio + os.sep + lv_NInforme
						lv_aceptar = 1
						if os.path.exists(self.destino):
							respuesta=QMessageBox.warning(self,"Adventencia", "El archivo ya existe en la biblioteca, desea sobre-escribir?", QMessageBox.Yes | QMessageBox.No)
							if respuesta == QMessageBox.No:
								lv_aceptar = 0
						if lv_aceptar == 1:
							shutil.copyfile(self.origen, self.destino)
							QMessageBox.information(self, "Sistema", "Archivo copiado en " + directorio + "\n Proceso completado...!", QMessageBox.Ok)
					else:
						QMessageBox.warning(self, "Sistema", "Error, usted no ha elejido la ruta destino...", QMessageBox.Ok)
				else:
					QMessageBox.warning(self, "Base de Datos", "El proyecto no tiene el documento/archivo solicitado", QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Error", "Por favor seleccione un proyecto para descargar", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Error", "La tabla esta vacía, por favor pulse el boton 'Cargar Tabla Proyectos' y seleccione el proyecto a descargar", QMessageBox.Ok)

	def descargaDesarrollo(self):
		if self.TotalRegistrosTabla > 0:
			if self.tablaProyectos.currentRow() > -1:
				index = self.tablaProyectos.currentRow()
				lv_desarrollo = self.tablaProyectos.item(index, 7).text()
				lv_NDesarrollo = self.tablaProyectos.item(index, 10).text()
				directorio = ""
				if lv_desarrollo == "SI":
					directorio = eg.diropenbox(msg="Seleccione Directorio a Guardar Archivo:", title="Control: diropenbox", default='/home')
					if directorio != None:
						self.origen = ('./proyectos/' + lv_NDesarrollo)  
						self.destino = directorio + os.sep + lv_NDesarrollo
						lv_aceptar = 1
						if os.path.exists(self.destino):
							respuesta=QMessageBox.warning(self,"Adventencia", "El archivo ya existe en la biblioteca, desea sobre-escribir?", QMessageBox.Yes | QMessageBox.No)
							if respuesta == QMessageBox.No:
								lv_aceptar = 0
						if lv_aceptar == 1:
							shutil.copyfile(self.origen, self.destino)
							QMessageBox.information(self, "Sistema", "Archivo copiado en " + directorio + "\n Proceso completado...!", QMessageBox.Ok)
					else:
						QMessageBox.warning(self, "Sistema", "Error, usted no ha elejido la ruta destino...", QMessageBox.Ok)
				else:
					QMessageBox.warning(self, "Base de Datos", "El proyecto no tiene el documento/archivo solicitado", QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Error", "Por favor seleccione un proyecto para descargar", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Error", "La tabla esta vacía, por favor pulse el boton 'Cargar Tabla Proyectos' y seleccione el proyecto a descargar", QMessageBox.Ok)

	def descargaManual(self):
		if self.TotalRegistrosTabla > 0:
			if self.tablaProyectos.currentRow() > -1:
				index = self.tablaProyectos.currentRow()
				lv_manuales = self.tablaProyectos.item(index, 8).text()
				lv_NManual = self.tablaProyectos.item(index, 11).text()
				directorio = ""
				if lv_manuales == "SI":
					directorio = eg.diropenbox(msg="Seleccione Directorio a Guardar Archivo:", title="Control: diropenbox", default='/home')
					if directorio != None:
						self.origen = ('./proyectos/' + lv_NManual)  
						self.destino = directorio + os.sep + lv_NManual
						lv_aceptar = 1
						if os.path.exists(self.destino):
							respuesta=QMessageBox.warning(self,"Adventencia", "El archivo ya existe en la biblioteca, desea sobre-escribir?", QMessageBox.Yes | QMessageBox.No)
							if respuesta == QMessageBox.No:
								lv_aceptar = 0
						if lv_aceptar == 1:
							shutil.copyfile(self.origen, self.destino)
							QMessageBox.information(self, "Sistema", "Archivo copiado en " + directorio + "\n Proceso completado...!", QMessageBox.Ok)
					else:
						QMessageBox.warning(self, "Sistema", "Error, usted no ha elejido la ruta destino...", QMessageBox.Ok)
				else:
					QMessageBox.warning(self, "Base de Datos", "El proyecto no tiene el documento/archivo solicitado", QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Error", "Por favor seleccione un proyecto para descargar", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Error", "La tabla esta vacía, por favor pulse el boton 'Cargar Tabla Proyectos' y seleccione el proyecto a descargar", QMessageBox.Ok)

	def actSeleccion(self):
		fila = self.tablaProyectos.currentRow()

	def buscarDato(self):
		lv_texto = self.txtFiltro.text().upper()
		validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
		if self.optTitulo.isChecked()== True:
			columna = 0
		elif self.optTrayecto.isChecked()==True:  
			columna = 2
		elif self.optTutor.isChecked()==True:  
			columna = 3
		elif self.optMetodo.isChecked()==True:  
			columna = 4
		else:
			columna = 5
		index = self.tablaProyectos.rowCount()
		fila=0
		encontrar = 0
		while fila < index:
			lv_busqueda = self.tablaProyectos.item(fila,columna).text()
			if lv_texto in lv_busqueda:
				encontrar = 1
				break;
			fila = fila + 1
		if encontrar == 1:
			posicion_inicial = self.tablaProyectos.item((index - 1), columna)
			self.tablaProyectos.scrollToItem(posicion_inicial)
			posicion_final = self.tablaProyectos.item(fila, columna)
			self.tablaProyectos.scrollToItem(posicion_final)
			self.tablaProyectos.setCurrentCell(fila, columna)
			
			return True
		else:
			return False


	def ordenarTabla(self):
		if self.optTitulo.isChecked():
			self.tablaProyectos.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		elif self.optTrayecto.isChecked():
			self.tablaProyectos.horizontalHeader().setSortIndicator(2, Qt.AscendingOrder)
		elif self.optTutor.isChecked():
			self.tablaProyectos.horizontalHeader().setSortIndicator(3, Qt.AscendingOrder)
		elif self.optMetodo.isChecked():
			self.tablaProyectos.horizontalHeader().setSortIndicator(4, Qt.AscendingOrder)
		else:
			self.tablaProyectos.horizontalHeader().setSortIndicator(5, Qt.AscendingOrder)

	def cerrar(self):
		self.close()

#app = QApplication(sys.argv)
#PBiblioteca = DialogoBiblioteca()
#PBiblioteca.show()
#app.exec_()
