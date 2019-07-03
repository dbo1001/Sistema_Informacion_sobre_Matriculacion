#!/usr/bin/env python
# coding: utf-8

# In[6]:


'''
Nombre del Proyecto: SIM - Sistema de Información sobre Matriculación
(Interfaz Gráfica y Algoritmos del Proyecto)

Autor: Mario de la Parte Izquierdo 
Tutor: Carlos Pardo Aguilar

Versión: 1.0

Licencia: Copyright (c) 2019 Mario de la Parte Izquierdo
This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation, either version 3 of the License, or any later version.

Fecha Inicio: 26/02/2019
Fecha Fin: 30/06/2019
'''

# -------------------------- Librerías utilizadas  ----------------------------- #  
from tkinter import * # Carga módulo tk (widgets estándar) para poder crear interfaz de una aplicación
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk

import os, sys, subprocess
#from PyQt5.QtWidgets import QFileDialog
import pandas as pd
import matplotlib.pyplot as plt

import sqlite3 # Biblioteca para la creación de la BBDD
import math # Librería para comprobar si un dato es "nan" o no

import re # Biblioteca para poder usar expresiones regulares

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


# -------------------------- Algoritmo de Preprocesado de ficheros  ----------------------------- # 
'''
Algoritmo que realiza las siguientes funciones:
    1. Abrir un fichero Excel (.xls) como si fuera un (.txt), para obtener un (.xml).
    2. Parsear el contenido del (.xml) y obtener toda la información del Excel(todas las celdas).
        2.1. Se obtiene toda la información de cada fila del Excel -> ROW.
        2.2. Se obtiene toda la información de cada celda del Excel -> CELL. 
            2.2.1. Se obtienen los valores MergeDown y MergeAcross de cada celda.
        2.3. Se obtiene la información "visual"  de cada celda -> DATA.
    3. Con toda la información anterior, se crea un fichero (.csv) y se va guardando la información correctamente.

Autor: Mario de la Parte Izquierdo 
Fecha: 31/03/2019

Cambio 12/06/2019: Permitir introducir datos a la BBDD a partir de un fichero Excel con múltiples titulaciones.
Se decide modificar el fichero (.csv) final, añadiendo a la cabecera principal de los datos, una nueva columna
llamada "Plan" e introduciendo el Plan o titulación de cada conjunto de datos. De esta forma, se pueden eliminar las cabeceras 
que se repetían en el Excel (.xls) original (en el caso de tener más de una titulación por Excel.
'''
def algoritmo(nombreFichero):
    f = open(nombreFichero,"r") # Se abre el fichero original corrupto [r: read(estamos abriendo un archivo para leerlo)].
    a = f.read() 
    f.close()
    
    quitarExtension = nombreFichero.split('.')[-2] # Se divide el nombre del fichero en 2 partes(antes del "." y después) y se coge la parte de antes(nombre del fichero seleccionado sin extensión)
    nombreDelArchivoFinal = quitarExtension + ".csv" # Variable global que recoge el nombre del archivo .csv que se va a crear.
    archivo = open(nombreDelArchivoFinal ,"w")  # 1. Se crear el fichero (.csv)

    posicion = 0
    lista_num_ceros_fila_siguiente = []
    filaMergeDownMayorQueCero = False
    filaEspecial = False
    flag = True
    Responsable = False
    Plan = ""
    hacerUnaVezSolo = True
    contadorFila = 0

    datos = re.findall("<Row>(.+?)</Row>", a) # Se obtiene toda la información de cada fila del Excel (ROW)

    for i, fila in enumerate(datos): # Se recorre cada fila    
        cell = re.findall("<Cell(.+?)</Cell>", fila) # CELL (es una lista de strings)
        contadorFila +=1
        primeraCeldaDeLaFilaEsNumDe4Dig = False

        for i, celd in enumerate(cell): 
            data = re.findall("<Data(.+?)>(.+?)</Data>", celd)
            
            if (len(data) >0 ):
                if ( (i == 0) and (len(data[0][1]) == 4) and (data[0][1] != "Rep.")):  # and (type(data[0][1]) == int)
                    primeraCeldaDeLaFilaEsNumDe4Dig = True
            if(len(data)>0):
                Plan234 = data[0][1]      
                if (  len(data[0][1] ) > 30 and  Plan234.find("Plan") == 0 ):
                    Plan = data[0][1] # Se almacena el plan a introducir 


        if ( contadorFila <= 6 or primeraCeldaDeLaFilaEsNumDe4Dig == True ): # Si cumple estas condiciones, se añade al csv final.
            
            for j, celda in enumerate(cell):
                step_0 = celda.split(' ss:MergeDown="')  # Se saca MergeDown y  MergeAcross de cada celda
                step_1 = step_0[1].split('" ss:MergeAcross="')
                step_2 = step_1[1].split('"')
                MergeDown = step_1[0] 
                MergeAcross = step_2[0]

                # Se rellena la lista_num_ceros_fila_siguiente 
                if(int(MergeDown) > 0):
                    filaMergeDownMayorQueCero = True
                if (filaMergeDownMayorQueCero == True):
                    lista_num_ceros_fila_siguiente.append(int(MergeDown)) # Para añadir MergeDown a la lista sea 1 o 0.
                    if(int(MergeAcross) > 0):
                        aux = int(MergeAcross)
                        while (aux > 0):
                            lista_num_ceros_fila_siguiente.append(0) # Para añadir un cero en caso de que haya celdas en blanco
                            aux -= 1

                if (filaEspecial == True and hacerUnaVezSolo == True): # Meter info de lista_num_ceros_fila_siguiente [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1]
                  
                    while (posicion < len(lista_num_ceros_fila_siguiente)   and flag == True):
                        
                            if (lista_num_ceros_fila_siguiente[posicion] == 1): # Hay un 1 en la lisya -> meter ; 
                                archivo.write(";")
                            else:                                           # Hay un 0 en la lisya -> meter datos 
                                flag = False
                
                                data = re.findall("<Data(.+?)>(.+?)</Data>", celda) # DATA 
                                
                                if(len(data)>0):
                                    if ( type(data[0][1]) != int ): # Si no es un entero, se entrecomilla
                                        archivo.write(data[0][1])
                                        archivo.write(";")
                                    else:  # si es un entero, no se entrecomilla
                                        archivo.write(data[0][1])
                                        archivo.write(";") # Siguiente columna
                                    num = int(MergeAcross)
                                    while(num > 0):            
                                        archivo.write(";")
                                        num -= 1
                                else: 
                                    archivo.write(";")
                            posicion += 1  
                else:   # Caso Normal         
                    # Sacar contenido de la celda (DATA)
                    data = re.findall("<Data(.+?)>(.+?)</Data>", celda) # DATA 
                    if(len(data)>0):

                        Plan234 = data[0][1]  # Variable para      
                        if (  len(data[0][1] ) > 30 and  Plan234.find("Plan") == 0 ):
                            Plan = data[0][1] # Se almacena el plan a introducir 

                        if ( str(data[0][1]) == "Responsable" ):
                            Responsable = True

                        if ( type(data[0][1]) != int ): # Si no es un entero, se entrecomilla
                            archivo.write(data[0][1])
                            archivo.write(";") # Siguiente columna
                        else:  # si es un entero, no se entrecomilla
                            archivo.write(data[0][1])
                            archivo.write(";") # Siguiente columna
                        num = int(MergeAcross)
                        while(num > 0):            
                            archivo.write(";")
                            num -= 1
                    else: # Es una celda en blanco (en data hay [])
                        archivo.write(";")

                flag = True

            if (filaEspecial == True and hacerUnaVezSolo == True):
                while (posicion < len(lista_num_ceros_fila_siguiente) ):
                    archivo.write(";") 
                    posicion += 1 
                archivo.write(";") # Se añade otra celda en blanco (la celda de debajo de la nueva columna "Plan")
                hacerUnaVezSolo = False 

            if (Responsable == True): # Para insertar la nueva columna llamada "Plan"
                archivo.write("Plan")
                archivo.write(";") 
                Responsable = False

            if (contadorFila == 1): # Para solucionar problema con la obtención del año en la lectura del (.csv)
                archivo.write(";;;;;;")
                
            if(contadorFila > 6): # Se introduce la info relevante a la nueva columna "Plan" añadida
                archivo.write(Plan)
                archivo.write(";")
                archivo.write("\n") 
            else: 
                archivo.write("\n") # Siguiente Fila.

            filaEspecial = False
            if(filaMergeDownMayorQueCero == True):
                filaEspecial = True
            filaMergeDownMayorQueCero = False

    archivo.close()

    
