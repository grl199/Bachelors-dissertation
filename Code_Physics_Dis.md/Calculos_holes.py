import os
import sys
import numpy as np
import random
import fileinput
import matplotlib.pyplot as plt
import math

from matplotlib import colors


# while 1>0:
#     print("-------------------------------------------------------------------------------")
#     Dimension = input("Introduce the dimensions of the system (e.g for 2x2x1 type 2,2,1 )  ")
#     NumHuecos= int(input("Introduce the number of holes in the system  "))
#     print("-------------------------------------------------------------------------------")
#     #  Console output
#     wait=False
#     print("Dimension: " + Dimension[0]+"x"+Dimension[2]+"x"+Dimension[4])
#     print("nº of holes: " + str(NumHuecos))
#     print(" ")
#     print(" ")
#     print(" ")
#     break

#Creamos array con temperatnuras
Tmax=100
Tmin=100
steps=1
T=np.linspace(Tmin,Tmax,steps)
#T=[2000,3000,4000,5000,6000,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,13000,14000,15000,16000,17000,18000,19000,20000]
Tmax=max(list(T))
Tmin=min(list(T))
Nsweeps=10
Nterm=0*Nsweeps
param=[0.1,1,10]
kb=1.38064852e-23#Constante de Boltzman
e=1.602176e-19#Factor de conversion J/ev

Dimension="4,4,1"
L=int(Dimension[0])
#L=int(Dimension[0]+Dimension[1])
#Diferentes valosres del parametro U/gamma a considerar
param=[0.1,1,10]
NumHuecos=1
huecos=[]



def SwapLines(input,output,perm):#Permuta dos lineas de un array
    input=open(input,"r")
    output=open(output,"w")
    lines=input.readlines()
    for i in range(len(lines)):
        if i==perm[0]:
            output.write(lines[perm[1]])
        elif i==perm[1]:
            output.write(lines[perm[0]])
        else:
            output.write(lines[i])
    output.close()


def random_binary():#Random binary variable
    if random.random()<0.5:
        return False
    else:
        return True

def CreateLattice(random):
    #Ejecuta Orden_holes.py y almacena el numero de huecos
    if random:
        os.system("python Orden_holes.py "+Dimension+" random "+str(NumHuecos))
    else:
        os.system("python Orden_holes.py 4,4,1 +,+,+,-,+,+,-,+,+,-,+,+,-,+,+,+ 4")
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
            break
        config_new.write(line)
    config_new.close()


    ###### Nos construimos el array con la posicion de los huecos que iremos cambiando con el metodo MC
    huecos=[]
    j=1
    while 1>0:
         huecos.append([int(holes[j]),int(holes[j+3]),int(holes[j+6])])
         j=j+9
         if len(huecos)==NumHuecos:
             break
    ######

    #Crea el .xml para diferentes valores de U/gamma
    for p in param:
        old_file=open("2d_template.xml","r")
        new_file=open("2d_hubbard_"+str(p)+".xml","w")
        for line in old_file:
            if "Cambiame" in line:
                new_file.write("                <interaction_ee gamma_1="+"\"1\""+" gamma_2="+"\"1\""+" hopa="+"\"0\""+" hopb="+"\"0\""+" hopc="+"\"0\""+" hubbard="+"\""+ str(2*p)+"\""+" stoner="+"\""+ str(2*p)+"\""+"></interaction_ee>"+ "\n")
            else:
                new_file.write(line)
        new_file.close()

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
    return huecos



#Ejecuta el codigo y guarda los resultados
def Ejecucion(p):
    os.system("../../Carrera/Quinto/TFG_Física/scale-up-1.0.0/build_dir/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")
    #os.system("/software/citimac/SCALE-UP/scale-up-1.0.0/build_gnu/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")
    #Devuelve la energia
    g=open("output","r")
    for line in g: #Lee la energia del sistema
        if "Total Energy" in line:
            l=line.split()
            return float(l[3]) #Me devuelve la energia



