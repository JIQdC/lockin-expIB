from RigolClass import RigolDS2000,RigolDG4000
from scipy.signal import hilbert
import numpy as np

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

def impedanciaFreq(freq):
    #esta funcion devuelve el valor de impedancia para la frecuencia freq que recibe
    #como argumento. Para ello configura el generador a la frecuencia freq, captura
    #las waveform correspondientes a la señal de excitación y a la señal de entrada
    #del circuito, les aplica el proceso del amplificador lock-in para caracterizar
    #la señal de entrada, y luego devuelve el valor de la impedancia con el divisor
    #de voltaje caracteristico del circuito.
    
    #Setear valores del generador
    gen.setFunc(1,"SIN")
    gen.setFreq(1,freq)
    gen.setAmpl(1,5,"VPP")
    gen.turnOutput(1,"ON")

    #definir profundidad de memoria y periodos a mostrar
    memdepth=int(7E3)
    periodos=30

    #preparo la medicion
    osc.autoSet()
    osc.setTriggerSourceIE('EXT')
    osc.setScalePeriod(periodos,freq)
    osc.setMemDepth(memdepth)

    #ajusto escala vertical para aumentar la resolucion de las ondas a medir
    osc.setOffset(2,0)
    osc.setVerticalScale(2,0.750)
    osc.setOffset(1,0)
    osc.setVerticalScale(1,osc.measureAmp(1)/5.5)

    #dejo correr al osciloscopio y capturo una medicion
    osc.runAndStop()

    #leo canal1
    osc.setRead(1,"RAW","BYTE",1,memdepth)
    data1=osc.getWaveformData()

    #leo canal2
    osc.setRead(2,"RAW","BYTE",1,memdepth)
    data2=osc.getWaveformData()

    #escribo la info que obtuve en un archivo
    path="data/data"+str(freq)+".csv"
    writeDoubleToFile(data1,data2,path)

    #defino Ri como la resist de entrada medida
    Ri=98646
    
    #antes de procesar, para quitar el posible offset de los datos, les resto su promedio
    v1prom=np.average(data1.v)
    v2prom=np.average(data2.v)
    data1.v=data1.v-v1prom
    data2.v=data2.v-v2prom

    #defino Vs (amplitud del generador de ondas) como el maximo valor de la señal de excitacion
    Vs=np.amax(data2.v)

    #genero la referencia normalizando la señal de excitacion con su amplitud
    ref=data2.v/Vs
    #para la referencia en cuadratura, uso transformada de Hilbert
    refq=-np.imag(hilbert(ref))

    #proceso de lock-in: multiplico la señal de salida por las referencias...
    y1=data1.v*ref
    y2=data1.v*refq
    #... y filtro pasabajo con un promediador
    y3=np.average(y1)
    y4=np.average(y2)

    #obtengo el modulo y fase del voltaje sobre la carga, y por lo tanto el complejo Vz
    modVz=2*(y3**2+y4**2)**0.5
    Phi=np.arctan(y4/y3)
    Vz=modVz*(np.cos(Phi)+1j*np.sin(Phi))

    #calculo la impedancia de carga con un divisor de impendancias
    ZL=(-Vz*Ri)/(Vz-Vs)

    return ZL

#defino archivo de salida
path2="data/impFreq.tsv"
file2=open(path2,'w')

#header
file2.write("n\tRL\tXL\t|ZL|\tPhi\n")
print("n\tRL\tXL\t|ZL|\tPhi")

for i in range(50,100):
    #aumento la frecuencia en pasos de 1kHz
    f=(i*1000)+1000
    zl=impedanciaFreq(f)
    print(f,"\t",np.real(zl),"\t",np.imag(zl),"\t",np.abs(zl),"\t",np.angle(zl,deg=True),"\n")
    file2.write("%d\t%.5f\t%.5f\t%.5f\t%.5f\n" % (f,np.real(zl),np.imag(zl),np.abs(zl),np.angle(zl,deg=True)))

file2.close()
