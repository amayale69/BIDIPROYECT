#------------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                           #
# Programador: Luis Amaya                                                            #
# Analistas: Jose Astudillo / josmary Botaban                                        #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre     #
# Octubre (2018)                                                                     #
# Version 1.0                                                                        #
# Modulo: Consulta de Proyectos                                                      #
# Descripción: Consulta los datos de los proyectos que se encuentran en la tabla de  #
#              los diez (10) ultimos proyectos en la pantalla principal del sistema  # 
#------------------------------------------------------------------------------------#

# Importacion de librerias
import sys, os, shutil, functools
from PyQt5.QtWidgets import QApplication, QPushButton, QAction, QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QMenu, QFileDialog
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
import ctypes #GetSystemMetrics
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib, select
import os.path as path
from datetime import datetime, date, time, timedelta
import calendar
import webbrowser as wb
import easygui as eg
import os.path as path

class DialogoConsultaProyectos(QDialog):
	#Método constructor de la clase
	def __init__(self):
		#Iniciar el objeto DialogoAcceso
		QDialog.__init__(self)
		uic.loadUi("consulta_proyectos.ui", self)
		#Habilitar Cuadro de Dialogo
		self.setEnabled(True)
		self.setWindowTitle("Consulta de Proyecto Reciente")
		self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)

		#Operacion para centrar la ventana en la pantalla
		resolucion = ctypes.windll.user32
		resolucion_ancho = resolucion.GetSystemMetrics(0)
		resolucion_alto = resolucion.GetSystemMetrics(1)
		left = (resolucion_ancho / 2) - (self.frameSize().width() / 2)
		top = (resolucion_alto / 2) - (self.frameSize().height() / 2) - 40
		self.move(left, top)

		# Declaracion de variables utilitarias en el sistema
		self.archivo_origen = ''
		self.extension = ''
		self.rutadestino = ''
		self.destino = '' 
		self.rutadestino = '' 
		self.nombreProyectoDestino = '' 
		self.nombreDesarrolloDestino = '' 
		self.nombreManualesDestino = '' 
		self.formato_fecha = "%Y-%m-%d %H:%M:%S"
		self.hoy = datetime.today()
		self.fechareg = self.hoy.strftime(self.formato_fecha)

		# Configuracion Tabla Integrantes
		self.tablaIntegrantes.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tablaIntegrantes.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tablaIntegrantes.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tablaIntegrantes.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tablaIntegrantes.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tablaIntegrantes.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tablaIntegrantes.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tablaIntegrantes.setSortingEnabled(True) # Habilitar clasificación
		self.tablaIntegrantes.setColumnCount(3) # Establecer el número de columnas
		self.tablaIntegrantes.setRowCount(0) # Establecer el número de filas
		self.tablaIntegrantes.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tablaIntegrantes.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tablaIntegrantes.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tablaIntegrantes.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tablaIntegrantes.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas
		# self.tabla_seccion_grupos_proyectos.verticalHeader().setHighlightSections(True)
		nombreColumnasIntegrantes = ("Cedula", "Nombre", "Apellido")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaIntegrantes.setHorizontalHeaderLabels(nombreColumnasIntegrantes)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((80, 120, 120), start=0):
			self.tablaIntegrantes.setColumnWidth(indice, ancho)


# Configuracion Tabla Tutores
		self.tablaTutores.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tablaTutores.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tablaTutores.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tablaTutores.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tablaTutores.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tablaTutores.setTextElideMode(Qt.ElideRight)  # Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tablaTutores.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tablaTutores.setSortingEnabled(True) # Habilitar clasificación
		self.tablaTutores.setColumnCount(4) # Establecer el número de columnas
		self.tablaTutores.setRowCount(0) # Establecer el número de filas
		self.tablaTutores.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tablaTutores.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tablaTutores.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tablaTutores.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tablaTutores.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas
		# self.tabla_seccion_grupos_proyectos.verticalHeader().setHighlightSections(True)
		nombreColumnasTutores = ("Cedula", "Nombre", "Apellido", "Tipo Tutor")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaTutores.setHorizontalHeaderLabels(nombreColumnasTutores)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((80, 120, 120, 120), start=0):
			self.tablaTutores.setColumnWidth(indice, ancho)

		#------------------------------------------------#
		# Botones y Disparadores Eventos Tab Principal   #
		#
		self.btnCerrar.clicked.connect(self.cerrar)
		self.btnLeeInforme.clicked.connect(self.VerProyecto)
		self.btnDescargaInforme.clicked.connect(self.descargaInforme)
		self.btnDescargaDesarrollo.clicked.connect(self.descargaDesarrollo)
		self.btnDescargaManual.clicked.connect(self.descargaManual)

	# Rutima para visualizar el documento del proyecto por pantalla
	def VerProyecto(self):
		lv_informe = self.txtEstadoInforme.text()
		lv_NInforme = self.txtNInformeCod.text()
		if lv_informe == 'Entregado':
			lv_archivo = (r'.\proyectos\%s') % lv_NInforme
			#Abriendo Archivo PDF
			wb.open_new(lv_archivo)
		else:
			QMessageBox.warning(self, "Base de Datos", "El proyecto no tiene el documento/archivo solicitado", QMessageBox.Ok)

	# Rutima para descargar el documento del proyecto a la carpeta solicitada al usuario
	def descargaInforme(self):
		lv_informe = self.txtEstadoInforme.text()
		lv_NInforme = self.txtNInformeCod.text()
		directorio = ""
		if lv_informe == "Entregado":
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

	# Rutima para descargar los codigos fuentes del proyecto a la carpeta solicitada al usuario
	def descargaDesarrollo(self):
		lv_desarrollo = self.txtEstadoDesarrollo.text()
		lv_NDesarrollo = self.txtNDesarrolloCod.text()
		directorio = ""
		if lv_desarrollo == "Entregado":
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

	# Rutima para descargar los manuales del proyecto a la carpeta solicitada al usuario
	def descargaManual(self):
		lv_manuales = self.txtEstadoManual.text()
		lv_NManual = self.txtEstadoManual.text()
		directorio = ""
		if lv_manuales == "Entregado":
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

	# Rutima para salir y cerrar el modulo
	def cerrar(self):
		self.close()

# Constructor para ejecutar el modulo independiente del programa principal, descarcar para hacer pruebas

#app = QApplication(sys.argv)
#PConsultaProyecto = DialogoConsultaProyectos()
#PConsultaProyecto.show()
#app.exec_()