def PerturbacionX(input,output,huecos):#Mueve un hueco al azar una posicion en X
    eleccion=random.choice(huecos)
    index=huecos.index(eleccion)
    Derecha=random_binary()#Seleccionamos aleatoriamente si queremos que se desplace hacia la derecha o hacia la izquierda
    #Cogemos tambien el spin del vecino correspondiente

    if Derecha:
        if int(eleccion[0])==int(L)-1: #Ojo a las cond. de contorno periodicas
            Cord=[0,eleccion[1],eleccion[2]]
            if Cord in huecos: #Si el hueco ya esta en la lista
                return True  #Devuelve variable booleana que indica que hay que buscar otra perturbacion
            huecos[index]=Cord
        else:
            Cord=[int(eleccion[0])+1,eleccion[1],eleccion[2]]
            if Cord in huecos:
                return True
            huecos[index]=Cord
    else:
        if int(eleccion[0])==0:
            Cord=[int(L)-1,eleccion[1],eleccion[2]]
            if Cord in huecos:
                return True
            huecos[index]=Cord
        else:
            Cord=[int(eleccion[0])-1,eleccion[1],eleccion[2]]
            if Cord in huecos:
                return True
            huecos[index]=Cord



    #Falta cambiar el .orbocc de acuerdo con esta perturbacion
    inic=open(input,"r")
    #Guarda la configuracion antigua
    #os.system("mv initial_occ.orbocc Referencia.orbocc")
    fin=open("Perturbacion1","w")
    lines=inic.readlines()
    fin.write(lines[0])
    fin.write(lines[1])
    fin.write(lines[2])
    fin.write(lines[3])
    for i in range(0,L**2):
        pos=4+i
        line=lines[pos].split()
        if [str(eleccion[0]),str(eleccion[1]),str(eleccion[2])]==[line[0],line[1],line[2]]:#Encontramos el hueco
            #print("Eleccion: "+str(eleccion[0])+"   "+str(eleccion[1])+"   "+str(eleccion[2]))
            #print(lines[pos])
            s=[lines[pos].split()[4],lines[pos].split()[5]]#Densidad spin de la posicion del hueco
            if Derecha:
                if int(eleccion[0])==int(L)-1: #Ojo a las cond. de contorno periodicas
                    s_x=[lines[pos-L*(L-1)].split()[4],lines[pos-L*(L-1)].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_x[0]+"    "+s_x[1]+ "\n")
                    PosNuevoHueco=pos-L*(L-1)

                else:
                    #print(str(pos)+"     "+str(eleccion[0]))
                    #print(lines[pos])
                    s_x=[lines[pos+L].split()[4],lines[pos+L].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_x[0]+"    "+s_x[1]+ "\n")
                    PosNuevoHueco=pos+L
            else:
                if int(eleccion[0])==0:
                    #print(str(pos)+"     "+str(eleccion[0]))
                    #print(lines[pos])
                    s_x=[lines[pos+L*(L-1)].split()[4],lines[pos+L*(L-1)].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_x[0]+"    "+s_x[1]+ "\n")
                    PosNuevoHueco=pos+L*(L-1)
                else:
                    s_x=[lines[pos-L].split()[4],lines[pos-L].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_x[0]+"    "+s_x[1]+ "\n")
                    PosNuevoHueco=pos-L
        else:
            fin.write(lines[pos])
    fin.close()
    inic.close()
    #Falta meter el nuevo hueco
    inic=open("Perturbacion1","r")
    fin=open("Perturbacion2","w")
    lines=inic.readlines()
    fin.write(lines[0])
    fin.write(lines[1])
    fin.write(lines[2])
    fin.write(lines[3])
    for i in range(0,L**2):
        pos=4+i
        if pos==PosNuevoHueco:
            fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s[0]+"   "+s[1]+ "\n")
        else:
            fin.write(lines[pos])
    fin.close()
    inic.close()
    #Renombra y borra archivos accesorios
    os.system("mv Perturbacion2 initial_occ.orbocc")
    os.system("rm Perturbacion1")

