import os
import sys


#Diferentes valosres del parametro U/gamma a considerar
param=[10]

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
    old_file=open("2d_template.fdf","r")
    new_file=open("2d_hubbard_"+str(p)+".fdf","w")
    for line in old_file:
        if "Cambiame" in line:
            new_file.write("Parameter_file 2d_hubbard_"+str(p)+".xml"+ "\n")
        else:
            new_file.write(line)
    new_file.close()

#Crea la lattice y guarda la configuracian inicial en el directorio de resultados

# os.system("cp initial_occ.orbocc Resultados")
#
#Ejecuta el codigo y guarda los resultados
n_sim=3000
for p in param:
    for n in range(1,n_sim+1):
        os.system("python Orden.py 10,10,1 random")
        os.system("/software/citimac/SCALE-UP/scale-up-1.0.0/build_gnu/src/scaleup.x <2d_hubbard_"+str(p)+".fdf> output")

        os.system("mv _2d_hubbard_FINAL.bands Resultados/Bandas/Bandas_"+str(p)+"/_2d_hubbard_FINAL.bands_"+str(n))

        os.system("mv initial_occ.orbocc Resultados/Config_inic/Config_inic_"+str(p)+"/initial_occ.orbocc_"+str(n))

        os.system("mv _2d_hubbard_FINAL.ener Resultados/Energia/Energia_"+str(p)+"/_2d_hubbard_FINAL.ener_"+str(n))

        os.system("mv _2d_hubbard_FINAL.orbocc Resultados/Config_final/Config_final_"+str(p)+"/_2d_hubbard_FINAL.orbocc_"+str(n))

        os.system("mv output Resultados/Output/Output_"+str(p)+"/output"+str(n))

