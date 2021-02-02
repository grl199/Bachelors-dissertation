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
from scipy.interpolate import lagrange


# #U=0.2
gamma=0.073529
# U=3*gamma
# factor=U/gamma
# gamma=2# eV


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
        return ener



String_E=DensityOfStates("_2d_hubbard_FINAL.ener",1)
E=[float(e)/gamma for e in String_E]

E_1=E

grid=list(np.linspace(min(E),max(E),70))
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
for i in range(len(dos_smooth)):
    if dos_smooth[i]<0:
        dos_smooth[i]=0
plt.plot(xnew,dos_smooth,'b',label="Spin up")
plt.plot([list(xnew)[-1],list(xnew)[-1]+0.01],[list(dos_smooth)[-1],0],'b')
plt.plot([list(xnew)[0],list(xnew)[0]+0.01],[list(dos_smooth)[0],0],'b')
#plt.legend()
#plt.plot(E_bis,dos,'r')


plt.xlabel("Energy/\u03B3",size=16)
#plt.ylabel("Density of states (arb.u.)",size=16)
#plt.show()




String_E=DensityOfStates("_2d_hubbard_FINAL.ener",2)
E=[float(e)/gamma for e in String_E]
E_2=E



grid=list(np.linspace(min(E),max(E),70))
E_bis=[]
dos=[]
for i in range(len(grid)-1):
    E_bis.append(0.5*(grid[i]+grid[i+1]))
    j=0
    for en in E:
        if en>=grid[i] and en<=grid[i+1]:
            j+=1
    dos.append(j)


dos=[-d for d in dos]
xnew = np.linspace(min(E_bis), max(E_bis), 1000)
dos_smooth = spline(E_bis, dos, xnew)
for i in range(len(dos_smooth)):
    if dos_smooth[i]>0:
        dos_smooth[i]=0
plt.plot(xnew,dos_smooth,'r',label="Spin down")
plt.plot([list(xnew)[-1],list(xnew)[-1]+0.01],[list(dos_smooth)[-1],0],'r')
plt.plot([list(xnew)[0],list(xnew)[0]+0.01],[list(dos_smooth)[0],0],'r')
#plt.plot(E_bis,dos,'r')
#plt.legend()

plt.plot([min(E_1+E_2),max(E_1+E_2)],[0,0],'k')
#plt.xlabel("Energy (a.u.)")
plt.ylabel("DOS (arb.u.)",size=16)
plt.yticks([],[])
plt.show()
