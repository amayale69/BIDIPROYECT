#---------------------------------------------------------------------------------#
# Programa: Biblioteca Digital de Proyectos de Informatica                        #
# Programador: Luis Amaya                                                         #
# Analistas: Jose Astudillo / josmary Botaban                                     #
# Producto desarrollado para el PNF de Informatica del UPTJAA Extension El Tigre  #
# Octubre (2018)                                                                  #
# Version 1.0                                                                     #
# Modulo: Pantalla principal del sistema                                          #
# Descripción: Genera la pantalla principal con el menu de opciones y coordina la #
#              comunicacion con los otros módulos del sistema                     # 
#---------------------------------------------------------------------------------#

# Importacion de librerias del sistema
import sys, re
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox, QDialog, QComboBox
from PyQt5.QtWidgets import QLineEdit, QLabel, QGridLayout, QTableWidget, QTableView, QTableWidgetItem
from PyQt5.QtWidgets import QPushButton, QGridLayout, QAbstractItemView, QHeaderView, QMenu, QActionGroup, QWidget

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QIODevice, QSortFilterProxyModel, QModelIndex, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib

import ctypes #GetSystemMetrics
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import webbrowser as wb
import easygui as eg
from datetime import datetime, date, time, timedelta
import calendar
import os.path as path

#Importando modulos del sistema
from registrar_usuario import *
from actualizar_claves import *
from emision_solvencias import *
from biblioteca import *
from manual_ayuda import *
from registro_integrado_proyectos import *
from consulta_proyectos import *
from estadisticas import *

