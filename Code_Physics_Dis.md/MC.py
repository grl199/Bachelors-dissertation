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

#Creamos array con temperatnuras
Tmax=20000
Tmin=100
steps=8
T=np.linspace(Tmin,Tmax,steps)
#T=[2000,3000,4000,5000,6000,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,13000,14000,15000,16000,17000,18000,19000,20000]
Tmax=max(list(T))
Tmin=min(list(T))
Nsweeps=10
Nterm=0.3*Nsweeps
param=[0.1,1,10]
kb=1.38064852e-23#Constante de Boltzman
e=1.602176e-19#Factor de conversion J/ev
gamma=0.073529
gamma_ev=gamma*27.2

Dimension="10,10,1"
#L=int(Dimension[0])
L=int(Dimension[0]+Dimension[1])
#Diferentes valosres del parametro U/gamma a considerar
param=[0.1,1,10]
NumHuecos=0

def CrearLattice():
    #Ejecuta Orden_holes.py y almacena el numero de huecos
    os.system("python Orden_holes.py "+Dimension+" random "+str(NumHuecos))
    config_old=open("initial_occ_old.orbocc","r")
    config_new=open("initial_occ.orbocc","w")
    os.system("rm initial_occ_old.orbocc")
    ReadHoles=False
    for line in config_old: #Lee del archivo .orbocc el num de huecos y borra esa linea
        if "Holes" in line:
            h=line[6:]
            ReadHoles=True
            continue
        if ReadHoles:
            holes=line[0:]
        config_new.write(line)
    config_new.close()

    # #Crea el .xml para diferentes valores de U/gamma
    # for p in param:
    #     old_file=open("2d_template.xml","r")
    #     new_file=open("2d_hubbard_"+str(p)+".xml","w")
    #     for line in old_file:
    #         if "Cambiame" in line:
    #             new_file.write("                <interaction_ee gamma_1="+"\"1\""+" gamma_2="+"\"1\""+" hopa="+"\"0\""+" hopb="+"\"0\""+" hopc="+"\"0\""+" hubbard="+"\""+ str(2*p)+"\""+" stoner="+"\""+ str(2*p)+"\""+"></interaction_ee>"+ "\n")
    #         else:
    #             new_file.write(line)
    #     new_file.close()

    #Crea el .fdf para diferentes valores de U/gamma
    for p in param:
        old_file=open("2d_template_holes.fdf","r")
        new_file=open("2d_hubbard_"+str(p)+".fdf","w")
        for line in old_file:
            if "Cambiame" in line:
                new_file.write("Parameter_file 2d_hubbard_"+str(p)+".xml"+ "\n")
            elif "Carga" in line:
                new_file.write("Totalcharge "+h+ "\n")
            elif "Dimensiones" in line:
                new_file.write(Dimension +"\n")
            else:
                new_file.write(line)
        new_file.close()
    #os.system("mv initial_occ.orbocc viejo")
    #os.system("mv nuevo initial_occ.orbocc")

def FlipSpin(input,output,posicion):#Cambia spin (lo flipea) en un .orbocc
    ##
    #Realizamos una leve permutacion en el spin de una posicion al azar
    ##
    old=open(input,"r")
    new=open(output,"w")
    lines=old.readlines()
    new.write(lines[0])
    new.write(lines[1])
    new.write(lines[2])
    new.write(lines[3])
    for i in range(L*L):
        pos=4+i
        if pos==posicion:
            line=lines[pos].split()
            #r=-1+2*random.random()
            #new.write("   "+line[0]+"   "+line[1]+"   "+line[2]+"   "+line[3]+"   "+str(r)+"   "+str(-r)+ "\n")
            new.write(line[0]+"   "+line[1]+"   "+line[2]+"   "+line[3]+"   "+str(-float(line[4]))+"   "+str(-float(line[5]))+ "\n")
        else:
            new.write(lines[pos])



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

def Perturbacion():
    ##
    #Realizamos una leve permutacion en el spin de una posicion al azar
    ##
    old=open("initial_occ.orbocc","r")
    new=open("nuevo","w")
    lines=old.readlines()
    #Cogemos la posicion
    posicion=3+random.choice([i for i in range(1,L*L+1)])
    new.write(lines[0])
    new.write(lines[1])
    new.write(lines[2])
    new.write(lines[3])
    for i in range(1,L**2+1):
        pos=3+i
        if pos==posicion:
            line=lines[pos].split()
            #Cambiamos el spin por un numero random entre -1 y 1
            r=-1+2*random.random()
            #new.write("   "+line[0]+"   "+line[1]+"   "+line[2]+"   "+line[3]+"   "+str(r)+"   "+str(-r)+ "\n")
            new.write("    "+line[0]+"   "+line[1]+"   "+line[2]+"   "+line[3]+"   "+str(-float(line[4]))+"   "+str(-float(line[5]))+ "\n")

        else:
            new.write("    "+lines[pos])

    os.system("mv initial_occ.orbocc viejo")
    os.system("mv nuevo initial_occ.orbocc")