# -------------------------- Creación de las Ventana Principal(raiz) de la Aplicación  ----------------------------- # 

raiz = Tk() #Se crea el Framework o raiz principal
raiz.title("Sistema de Información sobre Matriculación") #Título de la barra superior de la ventana 
raiz.resizable(0,0) # (width,height) Para que no se pueda redimensionar la pantalla ni horizontal ni verticalmente
raiz.iconbitmap("img\logo.ico") # Para introducir el icono de barra superior izquierdo
#raiz.geometry("850x550") # Para fijar un tamaño de ventana(raiz). La raiz siempre se va a adaptar al tamaño de los contenedores que contenga, por eso lo dejamos comentado.
raiz.config(bg = "beige") # Fijar color de fondo

miFrame = Frame() # Se crea el Frame
miFrame.pack() # Se asigna el Frame al Framework 
#miFrame.pack(fill="both", expand = "True")
miFrame.config(bg = "powder blue") # Asignarle color de fondo
miFrame.config(width ="850", height = "550")

miFrame.config(bd=15) # Para indicar que queremos el borde más grueso
miFrame.config(relief="ridge") #Para cambiar el tipo borde
miFrame.config(cursor = "arrow") # Para cambiar el cursor  (cursor = "target") (cursor = "circle")
miLabel = Label(miFrame, text="Bienvenidos a Sistema de Información sobre Matriculación", fg="black", font=("Comic Sans MS", 18)).place(x=10, y=20) 


# -------------------------- Variables Globales ----------------------------- #  
# Variables para almacenar los datos seleccionados por el usuario en los diferentes desplegables:
#--- Pantalla Gráfico 1 ---
temporadaG1 = ""
planG1 = "" 
cursoG1 = ""
tipologiaG1 = ""
#--- Pantalla Gráfico 2 ---      
temporadaG2 = ""
planG2 = "" 
#--- Pantalla Gráfico 2 --- 
temporadaG3 = ""
planG3 = "" 

# --------------------- Funciones para establecer los valores de las Variables Globales anteriores --------------------- #  
#--- Pantalla Gráfico1 ---  
""" 
""" 
def establecerTemporadaG1(eventObject):
    global temporadaG1
    temporadaG1 = eventObject 
    
def establecerPlanG1(eventObject):
    global planG1
    planG1 = eventObject 
    
def establecerCursoG1(eventObject):
    global cursoG1
    cursoG1 = eventObject 

def establecerTipologiaG1(eventObject):
    global tipologiaG1
    tipologiaG1 = eventObject 
    
#--- Pantalla Gráfico2 ---
def establecerTemporadaG2(eventObject):
    global temporadaG2
    temporadaG2 = eventObject 
    
def establecerPlanG2(eventObject):
    global planG2
    planG2 = eventObject 
    
#--- Pantalla Gráfico3 --- 
def establecerTemporadaG3(eventObject):
    global temporadaG3
    temporadaG3 = eventObject 
    
def establecerPlanG3(eventObject):
    global planG3
    planG3 = eventObject 

# -------------------------- Funciones Principales de la Aplicación----------------------------- # 