def PerturbacionY(input,output,huecos):#Mueve un hueco al azar una posicion en Y
    eleccion=random.choice(huecos)
    index=huecos.index(eleccion)
    Arriba=random_binary()#Seleccionamos aleatoriamente si queremos que se desplace hacia la derecha o hacia la izquierda
    #Cogemos tambien el spin del vecino correspondiente

    if Arriba:
        if int(eleccion[1])==int(L)-1: #Ojo a las cond. de contorno periodicas
            Cord=[eleccion[0],0,eleccion[2]]
            if Cord in huecos: #Si el hueco ya esta en la lista
                return True  #Devuelve variable booleana que indica que hay que buscar otra perturbacion
            huecos[index]=Cord
        else:
            Cord=[eleccion[0],int(eleccion[1])+1,eleccion[2]]
            if Cord in huecos:
                return True
            huecos[index]=Cord
    else:
        if int(eleccion[1])==0:
            Cord=[eleccion[0],int(L)-1,eleccion[2]]
            if Cord in huecos:
                return True
            huecos[index]=Cord
        else:
            Cord=[eleccion[0],int(eleccion[1])-1,eleccion[2]]
            if Cord in huecos:
                return True
            huecos[index]=Cord



    #Falta cambiar el .orbocc de acuerdo con esta perturbacion
    inic=open(input,"r")
    #os.system("mv initial_occ.orbocc OLD_CONFIGURATION")
    fin=open("Perturbacion1","w")
    lines=inic.readlines()
    fin.write(lines[0])
    fin.write(lines[1])
    fin.write(lines[2])
    fin.write(lines[3])
    for i in range(0,L**2):
        pos=4+i

        line=lines[pos].split()
        if [str(eleccion[0]),str(eleccion[1]),str(eleccion[2])]==[line[0],line[1],line[2]]:#Encontramos el hueco
            #print("Eleccion: "+str(eleccion[0])+"   "+str(eleccion[1])+"   "+str(eleccion[2]))
            #print(lines[pos])
            s=[lines[pos].split()[4],lines[pos].split()[5]]#Densidad spin de la posicion del hueco
            if Arriba:
                if int(eleccion[1])==int(L)-1: #Ojo a las cond. de contorno periodicas
                    s_y=[lines[pos-(L-1)].split()[4],lines[pos-(L-1)].split()[5]]#Spin de la posicion en la que queremos desplazar el hueco
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_y[0]+"    "+s_y[1]+ "\n")
                    PosNuevoHueco=pos-(L-1)

                else:
                    #print(str(pos)+"     "+str(eleccion[0]))
                    #print(lines[pos])
                    s_y=[lines[pos+1].split()[4],lines[pos+1].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_y[0]+"    "+s_y[1]+ "\n")
                    PosNuevoHueco=pos+1
            else:
                if int(eleccion[1])==0:
                    #print(str(pos)+"     "+str(eleccion[0]))
                    #print(lines[pos])
                    s_y=[lines[pos+(L-1)].split()[4],lines[pos+(L-1)].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_y[0]+"    "+s_y[1]+ "\n")
                    PosNuevoHueco=pos+(L-1)
                else:
                    s_y=[lines[pos-1].split()[4],lines[pos-1].split()[5]]
                    fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s_y[0]+"    "+s_y[1]+ "\n")
                    PosNuevoHueco=pos-1
        else:
            fin.write(lines[pos])
    fin.close()
    inic.close()
    #Falta meter el nuevo hueco
    inic=open("Perturbacion1","r")
    fin=open("Perturbacion2","w")
    lines=inic.readlines()
    fin.write(lines[0])
    fin.write(lines[1])
    fin.write(lines[2])
    fin.write(lines[3])
    for i in range(0,L**2):
        pos=4+i
        if pos==PosNuevoHueco:
            fin.write("    "+lines[pos].split()[0]+"    "+lines[pos].split()[1]+"    "+lines[pos].split()[2]+"    "+lines[pos].split()[3]+"    "+s[0]+"    "+s[1]+ "\n")
        else:
            fin.write(lines[pos])
    fin.close()
    inic.close()
    #Renombra y borra archivos accesorios
    os.system("mv Perturbacion2 initial_occ.orbocc")
    os.system("rm Perturbacion1")