def Permutar():
    ##
    #Realizamos una leve permutacion en el spin de una posicion al azar
    ##
    old=open("initial_occ.orbocc","r")
    new=open("nuevo","w")
    lines=old.readlines()
    #Cogemos la posicion
    posicion1=3+random.choice([i for i in range(1,L*L+1)])
    posicion2=posicion1
    while posicion2==posicion1:
        posicion2=3+random.choice([i for i in range(1,L*L+1)])
    new.write(lines[0])
    new.write(lines[1])
    new.write(lines[2])
    new.write(lines[3])
    linemax=lines[max(posicion1,posicion2)].split()
    linemin=lines[min(posicion1,posicion2)].split()
    for i in range(1,L**2+1):
        pos=3+i
        line=lines[pos].split()
        if pos==min(posicion1,posicion2):
            new.write("    "+line[0]+"    "+line[1]+"    "+line[2]+"    "+line[3]+"    "+linemax[4]+"    "+linemax[5]+ "\n")
        elif pos==max(posicion1,posicion2):
            new.write("    "+line[0]+"    "+line[1]+"    "+line[2]+"    "+line[3]+"    "+linemin[4]+"    "+linemin[5]+ "\n")
        else:
            new.write(lines[pos])
    # os.system("mv initial_occ.orbocc viejo")
    # os.system("mv nuevo initial_occ.orbocc")

#Ejecuta el codigo y guarda los resultados
def Ejecucion(p):
    os.system("../../Carrera/Quinto/TFG_Física/scale-up-1.0.0/build_dir/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")#Este es para local
    #os.system("/software/citimac/SCALE-UP/scale-up-1.0.0/build_gnu/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")#Este es para tejo
    #Devuelve la energia
    g=open("output","r")
    for line in g: #Lee la energia del sistema
        if "Total Energy" in line:
            l=line.split()
            return float(l[3]) #Me devuelve la energia

def Change_kSampling(k,p):#Me cambia el k-sampling del .fdf
    old=open("2d_hubbard_"+str(p)+".fdf","r")
    new=open("new","w")
    lines=old.readlines()
    for l in lines:
        if "%block k-sampling" in l:
            index=lines.index(l)+1
    for l in lines:
        if lines.index(l)==index:
            new.write(str(k)+" "+str(k)+" 1"+ "\n")
        else:
            new.write(l)
    os.system("mv new 2d_hubbard_"+str(p)+".fdf")



# def DensityOfStates(fichero):
#     output=open(fichero,"r")
#     #DOS=open("DOS","w")
#     lines=output.readlines()
#     ener=[]
#     i=5
#     while int(lines[i].split()[0])<2:
#         for element in lines[i].split():
#             if lines[i].split().index(element)>2:
#                 ener.append(element)
#         i+=1

#     # for element in lines[5].split():
#     #     if lines[5].split().index(element)>2:
#     #         dos.append(element)

#     ener=[float(d) for d in ener]
#     # grid=list(np.linspace(min(dos),max(dos),100))
#     # dos_y=[]
#     # E=[]
#     # for i in range(len(grid)-1):
#     #     E.append(0.5*(grid[i]+grid[i+1]))
#     #     j=0
#     #     for k in dos:
#     #         if k>=grid[i] and k<=grid[i+1]:
#     #             j+=1
#     #     dos_y.append(j)
#     #
#     # #plt.plot(E,dos_y,'r')
#     # #plt.show()
#     # return [E,dos_y]
#     return ener

def DensityOfStates(fichero,spin):
    output=open(fichero,"r")
    #DOS=open("DOS","w")
    lines=output.readlines()
    ener=[]
    if spin==1:
        i=5
        while int(lines[i].split()[0])<2:
            for element in lines[i].split():
                if lines[i].split().index(element)>2:
                    ener.append(element)
            i+=1

        ener=[float(d) for d in ener]
        return ener
    else:
        for l in lines:
            if l.split()[0]=="2":
                for element in l.split():
                    if l.split().index(element)>2:
                        ener.append(element)
        ener=[float(d) for d in ener]                
        return ener