""" 
Función que se encarga de generar y descargar el tipo de Gráfico 1 
en función de las opciones que el usuario seleccione en los desplegables.
    1. Se realiza una consulta a la BBDD en función a los datos seleccionados por el usuario 
    2. Se genera el gráfico, agrupando correctamente los datos anteriormente devueltos, 
    así como personalizando el gráfico (tipo, ejes, nombres, tamaños...)
    3. Se descarga el gráfico con el nombre generado con los parámetros seleccionados 
    por el usuario.
""" 
def descargarG1():
    global temporadaG1
    global planG1
    global cursoG1
    global tipologiaG1
    valor = messagebox.askquestion("Descargar Gráfica 1","¿Desea descargar la Gráfica 1?")
    if valor == "yes": # Descargar Gráfica
        if (tipologiaG1 == "Teoría"):
            # Se realiza la consulta a BBDD
            consulta = "SELECT a.Descripcion, g.Id_Grupo , g.Total_Alumnos "
            consulta += "FROM ASIGNATURAS a INNER JOIN GRUPOS g ON a.Id_Asignatura = g.Id_Asignatura "
            consulta += "WHERE g.Temporada = '" + str(temporadaG1) + "' "
            consulta += "AND  g.Id_Grupo < 100 "
            consulta += "AND a.Plan = '" + str(planG1) + "' "
            consulta += "AND a.Curso = " + cursoG1 + ""
            planesDiferentes = hacer_consulta(consulta) # tipo:  sqlite3.Cursor

            cols = ['Descripción','Grupo','Total'] # Columnas del Dataframe (en el mismo orden en el que se ha hecho la consulta)
            dframe= pd.DataFrame.from_records(data = planesDiferentes.fetchall(), columns = cols) # Se crea el DataFrame

            g1 = dframe.groupby(['Grupo','Descripción'])['Total'].sum().unstack('Grupo').plot(kind='barh', legend='Reverse', stacked =True)
            plt.xlabel('Total de alumnos matriculados')
            plt.ylabel('Asignaturas')
            plt.savefig("Grafica1T_curso_"+cursoG1+planG1+".png", bbox_inches='tight', dpi=100) # , dpi= 150 hace mas grande la imagen pero no modifica lo que se descarga.
            plt.clf() 
            
        if (tipologiaG1 == "Prácticas"):
            # Se realiza la consulta a BBDD
            consultaAux = "SELECT a.Descripcion, g.Id_Grupo , g.Total_Alumnos "
            consultaAux += "FROM ASIGNATURAS a INNER JOIN GRUPOS g ON a.Id_Asignatura = g.Id_Asignatura "
            consultaAux += "WHERE g.Temporada = '" + str(temporadaG1) + "' "
            consultaAux += "AND  g.Id_Grupo > 100 "
            consultaAux += "AND a.Plan = '" + str(planG1) + "' "
            consultaAux += "AND a.Curso = " + cursoG1 + ""
            planesDiferentesAux = hacer_consulta(consultaAux) # tipo:  sqlite3.Cursor

            colsAux = ['Descripción','Grupo','Total'] # Columnas del Dataframe (en el mismo orden en el que se ha hecho la consulta)
            dframeAux= pd.DataFrame.from_records(data = planesDiferentesAux.fetchall(), columns = colsAux) # Se crea el DataFrame

            g1Aux = dframeAux.groupby(['Grupo','Descripción'])['Total'].sum().unstack('Grupo').plot(kind='barh', legend='Reverse', stacked =True)
            plt.xlabel('Total de alumnos matriculados')
            plt.ylabel('Asignaturas')
            plt.savefig("Grafica1P_curso_"+cursoG1+planG1+".png", bbox_inches='tight', dpi=100) # , dpi= 150 hace mas grande la imagen pero no modifica lo que se descarga.
            plt.clf() 
        
""" 
Esta función se encarga de hacer una consulta a la BBDD en función de los 
parámetros que se le pasen por cabecera. 
Devuelve una lista con el número de matriculados en las 10 asignaturas del
curso que se le pase por parámetro.
Esta función se utiliza para generar la Gráfica 2.
"""        
def rellenarListaG2(temporadaG2, planG2, curso):
    datos_curso = []
    consulta1 = "SELECT Descripcion , sum(Total_Alumnos) "
    consulta1 += "FROM ( "
    consulta1 += "SELECT a.Descripcion , g.Total_Alumnos "
    consulta1 += "FROM ASIGNATURAS a INNER JOIN GRUPOS g ON a.Id_Asignatura = g.Id_Asignatura "
    consulta1 += "WHERE g.Temporada = '" + str(temporadaG2) + "' "
    consulta1 += "AND g.Id_Grupo < 100 "
    consulta1 += "AND a.Plan = '" + str(planG2) + "' "
    consulta1 += "AND a.Curso = " + str(curso) + ""
    consulta1 += " ) GROUP BY Descripcion"
    matriculadosEnCurso = hacer_consulta(consulta1)
    
    aux = matriculadosEnCurso.fetchall()
    for i in aux:
        print(i[0], i[1])
        datos_curso.append(i[1])
    return datos_curso

""" 
Esta función se encarga de hacer una consulta a la BBDD en función de los 
parámetros que se le pasen por cabecera. 
Devuelve una lista con el número de matriculados en las 5 asignaturas del
semestre que se le pase por parámetro.
Esta función se utiliza para generar la Gráfica 3.
"""        
def rellenarListaG3(temporadaG3, planG3, curso, semestre):
    datos_semestre = []
    consulta2 = "SELECT Descripcion , sum(Total_Alumnos) "
    consulta2 += "FROM ( "
    consulta2 += "SELECT a.Descripcion , g.Total_Alumnos "
    consulta2 += "FROM ASIGNATURAS a INNER JOIN GRUPOS g ON a.Id_Asignatura = g.Id_Asignatura "
    consulta2 += "WHERE g.Temporada = '" + str(temporadaG3) + "' "
    consulta2 += "AND g.Id_Grupo < 100 "
    consulta2 += "AND a.Plan = '" + str(planG3) + "' "
    consulta2 += "AND a.Curso = " + str(curso) + " "
    consulta2 += "AND a.Vp  = " + str(semestre) + ""
    consulta2 += " ) GROUP BY Descripcion"
    matriculadosEnSemestre = hacer_consulta(consulta2)
    
    aux = matriculadosEnSemestre.fetchall()
    for i in aux:
        print(i[0], i[1])
        datos_semestre.append(i[1])
    return datos_semestre
    
""" 
Función que se encarga de generar y descargar el tipo de Gráfico 2 
en función de las opciones que el usuario seleccione en los desplegables.
    1. Se realizan 4 consultas a la BBDD en función a los datos seleccionados por el usuario.
    Para esta tarea se llama a la función "rellenarListaG2" 4 veces.
    2. Se genera el gráfico, agrupando correctamente los datos anteriormente devueltos, 
    así como personalizando el gráfico (tipo, ejes, nombres, tamaños...)
    3. Se descarga el gráfico con el nombre generado con los parámetros seleccionados 
    por el usuario.
""" 
def descargarG2():
    global temporadaG2
    global planG2
    valor = messagebox.askquestion("Descargar Gráfica 2","¿Desea descargar la Gráfica 2?")
    if valor == "yes": # Descargar Gráfica
        # Se declaran 4 listas de los 4 cursos que se rellenarán con 4 consultas a BBDD
        datos_primero = rellenarListaG2(temporadaG2, planG2, 1) # Lista con el número de matriculados en las 10 asignaturas de Primero.
        datos_segundo = rellenarListaG2(temporadaG2, planG2, 2) # Lista con el número de matriculados en las 10 asignaturas de Segundo.
        datos_tercero = rellenarListaG2(temporadaG2, planG2, 3) # Lista con el número de matriculados en las 10 asignaturas de Tercero.
        datos_cuarto = rellenarListaG2(temporadaG2, planG2, 4) # Lista con el número de matriculados en las 10 asignaturas de Cuarto.
    
        datos_grafica2 = [datos_primero, datos_segundo, datos_tercero, datos_cuarto] # Se inroducen las 4 listas de los 4 cursos.
        
        figura = plt.figure(1, figsize=(8, 5)) # Se crea el objeto figura. figsize=(ancho, altura)
        subgrafico = figura.add_subplot(111) # Se crea el subgrafico.
        grafica2 = subgrafico.boxplot(datos_grafica2, labels=["1º", "2º", "3º", "4º"] ) # Se crea la gráfica de cuartiles y diagramas de cajas.
        plt.xlabel('Curso Académico') 
        plt.ylabel('Total de alumnos matriculados')
        plt.savefig("Grafica2_cursos_"+planG2+".png", bbox_inches='tight', dpi=100)
        plt.clf() 