#Debido a errores numericos de redondeo, la carga total del sistema no se conserva
#Esta funcion sustituye en el input la carga total que se ha dada en el output de la ultima iteracion
def CambiaInput(parametro,fichero):
    Config_final=open(fichero,"r")
    lines=Config_final.readlines()
    sum=0
    for line in lines:
        if lines.index(line)<4:
            continue
        l=line.split()
        sum=sum+float(l[4])+float(l[5])
    sum=-sum
    OldInput=open("2d_hubbard_"+parametro+".fdf","r")
    NewInput=open("NewInput","w")
    lines=OldInput.readlines()
    for line in lines:
        if "Totalcharge" in line:
            NewInput.write("Totalcharge "+str(sum)+ "\n")
        else:
            NewInput.write(line)
    NewInput.close()
    #Renombramos y sobreescribimos
    os.system("mv NewInput 2d_hubbard_"+parametro+".fdf")


#Crea un mapa binario con los huecos
def MapHoles(lattice,name):
    Config=open(lattice,"r")
    #Config=open("Ejemplo","r")
    lines=Config.readlines()
    D=np.zeros((L,L))#Matriz de densidad (la entrada D[f][c] representa la densidad en la pos. (f,c))
    f=L-1 #Fila
    c=0 #Columna
    #print(L)
    for i in range(4,4+L*L):
        s=float(lines[i].split()[4])-float(lines[i].split()[5])
        #Binarizamos
        if s<0:
             s=-s
        # elif s>=2/3:
        #      s=-1
        # else:
        #      s=1
        D[f,c]=s
        f+=-1
        if lines[i].split()[1]==str(L-1):#Cambio de columna
            c+=1
            f=L-1
    plt.imshow(D, cmap='Greys',  interpolation='nearest')
    plt.savefig("MapHoles"+name+".png")


