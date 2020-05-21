#-------------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                            #
# Programador: Luis Amaya                                                             #
# Analistas: Jose Astudillo / josmary Botaban                                         #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre      #
# Octubre (2018)                                                                      #
# Version 1.0                                                                         #
# Modulo: Actualizacion de Claves                                                     #
# Descripción: Solicita al usuario la nueva clave y su confirmación para actualizarla #
#              en la Base de Datos                                                    # 
#-------------------------------------------------------------------------------------#

# Importacion de librerias del sistema
import sys, re
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMainWindow, QAction, QPushButton, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib
import ctypes #GetSystemMetrics
import os.path as path

class DialogoActClave(QDialog):
	def __init__(self):

		QDialog.__init__(self)
		uic.loadUi("actualiza_clave.ui", self)
		self.setEnabled(True)
		#Colocar titulo de la pantalla
		self.setWindowTitle("Mantenimiento de Claves")
		self.lblTituloPantalla.setText("Actualización de Claves")
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

		#Conectar Base de Datos
		cad_con = "dbname='%s' user='%s' password='%s' host='localhost'" % (self.BD_Name, self.BD_User, self.BD_Pass)
		try:
			self.db = psycopg2.connect(cad_con)
		except:
			QMessageBox.warning(self, "Error de Base de Datos", "Ocurrio un error al intentar comunicarse con la Base de Datos", QMessageBox.Ok)
			self.quit()
		else:
			self.db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
			self.cursor = self.db.cursor()

		#configurando loa slots de señales de los botones
		self.btnGuardar.clicked.connect(self.actualizaRegistro)
		self.btnDescartar.clicked.connect(self.cerrar_dialogo)
		self.txtClaveNueva.textChanged.connect(self.validar_clave)
		self.txtClaveConfirmar.textChanged.connect(self.validar_clave2)

		#Iniciar valores de variables de control de registros
		self.usuario = self.txtUsuario.text()
		self.Responsable = self.txtResponsable.text()
		self.ClaveNueva = ''
		self.ClaveConfirmar = ''
		self.ClaveCodificada = ''
		self.mensaje1.setText("")
		self.mensaje2.setText("")
		
	def cerrar_dialogo(self):
		self.close()

	# Rutina para actualizar las claves del usuario en la Base de Datos
	def actualizaRegistro(self):
		if self.txtClaveNueva.text() != '':
			self.ClaveNueva = self.txtClaveNueva.text().upper()
			self.ClaveConfirmar = self.txtClaveConfirmar.text().upper()
			self.usuario = self.txtUsuario.text()
			self.Responsable = self.txtResponsable.text()
			self.ClaveCodificada = hashlib.sha256(bytes(self.ClaveNueva,'utf-8')).hexdigest()
			if self.ClaveNueva == self.ClaveConfirmar:
				actualiza_registro = "UPDATE usuarios SET clave = '%s' where usuario='%s'" % (self.ClaveCodificada, self.usuario)
				self.cursor.execute(actualiza_registro)
				QMessageBox.information(self, "Base de Datos", "Clave actualizada exitosamente..!!", QMessageBox.Ok)
				self.close()
			else:
				QMessageBox.warning(self, "Error..", "La clave de confirmacion no coincide con clave nueva", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Error..", "La clave no puede estar vacia. Introduzca una clave aceptable no menor de 4 digitos", QMessageBox.Ok)

	# Rutina que valida los caracteres que conforman la clave y su tamaño en caracteres
	def validar_clave(self):
		self.ClaveNueva = self.txtClaveNueva.text().upper()
		validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', self.ClaveNueva, re.I)
		if self.ClaveNueva == "":
			self.txtClaveNueva.setStyleSheet("border: 1px solid yellow;")
			return False
		elif not validar:
			self.txtClaveNueva.setStyleSheet("border: 1px solid red;")
			return False
		elif len(self.ClaveNueva) < 4:
			self.txtClaveNueva.setStyleSheet("border: 1px solid yellow;")
		else:
			self.txtClaveNueva.setStyleSheet("border: 1px solid green;")
			return True

	# Rutina valida la clave de verificacion
	def validar_clave2(self):
		self.ClaveConfirmar = self.txtClaveConfirmar.text().upper()
		validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', self.ClaveConfirmar, re.I)
		if self.ClaveConfirmar == "":
			self.txtClaveConfirmar.setStyleSheet("border: 1px solid yellow;")
			return False
		elif not validar:
			self.txtClaveConfirmar.setStyleSheet("border: 1px solid red;")
			return False
		elif len(self.ClaveConfirmar) < 4:
			self.txtClaveConfirmar.setStyleSheet("border: 1px solid yellow;")
		else:
			self.txtClaveConfirmar.setStyleSheet("border: 1px solid green;")
			return True

# Constructor para ejecutar el modulo independiente del programa principal, descarcar para hacer pruebas

#app = QApplication(sys.argv)
#PActClave = DialogoActClave()
#PActClave.show()
#app.exec_()