""" 
Función que se encarga de generar y descargar el tipo de Gráfico 3 
en función de las opciones que el usuario seleccione en los desplegables.
    1. Se realizan 8 consultas a la BBDD en función a los datos seleccionados por el usuario.
    Para esta tarea se llama a la función "rellenarListaG3" 8 veces.
    2. Se genera el gráfico, agrupando correctamente los datos anteriormente devueltos, 
    así como personalizando el gráfico (tipo, ejes, nombres, tamaños...)
    3. Se descarga el gráfico con el nombre generado con los parámetros seleccionados 
    por el usuario.
""" 
def descargarG3():
    global temporadaG3
    global planG3
    valor = messagebox.askquestion("Descargar Gráfica 3","¿Desea descargar la Gráfica 3?")
    if valor == "yes": # Descargar Gráfica
        # Se declaran 8 listas de los 8 semestres que se rellenarán con 8 consultas a BBDD
        datos_1s = rellenarListaG3(temporadaG3, planG3, 1, 1) # Lista con el número de matriculados en las 5 asignaturas del 1º Semestre.
        datos_2s = rellenarListaG3(temporadaG3, planG3, 1, 2) # Lista con el número de matriculados en las 5 asignaturas del 2º Semestre.
        datos_3s = rellenarListaG3(temporadaG3, planG3, 2, 1) # Lista con el número de matriculados en las 5 asignaturas del 3º Semestre.
        datos_4s = rellenarListaG3(temporadaG3, planG3, 2, 2) # Lista con el número de matriculados en las 5 asignaturas del 4º Semestre.
        datos_5s = rellenarListaG3(temporadaG3, planG3, 3, 1) # Lista con el número de matriculados en las 5 asignaturas del 5º Semestre.
        datos_6s = rellenarListaG3(temporadaG3, planG3, 3, 2) # Lista con el número de matriculados en las 5 asignaturas del 6º Semestre.
        datos_7s = rellenarListaG3(temporadaG3, planG3, 4, 1) # Lista con el número de matriculados en las 5 asignaturas del 7º Semestre.
        datos_8s = rellenarListaG3(temporadaG3, planG3, 4, 2) # Lista con el número de matriculados en las 5 asignaturas del 8º Semestre.

        datos_grafica3 = [datos_1s, datos_2s, datos_3s, datos_4s, datos_5s, datos_6s, datos_7s, datos_8s] # Se inroducen las 8 listas de los 8 semestres.
        
        figura2 = plt.figure(1, figsize=(8, 5)) # Se crea el objeto figura. figsize=(ancho, altura)
        subgrafico2 = figura2.add_subplot(111) # Se crea el subgrafico.
        grafica3 = subgrafico2.boxplot(datos_grafica3, labels=["1º","2º","3º","4º","5º","6º","7º","8º"] ) # Se crea la gráfica de cuartiles y diagramas de cajas.
        plt.xlabel('Semestre Académico') 
        plt.ylabel('Total de alumnos matriculados')    
        plt.savefig("Grafica3_semestres_"+planG3+".png", bbox_inches='tight', dpi=100)    
        plt.clf() 
        
""" 
Función que se encarga de generar la ventana secundaria para posteriormente
poder personalizar, generar y descargar el tipo de Gráfico 1.
    1. Se crea la ventana "hija" raiz2 con las mismas características que la ventana principal.
    2. Se realizan consultas a la BBDD para poder rellenar la información a mostrar 
    en los diferentes desplegables.
    3. Cada vez que se selecciona una opcion en los desplegables, se actualiza el valor
    de la variable global que almacena dicho valor.
    4. Finalmente se cuenta con 2 botones ("Salir" y "Descargar Gráfica"). El segundo 
    llama a la función "descargarG1" para que se proceda a la descarga.
"""         
def ventanaGrafica1(): 
    raiz2 = Toplevel(raiz) # Si creamos una nueva ventana a traves de Toplevel esta tomaria el nombre de la ventana padre.
    raiz2.title("Sistema de Información sobre Matriculación -> Gráfico 1") # Título de la barra superior de la ventana 
    raiz2.resizable(0,0) # (width,height) Para que no se pueda redimensionar la pantalla ni horizontal ni verticalmente
    raiz2.iconbitmap("img\logo.ico") # Para introducir el icono de barra superior izquierdo
    raiz2.geometry("850x550") # Para fijar un tamaño de ventana(raiz). La raiz siempre se va a adaptar al tamaño de los contenedores que contenga, por eso lo dejamos comentado.
    raiz2.config(bg = "powder blue") # Fijar color de fondo
    miLabel = Label(raiz2,  text="Gráfico 1: Gráfico Apilado de Asignaturas por Curso", fg="black", font=("Comic Sans MS", 18)).place(x=10, y=20) 

    # Obtener todos los Años diferentes de la BBDD 
    temporadaDiferentes = hacer_consulta("SELECT DISTINCT Temporada FROM GRUPOS")
    listaTemporadas =[]
    for i in temporadaDiferentes:
        listaTemporadas.append(i[0])
    tuplaTemporadas = tuple(listaTemporadas)

    # Para establecer la etiqueta y el desplegable del Año
    labelTemporada = Label(raiz2,  text="Año:", fg="black", font=("Arial", 10)).place(x=80, y=150) 
    comboTemporada = ttk.Combobox(raiz2,  width=12, state='readonly') # width : largo de la caja
    comboTemporada.place(x=160, y=150)
    comboTemporada['values'] = tuplaTemporadas #("2018-2019", "2019-2020") 
    #comboTemporada.current(0) # Para que por defecto se muestre el primer valor
    comboTemporada.bind("<<ComboboxSelected>>", lambda event: establecerTemporadaG1(comboTemporada.get()) )
    
    # Obtener todos los Planes diferentes de la BBDD 
    planesDiferentes = hacer_consulta("SELECT DISTINCT Plan FROM ASIGNATURAS")
    listaPlanes =[]
    for i in planesDiferentes:
        listaPlanes.append(i[0])
    tuplaPlanes = tuple(listaPlanes)

    # Para establecer la etiqueta y el desplegable de la Titulación
    labelTitulacion = Label(raiz2,  text="Titulación:", fg="black", font=("Arial", 10)).place(x=80, y=200) 
    comboTitulacion = ttk.Combobox(raiz2,  width=100, state='readonly') 
    comboTitulacion.place(x=160, y=200)
    comboTitulacion['values'] = tuplaPlanes #("Ingeniería Informática", "Ingeniería Mecánica")
    #comboTitulacion.current(0) 
    comboTitulacion.bind("<<ComboboxSelected>>", lambda event: establecerPlanG1(comboTitulacion.get())  )

    # Obtener todos los Cursos diferentes de la BBDD 
    cursosDiferentes = hacer_consulta("SELECT DISTINCT Curso FROM ASIGNATURAS")
    listaCursos =[]
    for i in cursosDiferentes:
        listaCursos.append(i[0])
    tuplaCursos = tuple(listaCursos)

    # Para establecer la etiqueta y el desplegable del Año
    labelCurso = Label(raiz2,  text="Curso:", fg="black", font=("Arial", 10)).place(x=400, y=150) 
    comboCurso = ttk.Combobox(raiz2,  width=12, state='readonly') 
    comboCurso.place(x=455, y=150) 
    comboCurso['values'] = tuplaCursos
    #comboCurso.current(0) 
    comboCurso.bind("<<ComboboxSelected>>", lambda event: establecerCursoG1(comboCurso.get()) ) 
    
    # Para establecer la etiqueta y el desplegable del Año
    labelTipologia = Label(raiz2,  text="Tipología:", fg="black", font=("Arial", 10)).place(x=620, y=150) 
    comboTipologia = ttk.Combobox(raiz2,  width=12, state='readonly') 
    comboTipologia.place(x=687, y=150) 
    comboTipologia['values'] = [("Teoría"),("Prácticas")] #tuplaTipologias
    #comboTipologia.current(0) 
    comboTipologia.bind("<<ComboboxSelected>>", lambda event: establecerTipologiaG1(comboTipologia.get()) )
   
    botonSalir = Button(raiz2, text="Salir", command = salir).place(x=410, y=450) 
    botonV = Button(raiz2, text="Descargar Gráfica", command = descargarG1).place(x=380, y=320) 