def MC(p,Nsweeps):
    #Change_kSampling(3)
    #Borramos archivos anteriores
    os.system("rm -r Archivos_orbocc/*")
    os.system("rm -r IndicadorAvance/*")
    D=np.zeros((L,L))#Matriz de densidad de spin (la entrada D[f][c] representa la densidad en la pos. (f,c))
    num=0#Numero de instantaneas

    energias=open("Energias","w")
    energias.write("************************************************************"+ "\n")
    energias.write("            OUTPUT OF MONTECARLO METHOD FOR DOPED SYSTEM"+ "\n")
    energias.write("************************************************************"+ "\n")
    energias.write("Temperatures   ")
    for t in T:
        energias.write(str(t)+"  ")
    energias.write("\n")
    energias.write("Lattice: "+str(L)+" x "+str(L)+" x 1"+ "\n")
    energias.write("Number of sweeps: "+str(Nsweeps)+ "\n")
    energias.write("Number of temperatures: "+str(len(list(T)))+ "\n")
    energias.write("Number of holes (initial): "+str(NumHuecos)+ "\n")
    energias.write("************************************************************"+ "\n")

    energias.write("\n")
    #Creamos la lattice y la guardamos en Referencia.orbocc
    #os.system("python Orden.py "+Dimension+" random False True")
    os.system("cp initial_occ.orbocc Referencia.orbocc")


    k=1
    os.system("mkdir IndicadorAvance")#Nos indica el avance de la simulacion
    snapshot=[]#Aqui guardamos las instantaneas
    corr=[]#Aqui la correlacion
    dos_inst=[]#Aqui la dos instantanea
    dos=[]#Aqui la dos promediada


    E=None
    while E==None:
        E=Ejecucion(p)#Guarda la energia
        huecos=CreateLattice(True)
        os.system("cp initial_occ.orbocc Referencia.orbocc")
        os.system("cp _2d_hubbard_FINAL.orbocc lattice") #Lattice donde se calcula densidad de hueco

    print("First energy  "+str(E)+"  eV")
    print(huecos)
    ReferenciaHuecos=[h for h in huecos]
    MapHoles("initial_occ.orbocc","_initial")#Mapa inicial

    energias.write("First energy  "+str(E)+"  eV"+ "\n")

    for t in T:
        energias.write("\n")
        energias.write("T="+str(t)+" K"+ "\n")
        energias.write("\n")
        #energias.write("SCF energy (eV)    "+"    Last energy (eV)    "+"    Energy difference (eV)    "+"    Boltzmann factor    "+"    Accept"+ "\n")
        energias.write("SCF energy (eV)    "+"    Last energy (eV)  "+"    Energy difference (eV)    "+"  "+"     Accept" +"\n")
        num=1
        for n in range(1,Nsweeps+1):
            for i in range(20):#Separamos los sweeps
                #FlipSpin("Referencia.orbocc","initial_occ.orbocc",pos)#Flipeamos spin
                ##Perturbamos
                if random_binary():
                    PerturbacionX("Referencia.orbocc","initial_occ.orbocc",huecos)
                else:
                    PerturbacionY("Referencia.orbocc","initial_occ.orbocc",huecos)
                ##
                E2=Ejecucion(p)#Guarda la energia
                if E2==None:
                    print("No converge")
                    num+=1
                    #huecos=ReferenciaHuecos
                    continue
                Dif=E2-E#Aqui tenemos la diferencia de energias
                print("Energy:  "+str(E2))
                print("Difference:  "+str(Dif))
                energias.write("   "+str(format(E2,'.5f'))+"      "+"      "+str(format(E,'.5f'))+"             "+str(format(Dif,'.5f'))+"        ")
                if Dif<0:#Aceptamos+s
                    E=E2#Actualizamos la energia
                    #os.system("mv _2d_hubbard_FINAL.orbocc lattice")
                    #os.system("mv _2d_hubbard_FINAL.ener DOS")#Actualizamos las energias
                    #energias.write("   Aceptamos"+"  Energía actual: "+str(E)+ "\n")
                    #energias.write("       YES"+"       "+str(Correlacion("lattice"))+ "\n")
                    energias.write("               YES"+"       " +"\n")
                    #energias.write("       YES"+"       "+str(Correlacion("initial_occ.orbocc"))+ "\n")
                    print("YES")
                    #print(str(i+n))
                    os.system("cp initial_occ.orbocc Referencia.orbocc")#Actualizamos la referencia
                    os.system("cp _2d_hubbard_FINAL.orbocc lattice")#Actualizamos la lattice
                    ReferenciaHuecos=[h for h in huecos]

                elif math.exp(-Dif*e/(kb*t))>random.random():#Aceptamos el Cambio
                    E=E2#Actualizamos la energia
                    #energias.write("   Aceptamos"+"  Energía actual: "+str(E)+ "\n")
                    #os.system("mv _2d_hubbard_FINAL.orbocc lattice")
                    #os.system("mv _2d_hubbard_FINAL.ener DOS")#Actualizamos las energias
                    #energias.write("       YES"+"       "+str(Correlacion("lattice"))+ "\n")
                    print("YES")
                    energias.write("               YES"+"       " +"\n")
                    #energias.write("       YES"+"       "+str(Correlacion("initial_occ.orbocc"))+ "\n")
                    os.system("cp initial_occ.orbocc Referencia.orbocc")#Actualizamos la referencia
                    os.system("cp _2d_hubbard_FINAL.orbocc lattice")#Actualizamos la lattice
                    ReferenciaHuecos=[h for h in huecos]

                else:
                    #energias.write("   NO aceptamos"+"  Energía actual: "+str(E)+ "\n")
                    #energias.write("        NO"+"       "+str(Correlacion("lattice"))+ "\n")
                    energias.write("               NO"+"       " +"\n")
                    huecos=[h for h in ReferenciaHuecos]
                    print("NO")
                print(str(100*k/(Nsweeps*len(list(T))*20))+" %")
                k+=1
                print("      ")
                print(huecos)
                print("      ")
                print(ReferenciaHuecos)
                print("      ")

            if n>=Nterm:
                Config=open("lattice","r")
                lines=Config.readlines()
                f=L-1 #Fila
                c=0 #Columna
                #print(L)
                for i in range(4,4+L*L):
                    s=float(lines[i].split()[4])-float(lines[i].split()[5])
                    #Binarizamos
                    # if s<0:
                    #     s=-s
                    # elif s>=2/3:
                    #      s=-1
                    # else:
                    #      s=1
                    D[f,c]+=s
                    f+=-1
                    if lines[i].split()[1]==str(L-1):#Cambio de columna
                        c+=1
                        f=L-1
                num+=1
                print(D/num)

            #snapshot.append(Correlacion("initial_occ.orbocc"))
            os.system("mkdir IndicadorAvance/"+str(100*k/(Nsweeps*len(list(T))*20)))
    f=L-1 #Fila
    c=0 #Columna
    #print(L)
    for i in range(L*L):
        #Binarizamos
        if D[f,c]<0:
            D[f,c]=-D[f,c]
        f+=-1
        if f==-1:#Cambio de columna
            c+=1
            f=L-1
    os.system("rm -r IndicadorAvance/*")
    return D/num