def MC(p,Nsweeps):
    CrearLattice()
    #Change_kSampling(3)
    #Borramos archivos anteriores
    os.system("rm -r Archivos_orbocc/*")
    os.system("rm -r IndicadorAvance/*")
    os.system("rm -r NoConvergidos/*")

    energias=open("Energias","w")
    energias.write("**********************************************************************************************************************************"+ "\n")
    energias.write("                                          OUTPUT OF MONTECARLO METHOD"+ "\n")
    energias.write("**********************************************************************************************************************************"+ "\n")
    energias.write("Temperatures   ")
    for t in T:
        energias.write(str(t)+"  ")
    energias.write("\n")
    energias.write("Lattice: "+str(L)+" x "+str(L)+" x 1"+ "\n")
    energias.write("Number of sweeps: "+str(Nsweeps)+ "\n")
    energias.write("Number of temperatures: "+str(len(list(T)))+ "\n")
    energias.write("************************************************************"+ "\n")

    ##Calcula la correlacion de los estados ferro y antiferro para despues normalizar


    #Ferro


    os.system("python Orden.py 2,2,1 random True False False False")
    for gamma in param:
        old_file=open("2d_template_holes.fdf","r")
        new_file=open("2d_hubbard_"+str(gamma)+".fdf","w")
        for line in old_file:
            if "Cambiame" in line:
                new_file.write("Parameter_file 2d_hubbard_"+str(gamma)+".xml"+ "\n")
            elif "Carga" in line:
                #new_file.write("Totalcharge 0" +"\n")
                pass
            elif "Dimensiones" in line:
                new_file.write("2,2,1" +"\n")
            elif "SCFthreshold" in line:
                #new_file.write("SCFthreshold 0.01" +"\n")
                pass
            else:
                new_file.write(line)
        new_file.close()

    #os.system("python Orden.py "+Dimension+" random True False")
    Change_kSampling(2,p)
    E_ferro=Ejecucion(p)
    corr_ferro=Correlacion("_2d_hubbard_FINAL.orbocc")[0]
    os.system("cp _2d_hubbard_FINAL.orbocc FM.orbocc")
    if E_ferro==None:
        print("FM no converge")
        corr_ferro=1
    else:
        corr_ferro=Correlacion("_2d_hubbard_FINAL.orbocc")[0]
        print(corr_ferro)




    CrearLattice()#Esto resetea el k-sampling

    #Antiferro

    # os.system("python Orden.py 8,8,1 random False True")
    # for gamma in param:
    #     old_file=open("2d_template_holes.fdf","r")
    #     new_file=open("2d_hubbard_"+str(gamma)+".fdf","w")
    #     for line in old_file:
    #         if "Cambiame" in line:
    #             new_file.write("Parameter_file 2d_hubbard_"+str(gamma)+".xml"+ "\n")
    #         elif "Carga" in line:
    #             new_file.write("Totalcharge 0 "+"\n")
    #         elif "Dimensiones" in line:
    #             new_file.write("8,8,1" +"\n")
    #         else:
    #             new_file.write(line)
    #     new_file.close()
    os.system("python Orden.py "+Dimension+" random False True False False")
    E_antiferro=Ejecucion(p)
    corr_antiferro=Correlacion("_2d_hubbard_FINAL.orbocc")[0]
    os.system("cp _2d_hubbard_FINAL.orbocc AFM.orbocc")
    if E_antiferro==None:
        print("AFM no converge")
        corr_antiferro=-1
    else:
        corr_antiferro=Correlacion("_2d_hubbard_FINAL.orbocc")[0]
        print(corr_antiferro)


    ##Correlaciones ferro y antiferro en X y en Y

    os.system("python Orden.py "+Dimension+" random False False True False")#Ferro X, antiferro Y
    Ejecucion(p)
    corr_FM_x=Correlacion("_2d_hubbard_FINAL.orbocc")[1]
    corr_AFM_y=Correlacion("_2d_hubbard_FINAL.orbocc")[2]

    os.system("python Orden.py "+Dimension+" random False False False True")#Ferro Y, antiferro X
    Ejecucion(p)
    corr_AFM_x=Correlacion("_2d_hubbard_FINAL.orbocc")[1]
    corr_FM_y=Correlacion("_2d_hubbard_FINAL.orbocc")[2]



    energias.write("Correlation FM: "+str(corr_ferro)+"         X-FM correlation: "+str(corr_FM_x)+"         Y-FM correlation: "+str(corr_FM_y)+"           Energy FM: "+str(E_ferro)+"  eV"+"\n")
    energias.write("Correlation AFM: "+str(corr_antiferro)+"        X-AFM correlation: "+str(corr_AFM_x)+"         Y-AFM correlation: "+str(corr_AFM_y)+"           Energy AFM: "+str(E_antiferro)+"  eV"+"\n")
    energias.write("\n")
    #CrearLattice()
    os.system("python Orden.py "+Dimension+" random False True False False")
    os.system("cp initial_occ.orbocc Referencia.orbocc")

    k=1
    os.system("mkdir IndicadorAvance")
    snapshot=[]#Aqui guardamos las instantaneas
    snapshot_x=[]#Aqui guardamos las instantaneas en X
    snapshot_y=[]#Aqui guardamos las instantaneas en Y
    corr=[]#Aqui la correlacion
    corr_x=[]#Aqui en X
    corr_y=[]#Aqui en Y
    dos_inst=[]#Aqui la dos instantanea
    dos=[]#Aqui la dos promediada

    #print(Ejecucion(p))
    E=Ejecucion(p)#Guarda la energia
    print("First energy  "+str(E)+"  eV ="+str(E/(2*p/gamma))+" U/\u03B3")
    print("First correlation "+str(Correlacion("initial_occ.orbocc")[0]))
    #os.system("mv _2d_hubbard_FINAL.orbocc initial_occ.orbocc")
    energias.write("First energy  "+str(E)+"  eV"+ "\n")
    energias.write("First correlation (initial lattice) "+str(format(Correlacion("initial_occ.orbocc")[0], '.16f'))+ "\n")
    #os.system("mv _2d_hubbard_FINAL.orbocc initial_occ.orbocc")
    #lattice="initial_occ.orbocc"
    os.system("cp initial_occ.orbocc lattice")#Lattice con la que calculamos la correlacion
    os.system("cp _2d_hubbard_FINAL.ener DOS")#Fichero con el que calculamos la dos para k-sampling=1
    os.system("mkdir Archivos_orbocc")#Directorio donde guardamos los .orboc de los que calculamos la dos para k-sampling el que queramos (despues del MC)
    os.system("mkdir NoConvergidos")#Guarda aqui los no convergidos
    for t in T:
        os.system("mkdir NoConvergidos/Temp_"+str(t))
        os.system("mkdir Archivos_orbocc/Temp_"+str(t))

    for t in T:
        energias.write("\n")
        energias.write("T="+str(t)+" K"+ "\n")
        energias.write("\n")
        #energias.write("SCF energy (eV)    "+"    Last energy (eV)    "+"    Energy difference (eV)    "+"    Boltzmann factor    "+"    Accept"+ "\n")
        #energias.write("SCF energy (eV)    "+"    Last energy (eV)    "+"     Accept"+"    "+"              Correlation"       +"           Normalized correlation"+"     ")
        #energias.write("              X correlation       "+"          Normalized X correlation           "+"          Y correlation         "+"         Normalized Y correlation" +"\n")
        energias.write("SCF energy (eV)    "+"    Last energy (eV)    "+"     Accept"+"    "+"              Correlation"+"           ")
        energias.write("              X correlation       "+"                Y correlation         "+"\n")
        num=1#Variable que cuenta el numero simulaciones a esta temperatura
        orb=0#Variable que cuenta el numero de .orbocc movidos a dicho fichero
        for n in range(Nsweeps):
            for i in range(L*L):
                pos=4+i
                FlipSpin("Referencia.orbocc","initial_occ.orbocc",pos)#Flipeamos spin
                E2=Ejecucion(p)#Guarda la energia
                if E2==None:
                    print("No converge")
                    energias.write("Does not converge, correlation: "+str(Correlacion("initial_occ.orbocc")[0])+"\n")
                    os.system("cp initial_occ.orbocc NoConvergidos/Temp_"+str(t)+"/initial_occ.orbocc_"+str(num))
                    num+=1
                    continue
                Dif=E2-E#Aqui tenemos la diferencia de energias
                print("Energy:  "+str(E2)+" eV ="+str(E2/(2*p/gamma))+" U/\u03B3")
                print("Difference:  "+str(Dif)+" eV ="+str(Dif/(2*p/gamma))+" U/\u03B3")
                #energias.write("Energía    "+str(E2)+"  eV")

                energias.write("   "+str(format(E2,'.5f'))+"      "+"      "+str(format(E,'.5f'))+"          ")
                #print(math.exp(-Dif*e/(k*t)))
                if Dif<0:#Aceptamos
                    E=E2#Actualizamos la energia
                    os.system("cp _2d_hubbard_FINAL.orbocc lattice")
                    os.system("cp _2d_hubbard_FINAL.ener DOS")#Actualizamos las energias
                    #energias.write("   Aceptamos"+"  Energía actual: "+str(E)+ "\n")
                    #energias.write("       YES"+"       "+str(Correlacion("lattice"))+ "\n")
                    energias.write("       YES"+"       ")
                    #energias.write("       YES"+"       "+str(Correlacion("initial_occ.orbocc"))+ "\n")
                    print("YES")
                    os.system("cp initial_occ.orbocc Referencia.orbocc")#Actualizamos la referencia

                elif math.exp(-Dif*e/(kb*t))>random.random():#Aceptamos el Cambio
                    E=E2#Actualizamos la energia
                    #energias.write("   Aceptamos"+"  Energía actual: "+str(E)+ "\n")
                    os.system("cp _2d_hubbard_FINAL.orbocc lattice")
                    os.system("cp _2d_hubbard_FINAL.ener DOS")#Actualizamos las energias
                    #energias.write("       YES"+"       "+str(Correlacion("lattice"))+ "\n")
                    energias.write("       YES"+"       ")
                    #energias.write("       YES"+"       "+str(Correlacion("initial_occ.orbocc"))+ "\n")
                    print("YES")
                    os.system("cp initial_occ.orbocc Referencia.orbocc")#Actualizamos la referencia

                else:
                    #energias.write("   NO aceptamos"+"  Energía actual: "+str(E)+ "\n")
                    #energias.write("        NO"+"       "+str(Correlacion("lattice"))+ "\n")
                    energias.write("       NO"+"       ")
                    print("NO")


                correl=Correlacion("lattice")[0]
                # if correl>corr_ferro:#Si es mayor que la ferro, se la asignamos
                #     correl=corr_ferro
                # elif correl<corr_antiferro:#Si es menor que la antiferro, se la asignamos
                #     correl=corr_antiferro
                #energias.write("         "+str(correl)+"                 ")

                correl_x=Correlacion("lattice")[1]
                #energias.write("           "+str(correl_x)+"                 ")
                if correl_x>-1 and correl_x <1: #Si no esta normalizada normalizamos
                    if correl_x>0:#Normalizamos
                        correl_x=correl_x/abs(corr_FM_x)
                    else:
                        correl_x=correl_x/abs(corr_AFM_x)
                if correl_x>1 or correl_x<-1:
                    energias.write("            "+str(format(correl_x,'.16f'))+"         " "\n")
                    print("Normalization fails")
                    return -1 #Si pasa esto, salimos del programa


                correl_y=Correlacion("lattice")[2]
                #energias.write("                     "+str(correl_y)+"            ")
                if correl_y>-1 and correl_y <1: #Si no esta normalizada normalizamos
                    if correl_y>0:#Normalizamos
                        correl_y=correl_y/abs(corr_FM_y)
                    else:
                        correl_y=correl_y/abs(corr_AFM_y)
                if correl_y>1 or correl_y<-1:
                    energias.write("       "+str(format(correl_y,'.16f'))+"\n")
                    print("Normalization fails")
                    return -1 #Si pasa esto, salimos del programa


                if correl>-1 and correl <1: #Si no esta normalizada normalizamos
                    if correl>0:#Normalizamos
                        correl=correl/abs(corr_ferro)
                    else:
                        correl=correl/abs(corr_antiferro)
                if correl>1 or correl<-1:
                    energias.write("               "+str(format(correl,'.16f'))+"          " "\n")
                    print("Normalization fails")
                    return -1

                correl=0.5*(correl_x+correl_y)
                energias.write("        "+str(format(correl,'.16f'))+"     ")
                energias.write("              "+str(format(correl_x,'.16f'))+"        ")
                energias.write("         "+str(format(correl_y,'.16f'))+"\n")


                print("Correlation: "+str(correl))
                print("Temperature: "+str(t)+" K")
                #Numero=(list(T).index(t)+1)*(n+i)
                k+=1
                print(str(100*k/(Nsweeps*len(list(T))*L*L))+" %")
                print("  ")
                print("  ")
                os.system("rm -r IndicadorAvance/*")
                os.system("mkdir IndicadorAvance/"+str(100*k/(Nsweeps*len(list(T))*L*L)))

            #Para ciertos pasos calculamos la Correlacion y la dos
            if n>=Nterm:
                snapshot.append(correl)
                snapshot_x.append(correl_x)
                snapshot_y.append(correl_y)
                dos_inst.append(DensityOfStates("DOS"))

                #Colocamos el initial.orbocc en un fichero aparte para despues calcular la DOS con mayor k-sampling
                os.system("cp Referencia.orbocc initial_occ.orbocc_"+str(orb))
                # os.system("mv initial_occ.orbocc_"+str(orb)+" Archivos_orbocc")
                # orb+=1

                os.system("mv initial_occ.orbocc_"+str(orb)+" Archivos_orbocc/Temp_"+str(t))
                # os.system("mv Archivos_orbocc/Temp_"+str(t)+"/initial_occ.orbocc Archivos_orbocc/Temp_"+str(t)+"/initial_occ.orboc_"+str(num))
                #os.system("cp lattice Archivos_orbocc/Temp_"+str(t))
                #os.system("mv Archivos_orbocc/Temp_"+str(t)+"/lattice Archivos_orbocc/Temp_"+str(t)+"/initial_occ.orboc_"+str(num))
                orb+=1
                num+=1


            #snapshot.append(Correlacion("initial_occ.orbocc"))
            os.system("mkdir IndicadorAvance/"+str(100*k/(Nsweeps*len(list(T))*L*L)))

        #Array promediado con densidad de estados a esta temperatura
        #array_dos=[sum(d)/len(dos_inst) for d in dos_inst]

        array_dos=[]
        for i in range(len(dos_inst[0])):
            s=0
            for j in range(len(dos_inst)):
                s+=dos_inst[j][i]
            array_dos.append(s/(len(dos_inst)))
        dos.append(array_dos)
        corr.append(sum(snapshot)/len(snapshot))
        corr_x.append(sum(snapshot_x)/len(snapshot_y))
        corr_y.append(sum(snapshot_y)/len(snapshot_y))
        energias.write("\n")
        energias.write("Average correlation: "+str(corr[len(corr)-1])+"\n")
        energias.write("Average X correlation: "+str(corr_x[len(corr_x)-1])+"\n")
        energias.write("Average Y correlation: "+str(corr_y[len(corr_y)-1])+"\n")
        snapshot_x=[]
        snapshot_y=[]
        snapshot=[]
        dos_inst=[]



        energias.write("DOS energies   ")
        for d in dos[list(T).index(t)]:
            energias.write(str(d)+"  ")
        energias.write("\n")
        energias.write("\n")
        # Ener=DensityOfStates("DOS")[1]
        # for en in Ener:
        #     energias.write(str(en)+"  ")
        # energias.write("\n")
        # energias.write("\n")



        # plt.plot(dos[0],Ener,'r')
        # plt.xlabel("Energy (eV)")
        # plt.ylabel("Density of states (arbitrary units)")
        # #plt.show()
        # plt.savefig("DOS_"+str(t)+".png")
        # plt.clf()
        # dos=[]
        # Ener=[]


    energias.write("\n")
    energias.write("Correlation   ")
    for c in corr:
        energias.write(str(c)+"  ")
    energias.write("\n")
    energias.write("\n")

    energias.write("X correlation   ")
    for c in corr_x:
        energias.write(str(c)+"  ")
    energias.write("\n")
    energias.write("\n")

    energias.write("Y correlation   ")
    for c in corr_y:
        energias.write(str(c)+"  ")
    energias.write("\n")
    energias.write("\n")

    energias.write("Temperatures   ")
    for t in T:
        energias.write(str(t)+"  ")
    os.system("rm viejo")
    os.system("rm -r IndicadorAvance")

    return [corr,corr_x,corr_y]



