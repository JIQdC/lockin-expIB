from RigolClass import RigolDS2000,RigolDG4000

def writeSingleToFile(wav,path):
    file=open(path,'w')

    #escribo el preamble con todas las caract como header
    parameters=wav.pre.split(",")
    if parameters[0]==0:
        fmat="WORD"
    elif parameters[0]==1:
        fmat="BYTE"
    else:
        fmat="ASCII"
    if parameters[1]==0:
        typ="Normal"
    elif parameters[1]==1:
        typ="Maximum"
    else:
        typ="Raw"
    pre="Format: "+fmat+"\nType: "+typ+"\nPoints: "+parameters[2]
    pre=pre+"\nCount: "+parameters[3]+"\nXinc = "+parameters[4]
    pre=pre+"\nXor = "+parameters[5]+"\nXref = "+parameters[6]
    pre=pre+"\nYinc = "+parameters[7]+"\nYor = "+parameters[8]
    pre=pre+"\nXref = "+parameters[6]+"\n"
    file.write("%s" % pre)

    #escribo los datos como csv
    for i in range(12,wav.points):
        file.write("%.9f,%.5f\n" % (wav.t[i-12],float(wav.t[i-12])))

    file.close()

def writeDoubleToFile(wav1,wav2,path):
    file=open(path,'w')

    #escribo los  dos preamble con todas las caract como header
    parameters=wav1.pre.split(",")
    if parameters[0]==0:
        fmat="WORD"
    elif parameters[0]==1:
        fmat="BYTE"
    else:
        fmat="ASCII"
    if parameters[1]==0:
        typ="Normal"
    elif parameters[1]==1:
        typ="Maximum"
    else:
        typ="Raw"
    pre="Format: "+fmat+"\nType: "+typ+"\nPoints: "+parameters[2]
    pre=pre+"\nCount: "+parameters[3]+"\nXinc = "+parameters[4]
    pre=pre+"\nXor = "+parameters[5]+"\nXref = "+parameters[6]
    pre=pre+"\nYinc = "+parameters[7]+"\nYor = "+parameters[8]
    pre=pre+"\nXref = "+parameters[6]+"\n"
    file.write("Preamble 1\n%s" % pre)
    parameters=wav2.pre.split(",")
    if parameters[0]==0:
        fmat="WORD"
    elif parameters[0]==1:
        fmat="BYTE"
    else:
        fmat="ASCII"
    if parameters[1]==0:
        typ="Normal"
    elif parameters[1]==1:
        typ="Maximum"
    else:
        typ="Raw"
    pre="Format: "+fmat+"\nType: "+typ+"\nPoints: "+parameters[2]
    pre=pre+"\nCount: "+parameters[3]+"\nXinc = "+parameters[4]
    pre=pre+"\nXor = "+parameters[5]+"\nXref = "+parameters[6]
    pre=pre+"\nYinc = "+parameters[7]+"\nYor = "+parameters[8]
    pre=pre+"\nXref = "+parameters[6]+"\n"
    file.write("Preamble 2\n%s" % pre)

    #escribo los datos como csv
    for i in range(0,wav1.points):
        file.write("%.9f,%.5f,%.5f\n" % (wav1.t[i],float(wav1.v[i]),float(wav2.v[i])))

    file.close()

#defino los instrumentos que voy a usar, e imprimo sus nombres
osc=RigolDS2000()
gen=RigolDG4000()
print("Generador: "+gen.ID())
print("\nOsciloscopio: "+osc.ID())

#Setear valores del generador
freq=1E3
gen.setFunc(1,"SIN")
gen.setFreq(1,freq)
gen.setAmpl(1,5,"VPP")
gen.turnOutput(1,"ON")

#definir profundidad de memoria y periodos a mostrar
memdepth=int(7E3)
periodos=20

#midamos
osc.autoSet()
osc.setScalePeriod(periodos,freq)
osc.setMemDepth(memdepth)
osc.runAndStop()

#leo canal1
osc.setRead(1,"RAW","BYTE",1,memdepth)
data1=osc.getWaveformData()

#leo canal2
osc.setRead(2,"RAW","BYTE",1,memdepth)
data2=osc.getWaveformData()

#escribo la info que obtuve en un archivo
path="data.csv"
writeDoubleToFile(data1,data2,path)



