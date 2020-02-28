import sys, re
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMainWindow, QAction, QPushButton, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QIODevice
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib
import ctypes #GetSystemMetrics
import os.path as path
class DialogoAcceso(QDialog):
	def __init__(self):

		QDialog.__init__(self)
		uic.loadUi("registrar_BD.ui", self)
		self.setEnabled(True)
		#Colocar titulo de la pantalla
		self.setWindowTitle("SIPROYECT - Registrar Base de Datos")
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
			#print("Extrayendo BD: " + self.BD_Name)
			#print("Extrayendo usuario: " + self.BD_User)
			#print("Extrayendo BD: " + self.BD_Pass)
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
		#print("Añadiendo BD: " + self.BD_Name)
		#print("Añadiendo usuario: " + self.BD_User)
		#print("Añadiendo BD: " + self.BD_Pass)
		if self.txtDatabase.text() == '' or self.txtUsuarioBD.text() == '':
			QMessageBox.warning(self, "Error", "No ha cargado los datos de acceso a la Base de Datos, registre los datos o pulse salir", QMessageBox.Ok)
		else:
			self.archivo_infosvr = open('regsvr.txt','w')
			self.archivo_infosvr.write(self.BD_Name + '\n')
			self.archivo_infosvr.write(self.BD_User + '\n')
			self.archivo_infosvr.write(self.BD_Pass)
			self.archivo_infosvr.close
			print("Proceso Archivo de Registro Creado y/o Actualizado...")
			self.close()

		
app = QApplication(sys.argv)
PRegserver = DialogoAcceso()
PRegserver.show()
app.exec_()