#os.system("rm -r IndicadorAvance/*")
#CrearLattice()
# os.system("python Orden.py "+Dimension+" random True False")
# print(Correlacion("initial_occ.orbocc"))


# p=0.1
# #Ferro
# #os.system("python Orden.py "+Dimension+" random True False")
# Ejecucion(p)
# corr_ferro=Correlacion("_2d_hubbard_FINAL.orbocc")
# print(corr_ferro)
# #Antiferro
# os.system("python Orden.py "+Dimension+" random False True")
# Ejecucion(p)
# corr_antiferro=Correlacion("_2d_hubbard_FINAL.orbocc")
# print(corr_antiferro)

#print(Correlacion("_2d_hubbard_FINAL.orbocc"))
#print(Correlacion("lattice"))
#print(Correlacion("Referencia.orbocc"))
#print(Correlacion("initial_occ.orbocc"))



#corr=MC(10,Nsweeps)
# plt.plot(T,corr,'bo',label="Correlation vs temperature")
# plt.savefig("Montecarlo_Ejemplo.png")
# plt.xlabel("Temperature (K)")
# plt.ylabel("Correlation")
# plt.show()



    # grid=list(np.linspace(min(dos),max(dos),100))
    # dos_y=[]
    # E=[]
    # for i in range(len(grid)-1):
    #     E.append(0.5*(grid[i]+grid[i+1]))
    #     j=0
    #     for k in dos:
    #         if k>=grid[i] and k<=grid[i+1]:
    #             j+=1
    #     dos_y.append(j)