#Clase heredada de QMainWindow (Constructor de Ventana)
class BDPIApp(QMainWindow, DialogoAyuda, DialogoActClave, DialogoRegUsuarios, DialogoIntProyectos, DialogoBiblioteca, DialogoConsultaProyectos, DialogoSolvencias,DialogoEstadistica):

    #Método constructor de ventana
    def __init__(self):
        self.archivo_infosvr = ''
        self.infosvr = []
        self.lista = []
        self.BD_Name = ''
        self.BD_User = ''
        self.BD_Pass = ''
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
            QMessageBox.warning(self, "Error de Base de Datos", "No se encuentra el archivo de configuracion de coneccion a Base de Datos, \n Ejecute programa registrar_server.pyw para crear informacion de conexion", QMessageBox.Ok)			
            self.close()

        # Abriendo Base de Datos
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

        #Iniciar el objeto DialogoAcceso

        DialogoRegUsuarios.__init__(self)
        self.setEnabled(True)
        self.PRegUsuarios = DialogoRegUsuarios()

        DialogoActClave.__init__(self)
        self.setEnabled(True)
        self.PActualizaClave = DialogoActClave()

        DialogoAyuda.__init__(self)
        self.setEnabled(True)
        self.PAyuda = DialogoAyuda()

        DialogoSolvencias.__init__(self)
        self.setEnabled(True)
        self.PSolvencias = DialogoSolvencias()

        DialogoBiblioteca.__init__(self)
        self.setEnabled(True)
        self.PBiblioteca = DialogoBiblioteca()

        DialogoIntProyectos.__init__(self)
        self.setEnabled(True)
        self.PControlProyectos = DialogoIntProyectos()

        DialogoConsultaProyectos.__init__(self)
        self.setEnabled(True)
        self.PConsultaProyectos = DialogoConsultaProyectos()

        DialogoEstadistica.__init__(self)
        self.setEnabled(True)
        self.PEstadistica = DialogoEstadistica()

        #Iniciar el objeto QMainWindow
        QMainWindow.__init__(self)
        #Cargar el diseño de la ventana PyQt
        uic.loadUi("BIDIPROYECT.ui", self)
        self.resize(1200, 600)
        #Barra de estado
        self.statusBar().showMessage("Bienvenidos...")

        self.menu_usuarios_cambio_clave.setEnabled(False)
        self.menu_usuarios_registrar_usuarios.setEnabled(False)
        self.menuProyectos.setEnabled(False)
        self.menuConsultas.setEnabled(True)
        self.menuReportes.setEnabled(False)

        #Operacion para centrar la ventana en la pantalla
        resolucion = ctypes.windll.user32
        resolucion_ancho = resolucion.GetSystemMetrics(0)
        resolucion_alto = resolucion.GetSystemMetrics(1)
        left = (resolucion_ancho / 2) - (self.frameSize().width() / 2)
        top = (resolucion_alto / 2) - (self.frameSize().height() / 2) - 40
        self.move(left, top)

        self.VentanaPrincipal = QMainWindow()
        
         # Configurando Tabla de Proyectos Recientes

        self.txtProyectoSeleccionado.setText("")
        self.tabla_proyectos_recientes.setAlternatingRowColors(True)
        #Instruccion para deshabilitar edicion
        self.tabla_proyectos_recientes.setEditTriggers(QTableWidget.NoEditTriggers)
        # Deshabilitar el comportamiento de arrastrar y soltar
        self.tabla_proyectos_recientes.setDragDropOverwriteMode(False)
        # Seleccionar toda la fila
        self.tabla_proyectos_recientes.setSelectionBehavior(QTableWidget.SelectRows)
        # Seleccionar una fila a la vez
        self.tabla_proyectos_recientes.setSelectionMode(QTableWidget.SingleSelection)
        # Especifica dónde deben aparecer los puntos suspensivos "..." cuando se muestran
        # textos que no encajan
        self.tabla_proyectos_recientes.setTextElideMode(Qt.ElideRight)# Qt.ElideNone
        # Establecer el ajuste de palabras del texto 
        self.tabla_proyectos_recientes.setWordWrap(False)
        # Habilitar clasificación
        self.tabla_proyectos_recientes.setSortingEnabled(True)
        # Establecer el número de columnas
        self.tabla_proyectos_recientes.setColumnCount(16)
        # Establecer el número de filas
        self.tabla_proyectos_recientes.setRowCount(0)
        # Alineación del texto del encabezado
        self.tabla_proyectos_recientes.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter| Qt.AlignCenter)
        # Deshabilitar resaltado del texto del encabezado al seleccionar una fila
        self.tabla_proyectos_recientes.horizontalHeader().setHighlightSections(True)
        # Hacer que la última sección visible del encabezado ocupa todo el espacio disponible
        self.tabla_proyectos_recientes.horizontalHeader().setStretchLastSection(True)
        # Ocultar encabezado vertical
        self.tabla_proyectos_recientes.verticalHeader().setVisible(False)
        # Establecer altura de las filas
        self.tabla_proyectos_recientes.verticalHeader().setDefaultSectionSize(20)
        # self.tabla_personas.verticalHeader().setHighlightSections(True)
        nombreColumnas = ("Proyecto", "Trayecto", "Titulo", "Metodologia", "Tipo Desarrollo", "Año", "ID Trayecto", "ID Seccion", "ID Proyecto", "Seccion", "Tipo Seccion", "Año Prosecucion", "Grupo Desarrollo", "Nombre Informe", "Nombre Desarrollo", "Nombre Manual")
        # Establecer las etiquetas de encabezado horizontal usando etiquetas
        self.tabla_proyectos_recientes.setHorizontalHeaderLabels(nombreColumnas)
        # Establecer ancho de las columnas
        for indice, ancho in enumerate((180, 85, 220, 140, 150, 90, 60, 60, 60, 60, 60, 60, 60, 80, 80, 80), start=0):
            self.tabla_proyectos_recientes.setColumnWidth(indice, ancho)
        self.tabla_proyectos_recientes.setColumnHidden(5, True)
        self.tabla_proyectos_recientes.setColumnHidden(6, True)
        self.tabla_proyectos_recientes.setColumnHidden(7, True)
        self.tabla_proyectos_recientes.setColumnHidden(8, True)
        self.tabla_proyectos_recientes.setColumnHidden(9, True)
        self.tabla_proyectos_recientes.setColumnHidden(10, True)
        self.tabla_proyectos_recientes.setColumnHidden(11, True)
        self.tabla_proyectos_recientes.setColumnHidden(12, True)
        self.tabla_proyectos_recientes.setColumnHidden(13, True)
        self.tabla_proyectos_recientes.setColumnHidden(14, True)
        self.tabla_proyectos_recientes.setColumnHidden(15, True)

        # Iniciando variables publicas
        self.proyecto = ""
        self.trayecto = ""
        self.titulo = ""
        self.metodologia = ""
        self.tdesarrollo = ""
        self.periodo_academico = ""
        self.IDTrayecto = ""
        self.IDSeccion = ""
        self.IDProyecto = ""
        self.usuario = ''
        self.lv_clavecod2 = ''
        self.lv_responsable2 = ''
        self.responsable = ''
        self.mensaje.setText('')
        self.txtUsuarioActivo.setText(self.usuario)
        self.txtResponsable.setText(self.responsable)

        # Configurar Slots de Eventos
        self.btnAcceder.clicked.connect(self.identificarse)
        self.btnSalir.clicked.connect(self.Salir)
        
        #Configurando informacion a mostrar en pantalla
        self.lblInicioSesion1.show()
        self.lblInicioSesion2.show()
        self.lblUsuario.show()
        self.lblClave.show()
        self.txtUsuario.show()
        self.txtClave.show()
        self.txtClavecod.hide()
        self.txtUsuarioActivo.hide()
        self.chkActivo.hide()
        self.txtProyectoSeleccionado.hide()
                        
        self.lblBienvenidoUsuario1.hide()
        self.lblBienvenidoUsuario2.setText('')
        self.lblBienvenidoUsuario2.hide()
        self.llenarTablaRecientes()
                
        self.optProyecto.clicked.connect(self.ordenarTabla)
        self.optTrayecto.clicked.connect(self.ordenarTabla)
        self.optTitulo.clicked.connect(self.ordenarTabla)
        self.optMetodo.clicked.connect(self.ordenarTabla)
        self.optTDesarrollo.clicked.connect(self.ordenarTabla)
        self.txtUsuario.textChanged.connect(self.validar_usuario)
        self.txtClave.textChanged.connect(self.validar_clave)
        
        #Crear disparador para saber el numero de la fila de la tabla que ha sido seleccionada
        self.tabla_proyectos_recientes.itemClicked.connect(self.actSeleccion)
        self.tabla_proyectos_recientes.itemDoubleClicked.connect(self.visualizarProyecto)

        #Crear disparador de evento para buscar datos en la tabla por texto introducido por usuario
        self.txtFiltro.textChanged.connect(self.buscarDato)

        #Configurando los eventos disparadores de los menus
        # Menu Cambio de Clave
        self.menu_usuarios_cambio_clave.setShortcut("Alt+a") #Atajo de teclado
        self.menu_usuarios_cambio_clave.setStatusTip("Actualizar claves") #Mensaje en la barra de estado
        self.menu_usuarios_cambio_clave.triggered.connect(self.menuUsuariosCClaves) #Lanzador
        self.menuUsuarios.addAction(self.menu_usuarios_cambio_clave)

        #Menu Registro de Usuario
        self.menu_usuarios_registrar_usuarios.setShortcut("Alt+u") #Atajo de teclado
        self.menu_usuarios_registrar_usuarios.setStatusTip("Acceder a Registro de Usuarios") #Mensaje en la barra de estado
        self.menu_usuarios_registrar_usuarios.triggered.connect(self.menuRegUsuarios) #Lanzador
        self.menuUsuarios.addAction(self.menu_usuarios_registrar_usuarios)

        self.menu_Control_Proyectos.setShortcut("Alt+p") #Atajo de teclado
        self.menu_Control_Proyectos.setStatusTip("Acceder a Registro de Proyectos") #Mensaje en la barra de estado
        self.menu_Control_Proyectos.triggered.connect(self.menuControlProyectos) #Lanzador
        self.menuProyectos.addAction(self.menu_Control_Proyectos)

        self.menuBiblioteca.setShortcut("Alt+b") #Atajo de teclado
        self.menuBiblioteca.setStatusTip("Acceso a Biblioteca") #Mensaje en la barra de estado
        self.menuBiblioteca.triggered.connect(self.Biblioteca) #Lanzador
        self.menuConsultas.addAction(self.menuBiblioteca)

        self.menu_reportes_solvencias.setShortcut("Alt+s") #Atajo de teclado
        self.menu_reportes_solvencias.setStatusTip("Emision de Solvencias Academicas") #Mensaje en la barra de estado
        self.menu_reportes_solvencias.triggered.connect(self.menuEmisionSolvencias) #Lanzador
        self.menuReportes.addAction(self.menu_reportes_solvencias)

        self.menu_reportes_estadisticas.setShortcut("Alt+e") #Atajo de teclado
        self.menu_reportes_estadisticas.setStatusTip("Reporte Estadistico de Proyectos") #Mensaje en la barra de estado
        self.menu_reportes_estadisticas.triggered.connect(self.Estadisticas) #Lanzador
        self.menuReportes.addAction(self.menu_reportes_estadisticas)

        self.Manual_de_Usuario.setShortcut("Ctrl+h") #Atajo de teclado
        self.Manual_de_Usuario.setStatusTip("Manual de ayuda del sistema") #Mensaje en la barra de estado
        self.Manual_de_Usuario.triggered.connect(self.manualAyuda) #Lanzador
        self.menuAyuda.addAction(self.Manual_de_Usuario)

        self.txtResponsable.setText('')
        self.txtUsuarioActivo.setText('')

        self.usuario_activo = True
        self.usuario = ""
        self.responsable = ""
        self.txtUsuarioActivo.hide()
        self.txtResponsable.hide()
        self.menuConsultas.setEnabled(True)
        self.menuReportes.setEnabled(False)
        self.menuUsuarios.setEnabled(False)
        self.mensaje1.setText("")
        self.mensaje2.setText("")
        self.lblBienvenidoUsuario2.hide()
        self.lblBienvenidoUsuario2.setText('')
        self.lblBienvenidoUsuario2.hide()

        self.setEnabled(True)

    def llenarTablaRecientes(self):

        #for filas in range(30):
        #    self.tabla_proyectos_recientes.insertRow(filas) 
        #    for columnas in range(9):
        #        texto = "Fila %s Columna %s" % (str(filas), str(columnas))
        #        self.tabla_proyectos_recientes.setItem(filas, columnas, QTableWidgetItem(texto))
        self.tabla_proyectos_recientes.setSortingEnabled(False)
        if self.tabla_proyectos_recientes.rowCount() > 0:
            self.tabla_proyectos_recientes.clearSelection()
            self.tabla_proyectos_recientes.clearContents()
            index2 = self.tabla_proyectos_recientes.rowCount()
            while index2 > 0:
                index = index2 - 1
                self.tabla_proyectos_recientes.removeRow(index)
                index2 = index2 - 1

        #cursor_lista_proyectos = "SELECT proy.codigo_proyecto, proy.titulo_proyecto, met.descripcion as metodo, tdes.tipo_desarrollo, tr.periodo_academico, tr.id_trayecto, proy.id_proyecto FROM proyectos AS proy INNER JOIN metodologia AS met ON proy.FK_id_metodo = met.id_metodo INNER JOIN tipo_de_desarrollo AS tdes ON tdes.id_tipo_desarrollo = proy.FK_id_tipo_desarrollo INNER JOIN secciones AS sec on sec.id_seccion = proy.FK_id_seccion INNER JOIN trayecto AS tr on tr.id_trayecto = sec.FK_id_trayecto ORDER BY proy.codigo_proyecto desc LIMIT 20"
        #self.cursor.execute(cursor_lista_proyectos)


        cursor_lista_proyectos = """SELECT proy.codigo_proyecto, tr.nivel, proy.titulo_proyecto, met.descripcion as metodologia, 
        tdes.tipo_desarrollo, tr.periodo_academico, tr.id_trayecto, sec.id_seccion, proy.id_proyecto, sec.siglas, sec.tipo_seccion,
        sec.ano_seccion, proy.numero_grupo_proyecto, proy.nombre_informe_codificado as informe, 
        proy.nombre_desarrollo_codificado as desarrollo, proy.nombre_manual_codificado as manuales 
        FROM proyectos as proy INNER JOIN metodologia as met ON proy.FK_id_metodo = met.id_metodo
        INNER JOIN tipo_de_desarrollo as tdes ON tdes.id_tipo_desarrollo = proy.FK_id_tipo_desarrollo
        INNER JOIN secciones as sec on sec.id_seccion = proy.FK_id_seccion
        INNER JOIN trayecto as tr on tr.id_trayecto = sec.FK_id_trayecto
        ORDER BY proy.codigo_proyecto desc LIMIT 20;
        """

        #for sentencia in cursor_lista_proyectos:
        #    self.cursor.execute(sentencia)

        self.cursor.execute(cursor_lista_proyectos)

        index = 0
        self.tabla_proyectos_recientes.setRowCount(0)
        for rows in self.cursor:
            self.proyecto = str(rows[0])
            self.trayecto = str(rows[1])
            self.titulo = str(rows[2])
            self.metodologia = str(rows[3])
            self.tdesarrollo = str(rows[4])
            self.periodo_academico = str(rows[5])
            self.IDTrayecto = str(rows[6])
            self.IDSeccion = str(rows[7])
            self.IDProyecto = str(rows[8])
            seccion = str(rows[9])
            tipoSeccion = str(rows[10])
            anoProsecucion = str(rows[11])  
            grupoDesarrollo = str(rows[12])
            nombre_informe = str(rows[13])
            nombre_desarrollo = str(rows[14])
            nombre_manual = str(rows[15])
            #Agregando valores a la tabla
            self.tabla_proyectos_recientes.insertRow(index)
            self.tabla_proyectos_recientes.setItem(index, 0, QTableWidgetItem(self.proyecto))
            self.tabla_proyectos_recientes.setItem(index, 1, QTableWidgetItem(self.trayecto))
            self.tabla_proyectos_recientes.setItem(index, 2, QTableWidgetItem(self.titulo))
            self.tabla_proyectos_recientes.setItem(index, 3, QTableWidgetItem(self.metodologia))
            self.tabla_proyectos_recientes.setItem(index, 4, QTableWidgetItem(self.tdesarrollo))
            self.tabla_proyectos_recientes.setItem(index, 5, QTableWidgetItem(self.periodo_academico))
            self.tabla_proyectos_recientes.setItem(index, 6, QTableWidgetItem(self.IDTrayecto))
            self.tabla_proyectos_recientes.setItem(index, 7, QTableWidgetItem(self.IDSeccion))
            self.tabla_proyectos_recientes.setItem(index, 8, QTableWidgetItem(self.IDProyecto))
            self.tabla_proyectos_recientes.setItem(index, 9, QTableWidgetItem(seccion))
            self.tabla_proyectos_recientes.setItem(index, 10, QTableWidgetItem(tipoSeccion))
            self.tabla_proyectos_recientes.setItem(index, 11, QTableWidgetItem(anoProsecucion))
            self.tabla_proyectos_recientes.setItem(index, 12, QTableWidgetItem(grupoDesarrollo))
            self.tabla_proyectos_recientes.setItem(index, 13, QTableWidgetItem(nombre_informe))
            self.tabla_proyectos_recientes.setItem(index, 14, QTableWidgetItem(nombre_desarrollo))
            self.tabla_proyectos_recientes.setItem(index, 15, QTableWidgetItem(nombre_manual))
            index += 1

        self.tabla_proyectos_recientes.setSortingEnabled(True)
        self.tabla_proyectos_recientes.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
        if index == 0:
#            self.evento = 'No registros'
#            self.btnEditarRegistro.setEnabled(False)
            self.txtFiltro.setEnabled(False)
            self.grpFiltrarPor.setEnabled(False)
#        else:
#            self.btnEditarRegistro.setEnabled(True)
            self.txtFiltro.setEnabled(True)
            self.grpFiltrarPor.setEnabled(True)

    def validar_formulario(self):
        if self.validar_usuario() and self.validar_clave():
            self.chkActivo.setCheckState(Qt.Unchecked)
            lv_clavetemp = bytes(self.txtClave.text().upper(),'utf-8')
            self.lv_clavecod2 = hashlib.sha256(lv_clavetemp).hexdigest()
            self.txtClavecod.setText(self.lv_clavecod2)
            lv_usuario2 = self.txtUsuario.text().upper()
            self.txtUsuario.setText(lv_usuario2)
            lv_clave2 = self.txtClave.text().upper()
            self.txtClave.setText(lv_clave2)
            cursorAcceso = "SELECT usuario, responsable, clave, estado from usuarios where usuario = '%s'" % lv_usuario2
            self.cursor.execute(cursorAcceso)
            rows = self.cursor.fetchone()
            if rows is not None:
                self.lv_responsable2 = rows[1]
                lv_activo = str(rows[3])
                if lv_activo == 'Activo':
                    clavecod = rows[2]
                    if self.lv_clavecod2 == clavecod:
                        self.txtResponsable.setText(self.lv_responsable2)
                        self.chkActivo.setCheckState(Qt.Checked)
                        self.mensaje.setText("")
                    else:
                        QMessageBox.warning(self,"Base de Datos", "La clave introducida esta errada... Intente de nuevo", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self,"Base de Datos", "El usuario ingresado se encuentra inactivo... comuniquese con el Coordinador", QMessageBox.Ok)
            else:
                self.mensaje.setText("Usuario invalido...")
        else:
            self.limpiar_datos()
            QMessageBox.warning(self, "Formulario incorrecto", "Validación incorrecta", QMessageBox.Discard)

    def validar_usuario(self):
        usuario = self.txtUsuario.text().upper()
        validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', usuario, re.I)
        if usuario == "":
            self.txtUsuario.setStyleSheet("border: 1px solid yellow;")
            return False
        elif not validar:
            self.txtUsuario.setStyleSheet("border: 1px solid red;")
            return False
        else:
            self.txtUsuario.setStyleSheet("border: 1px solid green;")
            return True

    def validar_clave(self):
        lv_clave = self.txtClave.text().upper()
        validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_clave, re.I)
        if lv_clave == "":
            self.txtClave.setStyleSheet("border: 1px solid yellow;")
            return False
        elif not validar:
            self.txtClave.setStyleSheet("border: 1px solid red;")
            return False
        elif len(lv_clave) < 4:
            self.txtClave.setStyleSheet("border: 1px solid yellow;")
        else:
            self.txtClave.setStyleSheet("border: 1px solid green;")
            return True
        

    def limpiar_datos(self):
        self.txtUsuario.setText("")
        self.txtUsuarioActivo.setText("")
        self.txtClave.setText("")
        self.txtClavecod.setText("")
        self.txtResponsable.setText("")
        self.chkActivo.setCheckState(Qt.Unchecked)


    def ordenarTabla(self):
        if self.optProyecto.isChecked():
            self.tabla_proyectos_recientes.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
        elif self.optTrayecto.isChecked():
            self.tabla_proyectos_recientes.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)
        elif self.optTitulo.isChecked():
            self.tabla_proyectos_recientes.horizontalHeader().setSortIndicator(2, Qt.AscendingOrder)
        elif self.optMetodo.isChecked():
            self.tabla_proyectos_recientes.horizontalHeader().setSortIndicator(3, Qt.AscendingOrder)
        else:
            self.tabla_proyectos_recientes.horizontalHeader().setSortIndicator(4, Qt.AscendingOrder)

    def actSeleccion(self):
        fila = self.tabla_proyectos_recientes.currentRow()
        IDProyecto = self.tabla_proyectos_recientes.item(fila, 8).text()
        self.txtProyectoSeleccionado.setText(IDProyecto) 
        
    def buscarDato(self):
        lv_texto = self.txtFiltro.text().upper()
        validar = re.match('^[a-zA-Z0-9\sáéíóúàèìòùäëïöüñ]+$', lv_texto, re.I)
        if self.optProyecto.isChecked()== True:
            columna = 0
        elif self.optTrayecto.isChecked()==True:  
            columna = 1
        elif self.optTitulo.isChecked()==True:  
            columna = 2
        elif self.optMetodo.isChecked()==True:  
            columna = 3
        else:
            columna = 4
        index = self.tabla_proyectos_recientes.rowCount()
        fila=0
        encontrar = 0
        while fila < index:
            lv_busqueda = self.tabla_proyectos_recientes.item(fila,columna).text()
            if lv_texto in lv_busqueda:
                encontrar = 1
                break;
            fila = fila + 1
        if encontrar == 1:
            posicion = self.tabla_proyectos_recientes.item(fila, columna)
            self.tabla_proyectos_recientes.scrollToItem(posicion)
            self.tabla_proyectos_recientes.setCurrentCell(fila, columna)
            #self.txtProyectoSeleccionado.setText(self.tabla_proyectos_recientes.item(fila, 8).text().replace(" ", ""))
            self.txtProyectoSeleccionado.setText(self.tabla_proyectos_recientes.item(fila, 8).text())
            return True
        else:
            return False

    def menuControlProyectos(self):
        self.hide()
        self.PControlProyectos.setEnabled(True)
        self.PControlProyectos.exec_()
        self.llenarTablaRecientes()
        self.show()

    def manualAyuda(self):
        #self.hide()
        self.PAyuda.setEnabled(True)
        self.PAyuda.exec_()
        #self.show()

    def visualizarProyecto(self):
        fila = self.tabla_proyectos_recientes.currentRow()
        codigo_proyecto = self.tabla_proyectos_recientes.item(fila, 0).text()
        ano_periodo = self.tabla_proyectos_recientes.item(fila, 5).text()
        trayecto = self.tabla_proyectos_recientes.item(fila, 1).text()
        seccion = self.tabla_proyectos_recientes.item(fila, 9).text()
        tipo_trayecto = self.tabla_proyectos_recientes.item(fila, 10).text()
        ano_prosecucion = self.tabla_proyectos_recientes.item(fila, 11).text()
        titulo_proyecto = self.tabla_proyectos_recientes.item(fila, 2).text()
        grupo_desarrollo = self.tabla_proyectos_recientes.item(fila, 12).text()
        metodo = self.tabla_proyectos_recientes.item(fila, 3).text()
        tipo_desarrollo = self.tabla_proyectos_recientes.item(fila, 4).text()
        IDTrayecto = int(self.tabla_proyectos_recientes.item(fila, 6).text())
        IDSeccion = int(self.tabla_proyectos_recientes.item(fila, 7).text())
        IDProyecto = int(self.tabla_proyectos_recientes.item(fila, 8).text())
        if int(grupo_desarrollo) < 10:
            grupo_desarrollo = '0' + grupo_desarrollo
        nombre_informe = self.tabla_proyectos_recientes.item(fila, 13).text()
        nombre_desarrollo = self.tabla_proyectos_recientes.item(fila, 14).text()
        nombre_manual = self.tabla_proyectos_recientes.item(fila, 15).text()
        if nombre_informe != 'None':
            entrego_informe = "Entregado"
        else:
            entrego_informe = "Pendiente"
        if trayecto == 'TRAYECTO III' or trayecto == 'TRAYECTO IV':
            if nombre_desarrollo != 'None':
                entrego_desarrollo = "Entregado"
            else:
                entrego_desarrollo = "Pendiente"
            if nombre_manual != 'None':
                entrego_manual = "Entregado"
            else:
                entrego_manual = "Pendiente"
        else:
            entrego_desarrollo = 'No requerido'
            entrego_manual = 'No requerido'
        consulta_seccion = "SELECT siglas, "
        self.PConsultaProyectos.txtCodigoProyecto.setText(codigo_proyecto)
        self.PConsultaProyectos.txtAnoPeriodo.setText(ano_periodo)
        self.PConsultaProyectos.txtTrayecto.setText(trayecto)
        self.PConsultaProyectos.txtSeccion.setText(seccion)
        self.PConsultaProyectos.txtTipoTrayecto.setText(tipo_trayecto)
        self.PConsultaProyectos.txtAnoProsecucion.setText(ano_prosecucion)
        self.PConsultaProyectos.txtTituloProyecto.setText(titulo_proyecto)
        self.PConsultaProyectos.txtGrupoDesarrollo.setText(grupo_desarrollo)
        self.PConsultaProyectos.txtMetodo.setText(metodo)
        self.PConsultaProyectos.txtTipoDesarrollo.setText(tipo_desarrollo)
        self.PConsultaProyectos.txtEstadoInforme.setText(entrego_informe)
        self.PConsultaProyectos.txtEstadoDesarrollo.setText(entrego_desarrollo)
        self.PConsultaProyectos.txtEstadoManual.setText(entrego_manual)
        self.PConsultaProyectos.txtNInformeCod.setText(nombre_informe)
        self.PConsultaProyectos.txtNDesarrolloCod.setText(nombre_desarrollo)
        self.PConsultaProyectos.txtNManualCod.setText(nombre_manual)
        self.txtEstadoInforme.setStyleSheet("border: 1px solid red; color: red;")
        if entrego_informe == "Entregado":
            self.PConsultaProyectos.txtEstadoInforme.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
        else:
            self.PConsultaProyectos.txtEstadoInforme.setStyleSheet("border: 1px solid darkred; color: darkred;")
        if entrego_desarrollo == "Entregado":
            self.PConsultaProyectos.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
        else:
            self.PConsultaProyectos.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkred; color: darkred;")
        if entrego_manual == "Entregado":
            self.PConsultaProyectos.txtEstadoManual.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
        else:
            self.PConsultaProyectos.txtEstadoManual.setStyleSheet("border: 1px solid darkred; color: darkred;")
        if trayecto == 'TRAYECTO I' or trayecto == 'TRAYECTO II':
            self.PConsultaProyectos.txtEstadoDesarrollo.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
            self.PConsultaProyectos.txtEstadoManual.setStyleSheet("border: 1px solid darkgreen; color: darkgreen;")
        consulta_estudiantes = ("""SELECT est.cedula_estudiante, est.nombre_estudiante, est.apellido_estudiante 
         FROM estudiante AS est INNER JOIN elaboran AS ela ON est.cedula_estudiante = ela.FK_cedula_estudiante
         INNER JOIN proyectos AS proy on proy.id_proyecto = ela.FK_id_proyecto
         WHERE proy.id_proyecto = '%i'
         ORDER BY est.cedula_estudiante""" % (int(IDProyecto)))
        self.cursor.execute(consulta_estudiantes)
        if self.PConsultaProyectos.tablaIntegrantes.rowCount() > 0:
            self.PConsultaProyectos.tablaIntegrantes.clearSelection()
            self.PConsultaProyectos.tablaIntegrantes.clearContents()
            index2 = self.PConsultaProyectos.tablaIntegrantes.rowCount()
            index3 = 0
            while index2 > 0:
                index3 = index2 - 1 
                self.PConsultaProyectos.tablaIntegrantes.removeRow(index3)
                index2 = index2 - 1
        index = 0
        self.tablaIntegrantes.setRowCount(0)
        rows = []
        index = 0
        for rows in self.cursor:
            if rows!=[]:
                self.PConsultaProyectos.tablaIntegrantes.insertRow(index)
                cedulaIntegrante = str(rows[0])
                NombreIntegrante = str(rows[1])
                ApellidoIntegrante = str(rows[2])
                self.PConsultaProyectos.tablaIntegrantes.setItem(index, 0, QTableWidgetItem(cedulaIntegrante))
                self.PConsultaProyectos.tablaIntegrantes.setItem(index, 1, QTableWidgetItem(NombreIntegrante))
                self.PConsultaProyectos.tablaIntegrantes.setItem(index, 2, QTableWidgetItem(ApellidoIntegrante))
            index = index + 1
        consulta_tutores = ("""SELECT tut.cedula_tutor, tut.nombre_tutor, tut.apellido_tutor, esa.rol 
         FROM tutores AS tut INNER JOIN es_asesorado AS esa ON tut.cedula_tutor = esa.FK_cedula_tutor
         INNER JOIN proyectos AS proy on proy.id_proyecto = esa.FK_id_proyecto
         WHERE proy.id_proyecto = '%i'
         ORDER BY tut.cedula_tutor""" % (int(IDProyecto)))
        self.cursor.execute(consulta_tutores)
        if self.PConsultaProyectos.tablaTutores.rowCount() > 0:
            self.PConsultaProyectos.tablaTutores.clearSelection()
            self.PConsultaProyectos.tablaTutores.clearContents()
            index2 = self.PConsultaProyectos.tablaTutores.rowCount()
            index3 = 0
            while index2 > 0:
                index3 = index2 - 1 
                self.PConsultaProyectos.tablaTutores.removeRow(index3)
                index2 = index2 - 1
        index = 0
        self.tablaTutores.setRowCount(0)
        rows = []
        index = 0
        for rows in self.cursor:
            if rows!=[]:
                self.PConsultaProyectos.tablaTutores.insertRow(index)
                cedulaTutor = str(rows[0])
                NombreTutor = str(rows[1])
                ApellidoTutor = str(rows[2])
                TipoTutor = str(rows[3])
                self.PConsultaProyectos.tablaTutores.setItem(index, 0, QTableWidgetItem(cedulaTutor))
                self.PConsultaProyectos.tablaTutores.setItem(index, 1, QTableWidgetItem(NombreTutor))
                self.PConsultaProyectos.tablaTutores.setItem(index, 2, QTableWidgetItem(ApellidoTutor))
                self.PConsultaProyectos.tablaTutores.setItem(index, 3, QTableWidgetItem(TipoTutor))
            index = index + 1
        self.hide()
        self.PConsultaProyectos.setEnabled(True)
        self.PConsultaProyectos.exec_()
        self.show()


    def menuRegUsuarios(self):
        lv_usuario2 = self.txtUsuarioActivo.text()
        self.PRegUsuarios.txtUsuarioActivo.setText(lv_usuario2)
        self.ActualizarTablaRegistroUsuarios()
        self.hide()
        self.PRegUsuarios.setEnabled(True)
        self.PRegUsuarios.exec_()
        self.show()
        
    def ActualizarTablaRegistroUsuarios(self):
        lv_TotalRegistrosTabla = self.PRegUsuarios.tabla_usuarios.rowCount()
        if lv_TotalRegistrosTabla > 0:
            self.PRegUsuarios.tabla_usuarios.clearSelection()
            #self.tabla_usuarios.disconnect()
            self.PRegUsuarios.tabla_usuarios.clearContents()
            #self.tabla_usuarios.setRowCount(0)
            index2 = self.PRegUsuarios.tabla_usuarios.rowCount()
            while index2 > 0:
                index = index2 - 1
                self.PRegUsuarios.tabla_usuarios.removeRow(index)
                index2 = index2 - 1
        cursor_lista_usuarios = "select usuario, responsable, estado from usuarios order by usuario"
        self.cursor.execute(cursor_lista_usuarios)
        index = 0
        #crear matriz de consultas
        self.registroUsuarios = []
        for rows in self.cursor:
            if rows==[]:
                self.PRegUsuarios.modo = 2
            else:
                self.PRegUsuarios.tabla_usuarios.insertRow(index)
                usuario = str(rows[0])
                responsable = str(rows[1])
                estado = str(rows[2])
                self.PRegUsuarios.tabla_usuarios.setItem(index, 0, QTableWidgetItem(usuario))
                self.PRegUsuarios.tabla_usuarios.setItem(index, 1, QTableWidgetItem(responsable))
                self.PRegUsuarios.tabla_usuarios.setItem(index, 2, QTableWidgetItem(estado))
                index += 1
        self.PRegUsuarios.txtUsuarioSeleccionado.setText("")
        self.PRegUsuarios.TotalReg.setText(str(index))
        if index == 0:
            self.PRegUsuarios.evento = 'No registros'
            self.PRegUsuarios.btnEditarRegistro.setEnabled(False)
        else:
            self.PRegUsuarios.btnEditarRegistro.setEnabled(True)

    def menuUsuariosCClaves(self):
        lv_usuario2 = self.txtUsuarioActivo.text()
        lv_responsable2 = self.txtResponsable.text()
        lv_clavecod2 = self.txtClavecod.text()
        lv_clave2 = self.txtClave.text()
        self.PActualizaClave.setEnabled(True)
        self.PActualizaClave.txtUsuario.setText(lv_usuario2)
        self.PActualizaClave.txtResponsable.setText(lv_responsable2)
        self.PActualizaClave.txtClaveNueva.setText('')
        self.PActualizaClave.txtClaveConfirmar.setText('')
        self.hide()
        self.PActualizaClave.setEnabled(True)
        self.PActualizaClave.exec_()
        self.show()

    def menuEmisionSolvencias(self):
        self.hide()
        self.PSolvencias.setEnabled(True)
        self.PSolvencias.exec_()
        self.show()

    def Estadisticas(self):
        self.hide()
        self.PEstadistica.setEnabled(True)
        self.PEstadistica.exec_()
        self.show()


    def Biblioteca(self):
        self.hide()
        self.PBiblioteca.setEnabled(True)
        self.PBiblioteca.exec_()
        self.show()

    def identificarse(self):
        if self.btnAcceder.text() == "Acceder":
            self.validar_formulario()
            if self.chkActivo.isChecked(): 
                self.lblInicioSesion1.hide()
                self.lblInicioSesion2.hide()
                self.lblUsuario.hide()
                self.lblClave.hide()
                self.txtUsuario.hide()
                self.txtClave.hide()
                self.lblBienvenidoUsuario1.show()
                self.usuario = self.txtUsuario.text().upper()
                self.responsable = self.txtUsuario.text().upper()
                self.lblBienvenidoUsuario2.setText('"'+self.usuario+'"')
                self.lblBienvenidoUsuario2.show()
                self.txtUsuarioActivo.setText(self.usuario)
                self.txtResponsable.setText(self.responsable)
                self.menu_usuarios_cambio_clave.setEnabled(True)
                self.menu_usuarios_registrar_usuarios.setEnabled(True)
                self.menuProyectos.setEnabled(True)
                self.menuUsuarios.setEnabled(True)
                self.menuReportes.setEnabled(True)
                self.btnAcceder.setText("Desconectar")
        else:
            resultado = QMessageBox.question(self, "Cerrar Sesion...", "¿Seguro que quieres cerrar la sesion activa?", QMessageBox.Yes | QMessageBox.No)
            if resultado == QMessageBox.Yes:
                self.lblInicioSesion1.show()
                self.lblInicioSesion2.show()
                self.lblUsuario.show()
                self.lblClave.show()
                self.txtUsuario.show()
                self.txtClave.show()
                self.usuario = ''
                self.responsable = ''
                self.txtUsuarioActivo.setText(self.usuario)
                self.txtResponsable.setText(self.responsable)
                self.txtUsuario.setText('')
                self.txtClave.setText('')
                self.lblBienvenidoUsuario1.hide()
                self.lblBienvenidoUsuario2.setText('')
                self.lblBienvenidoUsuario2.hide()
                self.menu_usuarios_cambio_clave.setEnabled(False)
                self.menu_usuarios_registrar_usuarios.setEnabled(False)
                self.menuProyectos.setEnabled(False)
                self.menuReportes.setEnabled(False)
                self.menuUsuarios.setEnabled(False)
                self.txtClavecod.setText('')
                self.txtUsuarioActivo.setText('')
                self.chkActivo.setCheckState(Qt.Unchecked)
                self.btnAcceder.setText("Acceder")

    def closeEvent(self, event):
        resultado = QMessageBox.question(self, "Salir ...", "¿Seguro que quieres salir de la aplicación?", QMessageBox.Yes | QMessageBox.No)
        if resultado == QMessageBox.Yes: event.accept()
        else: event.ignore() 

    def Salir(self):
        self.close()

app = QApplication(sys.argv)
MiApp = BDPIApp()
MiApp.show()
app.exec_()

