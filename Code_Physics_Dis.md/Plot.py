import os
import sys
import numpy as np
import random
import fileinput
import matplotlib.pyplot as plt
import math

from scipy.interpolate import spline
from matplotlib import colors
from scipy.interpolate import lagrange

input=open("Energias","r")
lines=input.readlines()
temperature=lines[3].split()[1:]
Ntemps=lines[6].split()[3]
Nsweeps=int(lines[5].split()[3])
Nterm=0.5*Nsweeps
L=int(lines[4].split()[1])

def PlotCorr():
    i=0
    n=0
    t=-1
    Cinst=[]
    C=[]
    ErrC=[]
    for l in lines:
        if "SCF energy (eV)" in l: #Resetea
            Cinst=[]
            t+=1
            n=0
            i=0
        if n>=Nterm and i==L*L-1:
            Cinst.append(float(l.split()[3]))
        if i==L*L-1:
            i=0
            n+=1
        if "Average correlation" in l:
            C.append(np.mean(Cinst))
            ErrC.append(np.std(Cinst))
        i+=1

    #print(len(C))

    #correlation=lines[len(lines)-7].split()[1:]
    #correlation_x=lines[len(lines)-5].split()[2:]
    #correlation_y=lines[len(lines)-3].split()[2:]
    temperature=lines[3].split()[1:]

    #print(correlation)
    #return 2

    #C=[float(c) for c in correlation]
    #CX=[float(c) for c in correlation_x]
    #CY=[float(c) for c in correlation_y]
    T=[float(t) for t in temperature]


    #plt.plot(T,C,'bo',label="Total correlation")
    plt.errorbar(T[:len(C)], C, yerr=ErrC, fmt='bo', color='blue',ecolor='black', elinewidth=0.6, capsize=1)
    #plt.plot(T,CX,'ro',label="X correlation")
    #plt.plot(T,CY,'go',label="Y correlation")
    plt.legend()
    plt.savefig("Correlation_vs_T.png")
    plt.show()
    plt.clf()

def PlotDOS():
    #input=open("Energias","r")
    input=open("DensEst","r")
    lines=input.readlines()
    t=list(temperature)
    k=0
    for l in lines:
        if "DOS energies" in l:
            index=lines.index(l)
            line=l.split()
            #print(line)
            line.pop(0)
            line.pop(0)
            if k==-1:
                line.pop(0)

            #return 1
            E=[float(e) for e in line]
            #print(len(E))

            grid=list(np.linspace(min(E),max(E),20))
            E_bis=[]
            dos=[]
            for i in range(len(grid)-1):
                E_bis.append(0.5*(grid[i]+grid[i+1]))
                j=0
                for en in E:
                    if en>=grid[i] and en<=grid[i+1]:
                        j+=1
                dos.append(j)
            xnew = np.linspace(min(E_bis), max(E_bis), 1000)
            dos_smooth = spline(E_bis, dos, xnew)
            #Ponemos a 0 lo que es negativo
            for i in range(len(dos_smooth)):
                if dos_smooth[i]<0:
                    dos_smooth[i]=0
                    #print(dos_smooth[i])

            # if "antiferro" in l:
            #     plt.plot(xnew,dos_smooth,'b')
            #     plt.title("Density of states for antiferromagnetic configuration")
            #     plt.savefig("Antiferro.png")
            # else:
            #     plt.plot(xnew,dos_smooth,'r',label="Current")
            #     plt.plot(xnew_AFM,dos_smooth_AFM,'b',label="Antiferro")
            #     plt.title("Density of states for "+str(t[k])+" K")
            #     plt.legend()
            #     plt.savefig("DOS_"+str(t[k])+".png")

            plt.plot(xnew,dos_smooth,'r')
            plt.title("Density of states for "+str(t[k])+" K")
            plt.savefig("DOS_"+str(t[k])+".png")
            plt.xlabel("Energy (eV)")
            plt.ylabel("Density of states (arbitrary units)")

            plt.xlim(-10,10)
            plt.ylim(-300,2500)
            if k==-1:#Guardamos antiferro
                xnew_AFM=xnew
                dos_smooth_AFM=dos_smooth

            #plt.show()
            plt.clf()
            E=[]
            E_bis=[]
            dos=[]
            k+=1

#print(temperature)
PlotCorr()
#PlotDOS()


# T=[2000 , 3000,  4000 , 5000  ,6000 , 7000,  7500,  8000  ,8500 , 9000  ,9500 , 10000 , 10500 , 11000 , 11500 , 12000,  12500 , 13000,  14000]
# C=[]
# T=[]
# CX=[]
# CY=[]
# file=open("Energias",'r')
# for line in file.readlines():
#     if "Temperatures" in line:
#         T=line.split()[1:]
#     if "Average correlation" in line:
#         C.append(line.split()[2])
#     if "Average X correlation" in line:
#         CX.append(line.split()[3])
#     if "Average Y correlation" in line:
#         CY.append(line.split()[3])
#
#
# plt.plot(T[:len(C)],C,'bo',label="Total correlation")
# plt.plot(T[:len(C)],CX,'ro',label="X correlation")
# plt.plot(T[:len(C)],CY,'go',label="Y correlation")
# plt.legend()
# plt.show()