#MonteCarlo(1e-9,10,10)


#MapHoles("initial_occ.orbocc","_initial")
#PerturbacionX("initial_occ.orbocc","perturbado")
Dens=MC(1,1)
# MapHoles("lattice","_final")
plt.imshow(Dens, cmap='Greys',  interpolation='nearest')
plt.savefig("MapHoles_final.png")

#MapHoles("_2d_hubbard_FINAL.orbocc","_final")


#PerturbacionX()
#p=0.1
#os.system("../../Carrera/Quinto/TFG_Física/scale-up-1.0.0/build_dir/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")
#os.system("mv _2d_hubbard_FINAL.orbocc initial_occ.orbocc")


# #def MapaHuecos(L):
# Config=open("initial_occ.orbocc","r")
# #Config=open("Ejemplo","r")
# lines=Config.readlines()
# D=np.zeros((L,L))#Matriz de densidad (la entrada D[f][c] representa la densidad en la pos. (f,c))
# f=L-1 #Fila
# c=0 #Columna
# #print(L)
# for i in range(4,4+L*L):
#     s=float(lines[i].split()[4])-float(lines[i].split()[5])
#
#     #Binarizamos
#     if s<0:
#          s=-s
#     # elif s>=2/3:
#     #      s=-1
#     # else:
#     #      s=1
#     D[f,c]=s
#     f+=-1
#     if lines[i].split()[1]==str(L-1):#Cambio de columna
#         c+=1
#         f=L-1
#
#
# def spinsFigure(data,inicial):
#     plt.imshow(data, cmap='Greys',  interpolation='nearest')
#     if inicial:
#         plt.savefig("Mapa_inicial.png")
#     else:
#         plt.savefig("Mapa.png")
#     #plt.show()
#     #os.system("open Mapa.png")
#
# spinsFigure(D,False)
# #
# #
# #def MapaHuecos(L):
# Config=open("Resultados/initial_occ.orbocc","r")
# #Config=open("Ejemplo","r")
# lines=Config.readlines()
# D=np.zeros((L,L))#Matriz de densidad (la entrada D[f][c] representa la densidad en la pos. (f,c))
# f=L-1 #Fila
# c=0 #Columna
# #print(L)
# for i in range(4,4+L*L):
#     s=float(lines[i].split()[4])-float(lines[i].split()[5])
#
#     #Binarizamos
#     if s<0:
#          s=-s
#     # elif s>=2/3:
#     #      s=-1
#     # else:
#     #      s=1
#     D[f,c]=s
#     f+=-1
#     if lines[i].split()[1]==str(L-1):#Cambio de columna
#         c+=1
#         f=L-1
# spinsFigure(D,True)
#
# os.system("open Mapa.png Mapa_inicial.png")