""" 
Función que se encarga de generar la ventana secundaria para posteriormente
poder personalizar, generar y descargar el tipo de Gráfico 2.
    1. Se crea la ventana "hija" raiz3 con las mismas características que la ventana principal.
    2. Se realizan consultas a la BBDD para poder rellenar la información a mostrar 
    en los diferentes desplegables.
    3. Cada vez que se selecciona una opcion en los desplegables, se actualiza el valor
    de la variable global que almacena dicho valor.
    4. Finalmente se cuenta con 2 botones ("Salir" y "Descargar Gráfica"). El segundo 
    llama a la función "descargarG2" para que se proceda a la descarga.
"""   
def ventanaGrafica2():    
    raiz3 = Toplevel(raiz) # si creamos una nueva ventana a traves de Toplevel esta tomaria el nombre de la ventana padre.
    raiz3.title("Sistema de Información sobre Matriculación -> Gráfico 2") #Título de la barra superior de la ventana 
    raiz3.resizable(0,0) # (width,height) Para que no se pueda redimensionar la pantalla ni horizontal ni verticalmente
    raiz3.iconbitmap("img\logo.ico") # Para introducir el icono de barra superior izquierdo
    raiz3.geometry("850x550") # Para fijar un tamaño de ventana(raiz). La raiz siempre se va a adaptar al tamaño de los contenedores que contenga, por eso lo dejamos comentado.
    raiz3.config(bg = "powder blue") # Fijar color de fondo
    miLabel = Label(raiz3,  text="Gráfico 2: Gráfico de Máximos, Mínimos y Medias por Curso", fg="black", font=("Comic Sans MS", 18)).place(x=10, y=20) 

    # Obtener todos los Años diferentes de la BBDD 
    temporadaDiferentes2 = hacer_consulta("SELECT DISTINCT Temporada FROM GRUPOS")
    listaTemporadas2 =[]
    for i in temporadaDiferentes2:
        listaTemporadas2.append(i[0])
    tuplaTemporadas2 = tuple(listaTemporadas2)

    # Para establecer la etiqueta y el desplegable del Año
    labelTemporada2 = Label(raiz3,  text="Año:", fg="black", font=("Arial", 10)).place(x=80, y=150) 
    comboTemporada2 = ttk.Combobox(raiz3,  width=12, state='readonly') 
    comboTemporada2.place(x=160, y=150)
    comboTemporada2['values'] = tuplaTemporadas2 
    #comboTemporada2.current(0) 
    comboTemporada2.bind("<<ComboboxSelected>>", lambda event: establecerTemporadaG2(comboTemporada2.get()) )
    
    # Obtener todos los Planes diferentes de la BBDD 
    planesDiferentes2 = hacer_consulta("SELECT DISTINCT Plan FROM ASIGNATURAS")
    listaPlanes2 =[]
    for i in planesDiferentes2:
        listaPlanes2.append(i[0])
    tuplaPlanes2 = tuple(listaPlanes2)

    # Para establecer la etiqueta y el desplegable de la Titulación
    labelTitulacion2 = Label(raiz3,  text="Titulación:", fg="black", font=("Arial", 10)).place(x=80, y=200) 
    comboTitulacion2 = ttk.Combobox(raiz3,  width=100, state='readonly') 
    comboTitulacion2.place(x=160, y=200)
    comboTitulacion2['values'] = tuplaPlanes2 
    #comboTitulacion2.current(0) 
    comboTitulacion2.bind("<<ComboboxSelected>>", lambda event: establecerPlanG2(comboTitulacion2.get()) )
    
    botonSalir2 = Button(raiz3, text="Salir", command=salir).place(x=410, y=450) 
    botonV2 = Button(raiz3, text="Descargar Gráfica", command = descargarG2).place(x=380, y=320) 
    
    
