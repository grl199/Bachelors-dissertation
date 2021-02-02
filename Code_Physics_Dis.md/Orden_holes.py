#Me crea un .orbocc con huecos
import random
import sys

v_cell= sys.argv[1].split(',')#Dimensiones de la celda
orden= sys.argv[2].split(',')#Random o no
N=sys.argv[3].split(',')#Numero de huecos


N=int(N[0])


def random_number():
    if random.random()<0.5:
        return -0.5
    else:
        return 0.5

def random_holes(N,dim):
    list=[]
    for x in range(int(dim[0])):
        for y in range(int(dim[1])):
            for z in range(int(dim[2])):
                list.append([x,y,z])
    holes=[]
    for n in range(N):
        pos=random.choice(list)
        holes.append(pos)
        list.pop(list.index(pos))
    return holes #Retorna array con los huecos

def OrdenMagnetico(v_cell,orden,N):
    output=open("initial_occ_old.orbocc","w")
    output.write(v_cell[0]+"   "+v_cell[1]+"   "+v_cell[2]+ "\n")
    output.write("1"+ "\n")
    output.write("cond_s"+ "\n")
    output.write("!"+"   "+"Supercell"+"   "+"orb"+" "+"occupations(spin)"+ "\n")

    #Si se pasa "random" como segunda variable, se determina el orden de manera aleatoria
    dim=v_cell#Dimension ce la celda (cuadrada)
    holes=random_holes(N,dim)#Array con los huecos

    if orden[0]=="random":
        for x in range(int(v_cell[0])):
            for y in range(int(v_cell[1])):
                for z in range(int(v_cell[2])):
                    if [x,y,z] in holes:
                        output.write(str(x)+"   "+str(y)+"   "+str(z)+"   "+"1"+"   "+str(-0.5)+"   "+str(-0.5)+ "\n")
                    else:
                        r=random_number()
                        output.write(str(x)+"   "+str(y)+"   "+str(z)+"   "+"1"+"   "+str(r)+"   "+str(-r)+ "\n")

    else:
        holes=[]
        #print(orden)
        # for i in range(len(orden)):
        #     if orden[i]=="+":
        #         orden[i]=0.5
        #     if orden[i]=="-":
        #         orden[i]=-0.5
        print(len(orden))
        k=0 #Contador
        for x in range(int(v_cell[0])):  
            for y in range(int(v_cell[1])):
                for z in range(int(v_cell[2])):                    
                    if orden[k]=="+":  
                        output.write(str(x)+"   "+str(y)+"   "+str(z)+"   "+"1"+"   "+str(0.5)+"   "+str(-0.5)+ "\n")
                    else:
                        holes.append([x,y,z])
                        output.write(str(x)+"   "+str(y)+"   "+str(z)+"   "+"1"+"   "+str(-0.5)+"   "+str(-0.5)+ "\n")
                k+=1
    output.write("Holes "+str(N)+ "\n")
    for h in holes:
        output.write(str(h))


OrdenMagnetico(v_cell,orden,N)
