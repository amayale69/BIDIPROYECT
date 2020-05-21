#-----------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                          #
# Programador: Luis Amaya                                                           #
# Analistas: Jose Astudillo / josmary Botaban                                       #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre    #
# Octubre (2018)                                                                    #
# Version 1.0                                                                       #
# Modulo: Manual de Ayuda en Linea                                                  #
# Descripción: Abre una ventana de ayuda con la informacion de como usar el sistema #
#-----------------------------------------------------------------------------------#

# Importacion de librerias del sistema
import sys, re
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMainWindow, QAction, QPushButton, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib
import ctypes #GetSystemMetrics
import os.path as path
from datetime import datetime, date, time, timedelta
import calendar

class DialogoAyuda(QDialog):
	def __init__(self):

		QDialog.__init__(self)
		uic.loadUi("manualSistema.ui", self)
		self.setEnabled(True)
		#Colocar titulo de la pantalla
		self.setWindowTitle("SIPROYECT - Manual de Ayuda Rapida del Usuario")
		self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
		#Operacion para centrar la ventana en la pantalla
		resolucion = ctypes.windll.user32
		resolucion_ancho = resolucion.GetSystemMetrics(0)
		resolucion_alto = resolucion.GetSystemMetrics(1)
		left = (resolucion_ancho / 2) - (self.frameSize().width() / 2)
		top = (resolucion_alto / 2) - (self.frameSize().height() / 2)
		self.move(left, top)

		self.btnAyudaPublico.clicked.connect(self.AyudaPublico)
		self.btnAyudaProyectoRecientes.clicked.connect(self.ProyectoReciente)
		self.btnProyectoRecientes.clicked.connect(self.ProyectoReciente)
		self.btnAyudaBiblioteca.clicked.connect(self.AyudaBiblioteca)
		self.btnAyudaBiblioteca2.clicked.connect(self.AyudaBiblioteca)
		self.btnAyudaIdentificarse.clicked.connect(self.AyudaIdentificarse)
		self.btnAyudaCambioClave.clicked.connect(self.AyudaCambioClave)
		self.btnAyudaRegUsuarios.clicked.connect(self.AyudaRegUsuarios)
		self.btnAyudaRegProyectos.clicked.connect(self.AyudaRegProyectos)
		self.btnAyudaSolvencias.clicked.connect(self.AyudaSolvencias)
		self.btnEstadistica.clicked.connect(self.AyudaEstadisticas)
		self.btnRegresarMenuGeneral.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_2.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_3.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_4.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_5.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_6.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_7.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_8.clicked.connect(self.VolverALista)
		self.btnRegresarMenuGeneral_9.clicked.connect(self.VolverALista)

		self.formato_fecha = "%Y-%m-%d %H:%M:%S"
		self.hoy = datetime.today()
		self.fechareg = self.hoy.strftime(self.formato_fecha)

		self.tabWidget.setTabEnabled(1, False)
		self.tabWidget.setTabEnabled(2, False)
		self.tabWidget.setTabEnabled(3, False)
		self.tabWidget.setTabEnabled(4, False)
		self.tabWidget.setTabEnabled(5, False)
		self.tabWidget.setTabEnabled(6, False)
		self.tabWidget.setTabEnabled(7, False)
		self.tabWidget.setTabEnabled(8, False)
		self.tabWidget.setTabEnabled(9, False)
		self.tabWidget.setTabEnabled(0, True)
		self.tabWidget.setCurrentIndex(0)



	def AyudaPublico(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(1, True)
		self.tabWidget.setCurrentIndex(1)

	def ProyectoReciente(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(2, True)
		self.tabWidget.setCurrentIndex(2)

	def AyudaBiblioteca(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(3, True)
		self.tabWidget.setCurrentIndex(3)

	def AyudaIdentificarse(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(4, True)
		self.tabWidget.setCurrentIndex(4)

	def AyudaRegUsuarios(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(5, True)
		self.tabWidget.setCurrentIndex(5)

	def AyudaCambioClave(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(6, True)
		self.tabWidget.setCurrentIndex(6)

	def AyudaRegProyectos(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(7, True)
		self.tabWidget.setCurrentIndex(7)

	def AyudaEstadisticas(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(8, True)
		self.tabWidget.setCurrentIndex(8)

	def AyudaSolvencias(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Principal
		self.tabWidget.setTabEnabled(TabActivo, False)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(9, True)
		self.tabWidget.setCurrentIndex(9)

	def VolverALista(self):
		TabActivo = self.tabWidget.currentIndex()
		#Deshabilita Tab Registro
		self.tabWidget.setTabEnabled(0, True)
		
		#Habilitar Tab Lista
		self.tabWidget.setTabEnabled(TabActivo, False)
		self.tabWidget.setCurrentIndex(0)


	def cerrar_dialogo(self):
		self.close()


# Constructor para ejecutar el modulo independiente del programa principal, descarcar para hacer pruebas

#app = QApplication(sys.argv)
#PAyuda = DialogoAyuda()
#PAyuda.show()
#app.exec_()

