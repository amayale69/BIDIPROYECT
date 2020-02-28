#------------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                           #
# Programador: Luis Amaya                                                            #
# Analistas: Jose Astudillo / josmary Botaban                                        #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre     #
# Octubre (2018)                                                                     #
# Version 1.0                                                                        #
# Modulo: Registro Integrado de Proyectos                                            #
# Descripción: Tiene como funcion crear las secciones de cada trayecto del periodo   #
#              academico y registrar los proyectos con sus integrantes de cada       #
#              sección y guardar y codificar los soportes digitales de cada proyecto # 
#------------------------------------------------------------------------------------#

import sys, os, shutil, functools, re
from PyQt5.QtWidgets import QApplication, QPushButton, QAction, QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QMenu, QFileDialog
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
import ctypes #GetSystemMetrics
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib, select
import os.path as path
from datetime import datetime, date, time, timedelta
import calendar

class DialogoIntProyectos(QDialog):
	#Método constructor de la clase
	def __init__(self):
		#Iniciar el objeto DialogoAcceso
		QDialog.__init__(self)
		uic.loadUi("registro_integrado_proyectos.ui", self)
		#Habilitar Cuadro de Dialogo
		self.setEnabled(True)
		self.setWindowTitle("Registro Integrado de Proyectos")
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

		# Declaracion de variables utilitarias en el sistema
		self.txtIdPeriodo.setText('')
		self.txtAnoPeriodo.setText('')
		self.optRegular.setChecked(True)
		self.txtAnoProsecucion.setText('')
		self.chkRInforme.setChecked(True)
		self.chkRDesarrollo.setChecked(True)
		self.chkRManual.setChecked(True)
		self.RegistroPeriodos = []
		self.RegistroProyectos= []
		self.RegistroGrProyecto = []
		self.RegistroEstudiantes = []
		self.RegistroProfesores = []
		self.TipoPersona = ''
		self.bdvacia = 0
		self.bdedita = 0
		self.bdnuevo = 0
		self.IdPeriodo = 0
		self.IdProyecto = 0
		self.IdSeccion = 0 
		self.cedula_Original = ''
		self.nuevoproyecto = 1
		self.idPeriodoOriginal = 0
		self.proyectoActual = 0
		self.RegActualPeriodo = 0
		self.regPeriodoAnterior = 0
		self.TotalRegPeriodo = 0
		self.ProxRegPeriodo = 0
		self.GrupoDesarrolloOriginal = '00'
		self.metodoOriginal = ''
		self.tipoDesarrolloOriginal = ''
		self.Tutor = ''
		self.archivo_origen = ''
		self.extension = ''
		self.rutadestino = ''
		self.destino = '' 
		self.rutadestino = '' 
		self.nombreProyectoDestino = '' 
		self.nombreDesarrolloDestino = '' 
		self.nombreManualesDestino = '' 
		self.extension = ''
		self.TotalTutores = 0 # Se utiliza para controlar la cantidad de Tutores Registrados en Sistema
		self.TotalEstudiantes = 0 # Se utiliza para controlar la cantidad de Estudiantes Registrados en Sistema
		self.TotalGeneralProyectos = 0
		self.TotalIntegrantes = 0 # Se utiliza para controlar la cantidad de integrantes que tiene un proyecto
		self.TotalGeneralIntegrantes = 0 # Se utiliza para controlar la cantidad de integrantes de proyectos
		self.TotalProyectosPorPeriodos = 0 # Se utiliza para controlar la cantidad de registros en la lista de proyectos
		self.encontrar=0
		self.continua = 0
		self.resultado_operacion = 0
		self.mensaje1.setText('')
		self.mensaje2.setText('')
		self.mensaje3.setText('')
		self.tipo_tutor = 0
		self.txtTotalRPeriodo.hide()
		self.txtTotalProyectos.hide()
		self.txtIdPeriodo.hide()
		self.txtIdSeccion.hide()
		self.txtIdProyecto.show()
		self.txtUsuarioActivo.hide()
		self.txtAnoPeriodo_2.hide()
		self.cmbTrayecto_2.hide()
		self.cmbSeccion_2.hide()
		self.txtAnoProsecucion_2.hide()
		self.grpTipoTrayecto_2.hide()
		self.codigoProyecto = ''
		self.formato_fecha = "%Y-%m-%d %H:%M:%S"
		self.hoy = datetime.today()
		self.fechareg = self.hoy.strftime(self.formato_fecha)
		self.usuarioActivo = self.txtUsuarioActivo.text()
		self.grpListaSecciones.hide()
		self.btnImprimeFicha.hide()
		self.txtIdMetodo.hide()
		self.txtIdTipoDesarrollo.hide()
		self.cmbTipoDesarrollo.hide()
		self.cmbMetotologia.hide()
		# Configuracion Tabla Grupos de Proyecto
		self.tabla_seccion_grupos_proyectos.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tabla_seccion_grupos_proyectos.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tabla_seccion_grupos_proyectos.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tabla_seccion_grupos_proyectos.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tabla_seccion_grupos_proyectos.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tabla_seccion_grupos_proyectos.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tabla_seccion_grupos_proyectos.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tabla_seccion_grupos_proyectos.setSortingEnabled(True) # Habilitar clasificación
		self.tabla_seccion_grupos_proyectos.setColumnCount(14) # Establecer el número de columnas
		self.tabla_seccion_grupos_proyectos.setRowCount(0) # Establecer el número de filas
		self.tabla_seccion_grupos_proyectos.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tabla_seccion_grupos_proyectos.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tabla_seccion_grupos_proyectos.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tabla_seccion_grupos_proyectos.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tabla_seccion_grupos_proyectos.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas
		# self.tabla_seccion_grupos_proyectos.verticalHeader().setHighlightSections(True)
		nombreColumnasGrProyecto = ("Proyecto No.", "Codigo Proyecto", "Grupo de Proyecto", "Titulo del Proyecto", "Metodologia", "Tipo de Desarrollo", "Nombre Informe", "Nombre Desarrollo", "Nombre Manual", "Id Proyecto", "Id Periodo", "Id Seccion", "Id Metodo", "Id Tipo Desarrollo")

		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tabla_seccion_grupos_proyectos.setHorizontalHeaderLabels(nombreColumnasGrProyecto)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((80, 180, 120, 430, 150, 150, 100, 100, 100, 80, 80, 80, 80, 80), start=0):
			self.tabla_seccion_grupos_proyectos.setColumnWidth(indice, ancho)

		self.tabla_seccion_grupos_proyectos.setColumnHidden(0, True)
		self.tabla_seccion_grupos_proyectos.setColumnHidden(9, True)
		self.tabla_seccion_grupos_proyectos.setColumnHidden(10, True)
		self.tabla_seccion_grupos_proyectos.setColumnHidden(11, True)
		self.tabla_seccion_grupos_proyectos.setColumnHidden(12, True)
		self.tabla_seccion_grupos_proyectos.setColumnHidden(13, True)

		# Configuracion Tabla Grupos de Proyecto
		self.tabla_periodos.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tabla_periodos.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tabla_periodos.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tabla_periodos.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tabla_periodos.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tabla_periodos.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tabla_periodos.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tabla_periodos.setSortingEnabled(True) # Habilitar clasificación
		self.tabla_periodos.setColumnCount(7) # Establecer el número de columnas
		self.tabla_periodos.setRowCount(0) # Establecer el número de filas
		self.tabla_periodos.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tabla_periodos.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tabla_periodos.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tabla_periodos.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tabla_periodos.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas

		nombreColumnasPeriodos = ("Id Periodo", "Año Academico", "Trayecto", "Seccion", "Tipo de Trayecto", "Año Prosecucion", "Id Seccion")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tabla_periodos.setHorizontalHeaderLabels(nombreColumnasPeriodos)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((80, 100, 100, 80, 100, 80, 80, 80, 80), start=0):
			self.tabla_periodos.setColumnWidth(indice, ancho)
		self.tabla_periodos.setColumnHidden(6, True)
		self.tabla_periodos.setColumnHidden(0, True)

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
		self.tablaIntegrantes.setColumnCount(4) # Establecer el número de columnas
		self.tablaIntegrantes.setRowCount(0) # Establecer el número de filas
		self.tablaIntegrantes.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tablaIntegrantes.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tablaIntegrantes.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tablaIntegrantes.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tablaIntegrantes.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas

		nombreColumnasIntegrantes = ("Cedula Estudiante", "Nombre Estudiante", "Apellido Estudiante", "Telefono de Contacto")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaIntegrantes.setHorizontalHeaderLabels(nombreColumnasIntegrantes)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((90, 130, 130, 120), start=0):
			self.tablaIntegrantes.setColumnWidth(indice, ancho)

		# Configuracion Tabla Tutores
		self.tablaTutores.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tablaTutores.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tablaTutores.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tablaTutores.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tablaTutores.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tablaTutores.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
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

		nombreColumnasIntegrantes = ("Cedula Tutor", "Nombre Tutor", "Apellido Tutor", "Tipo Asesoria")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tablaTutores.setHorizontalHeaderLabels(nombreColumnasIntegrantes)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((90, 130, 130, 100), start=0):
			self.tablaTutores.setColumnWidth(indice, ancho)

		#Configurando Tabla de Busqueda de Personas
		self.txtCedulaSeleccionada.setText("0")
		self.tabla_personas.setAlternatingRowColors(True)
		#Instruccion para deshabilitar edicion
		self.tabla_personas.setEditTriggers(QTableWidget.NoEditTriggers)
		# Deshabilitar el comportamiento de arrastrar y soltar
		self.tabla_personas.setDragDropOverwriteMode(False)
		# Seleccionar toda la fila
		self.tabla_personas.setSelectionBehavior(QTableWidget.SelectRows)
		# Seleccionar una fila a la vez
		self.tabla_personas.setSelectionMode(QTableWidget.SingleSelection)
		# Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran
		# textos que no encajan
		self.tabla_personas.setTextElideMode(Qt.ElideRight)# Qt.ElideNone
		# Establecer el ajuste de palabras del texto 
		self.tabla_personas.setWordWrap(False)
		# Habilitar clasificación
		self.tabla_personas.setSortingEnabled(True)
		# Establecer el número de columnas
		self.tabla_personas.setColumnCount(6)
		# Establecer el número de filas
		self.tabla_personas.setRowCount(0)
		# Alineación del texto del encabezado
		self.tabla_personas.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter)
		# Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tabla_personas.horizontalHeader().setHighlightSections(True)
		# Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tabla_personas.horizontalHeader().setStretchLastSection(True)
		# Ocultar encabezado vertical
		self.tabla_personas.verticalHeader().setVisible(False)
		# Establecer altura de las filas
		self.tabla_personas.verticalHeader().setDefaultSectionSize(20)
		# self.tabla_personas.verticalHeader().setHighlightSections(True)
		nombreColumnas = ("Cedula", "Nombre", "Apellido", "Sexo", "Telefono", "Estado")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tabla_personas.setHorizontalHeaderLabels(nombreColumnas)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((65, 150, 150, 70, 100, 70), start=0):
			self.tabla_personas.setColumnWidth(indice, ancho)

		# Configuracion Tabla Metodos
		self.tabla_metodos.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tabla_metodos.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tabla_metodos.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tabla_metodos.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tabla_metodos.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tabla_metodos.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tabla_metodos.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tabla_metodos.setSortingEnabled(True) # Habilitar clasificación
		self.tabla_metodos.setColumnCount(2) # Establecer el número de columnas
		self.tabla_metodos.setRowCount(0) # Establecer el número de filas
		self.tabla_metodos.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tabla_metodos.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tabla_metodos.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tabla_metodos.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tabla_metodos.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas

		nombreColumnasMetodos = ("Metodologia", "Id Metodo")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tabla_metodos.setHorizontalHeaderLabels(nombreColumnasMetodos)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((100, 80), start=0):
			self.tabla_metodos.setColumnWidth(indice, ancho)
		self.tabla_metodos.setColumnHidden(1, True)
		


		# Configuracion Tabla TDesarrollo
		self.tabla_tdesarrollo.setAlternatingRowColors(True) #Instruccion para Alternar color de las filas
		self.tabla_tdesarrollo.setEditTriggers(QTableWidget.NoEditTriggers) #Instruccion para deshabilitar edicion
		self.tabla_tdesarrollo.setDragDropOverwriteMode(False) # Deshabilitar el comportamiento de arrastrar y soltar
		self.tabla_tdesarrollo.setSelectionBehavior(QTableWidget.SelectRows) # Seleccionar toda la fila
		self.tabla_tdesarrollo.setSelectionMode(QTableWidget.SingleSelection) # Seleccionar una fila a la vez
		self.tabla_tdesarrollo.setTextElideMode(Qt.ElideRight)# Qt.ElideNone 
		                                                                   # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran 
																		   # textos que no encajan
		self.tabla_tdesarrollo.setWordWrap(False) # Establecer el ajuste de palabras del texto 
		self.tabla_tdesarrollo.setSortingEnabled(True) # Habilitar clasificación
		self.tabla_tdesarrollo.setColumnCount(2) # Establecer el número de columnas
		self.tabla_tdesarrollo.setRowCount(0) # Establecer el número de filas
		self.tabla_tdesarrollo.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter) # Alineación del texto del encabezado
		self.tabla_tdesarrollo.horizontalHeader().setHighlightSections(True) # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tabla_tdesarrollo.horizontalHeader().setStretchLastSection(True) # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tabla_tdesarrollo.verticalHeader().setVisible(False) # Ocultar encabezado vertical
		self.tabla_tdesarrollo.verticalHeader().setDefaultSectionSize(20) # Establecer altura de las filas

		nombreColumnasTDesarrollo = ("Tipo Desarrollo", "Id Tdesarrollo")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tabla_tdesarrollo.setHorizontalHeaderLabels(nombreColumnasTDesarrollo)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((100, 80), start=0):
			self.tabla_tdesarrollo.setColumnWidth(indice, ancho)
		self.tabla_tdesarrollo.setColumnHidden(1, True)

		self.tabla_personas.itemClicked.connect(self.actContadorActual)

		self.btnRegresar.clicked.connect(self.VolverALista)
		self.btnNuevoRegistro.clicked.connect(self.nuevoRegistro)
		self.btnEditarRegistro.clicked.connect(self.editarRegistro)