def ComputeDOS(k,p):#Corremos SCUP para los .orbocc en Archivos_orbocc con un k-sampling mas fino
    file=open("Energias","r")
    lines=file.readlines()
    T=lines[3].split()[1:]
    os.system("mkdir IndicadorAvanceDOS")
    contador=0
    fichero_up=open("DensEst_up","w")
    fichero_down=open("DensEst_down","w")
    Change_kSampling(k,p)#Cambiamos el k-sampling
    Temp=list(T)
    dos_inst_up=[]
    dos_inst_down=[]
    dos_up=[]
    dos_down=[]
    N=Nsweeps-int(math.ceil(Nterm))#numero de ficheros por temperatura

    for t in range(len(Temp)):
        print(Temp[t])
        fichero_up.write("T= "+str(T[t])+"  K"+"\n")
        fichero_up.write("\n")
        fichero_down.write("T= "+str(T[t])+"  K"+"\n")
        fichero_down.write("\n")
        # for n in range(1,N+1):
        #     index=N*t+n
        #     print(index)
        #     os.system("cp Archivos_orbocc/initial_occ.orbocc_"+str(index)+" ~/Desktop/TFG_Física/Main/initial_occ.orbocc")
        #     Ejecucion(p)#Ejecutamos
        #     dos_inst.append(DensityOfStates("_2d_hubbard_FINAL.ener"))
        for file in os.listdir("Archivos_orbocc/Temp_"+str(Temp[t])):
            os.system("python ErrorCarga.py")
            os.system("cp Archivos_orbocc/Temp_"+str(Temp[t])+"/"+file+" ~/Desktop/TFG_Física/Main/initial_occ.orbocc")
            Ejecucion(p)#Ejecutamos
            dos_inst_up.append(DensityOfStates("_2d_hubbard_FINAL.ener",1))
            dos_inst_down.append(DensityOfStates("_2d_hubbard_FINAL.ener",2))
            contador+=1
            os.system("rm -r IndicadorAvanceDOS/*")
            os.system("mkdir IndicadorAvanceDOS/"+str(contador/N*len(Temp)))
        array_dos_up=[]
        array_dos_down=[]
        for i in range(len(dos_inst_up[0])):
            up=0
            for j in range(len(dos_inst_up)):
                up+=dos_inst_up[j][i]
            array_dos_up.append(up/(len(dos_inst_up)))
        for i in range(len(dos_inst_down[0])):
            down=0
            for j in range(len(dos_inst_down)):
                down+=dos_inst_down[j][i]
            array_dos_down.append(down/(len(dos_inst_down)))
        dos_up.append(array_dos_up)
        dos_down.append(array_dos_down)
        fichero_up.write("DOS up energies   ")
        fichero_down.write("DOS down energies   ")
        for d in dos_up[t]:
            fichero_up.write(str(d)+"  ")
        for d in dos_down[t]:
            fichero_down.write(str(d)+"  ")
        fichero_up.write("\n")
        fichero_down.write("\n")
        snapshot=[]
        dos_inst_up=[]
        dos_inst_down=[]
    os.system("rm -r IndicadorAvanceDOS")



