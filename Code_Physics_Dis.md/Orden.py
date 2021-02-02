import random
import sys

v_cell= sys.argv[1].split(',')
orden= sys.argv[2].split(',')
Ferro= sys.argv[3].split(',')
Antiferro= sys.argv[4].split(',')
FerroX= sys.argv[5].split(',')
FerroY= sys.argv[6].split(',')

#Ejemplo: FerroX quiere decir que creamos una red perfectamente ferro en X y antiferro en Y

L=v_cell[0] #Longitud (es cuadrada)

if Ferro[0]=='True':
    Ferro=True
else:
    Ferro=False

if FerroX[0]=='True':
    FerroX=True
else:
    FerroX=False

if FerroY[0]=='True':
    FerroY=True
else:
    FerroY=False

if Antiferro[0]=='True':
    Antiferro=True
else:
    Antiferro=False


def random_number():
    if Ferro:
        return 0.5
    if random.random()<0.5:
        return -0.5
    else:
        return 0.5



def OrdenMagnetico(v_cell,orden):
    output=open("initial_occ.orbocc","w")
    output.write("    "+v_cell[0]+"    "+v_cell[1]+"    "+v_cell[2]+ "\n")
    output.write("1"+ "\n")
    output.write("cond_s"+ "\n")
    output.write("!"+"   "+"Supercell"+"   "+"orb"+" "+"occupations(spin)"+ "\n")
    if Antiferro:
        up=0.5 #Variable que nos dice si colocamos spin hacia arriba o hacia abajo
        for x in range(int(L)):
            for y in range(int(L)):
                for z in range(int(v_cell[2])):
                    if y==int(L)-1:
                        output.write("    "+str(x)+"    "+str(y)+"    "+str(z)+"    "+"1"+"    "+str(up)+"    "+str(-up)+ "\n")
                    else:
                        output.write("    "+str(x)+"    "+str(y)+"    "+str(z)+"    "+"1"+"    "+str(up)+"    "+str(-up)+ "\n")
                        up=-up
        return 0#Sale

    elif FerroX:
        up=0.5
        for x in range(int(L)):
            for y in range(int(L)):
                for z in range(int(v_cell[2])):
                    output.write("    "+str(x)+"    "+str(y)+"    "+str(z)+"    "+"1"+"    "+str(up)+"    "+str(-up)+ "\n")
                    up=-up
        return 0
    elif FerroY:
        up=0.5 #Variable que nos dice si colocamos spin hacia arriba o hacia abajo
        for x in range(int(L)):
            for y in range(int(L)):
                for z in range(int(v_cell[2])):
                    if x%2==0:
                        output.write("    "+str(x)+"    "+str(y)+"    "+str(z)+"    "+"1"+"    "+str(up)+"    "+str(-up)+ "\n")
                    else:
                        output.write("    "+str(x)+"    "+str(y)+"    "+str(z)+"    "+"1"+"    "+str(-up)+"    "+str(up)+ "\n")
        return 0
    else:
        #Si se pasa "random" como segunda variable, se determina el orden de manera aleatoria
        if orden[0]=="random":
            for x in range(int(v_cell[0])):
                for y in range(int(v_cell[1])):
                    for z in range(int(v_cell[2])):
                        r=random_number()
                        output.write("    "+str(x)+"    "+str(y)+"    "+str(z)+"    "+"1"+"    "+str(r)+"    "+str(-r)+ "\n")
        else:
            for i in range(len(orden)):
                if orden[i]=="+":
                    orden[i]=0.5
                if orden[i]=="-":
                    orden[i]=-0.5
            k=0 #Contador
            for x in range(int(v_cell[0])):
               for y in range(int(v_cell[1])):
                   for z in range(int(v_cell[2])):
                       r=random_number()
                       output.write(str(x)+"   "+str(y)+"   "+str(z)+"   "+"1"+"   "+str(orden[k])+"   "+str(-orden[k])+ "\n")
                       k=k+1




OrdenMagnetico(v_cell,orden)