#		self.btnSalir.clicked.connect(self.cerrar_dialogo)
		self.btnGuardarPersonas.clicked.connect(self.guardarRegistro)
		self.btnDescartarPersonas.clicked.connect(self.retornarValores)
		self.optCedula.clicked.connect(self.ordenarTablaPersonas)
		self.optNombre.clicked.connect(self.ordenarTablaPersonas)
		self.optApellido.clicked.connect(self.ordenarTablaPersonas)
		self.btnEstado.clicked.connect(self.cambiarEstado)
		self.grpPersonas.hide()

		#Crear disparador para saber el numero de la fila de la tabla que ha sido seleccionada
		self.tabla_personas.itemClicked.connect(self.actContadorActual)
		self.tabla_personas.itemDoubleClicked.connect(self.seleccionarRegistro)
		self.btnSelPersona.clicked.connect(self.seleccionarRegistro)

		#Crear disparador de evento para buscar datos en la tabla por texto introducido por usuario
		self.txtFiltro.textChanged.connect(self.buscarDato)
		self.txtFiltroPersonas.textChanged.connect(self.buscarDatoPersona)

		#Ocultar el campo de control de total de registros
		self.TotalRegPersonas.hide()
		self.contador_registros.hide()
		self.registroactual = 0
		self.proximo_registro = 0


		#------------------------------------------------#
		# Botones y Disparadores Eventos Tab Principal   #
		#
		
		#Vincular eventos de click de los botones a las funciones correspondientes
		# Botones del Tab Principal
		self.btnNuevo.clicked.connect(self.nuevoRegPeriodo)
		self.btnEditar.clicked.connect(self.editarRegPeriodo)
		self.btnGuardar.clicked.connect(self.guardarPeriodo)
		self.btnBuscar.clicked.connect(self.BuscarTablaPeriodo)
		self.btnDescartar.clicked.connect(self.retornarValores)
		self.btnEliminar.clicked.connect(self.eliminarPeriodo)
		self.btnLimpiar.clicked.connect(self.limpiarPeriodo)
		self.btnCerrar.clicked.connect(self.cerrar)
		self.btnPrimero.clicked.connect(self.primerRegistro)
		self.btnAtras.clicked.connect(self.registroAnterior)
		self.btnSiguiente.clicked.connect(self.registroSiguiente)
		self.btnUltimo.clicked.connect(self.ultimoRegistro)
		self.cmbTrayecto.currentTextChanged.connect(self.valida_cmbTrayecto)
		self.optRegular.clicked.connect(self.valOpcionTipoTrayecto)
		self.optProsecucion.clicked.connect(self.valOpcionTipoTrayecto)
		self.btnRegProyecto.clicked.connect(self.AccederNuevoProyecto)
		self.tabla_seccion_grupos_proyectos.itemDoubleClicked.connect(self.AccederEditarProyecto)
		self.btnConsultaProyecto.clicked.connect(self.AccederConsultaProyecto)

		#-------------------------------------------------------#
		# Botones y Disparadores Eventos Tab Lista de Periodos  #
		#
		# Botones del Tab Lista de Periodos
		self.btnCerrarLista.clicked.connect(self.regresoPrincipal)
		self.btnSeleccionar.clicked.connect(self.SeleccionyCerrar)
		self.optAno.clicked.connect(self.ordenarTabla)
		self.optTrayecto.clicked.connect(self.ordenarTabla)
		self.optSeccion.clicked.connect(self.ordenarTabla)
		#Crear disparador para saber el numero de la fila de la tabla que ha sido seleccionada
		self.tabla_periodos.itemClicked.connect(self.actContadorActualPeriodos)
		self.tabla_periodos.itemDoubleClicked.connect(self.SeleccionyCerrar)
		#Crear disparador de evento para buscar datos en la tabla por texto introducido por usuario
		self.txtFiltro.textChanged.connect(self.buscarDato)
		self.optAno.setChecked(True)

		#Habilita Tab Principal
		self.tabWidget.setTabEnabled(0, True)

		#Deshabilitar los Tabs Secundarios
		self.tabWidget.setTabEnabled(1, False)
		self.tabWidget.setTabEnabled(2, False)

		#Esconder Campos de Control
		self.txtIdPeriodo.hide()
		self.chkRInforme.hide()
		self.chkRDesarrollo.hide()
		self.chkRManual.hide()

		#Esconder cuadro de seleccion de tutores
		self.grpPersonas.hide()

		#-----------------------------------------------#
		# Botones y Disparadores Eventos Tab Proyectos  #
		#
		# Botones del Tab Proyectos

		self.btnCerrarProyectos.clicked.connect(self.CerrarVentanaProyectos)
		self.btnGuardarProyecto.clicked.connect(self.guardarProyecto)
		self.btnDescartarProyecto.clicked.connect(self.descartarProyecto)
		self.btnNuevoProyecto.clicked.connect(self.nuevoProyecto)
		self.btnEditarProyecto.clicked.connect(self.editarProyecto)
		self.btnEliminarProyecto.clicked.connect(self.eliminarProyecto)
		self.btnListaEstudiante.clicked.connect(self.mostrarListaEstudiantes)
		self.btnListaTutores.clicked.connect(self.mostrarListaTutores)
		self.tablaIntegrantes.itemClicked.connect(self.seleccionaEstudiante)
		self.tablaTutores.itemClicked.connect(self.seleccionaTutor)

		self.btnRemoverIntegrante.clicked.connect(self.RemoverIntegrante)
		self.btnAgregarIntegrante.clicked.connect(self.AgregarIntegrante)
		self.btnRemoverTutor.clicked.connect(self.RemoverTutor)
		self.btnAsignarTutor.clicked.connect(self.AgregarTutor)
		self.btnPrimerProyecto.clicked.connect(self.primerProyecto)
		self.btnProyectoAnterior.clicked.connect(self.proyectoAnterior)
		self.btnProyectoSiguiente.clicked.connect(self.proyectoSiguiente)
		self.btnUltimoProyecto.clicked.connect(self.ultimoProyecto)
		self.btnSubeInforme.clicked.connect(self.copiarInforme)
		self.btnSubeDesarrollo.clicked.connect(self.copiarDesarrollo)
		self.btnSubeManual.clicked.connect(self.copiarManual)
		self.cmbGrupoDesarrollo.currentTextChanged.connect(self.CodificarProyecto)
		self.btnRetorno.clicked.connect(self.cerrarGrpPersonas)
		self.btnMetodologia.clicked.connect(self.elejirmetodo)
		self.btnTipoDesarrollo.clicked.connect(self.elejir_tdesarrollo)
		self.tabla_metodos.itemDoubleClicked.connect(self.seleccionar_metodo)
		self.btnElejirMetodo.clicked.connect(self.seleccionar_metodo)
		self.tabla_metodos.itemClicked.connect(self.actMetodo)
		self.tabla_tdesarrollo.itemDoubleClicked.connect(self.seleccionar_tdesarrollo)
		self.btnElejirTipoDesarrollo.clicked.connect(self.seleccionar_tdesarrollo)
		self.tabla_tdesarrollo.itemClicked.connect(self.actTdesarrollo)
		self.txtIdMetodoSeleccionado.hide()
		self.txtIdTipoDesarrolloSeleccionado.hide()
		self.btnActualizaMetodo.clicked.connect(self.actualizarMetodo)
		self.btnAgregarMetodo.clicked.connect(self.agregarMetodo)
		self.btnActualizaTipoDesarrollo.clicked.connect(self.actualizarTipoDesarrollo)
		self.btnAgregarTipoDesarrollo.clicked.connect(self.agregarTipoDesarrollo)
		self.txtIdSeccionLista.hide()
		self.RegActualListaPeriodo.hide()
		self.TotalReg.hide()
		self.grpTDesarrollo.hide()
		self.grpMetodos.hide()
		self.txtCedulaSeleccionada.hide()
		self.RegActual.hide()

		self.tabPersonas.setTabEnabled(0, True)
		
		#Habilitar Tab Lista
		self.tabPersonas.setTabEnabled(1, False)
		self.tabPersonas.setCurrentIndex(0)
		self.txtIdProyecto.hide()

		#Ejecutar consultas a BD para armar matrices de datos
		self.cargarPeriodos()
		self.cargarMetodosTipoDesa()
		self.cargarDatosProyectos()
		self.desactivarCampos()

	def actMetodo(self):
		fila = self.tabla_metodos.currentRow()
		self.metodoOriginal = self.tabla_metodos.item(fila,0).text()
		self.txtMetodoNuevo.setText(self.tabla_metodos.item(fila,0).text())
		self.txtIdMetodoSeleccionado.setText(self.tabla_metodos.item(fila,1).text())

	def actTdesarrollo(self):
		fila = self.tabla_tdesarrollo.currentRow()
		self.tipoDesarrolloOriginal = self.tabla_tdesarrollo.item(fila,0).text()
		self.txtTipoDesarrolloNuevo.setText(self.tabla_tdesarrollo.item(fila,0).text())
		self.txtIdTipoDesarrolloSeleccionado.setText(self.tabla_tdesarrollo.item(fila,1).text())

	def actualizarMetodo(self):
		if self.tabla_metodos.currentRow() != -1:
			fila = self.tabla_metodos.currentRow()
			if self.txtMetodoNuevo.text().replace(" ", "") == '':
				QMessageBox.warning(self,"Base de Datos", "No puede reemplazar el metodo anterior por un campo vacio", QMessageBox.Ok)
			else:
				lvMetodoNuevo = self.txtMetodoNuevo.text()
				lvIdMetodo = int(self.txtIdMetodoSeleccionado.text())
				if lvMetodoNuevo != self.metodoOriginal:
					respuesta = QMessageBox.warning(self,"Base de Datos", "Seguro de reemplazar el metodo '" + self.metodoOriginal + "' por el metodo '" + lvMetodoNuevo + "'?", QMessageBox.Yes | QMessageBox.No)
					if respuesta == QMessageBox.Yes:
						index = 0
						encontrar = 0
						totalmetodos = self.tabla_metodos.rowCount()
						while index < totalmetodos:
							if self.tabla_metodos.item(index,0).text() == lvMetodoNuevo:
								encontrar = 1 
								break;
							index = index + 1
						if encontrar == 1:
							QMessageBox.warning(self,"Base de Datos", "Ya existe el metodo señalado, no se permite duplicar informacion...", QMessageBox.Ok)
						else:
							actualiza_metodo = "UPDATE metodologia SET descripcion = '%s' where id_metodo = '%i'" % (lvMetodoNuevo, lvIdMetodo)
							self.cursor.execute(actualiza_metodo)
							self.tabla_metodos.setItem(fila, 0, QTableWidgetItem(lvMetodoNuevo))
							QMessageBox.information(self,"Base de Datos", "Registro actualizado correctamente...!", QMessageBox.Ok)
							self.txtMetodoNuevo.setText('')
							self.txtIdMetodoSeleccionado.setText('')
					else:
						self.txtMetodoNuevo.setText('')
						self.txtIdMetodoSeleccionado.setText('')


	def agregarMetodo(self):
		proximafila = self.tabla_metodos.rowCount()
		if self.txtMetodoNuevo.text().replace(" ", "") == '':
			QMessageBox.warning(self,"Base de Datos", "No puede agregar metodos vacios", QMessageBox.Ok)
		else:
			lvMetodoNuevo = self.txtMetodoNuevo.text()
			index = 0
			encontrar = 0
			totalmetodos = self.tabla_metodos.rowCount()
			while index < totalmetodos:
				if self.tabla_metodos.item(index,0).text() == lvMetodoNuevo:
					encontrar = 1 
					break;
				index = index + 1
			if encontrar == 1:
				QMessageBox.warning(self,"Base de Datos", "Ya existe el metodo señalado, no se permite duplicar informacion...", QMessageBox.Ok)
			else:
				actualiza_metodo = "INSERT INTO metodologia (descripcion) values('%s')" % (lvMetodoNuevo)
				buscar_metodo = "SELECT id_metodo from metodologia where descripcion = '%s'" % lvMetodoNuevo
				self.cursor.execute(actualiza_metodo)
				self.cursor.execute(buscar_metodo)
				row = self.cursor.fetchone()
				lvIdMetodo = str(row[0])
				self.tabla_metodos.insertRow(proximafila)
				self.tabla_metodos.setItem(proximafila, 0, QTableWidgetItem(lvMetodoNuevo))
				self.tabla_metodos.setItem(proximafila, 1, QTableWidgetItem(lvIdMetodo))
				posicion = self.tabla_metodos.item(proximafila, 0)
				self.tabla_metodos.scrollToItem(posicion)
				self.tabla_metodos.setCurrentCell(proximafila, 0)
				self.txtIdMetodoSeleccionado.setText('')
				self.txtMetodoNuevo.setText('')
				QMessageBox.information(self,"Base de Datos", "Registro añadido correctamente...!", QMessageBox.Ok)

	def actualizarTipoDesarrollo(self):
		if self.tabla_tdesarrollo.currentRow() != -1:
			fila = self.tabla_tdesarrollo.currentRow()
			if self.txtTipoDesarrolloNuevo.text().replace(" ", "") == '':
				QMessageBox.warning(self,"Base de Datos", "No puede reemplazar el Tipo de Desarrollo anterior por un campo vacio", QMessageBox.Ok)
			else:
				lvTipoDesarrolloNuevo = self.txtTipoDesarrolloNuevo.text()
				lvIdTipoDesarrollo = int(self.txtIdTipoDesarrolloSeleccionado.text())
				if lvTipoDesarrolloNuevo != self.tipoDesarrolloOriginal:
					respuesta = QMessageBox.warning(self,"Base de Datos", "Seguro de reemplazar el Tipo de Desarrollo '" + self.tipoDesarrolloOriginal + "' por '" + lvTipoDesarrolloNuevo + "'?", QMessageBox.Yes | QMessageBox.No)
					if respuesta == QMessageBox.Yes:
						index = 0
						encontrar = 0
						totaltdesarrollo = self.tabla_tdesarrollo.rowCount()
						while index < totaltdesarrollo:
							if self.tabla_tdesarrollo.item(index,0).text() == lvTipoDesarrolloNuevo:
								encontrar = 1 
								break;
							index = index + 1
						if encontrar == 1:
							QMessageBox.warning(self,"Base de Datos", "Ya existe el metodo señalado, no se permite duplicar informacion...", QMessageBox.Ok)
						else:
							actualiza_tdesarrollo = "UPDATE tipo_de_desarrollo SET tipo_desarrollo = '%s' where id_tipo_desarrollo = '%i'" % (lvTipoDesarrolloNuevo, lvIdTipoDesarrollo)
							self.cursor.execute(actualiza_tdesarrollo)
							self.tabla_tdesarrollo.setItem(fila, 0, QTableWidgetItem(lvTipoDesarrolloNuevo))
							QMessageBox.information(self,"Base de Datos", "Registro actualizado correctamente...!", QMessageBox.Ok)
							self.txtTipoDesarrolloNuevo.setText('')
							self.txtIdTipoDesarrolloSeleccionado.setText('')
					else:
						self.txtTipoDesarrolloNuevo.setText('')
						self.txtIdTipoDesarrolloSeleccionado.setText('')


	def agregarTipoDesarrollo(self):
		proximafila = self.tabla_tdesarrollo.rowCount()
		if self.txtTipoDesarrolloNuevo.text().replace(" ", "") == '':
			QMessageBox.warning(self,"Base de Datos", "No puede agregar metodos vacios", QMessageBox.Ok)
		else:
			lvTipoDesarrolloNuevo = self.txtTipoDesarrolloNuevo.text()
			index = 0
			encontrar = 0
			totaltdesarrollo = self.tabla_tdesarrollo.rowCount()
			while index < totaltdesarrollo:
				if self.tabla_tdesarrollo.item(index,0).text() == lvTipoDesarrolloNuevo:
					encontrar = 1 
					break;
				index = index + 1
			if encontrar == 1:
				QMessageBox.warning(self,"Base de Datos", "Ya existe el tipo de desarrollo señalado, no se permite duplicar informacion...", QMessageBox.Ok)
			else:
				actualiza_tdesarrollo = "INSERT INTO tipo_de_desarrollo (tipo_desarrollo) values('%s')" % (lvTipoDesarrolloNuevo)
				buscar_tdesarrollo = "SELECT id_tipo_desarrollo from tipo_de_desarrollo where tipo_desarrollo = '%s'" % lvTipoDesarrolloNuevo
				self.cursor.execute(actualiza_tdesarrollo)
				self.cursor.execute(buscar_tdesarrollo)
				row = self.cursor.fetchone()
				lvIdTipoDesarrollo = str(row[0])
				self.tabla_tdesarrollo.insertRow(proximafila)
				self.tabla_tdesarrollo.setItem(proximafila, 0, QTableWidgetItem(lvTipoDesarrolloNuevo))
				self.tabla_tdesarrollo.setItem(proximafila, 1, QTableWidgetItem(lvIdTipoDesarrollo))

				posicion = self.tabla_tdesarrollo.item(proximafila, 0)
				self.tabla_tdesarrollo.scrollToItem(posicion)
				self.tabla_tdesarrollo.setCurrentCell(proximafila, 0)
				self.txtIdTipoDesarrolloSeleccionado.setText('')
				self.txtTipoDesarrolloNuevo.setText('')
				QMessageBox.information(self,"Base de Datos", "Registro añadido correctamente...!", QMessageBox.Ok)

	def elejirmetodo(self):
		self.grpMetodos.show()

	def seleccionar_metodo(self):
		fila = self.tabla_metodos.currentRow()
		self.txtIdMetodo.setText(self.tabla_metodos.item(fila, 1).text())
		self.btnMetodologia.setText(self.tabla_metodos.item(fila, 0).text())
		self.grpMetodos.hide()



	def elejir_tdesarrollo(self):
		self.grpTDesarrollo.show()

	def seleccionar_tdesarrollo(self):
		fila = self.tabla_tdesarrollo.currentRow()
		self.txtIdTipoDesarrollo.setText(self.tabla_tdesarrollo.item(fila,1).text())
		self.btnTipoDesarrollo.setText(self.tabla_tdesarrollo.item(fila,0).text())
		self.grpTDesarrollo.hide()

	def cargarMetodosTipoDesa(self):
		if self.tabla_metodos.rowCount() > 0:
			self.tabla_metodos.clearSelection()
			self.tabla_metodos.clearContents()
			index2 = self.tabla_metodos.rowCount()
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.tabla_metodos.removeRow(index3)
				index2 = index2 - 1
		if self.tabla_tdesarrollo.rowCount() > 0:
			self.tabla_tdesarrollo.clearSelection()
			self.tabla_tdesarrollo.clearContents()
			index2 = self.tabla_tdesarrollo.rowCount()
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.tabla_tdesarrollo.removeRow(index3)
				index2 = index2 - 1
		cursor_metodos = "SELECT descripcion, id_metodo from metodologia order by descripcion"
		cursor_tdesa = "SELECT tipo_desarrollo, id_tipo_desarrollo from tipo_de_desarrollo"
		self.cursor.execute(cursor_metodos)
		rows = []
		index = 0
		for rows in self.cursor:
			if rows==[]:
				self.bdvacia = 1
			else:
				self.tabla_metodos.insertRow(index)
				metodo = str(rows[0])
				id_metodo = str(rows[1])
				self.tabla_metodos.setItem(index, 0, QTableWidgetItem(metodo))
				self.tabla_metodos.setItem(index, 1, QTableWidgetItem(id_metodo))
				index = index + 1

		self.cursor.execute(cursor_tdesa)
		rows = []
		index = 0
		for rows in self.cursor:
			if rows==[]:
				self.bdvacia = 1
			else:
				self.tabla_tdesarrollo.insertRow(index)
				metodo = str(rows[0])
				id_metodo = str(rows[1])
				self.tabla_tdesarrollo.setItem(index, 0, QTableWidgetItem(metodo))
				self.tabla_tdesarrollo.setItem(index, 1, QTableWidgetItem(id_metodo))
				index = index + 1
			






	def cargarPeriodos(self):
		cursor_lista_periodos = ("""SELECT tray.id_trayecto, tray.periodo_academico, tray.nivel, sec.siglas, sec.tipo_seccion, 
			sec.ano_seccion, sec.id_seccion 
			FROM trayecto AS tray INNER JOIN secciones AS sec ON tray.id_trayecto = sec.fk_id_trayecto
			ORDER BY tray.periodo_academico, tray.nivel, sec.siglas, sec.tipo_seccion, sec.ano_seccion""")
		self.cursor.execute(cursor_lista_periodos)
		self.RegistroPeriodos = []
		rows = []
		index = 0
		for rows in self.cursor:
			if rows==[]:
				self.bdvacia = 1
			else:
				#Crear fila
				self.RegistroPeriodos.append([])
				#Crear columnas
				self.RegistroPeriodos[index].append([])
				self.RegistroPeriodos[index].append([])
				self.RegistroPeriodos[index].append([])
				self.RegistroPeriodos[index].append([])
				self.RegistroPeriodos[index].append([])
				self.RegistroPeriodos[index].append([])
				self.RegistroPeriodos[index].append([])
				#Asignar valor a campos
				self.RegistroPeriodos[index][0]=str(rows[0])
				self.RegistroPeriodos[index][1]=str(rows[1])
				self.RegistroPeriodos[index][2]=str(rows[2])
				self.RegistroPeriodos[index][3]=str(rows[3])
				self.RegistroPeriodos[index][4]=str(rows[4])
				self.RegistroPeriodos[index][5]=str(rows[5])
				self.RegistroPeriodos[index][6]=str(rows[6])
				index = index + 1
			self.TotalRegPeriodo = index

		if index == 0:
			self.txtContadorPeriodo.setText("0")
			self.txtTotalRPeriodo.setText("0")
			self.RegActualPeriodo = 0
			self.TotalRegPeriodo = 0
			self.ProxRegPeriodo = 1
			self.limpiarPeriodo()
		else:
			self.txtContadorPeriodo.setText("1")
			self.txtTotalRPeriodo.setText(str(index))
			self.RegActualPeriodo = 1
			self.TotalRegPeriodo = index
			self.ProxRegPeriodo = index + 1
			self.llenarPantPeriodo(0)
			self.cargarDatosProyectos()


	# Rutina para limpiar los valores den pantalla del periodo
	def limpiarPeriodo(self):
		self.continua = 1
		if self.bdedita == 1:
			#Se ejecuta cuando se se pulsa boton limpiar en una operacion de edicion de datos
			respuesta=QMessageBox.warning(self,"Adventencia", "Desea reiniciar los valores del registro activo?", QMessageBox.Yes | QMessageBox.No)
			if respuesta == QMessageBox.No:
				self.continua = 0
		if self.bdnuevo == 1:
			index2 = self.tabla_seccion_grupos_proyectos.rowCount()
			if index2 > 0:
				self.txtContadorPeriodo.setText(str(index2 + 1))
				self.tabla_seccion_grupos_proyectos.clearSelection()
				#self.tabla_seccion_grupos_proyectos.disconnect()
				self.tabla_seccion_grupos_proyectos.clearContents()
				#self.tabla_seccion_grupos_proyectos.setRowCount(0)
				index3 = 0
				while index2 > 0:
					index3 = index2 - 1
					self.tabla_seccion_grupos_proyectos.removeRow(index3)
					index2 = index2 - 1
			
		if self.continua==1:
			self.txtAnoPeriodo.setText('')
			self.txtAnoProsecucion.setText('')
			self.cmbTrayecto.setCurrentIndex(0)
			self.chkRInforme.setChecked(True)
			self.chkRDesarrollo.setChecked(False)
			self.chkRManual.setChecked(False)
			self.cmbSeccion.setCurrentIndex(0)
			self.optRegular.setChecked(True)
			self.txtLimiteEstudiantes.setText('5')
			self.AnoPeriodo = 0
			self.Trayecto = 'TRAYECTO I'
			self.TipoTrayecto = 'Regular'
			self.Seccion = 'IF-01'
			self.AnoProsecucion = 0
			self.RInforme = True
			self.RDesarrollo = False
			self.RManual = False

	def llenarPantPeriodo(self,nregistro):
		index = nregistro
		self.txtIdPeriodo.setText(str(self.RegistroPeriodos[nregistro][0]))
		self.txtAnoPeriodo.setText(str(self.RegistroPeriodos[nregistro][1]))

		#Asignar el valor al Cuadro de Seleccion Trayecto
		if self.RegistroPeriodos[nregistro][2] == 'TRAYECTO I':
			self.cmbTrayecto.setCurrentIndex(0)
			self.chkRInforme.setChecked(True)
			self.chkRDesarrollo.setChecked(False)
			self.chkRManual.setChecked(False)
		elif self.RegistroPeriodos[nregistro][2] == 'TRAYECTO II':
			self.cmbTrayecto.setCurrentIndex(1)
			self.chkRInforme.setChecked(True)
			self.chkRDesarrollo.setChecked(False)
			self.chkRManual.setChecked(False)
		elif self.RegistroPeriodos[nregistro][2] == 'TRAYECTO III':
			self.cmbTrayecto.setCurrentIndex(2)
			self.chkRInforme.setChecked(True)
			self.chkRDesarrollo.setChecked(True)
			self.chkRManual.setChecked(True)
		else:
			self.cmbTrayecto.setCurrentIndex(3)
			self.chkRInforme.setChecked(True)
			self.chkRDesarrollo.setChecked(True)
			self.chkRManual.setChecked(True)
		#Asignar el valor al Cuadro de Seleccion Seccion
		if self.RegistroPeriodos[nregistro][3] == 'IF-01':
			self.cmbSeccion.setCurrentIndex(0)
		elif self.RegistroPeriodos[nregistro][3] == 'IF-02':
			self.cmbSeccion.setCurrentIndex(1)
		elif self.RegistroPeriodos[nregistro][3] == 'IF-03':
			self.cmbSeccion.setCurrentIndex(2)
		elif self.RegistroPeriodos[nregistro][3] == 'IF-04':
			self.cmbSeccion.setCurrentIndex(3)
		elif self.RegistroPeriodos[nregistro][3] == 'IF-05':
			self.cmbSeccion.setCurrentIndex(4)
		else:
			self.cmbSeccion.setCurrentIndex(5)

		if self.RegistroPeriodos[nregistro][4]=="Regular":
			self.optRegular.setChecked(True)
			self.txtLimiteEstudiantes.setText('5')
		else:
			self.optProsecucion.setChecked(True)
			self.txtLimiteEstudiantes.setText('3')
		self.txtAnoProsecucion.setText(str(self.RegistroPeriodos[nregistro][5]))
		self.txtIdSeccion.setText(str(self.RegistroPeriodos[nregistro][6]))

	# Rutina para habilitar m odo de nuevo registro
	def nuevoRegPeriodo(self):
		self.bdnuevo = 1
		self.RegActualPeriodo = int(self.txtContadorPeriodo.text())
		self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
		self.ProxRegPeriodo = int(self.txtTotalRPeriodo.text()) + 1
		if self.TotalRegPeriodo == 0:
			self.txtIdPeriodo.setText("0")
			self.IdPeriodo = 0
		self.idPeriodoOriginal = int(self.txtIdPeriodo.text())
		self.txtContadorPeriodo.setText(str(self.ProxRegPeriodo))
		self.activarCampos()
		self.limpiarPeriodo()
		self.txtAnoPeriodo.setFocus()

	# Rutina para activar la edicion del registro activo en pantalla
	def editarRegPeriodo(self):
		self.bdnuevo == 0
		self.RegActualPeriodo = int(self.txtContadorPeriodo.text())
		self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
		self.ProxRegPeriodo = int(self.txtTotalRPeriodo.text()) + 1
		self.idPeriodoOriginal = int(self.txtIdPeriodo.text())
		self.seccion_original = self.cmbSeccion.currentText()
		self.bdedita = 1
		self.activarCampos()
		self.txtAnoPeriodo.setFocus()

	def guardarPeriodo(self):
		if self.bdnuevo == 1:
			self.txtContadorPeriodo.setText(str(self.ProxRegPeriodo))
			self.txtTotalRPeriodo.setText(str(self.ProxRegPeriodo))
			self.encontrar = 0
			if self.txtAnoPeriodo.text() < '2013':
				QMessageBox.warning(self,"Error...", "Debe introducir un año valido '> 2012'", QMessageBox.Ok)
				self.continua = 0
				self.estado = 1
			else:
				if self.optProsecucion.isChecked() and int(self.txtAnoProsecucion.text()) < 2015:
					QMessageBox.warning(self,"Error...", "Debe indicar el año de Prosecucion valido de la seccion antes de guardar datos", QMessageBox.Ok)
				else:
					self.resultado_operacion = 0
					self.agregarPeriodo()
					if self.resultado_operacion == 1:
						QMessageBox.information(self,"Base de Datos", "El registro fue agregado exitosamente...", QMessageBox.Ok)
						self.estado = 0
					else:
						self.estado = 1
		else:
			respuesta=QMessageBox.warning(self,"Adventencia", "Esta seguro de guardar cambios? ", QMessageBox.Yes | QMessageBox.No)
			if respuesta == QMessageBox.Yes:
				self.encontrar = 0
				self.idPeriodoOriginal = int(self.txtIdPeriodo.text())
				self.buscarPeriodo()
				if self.encontrar == 0:
					self.actualizaPeriodo()
					QMessageBox.information(self,"Base de Datos", "El registro fue actualizado exitosamente...", QMessageBox.Ok)
					self.estado = 2
				else:
					QMessageBox.warning(self,"Base de Datos", "No puede reemplazar datos por las de un registro existente.. revise su informacion!!!", QMessageBox.Ok)
					self.estado = 3
			else:
				self.estado = 1 

		if self.estado == 0:
			self.RegActualPeriodo = int(self.txtContadorPeriodo.text())
			self.ProxRegPeriodo = int(self.txtTotalRPeriodo.text()) + 1
			self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
			self.bdvacia=0
			self.desactivarCampos()
			self.bdnuevo=0
		elif self.estado == 2:
			self.desactivarCampos()
			self.bdedita=0

	# Rutina para consultar matriz de periodos 
	def buscarPeriodo(self):
		index = 0
		self.encontrar = 0
		self.continua = 1
		lv_totalregistros = 0
		lv_anoPeriodo = 0
		if self.txtAnoPeriodo.text() == '':
			lv_anoPeriodo = 0
		else:
			lv_anoPeriodo = int(self.txtAnoPeriodo.text())
		lv_trayecto = self.cmbTrayecto.currentText()
		lv_seccion = self.cmbSeccion.currentText()
		if self.optRegular.isChecked():
			lv_tipotrayecto = "Regular"
		else:
			lv_tipotrayecto = "Prosecución"
		if self.txtAnoProsecucion.text() == '':
			lv_anoprosecucion = 0
		else:
			lv_anoprosecucion = int(self.txtAnoProsecucion.text())
		lv_totalregistros = int(self.txtTotalRPeriodo.text())
		if lv_totalregistros > 0:
			while index < (lv_totalregistros - 1):
				if str(self.RegistroPeriodos[index][1]) == str(lv_anoPeriodo) and self.RegistroPeriodos[index][2] == lv_trayecto and self.RegistroPeriodos[index][3] == lv_seccion and self.RegistroPeriodos[index][4] == lv_tipotrayecto and self.RegistroPeriodos[index][5] == str(lv_anoprosecucion):
					self.IdPeriodo = int(self.RegistroPeriodos[index][0])
					if self.idPeriodoOriginal == self.IdPeriodo:
						self.encontrar = 0
					else:
						self.encontrar = 1
						break;
				index = index + 1		

	# Rutina para reestablecer los valores originales en pantalla de un registro en modificacion
	def retornarValores(self):
		if self.bdnuevo == 1:
			self.txtContadorPeriodo.setText(str(self.regPeriodoAnterior))
			self.ProxRegPeriodo = int(self.txtTotalRPeriodo.text())

		if self.ProxRegPeriodo>0:
			index = int(self.txtContadorPeriodo.text()) - 1
			self.llenarPantPeriodo(index)
		else:
			self.limpiarPeriodo()
		self.txtContadorPeriodo.setText(str(self.RegActualPeriodo))
		self.desactivarCampos()
		self.cargarDatosProyectos()

	def eliminarPeriodo(self):
		self.TotalProyectosPorPeriodos = self.tabla_seccion_grupos_proyectos.rowCount()
		if self.TotalProyectosPorPeriodos > 0:
			QMessageBox.warning(self,"Error", "Esta Seccion del Trayecto y Año Académico, tiene proyectos registrados. Debe eliminar los proyectos registrados antes de eliminar este registro...", QMessageBox.Ok)
		else:
			self.bdelimina = 0
			self.RegActualPeriodo = int(self.txtContadorPeriodo.text())
			self.ProxRegPeriodo = 1
			self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
			if self.RegActualPeriodo == 0:
				QMessageBox.warning(self,"Error", "No puede borrar fin de archivo", QMessageBox.Ok)
			else:
				respuesta=QMessageBox.warning(self,"Adventencia", "Desea eliminar el registro actual?", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.Yes:
					self.elimina = 1
					self.IdPeriodo = int(self.txtIdPeriodo.text())
					self.IdSeccion = int(self.txtIdSeccion.text())
					eliminar_seccion = "DELETE FROM secciones where id_seccion = '%d'" % (self.IdSeccion) 
					self.cursor.execute(eliminar_seccion)
					if self.RegActualPeriodo == self.TotalRegPeriodo:
						if self.RegActualPeriodo == 1:
							self.RegActualPeriodo = 0
							self.TotalRegPeriodo = 0
							self.ProxRegPeriodo = 0
						else:
							self.ProxRegPeriodo = self.RegActualPeriodo - 1
							self.RegActualPeriodo = self.RegActualPeriodo - 1
							self.TotalRegPeriodo = self.TotalRegPeriodo - 1
					else:
						self.ProxRegPeriodo = self.RegActualPeriodo
						self.TotalRegPeriodo = self.TotalRegPeriodo - 1
					self.cargarPeriodos()
					self.retornarValores()
					self.bdelimina = 0
					QMessageBox.information(self,"Base de Datos", "El registro fue eliminado exitosamente...", QMessageBox.Ok)

	# Activacion de Campos en Modo de Edicion o Nuevo Registro
	def activarCampos(self):
		aceptar = 0
		if self.bdnuevo==0:
			if self.TotalProyectosPorPeriodos > 0:
				respuesta = QMessageBox.warning(self,"Precaucion...", "Esta Seccion del Trayecto y Año Académico, tiene proyectos registrados. ¿Esta seguro de modificar este registro?", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.Yes:
					aceptar = 1
			else:
				aceptar = 1
		else:
			aceptar=1
		if aceptar == 1:
			self.txtAnoPeriodo.setEnabled(True)
			self.cmbTrayecto.setEnabled(True)
			self.grpTipoTrayecto.setEnabled(True)
			self.cmbSeccion.setEnabled(True)

			if self.cmbTrayecto.currentText() == "TRAYECTO I" or self.cmbTrayecto.currentText() == "TRAYECTO II":
				self.txtAnoProsecucion.setText('0')
				self.txtAnoProsecucion.setEnabled(False)
			else:
				self.txtAnoProsecucion.setEnabled(True)

			self.btnGuardar.show()
			self.btnDescartar.show()
			self.btnConsultaProyecto.setEnabled(False)
			self.tabla_seccion_grupos_proyectos.setEnabled(False)
			self.btnRegProyecto.setEnabled(False)
			self.btnLimpiar.show()
			self.btnNuevo.hide()
			self.btnBuscar.hide()
			self.btnCerrar.hide()
			self.btnPrimero.setEnabled(False)
			self.btnAtras.setEnabled(False)
			self.btnSiguiente.setEnabled(False)
			self.btnUltimo.setEnabled(False)
			self.btnRegProyecto.setEnabled(False)
	
	# Desactivacion de Campos en Modo de Consulta de Registro
	def desactivarCampos(self):
		self.txtAnoPeriodo.setEnabled(False)
		self.cmbTrayecto.setEnabled(False)
		self.grpTipoTrayecto.setEnabled(False)
		self.cmbSeccion.setEnabled(False)
		self.txtAnoProsecucion.setEnabled(False)
		self.btnConsultaProyecto.setEnabled(True)
		self.btnRegProyecto.setEnabled(True)
		self.tabla_seccion_grupos_proyectos.setEnabled(True)
		self.btnGuardar.hide()
		self.btnDescartar.hide()
		self.btnLimpiar.hide()
		self.btnNuevo.show()
		self.btnBuscar.show()
		self.btnCerrar.show()
		self.btnPrimero.setEnabled(True)
		self.btnAtras.setEnabled(True)
		self.btnSiguiente.setEnabled(True)
		self.btnUltimo.setEnabled(True)
		self.btnRegProyecto.setEnabled(True)
		self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
		if self.TotalRegPeriodo > 0:
			self.btnEliminar.setEnabled(True)
			self.btnEditar.setEnabled(True)
			self.btnBuscar.setEnabled(True)
		else:
			self.btnEliminar.setEnabled(False)
			self.btnEditar.setEnabled(False)
			self.btnBuscar.setEnabled(False)

	# Rutina para validar los parametros del sistema de acuerdo al trayecto
	def valida_cmbTrayecto(self):
		if self.bdnuevo == 1 or self.bdedita == 1:
			if self.cmbTrayecto.currentText() == "TRAYECTO III" or self.cmbTrayecto.currentText() == "TRAYECTO IV":
				self.grpTipoTrayecto.setEnabled(True)
				self.chkRDesarrollo.setChecked(True)
				self.chkRManual.setChecked(True)
				self.txtAnoProsecucion.setEnabled(True)
			else:
				self.grpTipoTrayecto.setEnabled(False)
				self.optRegular.setChecked(True)
				self.chkRDesarrollo.setChecked(False)
				self.chkRManual.setChecked(False)
				self.txtAnoProsecucion.setText('0')
				self.txtAnoProsecucion.setEnabled(False)
		
	# Rutina para controlar la activacion del año de prosecucion activo para Trayectos III y IV
	def valOpcionTipoTrayecto(self):
		if self.bdnuevo == 1 or self.bdedita == 1:
			if self.optRegular.isChecked():
				self.txtAnoProsecucion.setEnabled(False)
				self.txtAnoProsecucion.setText('0')
				self.txtLimiteEstudiantes.setText('5')
			else:
				self.txtAnoProsecucion.setEnabled(True)
				self.txtLimiteEstudiantes.setText('3')


	def actualizaPeriodo(self):
		lv_id_trayecto = int(self.txtIdPeriodo.text())
		lv_anoPeriodo = int(self.txtAnoPeriodo.text())
		lv_trayecto = self.cmbTrayecto.currentText()
		lv_seccion = self.cmbSeccion.currentText()
		lv_id_seccion = int(self.txtIdSeccion.text())
		if self.optRegular.isChecked() == True:
			lv_tipotrayecto = "Regular"
		else:
			lv_tipotrayecto = "Prosecución"
		lv_anoprosecucion = int(self.txtAnoProsecucion.text())  
		actualiza_trayecto = "UPDATE trayecto SET nivel = '%s', periodo_academico = '%i' where id_trayecto = '%i'" % (lv_trayecto, lv_anoPeriodo, lv_id_trayecto)
		actualiza_seccion = "UPDATE secciones SET siglas = ('%s'), tipo_seccion = ('%s'), ano_seccion = ('%i') WHERE id_seccion = '%i'" % (lv_seccion, lv_tipotrayecto, lv_anoprosecucion, lv_id_seccion)
		#lv_usuario_activo = 'ADMIN'
		#self.hoy = datetime.today()
		#self.fechareg = self.hoy.strftime(self.formato_fecha)
		#agregar_auditoria = "INSERT INTO accede (FK_usuario, fk_id_proyecto, actividad, fecha) VALUES ('%s', '%i', 'Actualizo', '%s')" % (lv_usuario_activo, lv_id_proyecto, self.fechareg)
		self.cursor.execute(actualiza_trayecto)
		self.cursor.execute(actualiza_seccion)
		index = int(self.txtContadorPeriodo.text()) -1
		self.RegistroPeriodos[index][1]=str(lv_anoPeriodo)
		self.RegistroPeriodos[index][2]=lv_trayecto
		self.RegistroPeriodos[index][3]=lv_seccion
		self.RegistroPeriodos[index][4]=lv_tipotrayecto
		self.RegistroPeriodos[index][5]=str(lv_anoprosecucion)

	def agregarPeriodo(self):
		self.RegActualPeriodo = int(self.txtContadorPeriodo.text()) 
		self.regPeriodoAnterior = int(self.txtContadorPeriodo.text()) 
		self.ProxRegPeriodo = int(self.txtContadorPeriodo.text()) + 1
		self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
		lv_anoPeriodo = int(self.txtAnoPeriodo.text())
		lv_trayecto = self.cmbTrayecto.currentText()
		lv_seccion = self.cmbSeccion.currentText()
		if self.optRegular.isChecked():
			lv_tipotrayecto = "Regular"
		else:
			lv_tipotrayecto = "Prosecución"
		if self.txtAnoProsecucion.text() == '':
			lv_anoprosecucion = 0
		else:
			lv_anoprosecucion = int(self.txtAnoProsecucion.text())
		self.hoy = datetime.today()
		self.fechareg = self.hoy.strftime(self.formato_fecha)

		inserta_trayecto = "INSERT INTO trayecto (nivel, periodo_academico) VALUES ('%s', '%i')" % (lv_trayecto, lv_anoPeriodo)
		consulta_trayecto = "SELECT id_trayecto FROM trayecto WHERE periodo_academico = '%i' and nivel = '%s'" % (lv_anoPeriodo, lv_trayecto)
		self.cursor.execute(consulta_trayecto)
		rows=self.cursor.fetchone()
		if rows == None:
			self.cursor.execute(inserta_trayecto)
			self.cursor.execute(consulta_trayecto)
			rows=self.cursor.fetchone()
		lv_id_trayecto = int(str(rows[0]))
		inserta_seccion = "INSERT INTO secciones (siglas, tipo_seccion, ano_seccion, nro_estudiantes, fk_id_trayecto) VALUES ('%s', '%s', '%i', 0, '%i')" % (lv_seccion, lv_tipotrayecto, lv_anoprosecucion, lv_id_trayecto)
		consulta_seccion = "SELECT id_seccion FROM secciones WHERE siglas = '%s' and tipo_seccion='%s' and ano_seccion = '%i' and fk_id_trayecto = '%i'" % (lv_seccion, lv_tipotrayecto, lv_anoprosecucion, lv_id_trayecto)
		self.cursor.execute(consulta_seccion)
		rows=self.cursor.fetchone()
		if rows == None:
			self.cursor.execute(inserta_seccion)
			self.cursor.execute(consulta_seccion)
			rows=self.cursor.fetchone()
			lv_id_seccion = int(str(rows[0]))
			self.IdPeriodo = lv_id_trayecto
			self.txtIdPeriodo.setText(str(self.IdPeriodo))
			self.IdSeccion = lv_id_seccion
			self.txtIdPeriodo.setText(str(self.IdSeccion))
			self.resultado_operacion = 1
			self.continuar = 1
		else:
			QMessageBox.warning(self,"Error...", "Esta seccion ya se encuentra registrada en el sistema, verifique sus datos", QMessageBox.Ok)			
			self.continuar = 0
		if self.continuar == 1:
			#creando una fila en la matriz
			self.cargarPeriodos()
			self.TotalRegPeriodo = int(self.txtTotalRPeriodo.text())
			index = 0
			while index < self.TotalRegPeriodo:
				if self.RegistroPeriodos[index][0] == str(self.IdPeriodo):
					self.ProxRegPeriodo = index + 1
					break;
				index = index + 1
			self.txtIdPeriodo.setText(str(self.IdPeriodo))

			#self.txtIdPeriodo.setText(str(self.IdPeriodo))
			self.txtContadorPeriodo.setText(str(self.ProxRegPeriodo))
			self.RegActualPeriodo = self.ProxRegPeriodo
			self.bdnuevo = 1
			index = int(self.txtContadorPeriodo.text()) - 1
			self.llenarPantPeriodo(index)
			self.txtContadorPeriodo.setText(str(index + 1))
			if self.TotalProyectosPorPeriodos > 0:
				self.tabla_seccion_grupos_proyectos.clearSelection()
				#self.tabla_seccion_grupos_proyectos.disconnect()
				self.tabla_seccion_grupos_proyectos.clearContents()
				#self.tabla_seccion_grupos_proyectos.setRowCount(0)
				index2 = self.TotalProyectosPorPeriodos
				index3 = 0
				while index2 > 0:
					index3 = index2 - 1
					self.tabla_seccion_grupos_proyectos.removeRow(index3)
					index2 = index2 - 1
			self.cargarDatosProyectos()

	def primerRegistro(self,event):
		index = int(self.txtContadorPeriodo.text())
		if index == 0:
			QMessageBox.information(self, "Principio de Archivo", "Archivo no tiene información", QMessageBox.Ok)
		elif index == 1:
			QMessageBox.information(self, "Principio de Archivo", "Usted ya se encuentra en el primer registro", QMessageBox.Ok)
		else:
			self.txtContadorPeriodo.setText("1")
			self.llenarPantPeriodo(0)
			self.cargarDatosProyectos()
			if self.optRegular.isChecked():
				self.txtLimiteEstudiantes.setText('5')
			else:
				self.txtLimiteEstudiantes.setText('3')

	def registroAnterior(self, event):
		ultimoRegistro = int(self.txtTotalRPeriodo.text())
		index = int(self.txtContadorPeriodo.text())
		if index == 1:
			QMessageBox.information(self, "Principio de Archivo", "Usted ya se encuentra en el primer registro...", QMessageBox.Ok)
		elif index == 0:
			QMessageBox.information(self, "Principio de Archivo", "El archivo no tiene registros", QMessageBox.Ok)
		else:
			index = index - 2
			self.txtContadorPeriodo.setText(str(index + 1))
			self.llenarPantPeriodo(index)
			self.cargarDatosProyectos()
			if self.optRegular.isChecked():
				self.txtLimiteEstudiantes.setText('5')
			else:
				self.txtLimiteEstudiantes.setText('3')

	def registroSiguiente(self,event):
		index = int(self.txtContadorPeriodo.text())
		ultimoRegistro = int(self.txtTotalRPeriodo.text())
		if ultimoRegistro==0:
			QMessageBox.information(self, "Fin de Archivo", "El archivo no tiene registros...", QMessageBox.Ok)
		elif index == ultimoRegistro:
			QMessageBox.information(self, "Fin de Archivo", "Usted ya se encuentra en el último registro...", QMessageBox.Ok)
		else:
			self.txtContadorPeriodo.setText(str(index + 1))
			self.llenarPantPeriodo(index)
			self.cargarDatosProyectos()
			if self.optRegular.isChecked():
				self.txtLimiteEstudiantes.setText('5')
			else:
				self.txtLimiteEstudiantes.setText('3')

	def ultimoRegistro(self,event):
		index = int(self.txtContadorPeriodo.text())
		lv_ultimoRegistro = int(self.txtTotalRPeriodo.text())
		if lv_ultimoRegistro == 0:
			QMessageBox.information(self, "Fin de Archivo", "El archivo no tiene registros...", QMessageBox.Ok)
		elif lv_ultimoRegistro == index:
			QMessageBox.information(self, "Fin de Archivo", "Usted ya se encuentra en el último registro...", QMessageBox.Ok)
		else:
			index = int(self.txtTotalRPeriodo.text()) - 1
			self.txtContadorPeriodo.setText(self.txtTotalRPeriodo.text()) 
			self.llenarPantPeriodo(index)
			self.cargarDatosProyectos()
			if self.optRegular.isChecked():
				self.txtLimiteEstudiantes.setText('5')
			else:
				self.txtLimiteEstudiantes.setText('3')

	def BuscarTablaPeriodo(self):
		self.cargarTablaListaPeriodos()
		self.grpListaSecciones.show()
		
	def cargarDatosProyectos(self):
		self.bdvacia = 0
		if self.txtIdSeccion.text() == "":
			self.IdSeccion = 0
		else:
			self.IdSeccion = int(self.txtIdSeccion.text())
		self.bdvacia = 0
		self.tabla_seccion_grupos_proyectos.clearSelection()
		self.tabla_seccion_grupos_proyectos.clearContents()
		index2 = self.tabla_seccion_grupos_proyectos.rowCount()
		index3 = 0
		while index2 > 0:
			index3 = index2 - 1
			self.tabla_seccion_grupos_proyectos.removeRow(index3)
			index2 = index2 - 1

		if self.TotalRegPeriodo > 0:
			self.TotalGeneralProyectos = 0
			cursor_RegProyectos = ("""SELECT proy.id_proyecto, proy.codigo_proyecto, proy.FK_id_seccion, sec.FK_id_trayecto,
				proy.numero_grupo_proyecto, met.descripcion AS metodo, tdes.tipo_desarrollo, proy.titulo_proyecto, 
				proy.nombre_informe_codificado, proy.nombre_desarrollo_codificado, proy.nombre_manual_codificado,
				met.id_metodo, tdes.id_tipo_desarrollo
			FROM proyectos AS proy INNER JOIN metodologia AS met ON proy.fk_id_metodo = met.id_metodo
			INNER JOIN tipo_de_desarrollo AS tdes ON proy.fk_id_tipo_desarrollo = tdes.id_tipo_desarrollo
			INNER JOIN secciones AS sec ON proy.FK_id_seccion = sec.id_seccion
			WHERE proy.FK_id_seccion = '%i'
			ORDER BY proy.codigo_proyecto""" % self.IdSeccion)
			self.cursor.execute(cursor_RegProyectos)
			self.RegistroProyectos = []
			rows = []
			index = 0
			for rows in self.cursor:
				if rows==[]:
					self.bdvacia = 1
				else:
					self.tabla_seccion_grupos_proyectos.insertRow(index)
					IDProyecto = str(rows[0])
					CodigoProyecto = str(rows[1])
					IDSeccion = str(rows[2])
					IDPeriodo = str(rows[3])
					GrupoProyecto = str(rows[4])
					Metodologia = str(rows[5])
					TipoDesarrollo = str(rows[6])
					TituloProyecto = str(rows[7])
					NombreInforme = str(rows[8])
					NombreDesarrollo = str(rows[9])
					NombreManual = str(rows[10])
					IdMetodo = str(rows[11])
					IdTipoDesarrollo = str(rows[12])
					self.tabla_seccion_grupos_proyectos.setItem(index, 0, QTableWidgetItem(str(index2 + 1)))
					self.tabla_seccion_grupos_proyectos.setItem(index, 1, QTableWidgetItem(CodigoProyecto))
					self.tabla_seccion_grupos_proyectos.setItem(index, 2, QTableWidgetItem(GrupoProyecto))
					self.tabla_seccion_grupos_proyectos.setItem(index, 3, QTableWidgetItem(TituloProyecto))
					self.tabla_seccion_grupos_proyectos.setItem(index, 4, QTableWidgetItem(Metodologia))
					self.tabla_seccion_grupos_proyectos.setItem(index, 5, QTableWidgetItem(TipoDesarrollo))
					self.tabla_seccion_grupos_proyectos.setItem(index, 6, QTableWidgetItem(NombreInforme))
					self.tabla_seccion_grupos_proyectos.setItem(index, 7, QTableWidgetItem(NombreDesarrollo))
					self.tabla_seccion_grupos_proyectos.setItem(index, 8, QTableWidgetItem(NombreManual))
					self.tabla_seccion_grupos_proyectos.setItem(index, 9, QTableWidgetItem(IDProyecto))
					self.tabla_seccion_grupos_proyectos.setItem(index, 10, QTableWidgetItem(IDPeriodo))
					self.tabla_seccion_grupos_proyectos.setItem(index, 11, QTableWidgetItem(IDSeccion))
					self.tabla_seccion_grupos_proyectos.setItem(index, 12, QTableWidgetItem(IdMetodo))
					self.tabla_seccion_grupos_proyectos.setItem(index, 13, QTableWidgetItem(IdTipoDesarrollo))
					index = index + 1
			self.TotalGeneralProyectos = index
		else:
			self.TotalGeneralProyectos = 0

	def regresoPrincipal(self):
		self.grpListaSecciones.hide()

	def SeleccionyCerrar(self):
		self.IdSeccion = int(self.txtIdSeccionLista.text())
		if self.IdSeccion == 0:
			respuesta=QMessageBox.warning(self,"Adventencia", "No ha seleccionado ningún registro de la tabla, Seguro que desea retornar?", QMessageBox.Yes | QMessageBox.No)
			if respuesta == QMessageBox.Yes:
				self.txtIdPeriodoLista.setText('0')
				self.regresoPrincipal()
		else:
			self.ProxRegPeriodo = int(self.TotalRegPeriodo)
			if self.ProxRegPeriodo > 0:
				self.localizarIdPeriodo()
				self.retornarValores()
			self.regresoPrincipal()

	def localizarIdPeriodo(self):
		index=0
		self.encontrado = 0
		while index < self.ProxRegPeriodo:
			if self.RegistroPeriodos[index][6]==str(self.IdSeccion):
				self.encontrado = 1
				break;
			index = index + 1
		if self.encontrado == 1:
			self.txtContadorPeriodo.setText(str(index + 1))
			self.RegActualPeriodo = self.txtContadorPeriodo.text()
		else:
			self.txtContadorPeriodo.setText('1')

	def actContadorActualPeriodos(self):
		row = self.tabla_periodos.currentRow()
		self.IdPeriodo = int(self.tabla_periodos.item(row, 0).text())
		self.IdSeccion = int(self.tabla_periodos.item(row, 6).text())
		self.txtIdSeccionLista.setText(str(self.IdSeccion))

		#row = self.tabla_periodos.currentRow() + 1
		self.RegActualListaPeriodo.setText(str(row+1)) 



	def cargarTablaListaPeriodos(self):
		self.tabla_periodos.clearSelection()
		self.tabla_periodos.clearContents()
		index2 = self.tabla_periodos.rowCount()
		index3 = 0
		while index2 > 0:
			index3 = index2 - 1
			self.tabla_periodos.removeRow(index3)
			index2 = index2 - 1

		index3 = int(self.txtTotalRPeriodo.text())
		index = 0
		self.tabla_periodos.setRowCount(0)
		while index < index3:
			self.tabla_periodos.insertRow(index)
			lv_idPeriodo = self.RegistroPeriodos[index][0]
			lv_anoPeriodo = self.RegistroPeriodos[index][1]
			lv_trayecto = self.RegistroPeriodos[index][2]
			lv_seccion = self.RegistroPeriodos[index][3]
			lv_tipotrayecto = self.RegistroPeriodos[index][4]
			lv_anoprosecucion = self.RegistroPeriodos[index][5]
			lv_id_seccion = self.RegistroPeriodos[index][6]
			self.tabla_periodos.setItem(index, 0, QTableWidgetItem(lv_idPeriodo))
			self.tabla_periodos.setItem(index, 1, QTableWidgetItem(lv_anoPeriodo))
			self.tabla_periodos.setItem(index, 2, QTableWidgetItem(lv_trayecto))
			self.tabla_periodos.setItem(index, 3, QTableWidgetItem(lv_seccion))
			self.tabla_periodos.setItem(index, 4, QTableWidgetItem(lv_tipotrayecto))
			self.tabla_periodos.setItem(index, 5, QTableWidgetItem(lv_anoprosecucion))
			self.tabla_periodos.setItem(index, 6, QTableWidgetItem(lv_id_seccion))
			index += 1
		self.TotalReg.setText(str(index))

	def buscarDato(self):
		lv_texto = self.txtFiltro.text().upper()
		if self.optAno.isChecked()== True:
			validar = re.match('^[0-9\s]+$', lv_texto, re.I)
			columna = 1
		elif self.optTrayecto.isChecked()==True:	
			validar = re.match('^[a-zA-Z\s]+$', lv_texto, re.I)
			columna = 2
		else:
			validar = re.match('^[a-zA-Z0-9\s]+$', lv_texto, re.I)
			columna = 3
		index = self.tabla_periodos.rowCount()
		fila=0
		encontrar = 0
		while fila < index:
			lv_busqueda = self.tabla_periodos.item(fila,columna).text()
			if lv_texto in lv_busqueda:
				encontrar = 1
				break;
			fila = fila + 1
		if encontrar == 1:
			fila_inicial = self.tabla_periodos.rowCount()
			posicion = self.tabla_periodos.item(fila_inicial, columna)
			self.tabla_periodos.scrollToItem(posicion)
			self.tabla_periodos.setCurrentCell(fila_inicial, columna)
			posicion = self.tabla_periodos.item(fila, columna)
			self.tabla_periodos.scrollToItem(posicion)
			self.tabla_periodos.setCurrentCell(fila, columna)
			self.txtIdSeccionLista.setText(self.tabla_periodos.item(fila, 6).text().replace(" ", ""))
			return True
		else:
			return False

	def ordenarTabla(self):
		if self.optAno.isChecked():
			self.tabla_periodos.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)
		elif self.optTrayecto.isChecked():
			self.tabla_periodos.horizontalHeader().setSortIndicator(2, Qt.AscendingOrder)
		else:
			self.tabla_periodos.horizontalHeader().setSortIndicator(3, Qt.AscendingOrder)

#---------------------------------------------#
# Rutinas de control de ventana de proyectos  #
#---------------------------------------------#

	def AccederConsultaProyecto(self):
		self.bdnuevo = 0
		self.bdedita = 0
		validar_vacio = self.tabla_seccion_grupos_proyectos.rowCount()
		if validar_vacio > 0:
			self.nuevoproyecto = 0
			self.IdSeccion = int(self.txtIdSeccion.text())
			row=self.tabla_seccion_grupos_proyectos.currentRow()
			if row == -1:
				self.proyectoActual = int(self.tabla_seccion_grupos_proyectos.item(0, 0).text()) - 1
				self.txtContadorProyectos.setText('1')
			else:
				self.proyectoActual = int(self.tabla_seccion_grupos_proyectos.item(row, 0).text()) - 1
			self.desactivarCamposProyecto()
			self.AbrirProyectos()
		else:
			QMessageBox.warning(self, "Archivo vacio", "Esta seccion no tiene proyectos registrados", QMessageBox.Ok)

	def AccederEditarProyecto(self):
		self.bdnuevo = 0
		self.bdedita = 0
		self.nuevoproyecto = 0
		self.IdSeccion = int(self.txtIdSeccion.text())
		row=self.tabla_seccion_grupos_proyectos.currentRow()
		if row != -1:
			self.proyectoActual = int(self.tabla_seccion_grupos_proyectos.item(row, 0).text()) - 1
			self.desactivarCamposProyecto()
			self.AbrirProyectos()
		else:
			self.proyectoActual = 0


	def desactivarCamposProyecto(self):
		self.btnMetodologia.setEnabled(False)
		self.btnTipoDesarrollo.setEnabled(False)
		self.txtTituloProyecto.setEnabled(False)
		self.btnMetodologia.setEnabled(False)
		self.btnTipoDesarrollo.setEnabled(False)
		self.cmbGrupoDesarrollo.setEnabled(False)
		self.cmbMetotologia.setEnabled(False)
		self.cmbTipoDesarrollo.setEnabled(False)
		self.btnAsignarTutor.setEnabled(True)
		self.btnAgregarIntegrante.setEnabled(True)
		if self.tablaIntegrantes.rowCount() > 0:
			self.btnRemoverIntegrante.setEnabled(False)
		else:
			self.btnRemoverIntegrante.setEnabled(True)
		if self.tablaTutores.rowCount() > 0:
			self.btnRemoverTutor.setEnabled(False)
		else:
			self.btnRemoverTutor.setEnabled(True)
		self.btnListaEstudiante.setEnabled(True)
		self.txtCedulaEstudiante.setEnabled(True)
		self.btnListaTutores.setEnabled(True)
		self.txtCedulaTutor.setEnabled(True)	
		self.TotalProyectosPorPeriodos = self.tabla_seccion_grupos_proyectos.rowCount()
		if self.TotalProyectosPorPeriodos > 0:
			self.btnSubeInforme.setEnabled(True)
			self.btnSubeDesarrollo.setEnabled(True)
			self.btnSubeManual.setEnabled(True)
			self.btnEditarProyecto.setEnabled(True)
			self.btnEliminarProyecto.setEnabled(True)
		else:
			self.btnSubeInforme.setEnabled(False)
			self.btnSubeDesarrollo.setEnabled(False)
			self.btnSubeManual.setEnabled(False)
			self.btnEditarProyecto.setEnabled(False)
			self.btnEliminarProyecto.setEnabled(False)
		self.btnPrimerProyecto.setEnabled(True)
		self.btnProyectoAnterior.setEnabled(True)
		self.btnProyectoSiguiente.setEnabled(True)
		self.btnUltimoProyecto.setEnabled(True)
		self.btnGuardarProyecto.hide()
		self.btnDescartarProyecto.hide()
		self.btnNuevoProyecto.show()
		self.btnEditarProyecto.show()
		self.btnEliminarProyecto.show()
		self.btnCerrarProyectos.show()

	def AbrirProyectos(self):
		#-----------------------------------
		# Iniciar encabezado del proyecto
		self.txtAnoPeriodo_2.setText(self.txtAnoPeriodo.text())
		self.txtAnoProsecucion_2.setText(self.txtAnoProsecucion.text())
		#self.txtTutor_2.setText(self.txtTutor.text())
		self.cmbTrayecto_2.setCurrentIndex(self.cmbTrayecto.currentIndex())
		self.cmbSeccion_2.setCurrentIndex(self.cmbSeccion.currentIndex())
		self.txtTotalProyectos.setText(str(self.TotalProyectosPorPeriodos))
		if self.TotalProyectosPorPeriodos > 0:
			self.btnEliminarProyecto.setEnabled(True)
			self.btnEditarProyecto.setEnabled(True)
		else:
			self.btnEliminarProyecto.setEnabled(False)
			self.btnEditarProyecto.setEnabled(False)

		if self.optRegular.isChecked():
			self.optRegular_2.setChecked(True)
		else:
			self.optProsecucion_2.setChecked(True)
		if self.nuevoproyecto == 1:
			self.nuevoProyecto()
		else:
			if self.tabla_seccion_grupos_proyectos.rowCount() > 0:
				self.proyectoActual = self.tabla_seccion_grupos_proyectos.currentRow()
				self.txtContadorProyectos.setText(str(self.proyectoActual + 1))
				if self.proyectoActual == -1:
					self.proyectoActual = 0
				self.llenarPantProyecto(self.proyectoActual)
			else:
				self.limpiarProyecto()
				self.txtContadorProyectos.setText('0')

		#--------------------------
		# Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(0, False)
		#Habilitar Tabs Registro de Proyectos
		self.tabWidget.setTabEnabled(1, True)
		self.tabWidget.setCurrentIndex(1)



	def llenarPantProyecto(self,nregistro):
		index = nregistro
		self.txtIdProyecto.setText(self.tabla_seccion_grupos_proyectos.item(index, 9).text())
		self.txtCodigoProyecto.setText(self.tabla_seccion_grupos_proyectos.item(index, 1).text())
		self.txtTituloProyecto.setText(self.tabla_seccion_grupos_proyectos.item(index, 3).text())
		self.txtNInformeCod.setText(self.tabla_seccion_grupos_proyectos.item(index, 6).text())
		self.txtNDesarrolloCod.setText(self.tabla_seccion_grupos_proyectos.item(index, 7).text())
		self.txtNManualCod.setText(self.tabla_seccion_grupos_proyectos.item(index, 8).text())
		self.cmbGrupoDesarrollo.setCurrentIndex(int(self.tabla_seccion_grupos_proyectos.item(index, 2).text())-1)
		self.btnMetodologia.setText(self.tabla_seccion_grupos_proyectos.item(index, 4).text())
		self.btnTipoDesarrollo.setText(self.tabla_seccion_grupos_proyectos.item(index, 5).text())
		self.txtIdSeccion.setText(self.tabla_seccion_grupos_proyectos.item(index, 11).text())
		self.txtIdMetodo.setText(self.tabla_seccion_grupos_proyectos.item(index, 12).text())
		self.txtIdTipoDesarrollo.setText(self.tabla_seccion_grupos_proyectos.item(index, 13).text())
		if self.tabla_seccion_grupos_proyectos.item(index, 6).text() == "None":
			self.txtEstadoInforme.setText('Pendiente')
			self.txtEstadoInforme.setStyleSheet("border: 1px solid red; color: red;")
		else:
			self.txtEstadoInforme.setText('Entregado')
			self.txtEstadoInforme.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")

		if self.tabla_seccion_grupos_proyectos.item(index, 7).text() == "None":
			self.txtEstadoDesarrollo.setText('Pendiente')
			self.txtEstadoDesarrollo.setStyleSheet("border: 1px solid red; color: red;")
			if self.cmbTrayecto.currentText() == 'TRAYECTO I' or self.cmbTrayecto.currentText() == 'TRAYECTO II':
				self.txtEstadoDesarrollo.setText('No Requerido')
				self.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
		else:
			self.txtEstadoDesarrollo.setText('Entregado')
			self.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")

		if self.tabla_seccion_grupos_proyectos.item(index, 8).text() == "None":
			self.txtEstadoManual.setText('Pendiente')
			self.txtEstadoManual.setStyleSheet("border: 1px solid red; color: red;")
			if self.cmbTrayecto.currentText() == 'TRAYECTO I' or self.cmbTrayecto.currentText() == 'TRAYECTO II':
				self.txtEstadoManual.setText('No Requerido')
				self.txtEstadoManual.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
		else:
			self.txtEstadoManual.setText('Entregado')
			self.txtEstadoManual.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
		if self.TotalIntegrantes > 0:
			self.txtContadorProyectos.setText(str(index + 1))
			self.tablaIntegrantes.clearSelection()
			self.tablaIntegrantes.clearContents()
			index2 = self.TotalIntegrantes
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.tablaIntegrantes.removeRow(index3)
				index2 = index2 - 1
		if self.bdnuevo == 0:
			self.btnAgregarIntegrante.setEnabled(True)
			self.txtCedulaEstudiante.setEnabled(True)
			if self.TotalIntegrantes > 0:
				self.btnRemoverIntegrante.setEnabled(True)
			else:
				self.btnRemoverIntegrante.setEnabled(False)
		else:
			self.btnAgregarIntegrante.setEnabled(False)
			self.txtCedulaEstudiante.setEnabled(False)
			self.btnRemoverIntegrante.setEnabled(False)
		self.LlenarTablaIntegrantes()
		lvTotalProyectos = int(self.txtTotalProyectos.text())
		if lvTotalProyectos > 0:
			self.btnAgregarIntegrante.setEnabled(True)
			self.btnRemoverIntegrante.setEnabled(True)
			self.txtCedulaEstudiante.setEnabled(True)
		else:
			self.btnAgregarIntegrante.setEnabled(False)
			self.btnRemoverIntegrante.setEnabled(False)
			self.txtCedulaEstudiante.setEnabled(False)

	def LlenarTablaIntegrantes(self):
		self.vaciarTablasEstudiantesTutores()
		if self.bdnuevo == 0:
			IDProyecto = int(self.txtIdProyecto.text())
			consulta_estudiantes = ("""SELECT est.cedula_estudiante, est.nombre_estudiante, est.apellido_estudiante, est.telefono_estudiante 
			 FROM estudiante AS est INNER JOIN elaboran AS ela ON est.cedula_estudiante = ela.FK_cedula_estudiante
			 INNER JOIN proyectos AS proy on proy.id_proyecto = ela.FK_id_proyecto
			 WHERE proy.id_proyecto = '%i'
			 ORDER BY est.cedula_estudiante""" % (int(IDProyecto)))
			self.cursor.execute(consulta_estudiantes)
			index = 0
			self.tablaIntegrantes.setRowCount(0)
			rows = []
			index = 0
			for rows in self.cursor:
				if rows!=[]:
					self.tablaIntegrantes.insertRow(index)
					cedulaIntegrante = str(rows[0])
					NombreIntegrante = str(rows[1])
					ApellidoIntegrante = str(rows[2])
					TelefonoIntegrante = str(rows[3])
					self.tablaIntegrantes.setItem(index, 0, QTableWidgetItem(cedulaIntegrante))
					self.tablaIntegrantes.setItem(index, 1, QTableWidgetItem(NombreIntegrante))
					self.tablaIntegrantes.setItem(index, 2, QTableWidgetItem(ApellidoIntegrante))
					self.tablaIntegrantes.setItem(index, 3, QTableWidgetItem(TelefonoIntegrante))
				index = index + 1
			consulta_tutores = ("""SELECT tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, esa.rol 
			 FROM tutores AS tut INNER JOIN es_asesorado AS esa ON tut.cedula_tutor = esa.FK_cedula_tutor
			 INNER JOIN proyectos AS proy on proy.id_proyecto = esa.FK_id_proyecto
			 WHERE proy.id_proyecto = '%i'
			 ORDER BY tut.cedula_tutor""" % (int(IDProyecto)))
			self.cursor.execute(consulta_tutores)
			index = 0
			self.tablaTutores.setRowCount(0)
			rows = []
			index = 0
			for rows in self.cursor:
				if rows!=[]:
					self.tablaTutores.insertRow(index)
					cedulaTutor = str(rows[0])
					NombreTutor = str(rows[1])
					ApellidoTutor = str(rows[2])
					TipoTutor = str(rows[3])
					self.tablaTutores.setItem(index, 0, QTableWidgetItem(cedulaTutor))
					self.tablaTutores.setItem(index, 1, QTableWidgetItem(NombreTutor))
					self.tablaTutores.setItem(index, 2, QTableWidgetItem(ApellidoTutor))
					self.tablaTutores.setItem(index, 3, QTableWidgetItem(TipoTutor))
				index = index + 1
			self.TotalIntegrantes = self.tablaIntegrantes.rowCount()
			self.TotalTutores = self.tablaTutores.rowCount()
			self.btnAgregarIntegrante.setEnabled(True)
			if self.TotalIntegrantes > 0:
				self.btnRemoverIntegrante.setEnabled(True)
			else:
				self.btnRemoverIntegrante.setEnabled(False)

	def nuevoProyecto(self):
		self.vaciarTablasEstudiantesTutores()
		self.TotalProyectosPorPeriodos = self.tabla_seccion_grupos_proyectos.rowCount()
		if self.TotalProyectosPorPeriodos > 0:
			if self.txtContadorProyectos.text() == '0':
				self.proyectoActual = 0
			else:
				self.proyectoActual = int(self.txtContadorProyectos.text()) - 1
		else:
			self.proyectoActual = 0
		self.txtContadorProyectos.setText(str(self.TotalProyectosPorPeriodos + 1))
		self.bdnuevo = 1
		self.limpiarProyecto()
		self.CodificarProyecto()
		self.activarCamposProyecto()
		self.txtCodigoProyecto.setText(self.codigoProyecto)
		self.txtTituloProyecto.setFocus()

	def activarCamposProyecto(self):
		self.txtTituloProyecto.setEnabled(True)
		self.cmbGrupoDesarrollo.setEnabled(True)
		self.btnMetodologia.setEnabled(True)
		self.btnTipoDesarrollo.setEnabled(True)
#		self.cmbMetotologia.setEnabled(True)
#		self.cmbTipoDesarrollo.setEnabled(True)
		self.btnSubeInforme.setEnabled(False)
		self.btnSubeDesarrollo.setEnabled(False)
		self.btnSubeManual.setEnabled(False)
		self.btnPrimerProyecto.setEnabled(False)
		self.btnProyectoAnterior.setEnabled(False)
		self.btnProyectoSiguiente.setEnabled(False)
		self.btnUltimoProyecto.setEnabled(False)
		self.btnGuardarProyecto.show()
		self.btnDescartarProyecto.show()
		self.btnNuevoProyecto.hide()
		self.btnEditarProyecto.hide()
		self.btnEliminarProyecto.hide()
		self.btnCerrarProyectos.hide()
		self.btnAgregarIntegrante.setEnabled(False)
		self.btnRemoverIntegrante.setEnabled(False)
		self.txtCedulaEstudiante.setEnabled(False)
		self.btnAsignarTutor.setEnabled(False)
		self.btnRemoverTutor.setEnabled(False)
		self.txtCedulaTutor.setEnabled(False)

	def CodificarProyecto(self):
		lv_ano = self.txtAnoPeriodo.text()
		lv_trayecto = "T0" + str(self.cmbTrayecto.currentIndex() + 1)
		lv_seccion = self.cmbSeccion.currentText()
		lv_grupo = "G" + self.cmbGrupoDesarrollo.currentText()
		if self.optRegular.isChecked():
			lv_tipo = 'R'
			lv_anoprosecucion = '0000'
		else:
		 	lv_tipo = 'P'
		 	lv_anoprosecucion = self.txtAnoProsecucion.text()
		self.codigoProyecto = 'PR-'+lv_ano+'-'+lv_trayecto+'-'+lv_seccion+'-'+lv_tipo+'-'+lv_anoprosecucion+'-'+lv_grupo
		self.txtCodigoProyecto.setText(self.codigoProyecto)

	def limpiarProyecto(self):
		self.txtTituloProyecto.setText('')
		self.txtNInformeCod.setText('')
		self.txtNDesarrolloCod.setText('')
		self.txtNManualCod.setText('')
		self.cmbGrupoDesarrollo.setCurrentIndex(0)
		self.CodificarProyecto()
		self.btnTipoDesarrollo.setText('Seleccionar Tipo de Desarrollo')
		self.btnMetodologia.setText('Seleccionar Metodologia')
		self.txtCodigoProyecto.setText(self.codigoProyecto)
		self.txtEstadoInforme.setText('Pendiente...')
		self.txtEstadoInforme.setStyleSheet("border: 1px solid red; color: red;")
		if self.cmbTrayecto.currentText() == 'TRAYECTO I' or self.cmbTrayecto.currentText() == 'TRAYECTO II':
			self.txtEstadoDesarrollo.setText('No Requerido')
			self.txtEstadoManual.setText('No Requerido')
			self.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
			self.txtEstadoManual.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
		else:
			self.txtEstadoDesarrollo.setText('Pendiente...')
			self.txtEstadoManual.setText('Pendiente...')
			self.txtEstadoDesarrollo.setStyleSheet("border: 1px solid red; color: red;")
			self.txtEstadoManual.setStyleSheet("border: 1px solid red; color: red;")
		self.vaciarTablasEstudiantesTutores()

	def vaciarTablasEstudiantesTutores(self):
		self.TotalIntegrantes = self.tablaIntegrantes.rowCount()
		if self.TotalIntegrantes > 0:
			self.tablaIntegrantes.clearSelection()
			self.tablaIntegrantes.clearContents()
			index2 = self.TotalIntegrantes
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.tablaIntegrantes.removeRow(index3)
				index2 = index2 - 1
		self.TotalTutores = self.tablaTutores.rowCount()
		if self.TotalTutores > 0:
			self.tablaTutores.clearSelection()
			self.tablaTutores.clearContents()
			index2 = self.TotalTutores
			index3 = 0
			while index2 > 0:
				index3 = index2 - 1
				self.tablaTutores.removeRow(index3)
				index2 = index2 - 1

	def descartarProyecto(self):
		self.txtContadorProyectos.setText(str(self.proyectoActual+1))
		if self.TotalProyectosPorPeriodos > 0:
			self.llenarPantProyecto(self.proyectoActual)
		else:
			self.limpiarProyecto()
		self.desactivarCamposProyecto()
		self.bdedita = 0
		self.bdnuevo = 0
		self.nuevoproyecto = 0

	def editarProyecto(self):
		self.bdedita = 1
		row=int(self.txtContadorProyectos.text()) - 1
		self.proyectoActual = int(self.tabla_seccion_grupos_proyectos.item(row, 0).text()) - 1
		self.IdPeriodo = int(self.txtIdPeriodo.text())
		self.IdSeccion = int(self.txtIdSeccion.text())
		self.IdProyecto = int(self.tabla_seccion_grupos_proyectos.item(row, 9).text())
		self.GrupoDesarrolloOriginal = self.cmbGrupoDesarrollo.currentText()
		self.proyectoActual = int(self.txtContadorProyectos.text()) - 1
		self.nuevoproyecto = 0
		self.activarCamposProyecto()
		if self.txtEstadoInforme.text() == 'Entregado' or self.txtEstadoDesarrollo.text() == 'Entregado' or self.txtEstadoManual.text() == 'Entregado':
			self.cmbGrupoDesarrollo.setEnabled(False)
		self.txtTituloProyecto.setFocus()

	def guardarProyecto(self):
		self.encontrar = 0
		self.CodificarProyecto()
		lv_id_seccion = int(self.txtIdSeccion.text())
		lvGrupoOriginal = int(self.GrupoDesarrolloOriginal)
		lvTituloProyecto = self.txtTituloProyecto.text().upper()
		self.txtTituloProyecto.setText(lvTituloProyecto)
		lvGrupoDesarrollo = int(self.cmbGrupoDesarrollo.currentText())
		lvIdTipoDesarrollo = int(self.txtIdTipoDesarrollo.text())
		lvIdMetodo = int(self.txtIdMetodo.text())

		if self.bdnuevo == 1:
			lvGrupoOriginal = '00'
			#self.hoy = datetime.today()
			#self.fechareg = self.hoy.strftime(self.formato_fecha)
			datosProyecto = """INSERT INTO proyectos (
			codigo_proyecto, numero_grupo_proyecto, titulo_proyecto, nombre_informe_codificado, 
			nombre_desarrollo_codificado, nombre_manual_codificado, FK_id_seccion, 
			FK_id_metodo, FK_id_tipo_desarrollo) 
			VALUES ('%s', '%i', '%s', NULL, NULL, NULL, '%i','%i','%i');"""	% (self.codigoProyecto, lvGrupoDesarrollo, lvTituloProyecto, lv_id_seccion, lvIdMetodo, lvIdTipoDesarrollo)
			if self.TotalProyectosPorPeriodos > 0:
				index = 0
				while index < self.TotalProyectosPorPeriodos:
					if self.tabla_seccion_grupos_proyectos.item(index, 2).text() == str(int(self.cmbGrupoDesarrollo.currentText())):
						self.encontrar = 1
						break;
					index = index + 1
		else:
			self.IdProyecto = int(self.txtIdProyecto.text())
			self.encontrar = 0
#			self.hoy = datetime.today()
#			self.fechareg = self.hoy.strftime(self.formato_fecha)
			self.txtCodigoProyecto.setText(self.codigoProyecto)
			datosProyecto = """UPDATE proyectos SET codigo_proyecto = '%s', numero_grupo_proyecto = '%i', 
			titulo_proyecto = '%s',	FK_id_seccion = '%i', FK_id_metodo = '%i', FK_id_tipo_desarrollo = '%i' 
			WHERE id_proyecto = '%i'""" % (self.codigoProyecto, lvGrupoDesarrollo, lvTituloProyecto,  lv_id_seccion, lvIdMetodo, lvIdTipoDesarrollo, self.IdProyecto)
			if lvGrupoDesarrollo == lvGrupoOriginal:
				self.encontrar = 0
			else:
				if self.TotalProyectosPorPeriodos > 0:
					index = 0
					while index < self.TotalProyectosPorPeriodos:
						if self.tabla_seccion_grupos_proyectos.item(index, 2).text() == str(int(self.cmbGrupoDesarrollo.currentText())):
							self.encontrar = 1
							break;
						index = index + 1
		if self.encontrar == 1:
			QMessageBox.warning(self,"Error..", "Ya existe otro proyecto registrado con el grupo No. " + self.cmbGrupoDesarrollo.currentText() + " No se puede procesar", QMessageBox.Ok)
		else:
			self.cursor.execute(datosProyecto)

			if self.bdnuevo == 1:
				self.TotalIntegrantes=0
			self.bdedita = 0
			self.bdnuevo = 0
			if self.TotalProyectosPorPeriodos > 0:
				self.tabla_seccion_grupos_proyectos.clearSelection()
				self.tabla_seccion_grupos_proyectos.clearContents()
				index2 = self.TotalProyectosPorPeriodos
				index3 = 0
				while index2 > 0:
					index3 = index2 - 1
					self.tabla_seccion_grupos_proyectos.removeRow(index3)
					index2 = index2 - 1
			self.cargarDatosProyectos()
			index = 0
			index2 = self.tabla_seccion_grupos_proyectos.rowCount()
			index = 0
			while index < index2:
				if int(self.tabla_seccion_grupos_proyectos.item(index, 2).text()) == int(self.cmbGrupoDesarrollo.currentText()):
					break;
				index = index + 1
			self.llenarPantProyecto(index)
			QMessageBox.information(self, "Base de Datos", "Registro guardado satisfactoriamente", QMessageBox.Ok)
			self.desactivarCamposProyecto()
			self.btnAgregarIntegrante.setEnabled(True)
			if self.tablaIntegrantes.rowCount() > 0:
				self.btnRemoverIntegrante.setEnabled(True)
			else:
				self.btnRemoverIntegrante.setEnabled(False)
			self.txtCedulaEstudiante.setEnabled(True)

	def eliminarProyecto(self):
		lv_IdProyecto = int(self.txtIdProyecto.text())
		self.elimina = 1
#		if self.txtEstadoInforme.text() == "Entregado" or self.txtEstadoDesarrollo.text() == "Entregado" or self.txtEstadoManual.text() == "Entregado":
#			QMessageBox.warning(self,"Error..", "No puede eliminar proyectos entregados por estudiantes..", QMessageBox.Ok)
#			self.elimina = 0
#		elif self.TotalIntegrantes > 0: 
		if self.TotalIntegrantes > 0: 
			respuesta = QMessageBox.warning(self,"Sistema", "Este proyecto tiene estudiantes registrados, desea eliminar el proyecto y sus integrantes?", QMessageBox.Yes | QMessageBox.No)
			if respuesta == QMessageBox.Yes:
				borrar_integrantes = "DELETE FROM integrantes WHERE FK_id_proyecto = '%i'" % lv_IdProyecto
				self.cursor.execute(borrar_integrantes)
			else:
				self.elimina = 0
		if self.elimina == 1:
			elimina_proyecto = "DELETE FROM proyectos WHERE id_proyecto = '%i'" % lv_IdProyecto
			self.cursor.execute(elimina_proyecto)
			totalproyectos = int(self.txtTotalProyectos.text()) - 1
			self.txtTotalProyectos.setText(str(totalproyectos))
			QMessageBox.information(self,"Base de Datos", "Proyecto ha sido eliminado...", QMessageBox.Ok)
			self.tabla_seccion_grupos_proyectos.clearSelection()
			self.tabla_seccion_grupos_proyectos.clearContents()
			index2 = self.TotalProyectosPorPeriodos
			while index2 > 0:
				index3 = index2 - 1
				self.tabla_seccion_grupos_proyectos.removeRow(index3)
				index2 = index2 - 1
			self.cargarDatosProyectos()
			if self.TotalProyectosPorPeriodos > 1:
				self.txtContadorProyectos.setText('1')
				self.llenarPantProyecto(0)
			else:
				self.txtContadorProyectos.setText('0')
				self.txtTotalProyectos.setText('0')
				self.limpiarProyecto()
			self.desactivarCamposProyecto()
			
	def primerProyecto(self):
		index = int(self.txtContadorProyectos.text())
		if index == 0:
			QMessageBox.information(self, "Principio de Archivo", "Archivo no tiene información", QMessageBox.Ok)
		elif index == 1:
			QMessageBox.information(self, "Principio de Archivo", "Usted ya se encuentra en el primer registro", QMessageBox.Ok)
		else:
			self.txtContadorProyectos.setText("1")
			self.llenarPantProyecto(0)

	def proyectoAnterior(self):
		ultimoRegistro = int(self.txtTotalProyectos.text())
		index = int(self.txtContadorProyectos.text())
		if index == 1:
			QMessageBox.information(self, "Principio de Archivo", "Usted ya se encuentra en el primer registro...", QMessageBox.Ok)
		elif index == 0:
			QMessageBox.information(self, "Principio de Archivo", "El archivo no tiene registros", QMessageBox.Ok)
		else:
			index = index - 2
			self.txtContadorProyectos.setText(str(index + 1))
			self.llenarPantProyecto(index)


	def proyectoSiguiente(self):
		index = int(self.txtContadorProyectos.text())
		ultimoRegistro = int(self.txtTotalProyectos.text())
		if ultimoRegistro==0:
			QMessageBox.information(self, "Fin de Archivo", "El archivo no tiene registros...", QMessageBox.Ok)
		elif index == ultimoRegistro:
			QMessageBox.information(self, "Fin de Archivo", "Usted ya se encuentra en el último registro...", QMessageBox.Ok)
		else:
			self.txtContadorProyectos.setText(str(index + 1))
			self.llenarPantProyecto(index)


	def ultimoProyecto(self):
		index = int(self.txtContadorProyectos.text())
		lv_ultimoRegistro = int(self.txtTotalProyectos.text())
		if lv_ultimoRegistro == 0:
			QMessageBox.information(self, "Fin de Archivo", "El archivo no tiene registros...", QMessageBox.Ok)
		elif lv_ultimoRegistro == index:
			QMessageBox.information(self, "Fin de Archivo", "Usted ya se encuentra en el último registro...", QMessageBox.Ok)
		else:
			index = int(self.txtTotalProyectos.text()) - 1
			self.txtContadorProyectos.setText(self.txtTotalProyectos.text()) 
			self.llenarPantProyecto(index)


	def copiarInforme(self):
		self.CodificarArchivos()
		archivo = QFileDialog.getOpenFileName(self, 'Seleccionar Archivo...', './', filter="Documentos permitidos(*.pdf *.doc *.docx);;Archivos Comprimidos(*.zip *.rar *.tar *.tar.gz)")
		if archivo[0]:
			self.archivo_origen = archivo[0]
			self.extension = (archivo[0].split('.'))[-1]
			self.rutadestino = os.getcwd() + os.sep + 'Proyectos' + os.sep
			self.destino = self.rutadestino + self.nombreProyectoDestino + self.extension
			lv_aceptar = 1
			if os.path.exists(self.destino):
				respuesta=QMessageBox.warning(self,"Adventencia", "El archivo ya existe en la biblioteca, desea sobre-escribir?", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.No:
					lv_aceptar = 0
			if lv_aceptar == 1:
				shutil.copyfile(self.archivo_origen, self.destino)
				lv_IdProyecto = int(self.txtIdProyecto.text())
				lv_ndestino = self.nombreProyectoDestino + self.extension
				actualiza_proyecto = "UPDATE proyectos SET nombre_informe_codificado = ('%s') WHERE id_proyecto = '%i'" % (lv_ndestino, lv_IdProyecto)
				self.cursor.execute(actualiza_proyecto)
				QMessageBox.information(self, "Sistema", "El informe ha sido archivado satisfactoriamente", QMessageBox.Ok)
				self.txtEstadoInforme.setText('Entregado...')
				self.txtNInformeCod.setText(lv_ndestino)
				self.txtEstadoInforme.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
		self.archivo_origen = ''
		self.extension = ''
		self.rutadestino = ''
		self.destino = '' 
		self.rutadestino = '' 
		self.nombreProyectoDestino = '' 
		self.nombreDesarrolloDestino = '' 
		self.nombreManualesDestino = '' 
		self.extension = ''

	def copiarDesarrollo(self):
		self.CodificarArchivos()
		archivo = QFileDialog.getOpenFileName(self, 'Seleccionar Archivo...', './', filter="Archivo comprimidos(*.zip *.tar *.tar.gz *.rar)")
		if archivo[0]:
			self.archivo_origen = archivo[0]
			self.extension = (archivo[0].split('.'))[-1]
			self.rutadestino = os.getcwd() + os.sep + 'Proyectos' + os.sep
			self.destino = self.rutadestino + self.nombreDesarrolloDestino + self.extension
			lv_ndestino = self.nombreDesarrolloDestino + self.extension
			lv_aceptar = 1
			if os.path.exists(self.destino):
				respuesta=QMessageBox.warning(self,"Adventencia", "El archivo ya existe en la biblioteca, desea sobre-escribir?", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.No:
					lv_aceptar = 0
			if lv_aceptar == 1:
				shutil.copyfile(self.archivo_origen, self.destino)
				lv_IdProyecto = self.txtIdProyecto.text()
				actualiza_proyecto = "UPDATE proyectos SET nombre_desarrollo_codificado = ('%s') WHERE id_proyecto = '%s'" % (lv_ndestino, lv_IdProyecto)
				self.cursor.execute(actualiza_proyecto)
				QMessageBox.information(self, "Sistema", "El producto desarrollado ha sido archivado satisfactoriamente", QMessageBox.Ok)
				self.txtEstadoDesarrollo.setText('Entregado...')
				self.txtNDesarrolloCod.setText(lv_ndestino)
				self.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
		self.archivo_origen = ''
		self.extension = ''
		self.rutadestino = ''
		self.destino = '' 
		self.rutadestino = '' 
		self.nombreProyectoDestino = '' 
		self.nombreDesarrolloDestino = '' 
		self.nombreManualesDestino = '' 
		self.extension = ''

	def copiarManual(self):
		self.CodificarArchivos()
		archivo = QFileDialog.getOpenFileName(self, 'Seleccionar Archivo...', './', filter="Archivo comprimidos(*.zip *.tar *.tar.gz *.rar)")
		if archivo[0]:
			self.archivo_origen = archivo[0]
			self.extension = (archivo[0].split('.'))[-1]
			self.rutadestino = os.getcwd() + os.sep + 'Proyectos' + os.sep
			self.destino = self.rutadestino + self.nombreManualesDestino + self.extension
			lv_ndestino = self.nombreManualesDestino + self.extension
			lv_aceptar = 1
			if os.path.exists(self.destino):
				respuesta=QMessageBox.warning(self,"Adventencia", "El archivo ya existe en la biblioteca, desea sobre-escribir?", QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.No:
					lv_aceptar = 0
			if lv_aceptar == 1:
				shutil.copyfile(self.archivo_origen, self.destino)
				lv_IdProyecto = self.txtIdProyecto.text()
				actualiza_proyecto = "UPDATE proyectos SET nombre_manual_codificado = ('%s') WHERE id_proyecto = '%s'" % (lv_ndestino, lv_IdProyecto)
				self.cursor.execute(actualiza_proyecto)
				self.txtEstadoManual.setText('Entregado...')
				self.txtNManualCod.setText(lv_ndestino)
				self.txtEstadoManual.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
				QMessageBox.information(self, "Sistema", "El/Los manuales han sido archivado satisfactoriamente", QMessageBox.Ok)
		self.archivo_origen = ''
		self.extension = ''
		self.rutadestino = ''
		self.destino = '' 
		self.rutadestino = '' 
		self.nombreProyectoDestino = '' 
		self.nombreDesarrolloDestino = '' 
		self.nombreManualesDestino = '' 
		self.extension = ''

	def cerrarGrpPersonas(self):
		self.TipoPersona = ''
		self.grpPersonas.hide()

	def CodificarArchivos(self):
		lv_ano = self.txtAnoPeriodo.text()
		lv_trayecto = "T0" + str(self.cmbTrayecto.currentIndex() + 1)
		lv_seccion = self.cmbSeccion.currentText()
		lv_grupo = "G" + self.cmbGrupoDesarrollo.currentText()
		if self.optRegular.isChecked():
			lv_tipo = 'R'
			lv_anoprosecucion = '0000'
		else:
		 	lv_tipo = 'P'
		 	lv_anoprosecucion = self.txtAnoProsecucion.text()
		self.nombreProyectoDestino = 'PROY-'+lv_ano+'-'+lv_trayecto+'-'+lv_seccion+'-'+lv_tipo+'-'+lv_anoprosecucion+'-'+lv_grupo+'.'
		self.nombreDesarrolloDestino = 'DESA-'+lv_ano+'-'+lv_trayecto+'-'+lv_seccion+'-'+lv_tipo+'-'+lv_anoprosecucion+'-'+lv_grupo+'.'
		self.nombreManualesDestino = 'MANUAL-'+lv_ano+'-'+lv_trayecto+'-'+lv_seccion+'-'+lv_tipo+'-'+lv_anoprosecucion+'-'+lv_grupo+'.'

	def AccederNuevoProyecto(self):
		self.IdSeccion = int(self.txtIdSeccion.text())
		self.vaciarTablasEstudiantesTutores()
		self.nuevoproyecto = 1
		self.TotalProyectosPorPeriodos = self.tabla_seccion_grupos_proyectos.rowCount()
		if self.TotalProyectosPorPeriodos > 0:
			if self.txtContadorProyectos.text() == '0':
				self.proyectoActual = 0
			else:
				self.proyectoActual = self.TotalProyectosPorPeriodos - 1
		else:
			self.proyectoActual = 0
		self.txtContadorProyectos.setText(str(self.TotalProyectosPorPeriodos + 1))
		self.bdnuevo = 1
		self.limpiarProyecto()
		self.CodificarProyecto()
		self.activarCamposProyecto()
		self.AbrirProyectos()
		self.txtCodigoProyecto.setText(self.codigoProyecto)
		self.txtIdTipoDesarrollo.setText('1')
		self.txtIdMetodo.setText('1')
		self.txtTituloProyecto.setFocus()


	def CerrarVentanaProyectos(self):
		#--------------------------
		# Habilita Tab Principal
		self.tabWidget.setTabEnabled(0, True)
		#Deshabilitar Tabs Registro de Proyectos
		self.tabWidget.setTabEnabled(1, False)
		self.tabWidget.setCurrentIndex(0)
		self.cargarDatosProyectos()

	def mostrarListaEstudiantes(self):
		self.TipoPersona = 'EST'
		self.lblTituloPersonas.setText('Datos de Estudiantes')
		self.llenarTablaPersonas()
		self.grpPersonas.show()

	def mostrarListaTutores(self):
		self.TipoPersona = 'TUT'
		self.lblTituloPersonas.setText('Datos de Tutores')
		self.llenarTablaPersonas()
		self.grpPersonas.show()


	def llenarTablaPersonas(self):
		self.tabla_personas.setSortingEnabled(False)
		if self.tabla_personas.rowCount() > 0:
			self.tabla_personas.clearSelection()
			#self.tabla_personas.disconnect()
			self.tabla_personas.clearContents()
			#self.tabla_personas.setRowCount(0)
			index2 = self.tabla_personas.rowCount()
			while index2 > 0:
				index = index2 - 1
				self.tabla_personas.removeRow(index)
				index2 = index2 - 1
		if self.TipoPersona == 'EST':
			cursor_lista_personas = "SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante, genero_estudiante, telefono_estudiante, estado FROM estudiante WHERE cedula_estudiante != '0' ORDER BY cedula_estudiante"
		else:
			cursor_lista_personas = "SELECT cedula_tutor, nombre_tutor, apellido_tutor, genero_tutor, telefono_tutor, estado FROM tutores WHERE cedula_tutor != '0' ORDER BY cedula_tutor"
		self.cursor.execute(cursor_lista_personas)
		index = 0
		self.tabla_personas.setRowCount(0)
		for rows in self.cursor:
			self.cedula = str(rows[0])
			self.nombre = str(rows[1])
			self.apellido = str(rows[2])
			self.genero = str(rows[3])
			if str(rows[4]) == 'None':
				self.telefono = ''
			else:
				self.telefono = str(rows[4])
			self.estatus = str(rows[5])
			#Agregando valores a la tabla
			self.tabla_personas.insertRow(index)
			self.tabla_personas.setItem(index, 0, QTableWidgetItem((' '+self.cedula)[-8:]))
			self.tabla_personas.setItem(index, 1, QTableWidgetItem(self.nombre))
			self.tabla_personas.setItem(index, 2, QTableWidgetItem(self.apellido))
			self.tabla_personas.setItem(index, 3, QTableWidgetItem(self.genero))
			self.tabla_personas.setItem(index, 4, QTableWidgetItem(self.telefono))
			self.tabla_personas.setItem(index, 5, QTableWidgetItem(self.estatus))
			index += 1
		self.TotalRegPersonas.setText(str(index))
		self.tabla_personas.setSortingEnabled(True)
		self.tabla_personas.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		if index == 0:
			self.btnEditarRegistro.setEnabled(False)
			self.txtFiltroPersonas.setEnabled(False)
			self.grpFiltrarPersonas.setEnabled(False)
		else:
			self.btnEditarRegistro.setEnabled(True)
			self.txtFiltroPersonas.setEnabled(True)
			self.grpFiltrarPersonas.setEnabled(True)

	def ordenarTablaPersonas(self):
		if self.optCedula.isChecked():
			self.tabla_personas.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		elif self.optNombre.isChecked():
			self.tabla_personas.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)
		else:
			self.tabla_personas.horizontalHeader().setSortIndicator(2, Qt.AscendingOrder)


	def VolverALista(self):
		#Deshabilita Tab Registro
		self.tabPersonas.setTabEnabled(0, True)
		
		#Habilitar Tab Lista
		self.tabPersonas.setTabEnabled(1, False)
		self.tabPersonas.setCurrentIndex(0)


	def nuevoRegistro(self):
		self.modo = 0
		self.registroactual = self.tabla_personas.currentRow()
		self.proximo_registro = self.tabla_personas.rowCount() + 1
		self.total_registros = self.tabla_personas.rowCount()
		self.contador_registros.setText(str(self.proximo_registro))
		self.txtCedula.setText("")
		self.txtNombre.setText("")
		self.txtApellido.setText("")
		self.txtTelefono.setText("")
		if self.TipoPersona=='EST':
			self.lblCedPersona.setText("Cedula Estudiante:")
		else:
			self.lblCedPersona.setText("Cedula Tutor:")
		self.btnEstado.setText("Activo")
		self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
		#Habilita Tab Registro
		self.tabPersonas.setTabEnabled(0, False)
		#Deshabilitar Tab Lista
		self.tabPersonas.setTabEnabled(1, True)
		self.tabPersonas.setCurrentIndex(1)
		self.txtCedula.setFocus()

	def editarRegistro(self):
		if self.tabla_personas.currentRow() != -1:
			self.registroactual = self.tabla_personas.currentRow()
			self.total_registros = self.tabla_personas.rowCount()
			self.cedula_Original = self.tabla_personas.item(self.registroactual,0).text().replace(" ", "")

			self.modo = 1
			index = self.tabla_personas.currentRow()
			self.txtCedula.setText(self.tabla_personas.item(index,0).text())
			self.txtNombre.setText(self.tabla_personas.item(index,1).text())
			self.txtApellido.setText(self.tabla_personas.item(index,2).text())
			self.txtTelefono.setText(self.tabla_personas.item(index,4).text())
			if self.tabla_personas.item(index,3).text()=="Femenino":
				self.optFemenino.setChecked(True)
			else:
				self.optMasculino.setChecked(True)
			if self.tabla_personas.item(index,5).text() == "Inactivo":
				self.btnEstado.setText("Inactivo")
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkred; color: white; font-size: 12px;")
			else:
				self.btnEstado.setText("Activo")
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
			self.contador_registros.setText(str(self.registroactual + 1))
			#Habilita Tab Registro
			self.tabPersonas.setTabEnabled(0, False)
			#Deshabilitar Tab Lista
			self.tabPersonas.setTabEnabled(1, True)
			self.tabPersonas.setCurrentIndex(1)		
			self.txtNombre.setFocus()
		else:
			QMessageBox.warning(self,"Sistema", "Debe seleccionar un registro antes de realizar click en editar", QMessageBox.Ok)


	def seleccionaEstudiante(self):
		row=self.tablaIntegrantes.currentRow()
		self.txtCedulaEstudiante.setText(self.tablaIntegrantes.item(row, 0).text()) 

	def seleccionaTutor(self):
		row=self.tablaTutores.currentRow()
		self.txtCedulaTutor.setText(self.tablaTutores.item(row, 0).text())
		if self.tablaTutores.item(row, 3).text() == "Academico":
			self.cmbTipoAsesor.setCurrentIndex(0)
		elif self.tablaTutores.item(row, 3).text() == "Tecnico Metodologico":
			self.cmbTipoAsesor.setCurrentIndex(1)
		else:
			self.cmbTipoAsesor.setCurrentIndex(2)

	def actContadorActual(self):
		fila = self.tabla_personas.currentRow()
		totalregistros = self.tabla_personas.rowCount()
		cedula = self.tabla_personas.item(fila, 0).text().replace(" ", "")
		self.txtCedulaSeleccionada.setText(cedula) 
		self.RegActual.setText(str(fila+1))
		self.TotalReg.setText(str(totalregistros))

	def buscarDatoPersona(self):
		lv_texto = self.txtFiltroPersonas.text().upper()
		if self.optCedula.isChecked()== True:
			validar = re.match('^[0-9\s]+$', lv_texto, re.I)
			columna = 0
		elif self.optNombre.isChecked()==True:	
			validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
			columna = 1
		else:
			validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
			columna = 2
		index = self.tabla_personas.rowCount()
		fila=0
		encontrar = 0
		while fila < index:
			lv_busqueda = self.tabla_personas.item(fila,columna).text()
			if lv_texto in lv_busqueda:
				encontrar = 1
				break;
			fila = fila + 1
		if encontrar == 1:
			fila_inicial = self.tabla_personas.rowCount() - 1
			posicion_inicial = self.tabla_personas.item(fila_inicial, columna)
			self.tabla_personas.scrollToItem(posicion_inicial)
			self.tabla_personas.setCurrentCell(fila_inicial, columna)
			posicion = self.tabla_personas.item(fila, columna)
			self.tabla_personas.scrollToItem(posicion)
			self.tabla_personas.setCurrentCell(fila, columna)
			self.txtCedulaSeleccionada.setText(self.tabla_personas.item(fila, 0).text().replace(" ", ""))
			return True
		else:
			return False

	def cambiarEstado(self):
		fila = self.tabla_personas.currentRow()
		lv_cedula = self.tabla_personas.item(fila,0).text().replace(" ", "")
		if self.btnEstado.text() == "Inactivo":
			self.btnEstado.setText("Activo")
			self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
			lv_activo = 'Activo'
		else:
			self.btnEstado.setText("Inactivo")
			self.btnEstado.setStyleSheet("border: 1px solid black; background: darkred; color: white; font-size: 12px;")
			lv_activo = 'Inactivo'
		if self.modo == 1:
			self.hoy = datetime.today()
			self.fechareg = self.hoy.strftime(self.formato_fecha)
			if self.TipoPersona == 'EST':
				actualiza_registro = "UPDATE estudiante SET estado = '%s' where cedula_estudiante='%d'" % (lv_activo, int(lv_cedula))
			else:
				actualiza_registro = "UPDATE tutores SET estado = '%s' where cedula_tutor='%d'" % (lv_activo, int(lv_cedula))
			self.cursor.execute(actualiza_registro)

			if self.btnEstado.text() == "Inactivo":
				self.tabla_personas.setItem(fila, 5, QTableWidgetItem('Inactivo'))
			else:
				self.tabla_personas.setItem(fila, 5, QTableWidgetItem('Activo'))

	def guardarRegistro(self):
		if self.txtCedula.text().replace(" ", "") != '':
			self.nombre = self.txtNombre.text().upper()
			self.apellido = self.txtApellido.text().upper()
			self.telefono = self.txtTelefono.text()
			if self.optMasculino.isChecked():
				self.genero = 'Masculino'
			else:
				self.genero = 'Femenino'
			if self.modo == 1:
				fila = self.tabla_personas.currentRow()
				self.cedula_Original = self.tabla_personas.item(fila,0).text().replace(" ", "")
			else:
				self.cedula_Original = self.txtCedula.text().replace(" ", "")
			self.cedula_Nueva = self.txtCedula.text().replace(" ", "")

			if self.modo == 0:
				self.buscarCedula(self.cedula_Nueva)
				if self.encontrar == True:
					QMessageBox.warning(self,"Base de Datos", "La cedula a registrar ya esta asignado a otra persona...", QMessageBox.Ok)
					self.txtCedula.setText(self.cedula_Original)
				else:
					self.agregarRegistro()
					QMessageBox.information(self,"Base de Datos", "El registro fue agregado exitosamente...", QMessageBox.Ok)
					#Habilita Tab Registro
					self.tabPersonas.setTabEnabled(1, False)
					#Deshabilitar Tab Lista
					self.tabPersonas.setTabEnabled(0, True)
					self.tabPersonas.setCurrentIndex(0)	
			else:
				if self.cedula_Original == self.txtCedula.text():
					self.actualizaRegistro(self.cedula_Original, self.cedula_Original,False)
					QMessageBox.information(self,"Base de Datos", "El registro fue actualizado exitosamente...", QMessageBox.Ok)
					#Habilita Tab Registro
					self.tabPersonas.setTabEnabled(0, True)
					#Deshabilitar Tab Lista
					self.tabPersonas.setTabEnabled(1, False)
					self.tabPersonas.setCurrentIndex(0)	
				else:
					respuesta=QMessageBox.warning(self,"Adventencia", "Esta seguro de cambiar cedula: " + self.cedula_Original + " por la cedula: " + self.txtCedula.text(), QMessageBox.Yes | QMessageBox.No)
					if respuesta == QMessageBox.Yes:
						self.buscarCedula(self.cedula_Nueva)
						if self.encontrar == False:
							self.actualizaRegistro(self.cedula_Nueva, self.cedula_Original,True)
							QMessageBox.information(self,"Base de Datos", "El registro fue actualizado exitosamente...", QMessageBox.Ok)
							#Habilita Tab Registro
							self.tabPersonas.setTabEnabled(0, True)
							#Deshabilitar Tab Lista
							self.tabPersonas.setTabEnabled(1, False)
							self.tabPersonas.setCurrentIndex(0)	
						else:
							QMessageBox.warning(self,"Base de Datos", "La cedula a registrar ya esta asignado a otra persona...", QMessageBox.Ok)
							self.txtCedula.setText(self.cedula_Original)
					else:
						self.txtCedula.setText(self.cedula_Original)
		else:
			QMessageBox.warning(self,"Base de Datos", "La cedula no puede estar vacia...", QMessageBox.Ok)


	def agregarRegistro(self):
		self.nombre = self.txtNombre.text().upper()
		self.apellido = self.txtApellido.text().upper()
		self.telefono = self.txtTelefono.text()
		self.txtNombre.setText(self.nombre)
		self.txtApellido.setText(self.apellido)
		if self.optMasculino.isChecked():
			self.genero = 'Masculino'
		else:
			self.genero = 'Femenino'

		lv_activo = self.btnEstado.text()

		self.cedula = self.txtCedula.text()
		self.telefono = self.txtTelefono.text()
		#self.hoy = datetime.today()
		#self.fechareg = self.hoy.strftime(self.formato_fecha)
		if self.TipoPersona == 'EST':
			inserta_registro = "INSERT INTO estudiante VALUES('%d', '%s', '%s', '%s', '%s', '%s')" % (int(self.cedula), self.nombre, self.apellido, self.genero, self.telefono, lv_activo)
		else:
			inserta_registro = "INSERT INTO tutores VALUES('%d', '%s', '%s', '%s', '%s', 0, '%s')" % (int(self.cedula), self.nombre, self.apellido, self.genero, self.telefono, lv_activo)

		self.cursor.execute(inserta_registro)
		#creando una fila en la matriz
		self.llenarTablaPersonas()
		total_personas = self.tabla_personas.rowCount()
		index = 0
		while index < total_personas:
			if self.tabla_personas.item(index,0).text().replace(" ", "") == self.cedula:
				break;
			index = index + 1
		fila = index
		columna = 0
		fila_inicial = total_personas - 1
		posicion_inicial = self.tabla_personas.item(fila_inicial, columna)
		self.tabla_personas.scrollToItem(posicion_inicial)
		self.tabla_personas.setCurrentCell(fila_inicial, columna)
		posicion = self.tabla_personas.item(fila, columna)
		self.tabla_personas.scrollToItem(posicion)
		self.tabla_personas.setCurrentCell(fila, columna)
		self.RegActual.setText(str(index))
		self.TotalReg.setText(str(self.total_registros))


	def actualizaRegistro(self, lv_cedulaNueva, lv_cedula, lv_reemplaza_cedula):
		lv_activo = "False"
		self.nombre = self.txtNombre.text().upper()
		self.apellido = self.txtApellido.text().upper()
		self.telefono = self.txtTelefono.text()
		if self.optMasculino.isChecked():
			self.genero = 'Masculino'
		else:
			self.genero = 'Femenino'
		lv_activo = self.btnEstado.text()
		#self.hoy = datetime.today()
		#self.fechareg = self.hoy.strftime(self.formato_fecha)

		if self.TipoPersona == 'EST':
			if lv_reemplaza_cedula == True:
				actualiza_registro = "UPDATE estudiante SET cedula_estudiante = '%d', nombre_estudiante = '%s', apellido_estudiante = '%s', genero_estudiante='%s', telefono_estudiante= '%s', estado = '%s' where cedula_estudiante='%d'" % (int(lv_cedulaNueva), self.nombre, self.apellido, self.genero, self.telefono, lv_activo, int(lv_cedula))
				lv_cedula = lv_cedulaNueva
			else:
				actualiza_registro = "UPDATE estudiante SET nombre_estudiante = '%s', apellido_estudiante = '%s', genero_estudiante='%s', telefono_estudiante= '%s', estado = '%s' where cedula_estudiante='%d'" % (self.nombre, self.apellido, self.genero, self.telefono, lv_activo, int(lv_cedula))
		else:
			if lv_reemplaza_cedula == True:
				actualiza_registro = "UPDATE tutores SET cedula_tutor = '%d', nombre_tutor = '%s', apellido_tutor = '%s', genero_tutor='%s', telefono_tutor= '%s', estado = '%s' where cedula_tutor='%d'" % (int(lv_cedulaNueva), self.nombre, self.apellido, self.genero, self.telefono, lv_activo, int(lv_cedula))
				lv_cedula = lv_cedulaNueva
			else:
				actualiza_registro = "UPDATE tutores SET nombre_tutor = '%s', apellido_tutor = '%s', genero_tutor='%s', telefono_tutor= '%s', estado = '%s' where cedula_tutor='%d'" % (self.nombre, self.apellido, self.genero, self.telefono, lv_activo, int(lv_cedula))

		self.cursor.execute(actualiza_registro)
		self.txtNombre.setText(self.nombre)
		self.txtApellido.setText(self.apellido)
		#Asignando valores a la matriz
		self.tabla_personas.setItem(self.registroactual,0, QTableWidgetItem((' '+self.txtCedula.text())[-8:]))
		self.tabla_personas.setItem(self.registroactual,1, QTableWidgetItem(self.txtNombre.text()))
		self.tabla_personas.setItem(self.registroactual,2, QTableWidgetItem(self.txtApellido.text()))
		if self.optMasculino.isChecked():
			self.tabla_personas.setItem(self.registroactual,3, QTableWidgetItem('Masculino'))
		else:
			self.tabla_personas.setItem(self.registroactual,3, QTableWidgetItem('Femenino'))
		self.tabla_personas.setItem(self.registroactual,4, QTableWidgetItem(self.txtTelefono.text()))
		if self.btnEstado.text() == 'Activo':
			self.tabla_personas.setItem(self.registroactual,5, QTableWidgetItem('Activo'))
		else:
			self.tabla_personas.setItem(self.registroactual,5, QTableWidgetItem('Inactivo'))


	def seleccionarRegistro(self):
		fila = self.tabla_personas.currentRow()
		if fila != -1:
			if self.TipoPersona == 'EST':
				self.txtCedulaEstudiante.setText(self.tabla_personas.item(fila,0).text().replace(" ", ""))
				self.grpPersonas.hide()
				self.AgregarIntegrante()
			else:
				self.txtCedulaTutor.setText(self.tabla_personas.item(fila,0).text().replace(" ", ""))
				self.grpPersonas.hide()
				self.AgregarTutor()
		else:
			QMessageBox.warning(self,"Adventencia", "Debe elegir una persona de la lista antes de pulsar 'Seleccionar'", QMessageBox.Ok)
	def AgregarIntegrante(self):
		self.continua = 1
		self.encontrar = 0
		self.encontrado = 0
		self.TotalIntegrantes = self.tablaIntegrantes.rowCount()
		if self.txtCedulaEstudiante.text() == '' or self.txtCedulaEstudiante.text() == '0':
			QMessageBox.warning(self,"Adventencia", "La cedula del integrante no puede ser igual a 0 o con valor nulo", QMessageBox.Ok)
			self.continua = 0
		elif int(self.txtLimiteEstudiantes.text()) <= self.TotalIntegrantes:
			respuesta=QMessageBox.warning(self,"Adventencia", "Este proyecto ya ha alcanzado el limite de estudiantes permitido, desea ignorar el limite?", QMessageBox.Yes | QMessageBox.No)
			if respuesta == QMessageBox.No:
				self.continua = 0
		if self.continua == 1:
			if self.TotalIntegrantes > 0:
				index = 0
				self.encontrar = 0
				while index < self.TotalIntegrantes:
					if self.tablaIntegrantes.item(index, 0).text() == self.txtCedulaEstudiante.text():
						self.encontrar = 1
						break;
					index = index + 1
			if self.encontrar == 1:
				QMessageBox.warning(self,"Adventencia", "El estudiante que desea ingresar ya esta registrado en el grupo de desarrollo", QMessageBox.Ok)
			else:
				self.encontrado = 0
				lvcedula = int(self.txtCedulaEstudiante.text())
				bdbuscar_estudiante = "SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante FROM estudiante WHERE cedula_estudiante = %i" % lvcedula
				self.cursor.execute(bdbuscar_estudiante)
				rows=self.cursor.fetchone()
				if rows == None:
					self.encontrado = 0
				else:
					self.encontrado = 1
				if self.encontrado == 1:
					lv_proyecto = int(self.txtIdProyecto.text())
					self.IdProyecto = int(self.txtIdProyecto.text())
					lv_cedula = int(self.txtCedulaEstudiante.text())
					self.hoy = datetime.today()
					self.fechareg = self.hoy.strftime(self.formato_fecha)
					inserta_integrante = "INSERT INTO elaboran (FK_id_proyecto, FK_cedula_estudiante) VALUES ('%i', '%i')" % (lv_proyecto, lv_cedula)
					self.cursor.execute(inserta_integrante)
					self.tablaIntegrantes.clearSelection()
					self.tablaIntegrantes.clearContents()
					index2 = self.TotalIntegrantes
					index3 = 0
					while index2 > 0:
						index3 = index2 - 1
						self.tablaIntegrantes.removeRow(index3)
						index2 = index2 - 1
					self.LlenarTablaIntegrantes()
					QMessageBox.information(self,"Base de Datos", "Estudiante fue añadido al grupo de proyectos...", QMessageBox.Ok)
					self.txtCedulaEstudiante.setText("")
				else:
					QMessageBox.warning(self,"Adventencia", "La cedula indicada no se encuentra en el registro de estudiantes.. operacion detenida!", QMessageBox.Ok)

	def RemoverIntegrante(self):
		if self.txtCedulaEstudiante.text() == '' or self.txtCedulaEstudiante.text() == '0':
			QMessageBox.warning(self,"Error", "Debe seleccionar un estudiante antes de eliminar integrante", QMessageBox.Ok)
		else:
			row=int(self.txtContadorProyectos.text()) - 1
			lv_proyecto = int(self.txtIdProyecto.text())
			lv_cedula = int(self.txtCedulaEstudiante.text())
			respuesta=QMessageBox.warning(self,"Adventencia", "Esta seguro de quitar al estudiante del grupo de desarrollo?", QMessageBox.Yes | QMessageBox.No)			
			if respuesta == QMessageBox.Yes:
				eliminar_integrante = "DELETE FROM elaboran WHERE FK_id_proyecto = '%i' and FK_cedula_estudiante = '%i'" % (lv_proyecto, lv_cedula)
				self.cursor.execute(eliminar_integrante)
				self.LlenarTablaIntegrantes()
				QMessageBox.warning(self,"Base de Datos", "Integrante fue removido exitosamente...", QMessageBox.Ok)
				self.txtCedulaEstudiante.setText("")		

	def AgregarTutor(self):
		self.continua = 1
		self.encontrar = 0
		self.encontrado = 0
		lv_total_tutores = self.tablaTutores.rowCount()
		lv_tipo_tutor = self.cmbTipoAsesor.currentText()
		if self.txtCedulaTutor.text() == '' or self.txtCedulaTutor.text() == '0':
			QMessageBox.warning(self,"Adventencia", "La cedula del integrante no puede ser igual a 0 o con valor nulo", QMessageBox.Ok)
		else:
			self.continua = 0
			if lv_total_tutores > 0:
				index = 0
				self.encontrar = 0
				while index < lv_total_tutores:
					if self.tablaTutores.item(index,3).text() == lv_tipo_tutor:
						self.encontrar = 1
						break;
					index = index + 1
			if self.encontrar == 1:
				QMessageBox.warning(self,"Adventencia", "Ya se encuentra asignado un tutor del tipo " + lv_tipo_tutor + " para este proyecto", QMessageBox.Ok)
			else:
				self.encontrado = 0
				lvcedula = int(self.txtCedulaTutor.text())
				bdbuscar_tutor = "SELECT cedula_tutor, nombre_tutor, apellido_tutor FROM tutores WHERE cedula_tutor = %i" % lvcedula
				self.cursor.execute(bdbuscar_tutor)
				rows=self.cursor.fetchone()
				if rows == None:
					self.encontrado = 0
				else:
					self.encontrado = 1
				if self.encontrado == 1:
					lv_proyecto = int(self.txtIdProyecto.text())
					self.IdProyecto = int(self.txtIdProyecto.text())
					lv_cedula = int(self.txtCedulaTutor.text())
					self.hoy = datetime.today()
					self.fechareg = self.hoy.strftime(self.formato_fecha)
					inserta_tutor = "INSERT INTO es_asesorado (FK_id_proyecto, FK_cedula_tutor, rol) VALUES ('%i', '%i', '%s')" % (lv_proyecto, lv_cedula, lv_tipo_tutor)
					self.cursor.execute(inserta_tutor)
					self.LlenarTablaIntegrantes()
					QMessageBox.information(self,"Base de Datos", "Tutor fue añadido al grupo de proyectos...", QMessageBox.Ok)
					self.txtCedulaTutor.setText("")
				else:
					QMessageBox.warning(self,"Adventencia", "La cedula indicada no se encuentra en el registro de tutores.. operacion detenida!", QMessageBox.Ok)

	def RemoverTutor(self):
		if self.txtCedulaTutor.text() == '' or self.txtCedulaEstudiante.text() == '0':
			QMessageBox.warning(self,"Error", "Debe seleccionar un tutor de la lista antes de eliminar asesor", QMessageBox.Ok)
		else:
			#row=int(self.txtContadorProyectos.text()) - 1
			lv_proyecto = int(self.txtIdProyecto.text())
			lv_cedula = int(self.txtCedulaTutor.text())
			#lv_tipo_tutor = ''
			lv_tipo_tutor = self.cmbTipoAsesor.currentText()
			respuesta=QMessageBox.warning(self,"Adventencia", "Esta seguro de remover al tutor del proyecto?", QMessageBox.Yes | QMessageBox.No)			
			if respuesta == QMessageBox.Yes:
				eliminar_tutor = "DELETE FROM es_asesorado WHERE FK_id_proyecto = '%i' and FK_cedula_tutor = '%i' and rol = '%s'" % (lv_proyecto, lv_cedula, lv_tipo_tutor)
				self.cursor.execute(eliminar_tutor)
				self.LlenarTablaIntegrantes()
				QMessageBox.warning(self,"Base de Datos", "Tutor fue removido exitosamente...", QMessageBox.Ok)
				self.txtCedulaTutor.setText("")		

	def buscarCedula(self,lv_cedula):
		rows=[]
		if self.TipoPersona=='EST':
			buscar_cedula = "select cedula_estudiante, nombre_estudiante, apellido_estudiante from estudiante WHERE cedula_estudiante = '%d'" % (int(lv_cedula))
		else:
			buscar_cedula = "select cedula_tutor, nombre_tutor, apellido_tutor from tutores WHERE cedula_tutor = '%d'" % (int(lv_cedula))
		self.cursor.execute(buscar_cedula)
		for rows in self.cursor:
			continue
		if rows==[]:
			self.encontrar = False
		else:
			self.encontrar = True


	def cerrar(self):
		self.close()

#app = QApplication(sys.argv)
#PIntegradoProyecto = DialogoIntProyectos()
#PIntegradoProyecto.show()
#app.exec_()