""" 
Función que se encarga de generar la ventana secundaria para posteriormente
poder personalizar, generar y descargar el tipo de Gráfico 3.
    1. Se crea la ventana "hija" raiz4 con las mismas características que la ventana principal.
    2. Se realizan consultas a la BBDD para poder rellenar la información a mostrar 
    en los diferentes desplegables.
    3. Cada vez que se selecciona una opcion en los desplegables, se actualiza el valor
    de la variable global que almacena dicho valor.
    4. Finalmente se cuenta con 2 botones ("Salir" y "Descargar Gráfica"). El segundo 
    llama a la función "descargarG3" para que se proceda a la descarga.
"""    
def ventanaGrafica3():    
    raiz4 = Toplevel(raiz) # si creamos una nueva ventana a traves de Toplevel esta tomaria el nombre de la ventana padre.
    raiz4.title("Sistema de Información sobre Matriculación -> Gráfico 3") #Título de la barra superior de la ventana 
    raiz4.resizable(0,0) # (width,height) Para que no se pueda redimensionar la pantalla ni horizontal ni verticalmente
    raiz4.iconbitmap("img\logo.ico") # Para introducir el icono de barra superior izquierdo
    raiz4.geometry("850x550") # Para fijar un tamaño de ventana(raiz). La raiz siempre se va a adaptar al tamaño de los contenedores que contenga, por eso lo dejamos comentado.
    raiz4.config(bg = "powder blue") # Fijar color de fondo
    miLabel = Label(raiz4,  text="Gráfico 3: Gráfico de Máximos, Mínimos y Medias por Semestre", fg="black", font=("Comic Sans MS", 18)).place(x=10, y=20) 

    # Obtener todos los Años diferentes de la BBDD 
    temporadaDiferentes3 = hacer_consulta("SELECT DISTINCT Temporada FROM GRUPOS")
    listaTemporadas3 =[]
    for i in temporadaDiferentes3:
        listaTemporadas3.append(i[0])
    tuplaTemporadas3 = tuple(listaTemporadas3)

    # Para establecer la etiqueta y el desplegable del Año
    labelTemporada3 = Label(raiz4,  text="Año:", fg="black", font=("Arial", 10)).place(x=80, y=150) 
    comboTemporada3 = ttk.Combobox(raiz4,  width=12, state='readonly') 
    comboTemporada3.place(x=160, y=150)
    comboTemporada3['values'] = tuplaTemporadas3  
    #comboTemporada3.current(0) 
    comboTemporada3.bind("<<ComboboxSelected>>", lambda event: establecerTemporadaG3(comboTemporada3.get()) )
    
    # Obtener todos los Planes diferentes de la BBDD 
    planesDiferentes3 = hacer_consulta("SELECT DISTINCT Plan FROM ASIGNATURAS")
    listaPlanes3 =[]
    for i in planesDiferentes3:
        listaPlanes3.append(i[0])
    tuplaPlanes3 = tuple(listaPlanes3)

    # Para establecer la etiqueta y el desplegable de la Titulación
    labelTitulacion3 = Label(raiz4,  text="Titulación:", fg="black", font=("Arial", 10)).place(x=80, y=200) 
    comboTitulacion3 = ttk.Combobox(raiz4,  width=100, state='readonly') 
    comboTitulacion3.place(x=160, y=200)
    comboTitulacion3['values'] = tuplaPlanes3
    #comboTitulacion3.current(0) 
    comboTitulacion3.bind("<<ComboboxSelected>>", lambda event: establecerPlanG3(comboTitulacion3.get()) )
    
    botonSalir3 = Button(raiz4, text="Salir", command=salir).place(x=410, y=450) 
    botonV3 = Button(raiz4, text="Descargar Gráfica", command = descargarG3).place(x=380, y=320)

    
""" 
Función que se encarga de convertir los (.xls) corruptos que seleccionemos en ficheros (.csv)
para su posterior carga en la BBDD.
Para esta labor, esta función llama a "algoritmo" pasándole el nombre del archivo selecionado 
por el usuario con anterioridad.
"""
def preprocesar():
    raiz.fileName = filedialog.askopenfilename( title = "Seleccione un archivo .xls para procesar", filetypes=((".xls (No parseados)", "*.xls"),))
    nombreArchivo = raiz.fileName.split('/')[-1] # Se divide por "/" el string de la ruta y se obtiene la última posición con [-1]
    algoritmo(nombreArchivo)

""" 
Función que se encarga de la creación de la Base de Datos.
Crea una Base de Datos llamada "BBDD" con 3 tablas: ASIGNATURAS, GRUPOS y PROFESORES.
Si ya existiera creada la Base de Datos "BBDD" muestra una ventana de tipo warning 
mostrando por pantalla el mensaje: "La BBDD ya está creada".
"""
def crearBBDD():
    # La creación de la BBDD se debería ejecutar 1 única vez
    nombreBD = "BBDD" # Nombre de nuestra Base de Datos (BBDD)
    miConexion = sqlite3.connect(nombreBD) # Se crea la conexión y nuestra BBDD.
    miCursor = miConexion.cursor() # Se crea el cursor o puntero para crear una tabla.
    try:  # Por si ya estuviera creada la BBDD
        # Se crea la tabla "ASIGNATURAS"
        miCursor.execute('''
                         CREATE TABLE ASIGNATURAS(
                             Id_Asignatura  INTEGER PRIMARY KEY,
                             Descripcion VARCHAR(50),
                             Curso INTEGER, Plan VARCHAR(50),
                             Tipologia VARCHAR(10),
                             Activ VARCHAR(10),
                             Tp VARCHAR(10),
                             Vp INTEGER,
                             Turno VARCHAR(10)
                         )''') # Ejecutar la consulta en SQL para crear 1 tabla.
        # Se crea la tabla "GRUPOS"
        miCursor.execute('''
                        CREATE TABLE GRUPOS(
                            Id_Asignatura  INTEGER,
                            Id_Grupo INTEGER,
                            Temporada VARCHAR(50),
                            Total_Alumnos INTEGER,
                            PRIMARY KEY(Id_Asignatura, Id_Grupo, Temporada)
                        )''') 
        # Se crea la tabla "PROFESORES"
        miCursor.execute('''
                        CREATE TABLE PROFESORES(
                            Id_Profesor  INTEGER,
                            Id_Asignatura INTEGER,
                            Id_Grupo INTEGER,
                            Temporada VARCHAR(50),
                            Acta VARCHAR(1), 
                            Nombre_Apellidos VARCHAR(50),
                            PRIMARY KEY(Id_Profesor, Id_Asignatura, Id_Grupo, Temporada)
                        )''') 
    except: # Si la BBDD ya estuviera creada, no se crea de nuevo y realiza lo siguiente
        messagebox.showwarning("¡Atención!", "La BBDD ya está creada")
    miConexion.commit() # Se guardan los cambios anteriores
    miConexion.close() # Se cierra la conexión

    
""" 
Función que se encarga de abrir el fichero que se le pasa por parámetro (ruta),
siempre y cuando, este fichero se encuentre en el directorio donde nos encontremos.
Devuelve un dataFrame con todos los datos del fichero(SIN CONTAR LAS 4 PRIMERAS FILAS DE DATOS).
"""    
def CargarDatos(ruta):
    #print("Se van a cargar los datos:")
    # Esto funciona y abre el csv:
    #df = pd.read_csv('C:\\Users\\mdmar\\Desktop\\ficheroBueno.csv', sep=';',error_bad_lines=False, encoding='latin-1', header = 4)
    # Esto también funciona
    #df = pd.read_csv('ficheroBueno.csv', sep=';',error_bad_lines=False, encoding='latin-1', header = 4)
    df = pd.read_csv(ruta, sep=';',error_bad_lines=False, encoding='latin-1', header = 4)
    return df