#ComputeDOS(4,0.1)


def PlotDOS():
    os.system("rm DOS_*")
    en=open("Energias","r")
    lines=en.readlines()
    t=lines[3].split()[1:]

    input_up=open("DensEst_up","r")
    input_down=open("DensEst_down","r")
    lines_up=input_up.readlines()
    lines_down=input_down.readlines()
    k=0
    for l in lines_up:
        if "DOS up energies" in l:
            index=lines_up.index(l)
            line=l.split()
            line.pop(0)
            line.pop(0)
            line.pop(0)
            E=[float(e) for e in line]

            # line=lines[index+2].split()
            # line.pop(0)
            # line.pop(0)
            # line.pop(0)
            # dos=[float(d) for d in line]

            grid=list(np.linspace(min(E),max(E),60))
            E_bis=[]
            dos=[]
            for i in range(len(grid)-1):
                E_bis.append(0.5*(grid[i]+grid[i+1]))
                j=0
                for en in E:
                    if en>=grid[i] and en<=grid[i+1]:
                        j+=1
                dos.append(j)
            xnew = np.linspace(min(E_bis), max(E_bis), 10000)
            dos_smooth = spline(E_bis, dos, xnew)
            for i in range(len(dos_smooth)):
                if dos_smooth[i]<0:
                    dos_smooth[i]=0
                if float(t[k])<=3000:
                    if xnew[i]<3.75 and xnew[i]>-3.75:
                         dos_smooth[i]=0
            plt.plot(E_bis,dos,'r',label="Spin up")   
            #plt.plot(xnew,dos_smooth,'b',label="Spin up")
            #plt.plot(xnew,dos_smooth,'b')
            plt.plot([list(xnew)[-1],list(xnew)[-1]+0.0001],[list(dos_smooth)[-1],0],'b')
            plt.plot([list(xnew)[0],list(xnew)[0]+0.0001],[list(dos_smooth)[0],0],'b')
            #plt.legend()

            # t=Tmin+(Tmax-Tmin)*k/steps #Temperatura
            if "antiferro" in l:
                plt.plot(E_bis,dos,'r')
                plt.title("Density of states for antiferromagnetic configuration")
            else:
                plt.title("Density of states for "+str(t[k])+" K")
            plt.xlabel("Energy/\u03B3",size=18)
            #plt.ylabel("DOS (arb. units)",size=18)
            #plt.xticks([])
            plt.yticks([])

            #plt.xlim(-10,10)
            # plt.ylim(-300,2500)
            #plt.show()
            #plt.clf()
            E=[]
            E_bis=[]
            dos=[]

    # for l in lines_down:
    #     if "DOS down energies" in l:

            line=lines_down[index].split()
            line.pop(0)
            line.pop(0)
            line.pop(0)
            E=[float(e) for e in line]

            # line=lines[index+2].split()
            # line.pop(0)
            # line.pop(0)
            # line.pop(0)
            # dos=[float(d) for d in line]

            grid=list(np.linspace(min(E),max(E),60))
            E_bis=[]
            dos=[]
            for i in range(len(grid)-1):
                E_bis.append(0.5*(grid[i]+grid[i+1]))
                j=0
                for en in E:
                    if en>=grid[i] and en<=grid[i+1]:
                        j-=1
                dos.append(j)

            xnew = np.linspace(min(E_bis), max(E_bis), 10000)
            dos_smooth = spline(E_bis, dos, xnew)
            for i in range(len(dos_smooth)):
                if dos_smooth[i]>0:
                    dos_smooth[i]=0
                if float(t[k])<=3000:
                    if xnew[i]<3.75 and xnew[i]>-3.75:
                         dos_smooth[i]=0
            plt.plot(E_bis,dos,'r',label="Spin down")     
            #plt.plot(xnew,dos_smooth,'r',label="Spin down")
            #plt.plot(xnew,dos_smooth,'r')
            #plt.legend()
            plt.plot(list(np.linspace(min(E_bis)-1,max(E_bis)+1,100)),[0 for i in range(100)],'k')
            plt.plot([list(xnew)[-1],list(xnew)[-1]+0.0001],[list(dos_smooth)[-1],0],'r')
            plt.plot([list(xnew)[0],list(xnew)[0]+0.0001],[list(dos_smooth)[0],0],'r')
            plt.xlim(min(E_bis)-1,max(E_bis)+1)


            # t=Tmin+(Tmax-Tmin)*k/steps #Temperatura
            if "antiferro" in l:
                plt.plot(E_bis,dos,'r')
                plt.title("Density of states for antiferromagnetic configuration")
            else:
                a=kb*float(t[k])/(e*gamma_ev)
                #plt.title("Density of states for $K_B$T/\u03B3="+str(round(a,2))+" K")
                plt.title("$K_B$T/\u03B3="+str(round(a,2)),size=18)
                #plt.title("Density of states for T="+str(t[k])+" K")
            #plt.xlabel("Energy/\u03B3",size=18)
            plt.ylabel("DOS (arb. u.)",size=18)
            plt.xticks(np.linspace(-10,10,5),fontsize = 19)
            plt.yticks([])

            #plt.xlim(-10,10)
            # plt.ylim(-300,2500)          
            #plt.show()



            plt.savefig("DOS_"+str(t[k])+".png")
            plt.clf()
            E=[]
            E_bis=[]
            dos=[]
            k+=1
            
