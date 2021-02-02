#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import random
import fileinput
import matplotlib.pyplot as plt
import math



from scipy.interpolate import spline
from matplotlib import colors

gamma=0.073529
parameters=[0.1,1,10]

param= sys.argv[1].split(',')[0]
if "." in param:
    param=float(param)
else:
    param=int(param)

#Crea el .fdf para diferentes valores de U/gamma
for p in parameters:
    old_file=open("2d_template_holes.fdf","r")
    new_file=open("2d_hubbard_"+str(p)+".fdf","w")
    for line in old_file:
        if "Cambiame" in line:
            new_file.write("Parameter_file 2d_hubbard_"+str(p)+".xml"+ "\n")
        elif "Dimensiones" in line:
            new_file.write("10,10,1"+ "\n")
        else:
            new_file.write(line)
    new_file.close()


def Correlacion(file):
    f=open(file,"r")
    lines=f.readlines()
    line=lines[0].split()
    dimension=int(line[0])*int(line[1])*int(line[2])
    x=[]#Array de correlacion en x
    y=[]#Array de correlacion en y
    L=int(math.sqrt(dimension))#Longitud de la celda (suponemos cuadrada)
    S=np.zeros((L,L))#Matriz con los spines (la entrada S[f][c] representa el spin en la pos. (f,c))
    f=9 #Fila
    c=0 #Columna
    J=0 #Spin total del sistema
    for i in range(0,dimension):
        pos=4+i#Posicion del atomo considerado
        line=lines[pos].split()
        s=float(line[4])-float(line[5])#Spin del atomo considerado
        J=+s
        #s=float(lines[pos][22:29])-float(lines[pos][31:])
        #print(s)

        # #print("Posición: ("+str(f)+","+str(c)+")")
        # S[f,c]=s
        # #print("fila: "+str(f))
        # #print("columna: "+str(c))
        # #print(S)
        # f+=-1
        # if lines[pos][9]==str(L-1):#Cambio de columna
        #     c+=1
        #     f=9

        #CONDICIONES DE CONTORNO PERIODICAS: (L+1,k)=(0,k); (k,L+1)=(k,0)

        #Calcula spin para vecino en x
        if line[0]==str(L-1):#Si esta en el borde, vuelve al primero de la columna
            s_x=float(lines[pos-L*(L-1)].split()[4])-float(lines[pos-L*(L-1)].split()[5])

        else:#Si no, coge el siguiente
            s_x=float(lines[pos+L].split()[4])-float(lines[pos+L].split()[5])

        #Calcula spin para vecino en y
        if line[1]==str(L-1): #Si esta en el borde, vuelve al primero de la columna
            s_y=float(lines[pos-(L-1)].split()[4])-float(lines[pos-(L-1)].split()[5])

        else:#Si no, coge el siguiente
            s_y=float(lines[pos+1].split()[4])-float(lines[pos+1].split()[5])

        x.append(s*s_x)#Realiza la resta en x
        y.append(s*s_y)#Realiza la resta en y

    corr_x=sum(x)/dimension #Calcula la correlacion en X
    corr_y=sum(y)/dimension #Calcula la correlacion en Y

    return [0.5*(corr_x+corr_y),corr_x,corr_y] #Devuelve la semisuma de las correlaciones y las correlaciones


def Ejecucion(p):
    os.system("../../Carrera/Quinto/TFG_Física/scale-up-1.0.0/build_dir/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")#Este es para local
    #os.system("/software/citimac/SCALE-UP/scale-up-1.0.0/build_gnu/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")#Este es para tejo
    #Devuelve la energia
    g=open("output","r")
    for line in g: #Lee la energia del sistema
        if "Total Energy" in line:
            l=line.split()
            return float(l[3]) #Me devuelve la energia

E=Ejecucion(param)
print("Parameter: "+str(param))
print("Energy: "+str(E)+" eV = "+str(E/(2*param/gamma))+" U/\u03B3")
#print("Energy: "+str(E/(2*param/gamma))+" U/\u03B3")
print("Initial correlation: "+str(Correlacion("initial_occ.orbocc")))
print("Final correlation: "+str(Correlacion("_2d_hubbard_FINAL.orbocc")))