""" 
Función que se encarga de abrir el fichero que se le pasa por parámetro (ruta),
(siempre y cuando, este fichero se encuentre en el directorio donde nos encontremos);
y devuelve el valor del año académico de la titulación/plan del fichero.
"""  
def obtenerTemporada(ruta):
    df = pd.read_csv(ruta, sep=';',error_bad_lines=False, encoding='latin-1', header = 0) 
    temporada = df.iloc[0,1]
    print(temporada)
    return temporada


""" 
Función que se encarga de añadir los datos necesarios del dataframe que se 
le pasa por parámetro a la tabla "ASIGNATURAS" de la BBDD. Esto se realiza 
fila a fila, introduciendo únicamente los datos que se necesitan en la BBDD.
Por cada fila que no se introduzca en la BBDD, se mostrará un mensaje en la consola,
como el siguiente: "No se ha introducido el Id_Asignatura(ASIGNATURAS): x"
"""
def addAsignaturasRows(dataframe):
    numeroFilasTotal = len(dataframe['Código']) -1 # Dá 41 filas (se le resta 1 por la primera fila, ya que es un valor nan[celda vacía])
    numeroFila = 1
       
    while (numeroFila <= numeroFilasTotal):
        # -------------Se obtienen los datos a insertar fila a fila:-------------
        cod = dataframe['Código'][numeroFila]
        des = dataframe['Descripción'][numeroFila]
        cur = dataframe['Curso'][numeroFila]
        pla = dataframe['Plan'][numeroFila] #"Plan 263 - MÁSTER UNIVERSITARIO EN INTELIGENCIA DE NEGOCIO Y BIG DATA EN ENTORNOS SEGUROS" 
        tip = dataframe['Tipología académica'][numeroFila]
        act = dataframe['Activ.'][numeroFila]
        tp = dataframe['Tp'][numeroFila]
        vp = dataframe['Vp'][numeroFila]
        tur = dataframe['Turno'][numeroFila]
        # --------------------------------------------------------------------------
        # Se introducen los valores de tabla ASIGNATURAS en la BBDD:
        #try: 
        r = hacer_consulta("INSERT INTO ASIGNATURAS VALUES("+str(cod)+", '"+str(des)+"',"+str(cur)+", '"+str(pla)+"', '"+str(tip)+"','"+str(act)+"','"+str(tp)+"',"+str(vp)+",'"+str(tur)+"')") 
        if(r==2):
            print("No se ha introducido el Id_Asignatura(ASIGNATURAS): "+str(cod))
        numeroFila = numeroFila + 1 # Se incrementa el número de filas (contador)

""" 
Función que se encarga de añadir los datos necesarios del dataframe y de la temporada que se 
le pasa por parámetro a la tabla "GRUPOS" de la BBDD. Esto se realiza 
fila a fila, introduciendo únicamente los datos que se necesitan en la BBDD.
Por cada fila que no se introduzca en la BBDD, se mostrará un mensaje en la consola,
como el siguiente: "No se ha introducido el Id_Asignatura(GRUPOS): x"
"""
def addGruposRows(dataframe, temporada):
    numeroFilasTotal = len(dataframe['Código']) -1 # Dá 41 filas (se le resta 1 por la primera fila, ya que es un valor nan[celda vacía])
    numeroFila = 1
       
    while (numeroFila <= numeroFilasTotal):
        # -------------Se obtienen los datos a insertar fila a fila:-------------
        cod = dataframe['Código'][numeroFila]
        gru = dataframe['Grupo'][numeroFila]
        # Temporada(Año académico) no aparece en el dataframe, luego se le pasa por cabecera (anteriormente se obtiene con función obtenerTemporada)
        tem = temporada #"2018/19-0" 
        tot = dataframe['Total'][numeroFila]
        # --------------------------------------------------------------------------
        # Se introducen los valores de tabla ASIGNATURAS en la BBDD:
        r = hacer_consulta("INSERT INTO GRUPOS VALUES("+str(cod)+", "+str(gru)+",'"+tem+"', "+str(tot)+" )") 
        if(r==2):
            print("No se ha introducido el Id_Asignatura(GRUPOS): "+str(cod))
        numeroFila = numeroFila + 1 # Se incrementa el número de filas (contador)

""" 
Función que se encarga de añadir los datos necesarios del dataframe y de la temporada que se 
le pasa por parámetro a la tabla "PROFESORES" de la BBDD. Esto se realiza 
fila a fila, introduciendo únicamente los datos que se necesitan en la BBDD.
Por cada fila que no se introduzca en la BBDD, se mostrará un mensaje en la consola,
como el siguiente: "No se ha introducido el Id_Asignatura(PROFESORES): x"
"""
def addProfesoresRows(dataframe, temporada):    
    numeroFilasTotal = len(dataframe['Código']) -1 # Dá 41 filas (se le resta 1 por la primera fila, ya que es un valor nan[celda vacía])
    numeroFila = 1
       
    while (numeroFila <= numeroFilasTotal):
        # -------------Se obtienen los datos a insertar fila a fila:-------------
        idP = dataframe['PF'][numeroFila]
        cod = dataframe['Código'][numeroFila]
        gru = dataframe['Grupo'][numeroFila]
        # Temporada(Año académico) no aparece en el dataframe, luego se le pasa por cabecera (anteriormente se obtiene con función obtenerTemporada)
        tem = temporada #"2018/19-0" 
        act = dataframe['Actas'][numeroFila]
        NyA = dataframe['Nombre y Apellidos'][numeroFila]
        # --------------------------------------------------------------------------
        # Se introducen los valores de tabla ASIGNATURAS en la BBDD:
        r = hacer_consulta("INSERT INTO PROFESORES VALUES("+str(idP)+", "+str(cod)+", "+str(gru)+", '"+str(tem)+"','"+str(act)+"', '"+str(NyA)+"')") 
        if(r==2):
            print("No se ha introducido el Id_Asignatura(PROFESORES): "+str(cod))
        numeroFila = numeroFila + 1 # Se incrementa el número de filas (contador)   
        