PlotDOS()           
def PlotCorr():
    file=open("Energias","r")
    lines=file.readlines()
    correlation=lines[len(lines)-3].split()
    temperature=lines[len(lines)-1].split()
    C=[]
    T=[]
    for c in correlation:
        if correlation.index(c)>0:
            C.append(float(c))

    for t in temperature:
        if temperature.index(t)>0:
            T.append(float(t))

    T=list(T)
    plt.plot(T,C,'bo')
    plt.savefig("Correlation_vs_T.png")
    #plt.show()
    plt.clf()

#PlotCorr()

# old=open("DensEst","r")
# new=open("new","w")
# new.write("Antiferro" +"\n")
# new.write("DOS energies antiferro  ")
# for e in DensityOfStates("_2d_hubbard_FINAL.ener"):
#     new.write(str(e)+"  ")
# new.write("\n")
# new.write("\n")
# for line in old.readlines():
#     new.write(line)


def MapSpin():#Mapa spin de los Archivos_orbocc
    file=open("Energias","r")
    lines=file.readlines()
    Temp=lines[3].split()[1:]
    Temp=[int(t) for t in Temp]
    N=Nsweeps-int(math.ceil(Nterm))#numero de ficheros por temperatura


    for t in range(len(Temp)):
        contador=0
        D=np.zeros((L,L))#Matriz de densidad (la entrada D[f][c] representa la densidad en la pos. (f,c))

        for f in os.listdir("Archivos_orbocc/Temp_"+str(Temp[t])):
            print("cp Archivos_orbocc/Temp_"+str(Temp[t])+"/"+f)
            os.system("cp Archivos_orbocc/Temp_"+str(Temp[t])+"/"+f+" ~/Desktop/TFG_Física/Main/initial_occ.orbocc")
            file=open("initial_occ.orbocc","r")
            print(file)
            lines=file.readlines()
            f=L-1 #Fila
            c=0 #Columna
            for i in range(4,4+L*L):
                s=float(lines[i].split()[4])-float(lines[i].split()[5])
                #Binarizamos
                # if s<0:
                #      s=-s
                # elif s>=2/3:
                #      s=-1
                # else:
                #      s=1
                #print("Fila: "+str(f)+"   Columna: "+str(c))
                D[f,c]+=s
                f+=-1
                if lines[i].split()[1]==str(L-1):#Cambio de columna
                    c+=1
                    f=L-1
            contador+=1
        D=D/contador
        print("Temperature: "+str(Temp[t])+"  K")
        print("  ")
        print(D)
        print(" ")
        img=plt.imshow(D, cmap='Greys', interpolation='nearest')
        plt.xticks([])
        plt.yticks([])
        if t==0:
            plt.colorbar()
        # cb = plt.colorbar()

        # cb.ax.tick_params(labelsize=7)
        plt.savefig("MapaSpin_"+str(Temp[t])+".png")

        
        #plt.show()
        #os.system("open Mapa.png")

