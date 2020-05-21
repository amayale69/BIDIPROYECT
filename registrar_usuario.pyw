import sys, re
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMainWindow, QAction, QPushButton, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib
import ctypes #GetSystemMetrics
import os.path as path

class DialogoRegUsuarios(QDialog):
	def __init__(self):

		QDialog.__init__(self)
		uic.loadUi("registrar_usuario.ui", self)
		self.setEnabled(True)
		#Colocar titulo de la pantalla
		self.setWindowTitle("Registro de Usuarios")
		self.lblTituloPantalla.setText("Registro de Usuarios")
		#Operacion para centrar la ventana en la pantalla
		resolucion = ctypes.windll.user32
		resolucion_ancho = resolucion.GetSystemMetrics(0)
		resolucion_alto = resolucion.GetSystemMetrics(1)
		left = (resolucion_ancho / 2) - (self.frameSize().width() / 2)
		top = (resolucion_alto / 2) - (self.frameSize().height() / 2)
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
		#Iniciar valor de usuario
		self.txtUsuarioSeleccionado.setText('')
		self.mensaje1.setText("")
		self.txtUsuarioActivo.hide()
		self.tabla_usuarios.setAlternatingRowColors(True)
		#Instruccion para deshabilitar edicion
		self.tabla_usuarios.setEditTriggers(QTableWidget.NoEditTriggers)
		# Deshabilitar el comportamiento de arrastrar y soltar
		self.tabla_usuarios.setDragDropOverwriteMode(False)
		# Seleccionar toda la fila
		#self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectRows)
		# Seleccionar una fila a la vez
		self.tabla_usuarios.setSelectionMode(QTableWidget.SingleSelection)
		#self.tabla_usuarios.setSelectionMode(QAbstractItemView.SingleSelection)
		# Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran
		# textos que no encajan
		self.tabla_usuarios.setTextElideMode(Qt.ElideRight)# Qt.ElideNone
		# Establecer el ajuste de palabras del texto 
		self.tabla_usuarios.setWordWrap(False)
		# Habilitar clasificación
		self.tabla_usuarios.setSortingEnabled(True)
		# Establecer el número de columnas
		self.tabla_usuarios.setColumnCount(3)
		# Establecer el número de filas
		self.tabla_usuarios.setRowCount(0)
		# Alineación del texto del encabezado
		self.tabla_usuarios.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter)
		# Deshabilitar resaltado del texto del encabezado al seleccionar una fila
		self.tabla_usuarios.horizontalHeader().setHighlightSections(True)
		# Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
		self.tabla_usuarios.horizontalHeader().setStretchLastSection(True)
		# Ocultar encabezado vertical
		self.tabla_usuarios.verticalHeader().setVisible(False)
		# Establecer altura de las filas
		self.tabla_usuarios.verticalHeader().setDefaultSectionSize(20)
		# self.tabla_usuarios.verticalHeader().setHighlightSections(True)
		nombreColumnas = ("Usuario","Responsable", "Estado")
		# Establecer las etiquetas de encabezado horizontal usando etiquetas
		self.tabla_usuarios.setHorizontalHeaderLabels(nombreColumnas)
		# Establecer ancho de las columnas
		for indice, ancho in enumerate((150, 300, 100), start=0):
			self.tabla_usuarios.setColumnWidth(indice, ancho)

		#Vincular eventos de click de los botones a las funciones correspondientes
		self.btnRegresar.clicked.connect(self.VolverALista)
		self.btnNuevoRegistro.clicked.connect(self.nuevoRegistro)
		self.btnEditarRegistro.clicked.connect(self.editarRegistro)
		self.btnSalir.clicked.connect(self.cerrar_dialogo)
		self.btnGuardar.clicked.connect(self.guardarRegistro)
		self.btnDescartar.clicked.connect(self.retornarValores)
		self.optUsuario.clicked.connect(self.ordenarTabla)
		self.optResponsable.clicked.connect(self.ordenarTabla)
		self.btnEstado.clicked.connect(self.cambiarEstado)
		self.btnReinicioClave.clicked.connect(self.reiniciarClave)
		#Ejecutar funcion para llenar la tabla de datos	

		#Crear disparador para saber el numero de la fila de la tabla que ha sido seleccionada
		self.tabla_usuarios.itemClicked.connect(self.actContadorActual)
		self.tabla_usuarios.itemDoubleClicked.connect(self.editarRegistro)

		#Crear disparador de evento para buscar datos en la tabla por texto introducido por usuario
		self.txtFiltro.textChanged.connect(self.buscarDatoUsuario) 


		#Ocultar el campo de control de total de registros
		self.totalRegistros.hide()
		self.contador_registros.hide()
		self.registroactual = 0
		self.proximo_registro = 0
		#configurando loa slots de señales de los botones
		self.modo = 0

		#Deshabilita Tab Registro
		self.tabWidget.setTabEnabled(0, False)
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(1, True)

		self.usuario_Original = ''
		self.Usuario_Nuevo = ''
		self.responsable = ''
		self.estado = 0
		self.encontrar = False

		#Cargar Matriz de Datos
		self.consultarTabla()
		#Iniciar valores de variables de control de registros
		self.evento = "Inicio"
		if self.modo == 2:
			self.mensaje1.setText("Archivo no tiene registros")

	def VolverALista(self):
		self.btnEstado.setEnabled(True)
		self.btnReinicioClave.setEnabled(True)
		#Deshabilita Tab Registro
		self.tabWidget.setTabEnabled(0, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(1, True)


	def consultarTabla(self):
		lv_TotalRegistrosTabla = self.tabla_usuarios.rowCount()
		if lv_TotalRegistrosTabla > 0:
			self.tabla_usuarios.clearSelection()
			#self.tabla_usuarios.disconnect()
			self.tabla_usuarios.clearContents()
			#self.tabla_usuarios.setRowCount(0)
			index2 = self.tabla_usuarios.rowCount()
			while index2 > 0:
				index = index2 - 1
				self.tabla_usuarios.removeRow(index)
				index2 = index2 - 1
		cursor_lista_usuarios = "select usuario, responsable, estado from usuarios order by usuario"
		self.cursor.execute(cursor_lista_usuarios)
		index = 0
		#crear matriz de consultas
		self.registroUsuarios = []
		for rows in self.cursor:
			if rows==[]:
				self.modo = 2
			else:
				self.tabla_usuarios.insertRow(index)
				usuario = str(rows[0])
				responsable = str(rows[1])
				estado = str(rows[2])
				self.tabla_usuarios.setItem(index, 0, QTableWidgetItem(usuario))
				self.tabla_usuarios.setItem(index, 1, QTableWidgetItem(responsable))
				self.tabla_usuarios.setItem(index, 2, QTableWidgetItem(estado))
				index += 1
		self.txtUsuarioSeleccionado.setText("")
		self.TotalReg.setText(str(index))
		if index == 0:
			self.evento = 'No registros'
			self.btnEditarRegistro.setEnabled(False)
#			self.btnEliminar.setEnabled(False)
		else:
			self.btnEditarRegistro.setEnabled(True)
#			self.btnEliminar.setEnabled(True)

	def retornarValores(self):
		lv_TotalRegistros = self.tabla_usuarios.rowCount()
		if self.modo == 0:
			self.txtUsuario.setText('')
			self.txtResponsable.setText('')
			self.registroactual = lv_TotalRegistros
			self.btnEstado.setText("Activo")
			self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
		else:
			fila = self.tabla_usuarios.currentRow()
			self.txtUsuario.setText(self.tabla_usuarios.item(fila,0).text())
			self.txtResponsable.setText(self.tabla_usuarios.item(fila,1).text())
			self.registroactual = fila
			lv_activo = self.tabla_usuarios.item(fila,2).text()
			if lv_activo == 'Activo':
				self.btnEstado.setText('Activo')
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
			else:
				self.btnEstado.setText('Inactivo')
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkred; color: white; font-size: 12px;")

		self.contador_registros.setText(str(self.registroactual))
		self.totalRegistros.setText(str(lv_TotalRegistros))


	def nuevoRegistro(self):
		self.modo = 0
		self.txtUsuario.setEnabled(True)
		self.txtUsuario.setText('')
		self.txtResponsable.setText('')
		self.btnEstado.setEnabled(False)
		self.btnReinicioClave.setEnabled(False)
		self.btnEstado.setText("Activo")
		self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")

		#Habilita Tab Registro
		self.tabWidget.setTabEnabled(0, True)
		#Deshabilitar Tab Lista
		self.tabWidget.setTabEnabled(1, False)


	def editarRegistro(self):
		self.modo = 1
		fila = self.tabla_usuarios.currentRow()
		if fila != -1:
			lv_Usuario = self.tabla_usuarios.item(fila,0).text()
			lv_Responsable = self.tabla_usuarios.item(fila,1).text()
			lv_activo = self.tabla_usuarios.item(fila,2).text()
			self.usuario_Original = lv_Usuario
			self.txtUsuario.setText(lv_Usuario)
			self.txtResponsable.setText(lv_Responsable)
			self.btnEstado.setText(lv_activo)
			if self.btnEstado.text() == "Activo":
				self.btnEstado.setText("Activo")
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
				lv_activo = 'Activo'
			else:
				self.btnEstado.setText("Inactivo")
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkred; color: white; font-size: 12px;")
				lv_activo = 'Inactivo'

			if lv_Usuario == "ADMIN":
				#QMessageBox.warning(self,"Alerta...!", "El usuario <ADMIN> esta protegido, no puede editar este registro", QMessageBox.Ok)
				self.txtUsuario.setEnabled(False)
				#Habilita Tab Registro
				self.tabWidget.setTabEnabled(0, True)
				#Deshabilitar Tab Lista
				self.tabWidget.setTabEnabled(1, False)
				self.txtResponsable.setFocus()
			else:
				self.txtUsuario.setEnabled(True)
				self.registroactual = self.tabla_usuarios.currentRow()
				self.total_registros = self.tabla_usuarios.rowCount()
				self.modo = 3
				#Habilita Tab Registro
				self.tabWidget.setTabEnabled(0, True)
				#Deshabilitar Tab Lista
				self.tabWidget.setTabEnabled(1, False)
				self.txtUsuario.setFocus()
		else:
			QMessageBox.warning(self,"Alerta...!", "Debe seleccionar un usuario de la lista antes de editar", QMessageBox.Ok)


	def buscarUsuario(self,lv_usuario):
		rows=[]
		buscar_usuario = "select usuario, responsable from usuarios WHERE usuario = '%s'" % (lv_usuario)
		self.cursor.execute(buscar_usuario)
		for rows in self.cursor:
			continue
		if rows==[]:
			self.encontrar = False
		else:
			self.encontrar = True

	def actualizaRegistro(self, lv_usuarioNuevo, lv_usuario, lv_reemplaza_usuario):
		self.responsable = self.txtResponsable.text().upper()
		lv_activo = self.btnEstado.text()
		fila = self.tabla_usuarios.currentRow()
		if lv_reemplaza_usuario == True:
			actualiza_registro = "UPDATE usuarios SET usuario = '%s', responsable = '%s', estado = '%s' where usuario='%s'" % (lv_usuarioNuevo, self.responsable, lv_activo, lv_usuario)
		else:
			actualiza_registro = "UPDATE usuarios SET responsable = '%s', estado = '%s' where usuario='%s'" % (self.responsable, lv_activo, lv_usuario)
		self.cursor.execute(actualiza_registro)
		self.tabla_usuarios.setItem(fila,0, QTableWidgetItem(lv_usuarioNuevo))
		self.tabla_usuarios.setItem(fila,1, QTableWidgetItem(self.responsable))
		self.tabla_usuarios.setItem(fila,2, QTableWidgetItem(lv_activo))


	def agregarRegistro(self):
		self.Usuario_Nuevo = self.txtUsuario.text().upper()
		self.responsable = self.txtResponsable.text().upper()
		lv_clave_temporal = bytes("TEMPORAL", 'utf-8')
		lv_password = hashlib.sha256(lv_clave_temporal).hexdigest()
		inserta_registro = "INSERT INTO usuarios VALUES('%s', '%s', '%s')" % (self.Usuario_Nuevo, self.responsable, lv_password)
		self.cursor.execute(inserta_registro)
		#creando una fila en la matriz
		self.consultarTabla()
		self.total_registros = self.tabla_usuarios.rowCount()
		index = 0
		while index < self.total_registros:
			if self.tabla_usuarios.item(index,0).text() == self.Usuario_Nuevo:
				break;
			index = index + 1
		fila = index
		columna = 0
		posicion = self.tabla_usuarios.item(fila, columna)
		self.tabla_usuarios.scrollToItem(posicion)
		self.tabla_usuarios.setCurrentCell(fila, columna)
		self.txtUsuarioSeleccionado.setText(self.tabla_usuarios.item(fila, 0).text())

	def guardarRegistro(self):
		self.estado = 0
		self.Usuario_Nuevo = self.txtUsuario.text().upper()
		self.responsable = self.txtResponsable.text().upper()
		self.txtUsuario.setText(self.Usuario_Nuevo)
		self.txtResponsable.setText(self.responsable)
		if self.modo == 0:
			self.contador_registros.setText(str(self.proximo_registro))
			self.totalRegistros.setText(str(self.proximo_registro))
			self.buscarUsuario(self.Usuario_Nuevo)
			if self.encontrar == True:
				QMessageBox.warning(self,"Base de Datos", "El usuario a registrar ya esta existe previamente...", QMessageBox.Ok)
				self.txtUsuario.setText(self.usuario_Original)
				self.estado = 1
			else:
				self.agregarRegistro()
				QMessageBox.information(self,"Base de Datos", "El registro fue agregado exitosamente...Clave Temporal: 'TEMPORAL'", QMessageBox.Ok)
				self.estado = 0
				self.mensaje1.setText("")
				self.btnEstado.setEnabled(True)
				self.btnReinicioClave.setEnabled(True)
				self.consultarTabla()
				#Deshabilita Tab Registro
				self.tabWidget.setTabEnabled(0, False)
				#Habilitar Tab Lista
				self.tabWidget.setTabEnabled(1, True)
		else:
			if self.usuario_Original == self.txtUsuario.text():
				self.actualizaRegistro(self.usuario_Original, self.usuario_Original,False)
				QMessageBox.information(self,"Base de Datos", "El registro fue actualizado exitosamente...", QMessageBox.Ok)
				self.estado = 0
				self.mensaje1.setText("")
				#Deshabilita Tab Registro
				self.tabWidget.setTabEnabled(0, False)
				#Habilitar Tab Lista
				self.tabWidget.setTabEnabled(1, True)
			else:
				respuesta=QMessageBox.warning(self,"Adventencia", "Esta seguro de cambiar usuario: " + self.usuario_Original + " por el usuario: " + self.txtUsuario.text(), QMessageBox.Yes | QMessageBox.No)
				if respuesta == QMessageBox.Yes:
					self.buscarUsuario(self.Usuario_Nuevo)
					if self.encontrar == False:
						self.actualizaRegistro(self.Usuario_Nuevo, self.usuario_Original,True)
						QMessageBox.information(self,"Base de Datos", "El registro fue actualizado exitosamente...", QMessageBox.Ok)
						self.estado = 2
						#Deshabilita Tab Registro
						self.tabWidget.setTabEnabled(0, False)
						#Habilitar Tab Lista
						self.tabWidget.setTabEnabled(1, True)
					else:
						QMessageBox.warning(self,"Base de Datos", "El usuario a registrar ya existe en sistema...", QMessageBox.Ok)
						self.txtUsuario.setText(self.usuario_Original)
						self.estado = 1
				else:
					self.txtUsuario.setText(self.usuario_Original)
					self.estado = 1

	def cambiarEstado(self):
		fila = self.tabla_usuarios.currentRow()
		lv_usuario = self.tabla_usuarios.item(fila,0).text()
		if lv_usuario != 'ADMIN':
			if self.btnEstado.text() == "Inactivo":
				self.btnEstado.setText("Activo")
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkgreen; color: white; font-size: 12px;")
				lv_activo = 'Activo'
			else:
				self.btnEstado.setText("Inactivo")
				self.btnEstado.setStyleSheet("border: 1px solid black; background: darkred; color: white; font-size: 12px;")
				lv_activo = 'Inactivo'
			if self.modo != 0:
				actualiza_registro = "UPDATE usuarios SET estado = '%s' where usuario ='%s'" % (lv_activo, lv_usuario)
				self.cursor.execute(actualiza_registro)

				if self.btnEstado.text() == "Inactivo":
					self.tabla_usuarios.setItem(fila, 2, QTableWidgetItem('Inactivo'))
				else:
					self.tabla_usuarios.setItem(fila, 2, QTableWidgetItem('Activo'))
		else:
			QMessageBox.information(self,"Base de Datos", "Usuario ADMIN esta protegido, no se puede inactivar", QMessageBox.Ok)

	def reiniciarClave(self):
		lv_usuario_activo = self.txtUsuarioActivo.text()
		fila = self.tabla_usuarios.currentRow()
		lv_usuario = self.tabla_usuarios.item(fila,0).text()
		if lv_usuario_activo == 'ADMIN':
			if lv_usuario != 'ADMIN':
				lv_clave_temporal = bytes("TEMPORAL", 'utf-8')
				lv_password = hashlib.sha256(lv_clave_temporal).hexdigest()
				actualiza_registro = "UPDATE usuarios SET clave = '%s' where usuario ='%s'" % (lv_password, lv_usuario)
				QMessageBox.information(self,"Base de Datos", "La clave ha sido reiniciada exitosamente...Clave Temporal: 'TEMPORAL'", QMessageBox.Ok)
			else:
				QMessageBox.information(self,"Base de Datos", "El usuario ADMIN esta protegido no puede reiniciar clave, \n Si desea cambiar la clave de Admin dirijase al modulo \n 'Cambiar Clave' del menu usuarios", QMessageBox.Ok)
		else:
			QMessageBox.information(self,"Base de Datos", "Solo el usuario ADMIN puede reiniciar claves...", QMessageBox.Ok)


	def actContadorActual(self):
		fila = self.tabla_usuarios.currentRow()
		usuario = self.tabla_usuarios.item(fila, 0).text()
		self.txtUsuarioSeleccionado.setText(usuario) 


	def cerrar_dialogo(self):
		self.close()

	def ordenarTabla(self):
		if self.optUsuario.isChecked():
			self.tabla_usuarios.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		else:
			self.tabla_usuarios.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)

	def buscarDatoUsuario(self):
		lv_texto = self.txtFiltro.text().upper()
		validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
		if self.optUsuario.isChecked()== True:
			columna = 0
		else:
			columna = 1
		index = self.tabla_usuarios.rowCount()
		fila=0
		encontrar = 0
		while fila < index:
			lv_busqueda = self.tabla_usuarios.item(fila,columna).text()
			if lv_texto in lv_busqueda:
				encontrar = 1
				break;
			fila = fila + 1
		if encontrar == 1:
			posicion = self.tabla_usuarios.item(fila, columna)
			self.tabla_usuarios.scrollToItem(posicion)
			self.tabla_usuarios.setCurrentCell(fila, columna)
			self.txtUsuarioSeleccionado.setText(self.tabla_usuarios.item(fila, 0).text())
			return True
		else:
			return False