""" 
Función que se encarga de: 
    1. Mostrar una ventana del sistema operativo que nos permite seleccionar archivos.
    2. Una vez seleccionado un archivo, obtiene el nombre y se lo pasa a la función
    "CargarDatos", para que devuelva un dataframe con todos los datos.
    3. Se rellenan los datos en las 3 tablas de la BBBD, llamando a las funciones
    "addAsignaturasRows", "addGruposRows" y "addProfesoresRows". 
    4. También se llama a la función "obtenerTemporada", ya que es la única forma de 
    recuperar u obtener dicho valor.
"""
def funcionCargar():
    raiz.fileName = filedialog.askopenfilename( title = "Seleccione un archivo .csv para cargar en la BBDD", filetypes=((".csv (Ya parseados)", "*.csv"),) )
    nombreArchivo = raiz.fileName.split('/')[-1] # Se divide por "/" el string de la ruta y se obtiene la última posición con [-1]
    df = CargarDatos(nombreArchivo)
    dframe = pd.DataFrame(df) # Se crea el DataFrame de los datos
    
    #Se Rellena la tabla ASIGNATURAS en la BBDD
    addAsignaturasRows(dframe)  
    
    #Se Rellena la tabla GRUPOS en la BBDD
    temporada = obtenerTemporada(nombreArchivo) # Se obtiene el año académico 
    addGruposRows(dframe, temporada)               
    
    #Se Rellena la tabla PROFESORES en la BBDD
    addProfesoresRows(dframe, temporada)
    

""" 
Función que se encarga de mostrar una ventana emergente con 2 opciones para 
confirmar si se quiere salir de la aplicaión. Si se pulsa que sí, 
se cierra la aplicación, si se pulsa que no, se continúa en la misma.
"""
def salir():
    valor = messagebox.askquestion("Salir","¿Desea salir de la aplicación?")
    if valor == "yes":
        raiz.destroy()

        
""" 
Función que se encarga de realizar consultas a la Base de Datos.
Realiza la consulta que se le pase por parámetro(consulta) y devuelve 
un cursor con el resultado de la misma.
"""        
def hacer_consulta(consulta, parametros = () ):
    nombreBD = "BBDD"
    with sqlite3.connect(nombreBD) as conn:
        cursor = conn.cursor()
        try:  
            result = cursor.execute(consulta, parametros)
            conn.commit()
            return result
        except:
            return 2
            

""" 
Función que se encarga de abrir y visualizar el archivo que se 
le pasa por parámetro.
"""      
def abrirArchivo(archivo): 
    if sys.platform == "win32":
        os.startfile(archivo)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, archivo])

        
""" 
Clase para crear el menú superior de la aplicación.
"""
class menuSuperior:
    def __init__(self, master):
        self.master = master
        self.menu = Menu(master)
        master.config(menu=self.menu)

        self.submenu = Menu(self.menu)
        self.submenu2 = Menu(self.menu)

        # ------------------ Submenú de Configuración ------------------ #
        self.submenu_config = Menu(self.submenu)
        # Opciones del submenu:
        self.submenu.add_cascade(label="Crear BBDD", command=crearBBDD)
             
        # ------------------ Submenú de Ayuda ------------------ #
        self.submenu_ayuda = Menu(self.submenu2)
        # Opciones del submenu2:
        self.submenu2.add_cascade(label="Ayuda Local", command=self.abrirAyudaLocal)
        self.submenu2.add_cascade(label="Ayuda Web", command=self.abrirAyudaWeb)

        # ------------------ Opciones Principales del Menú ------------------ #
        self.menu.add_cascade(label = "Configuración", underline = 0, menu = self.submenu)
        self.menu.add_cascade(label = "Ayuda",  underline = 0, menu = self.submenu2)
        self.menu.add_command(label="Acerca de...", command = self.abrirAbout)
        
    def abrirAyudaWeb(self):
        abrirArchivo('https://github.com/mdi0007/Sistema-Informacion-sobre-Matriculacion/blob/master/Code/ayuda.pdf') # Se abre el pdf de ayuda

    def abrirAyudaLocal(self):
        abrirArchivo('ayuda.pdf') # Se abre el pdf de "Ayuda" 
        
    def abrirAbout(self):
        abrirArchivo('about.pdf') # Se abre el pdf de "Acerca de"
        
# -------------------------- Botones de la Ventana Principal ----------------------------- #        

# Botón de "Preprocesado", llama a la función "preprocesar"
botonPreprocesado = Button(raiz, text="Preprocesado", command = preprocesar).place(x=40, y=100) 

# Botón de "Cargar Archivos", llama a la función "funcionCargar"
botonCargar = Button(raiz, text="Cargar Archivos", command = funcionCargar).place(x=160, y=100) 

# Botón de "Salir", llama a la función "salir"
botonSalir = Button(raiz, text="Salir", command = salir).place(x=410, y=450) 

# Botón de Tipo de Gráfica 1, llama a la función "ventanaGrafica1"
imagen1 = PhotoImage(file = "img\g1.png")
botonImagen1 = Button(raiz, image = imagen1, command = ventanaGrafica1, height=120, width =200).place(x= 80, y = 200) # 240 px entre una imagen y otra

# Botón de Tipo de Gráfica 2, llama a la función "ventanaGrafica2"
imagen2 = PhotoImage(file = "img\g2.png")
botonImagen2 = Button(raiz, image = imagen2, command = ventanaGrafica2, height=120, width =200).place(x= 320, y = 200) 

# Botón de Tipo de Gráfica 3, llama a la función "ventanaGrafica3"
imagen3 = PhotoImage(file = "img\g3.png")
botonImagen3 = Button(raiz, image = imagen3, command = ventanaGrafica3, height=120, width =200).place(x= 560, y = 200) 


# Pie de foto del Tipo de Gráfica 1
tituloImagen1 = Label(miFrame, text="Gráfico Apilado de Asignaturas", fg="black", font=("Arial", 10)).place(x=70, y=320) 
titulo2Imagen1 = Label(miFrame, text="por Curso", fg="black", font=("Arial", 10)).place(x=70, y=342) # Dejar 22 px entre líneas.

# Pie de foto del Tipo de Gráfica 2
tituloImagen2 = Label(miFrame, text="Gráfico de Máximos, Mínimos y", fg="black", font=("Arial", 10)).place(x=310, y=320)
titulo2Imagen2 = Label(miFrame, text="Medias por Curso", fg="black", font=("Arial", 10)).place(x=310, y=342)

# Pie de foto del Tipo de Gráfica 3
tituloImagen3 = Label(miFrame, text="Gráfico de Máximos, Mínimos y", fg="black", font=("Arial", 10)).place(x=550, y=320)
titulo2Imagen3 = Label(miFrame, text="Medias por Semestre", fg="black", font=("Arial", 10)).place(x=550, y=342)

menu = menuSuperior(raiz) # Se llama a la clase anterior y se crea el menu.

raiz.mainloop() # Para que la aplicación se ejecute continuamente