# # print(Correlacion("initial_occ.orbocc"))
# # print(Correlacion("_2d_hubbard_FINAL.orbocc"))
# #MapSpin("initial_occ.orbocc")


MapSpin()

######PRUEBA CON DOS
# E=DensityOfStates("_2d_hubbard_FINAL.ener")
# grid=list(np.linspace(min(E),max(E),25))
# E_bis=[]
# dos=[]
# for i in range(len(grid)-1):
#     E_bis.append(0.5*(grid[i]+grid[i+1]))
#     j=0
#     for en in E:
#         if en>=grid[i] and en<=grid[i+1]:
#             j+=1
#     dos.append(j)
#
# xnew = np.linspace(min(E_bis), max(E_bis), 300)
# dos_smooth = spline(E_bis, dos, xnew)
# plt.plot(xnew,dos_smooth,'r')
# plt.xlabel("Energy (eV)")
# plt.ylabel("Density of states (arbitrary units)")
# plt.savefig("Prueba_AFM.png")
# plt.show()

# T=[2000 , 3000,  4000 , 5000  ,6000 , 7000,  7500,  8000  ,8500 , 9000  ,9500 , 10000 , 10500 , 11000 , 11500 , 12000,  12500 , 13000,  14000]
# C=[]
# file=open("Energias",'r')
# for line in file.readlines():
#     if "Average " in line:
#         C.append(line.split()[2])
#
#
# plt.plot(T,C,'ro')
# plt.show()