#	def eliminarRegistro(self):
#		if self.txtUsuario.text() == "ADMIN":
#			QMessageBox.warning(self,"Alerta...!", "El usuario <ADMIN> esta protegido, no puede eliminar este registro", QMessageBox.Ok)
#		elif self.txtUsuarioActivo.text() == self.txtUsuario.text():
#			QMessageBox.warning(self,"Alerta...!", "No puede eliminar al usuario activo, desloguee e ingrese con otra cuenta administrador para eliminar", QMessageBox.Ok)
#		else:
#			self.modo = 3
#			self.registroactual = self.tabla_usuarios.currentRow() + 1
#			self.proximo_registro = 1
#			self.total_registros = self.tabla_usuarios.rowCount()
#			if self.registroactual == 0:
#				QMessageBox.warning(self,"Error", "No puede borrar fin de archivo", QMessageBox.Ok)
#			else:
#				respuesta=QMessageBox.warning(self,"Adventencia", "Desea eliminar el registro actual?", QMessageBox.Yes | QMessageBox.No)
#				if respuesta == QMessageBox.Yes:
#					self.usuario_Original = self.txtUsuario.text()
#					eliminar_usuario = "DELETE from usuarios WHERE usuario='%s'" % (self.usuario_Original) 
#					self.cursor.execute(eliminar_usuario)
#					self.consultarTabla()
#					QMessageBox.information(self,"Base de Datos", "El registro fue eliminado exitosamente...", QMessageBox.Ok)
#					self.usuario_Original = ''
#					self.Usuario_Nuevo = ''
#					self.responsable = ''
#					self.estado = 0
#					self.encontrar = False
					#Deshabilita Tab Registro
#					self.tabWidget.setTabEnabled(0, False)
					#Habilitar Tab Lista
#					self.tabWidget.setTabEnabled(1, True)



#app = QApplication(sys.argv)
#PRegistroUsuario = DialogoRegUsuarios()
#PRegistroUsuario.show()
#app.exec_()

