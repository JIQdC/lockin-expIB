import numpy as np
import csv

class waveform:
    def __init__(self):
        self.t=np.arange
        self.vi=np.arange
        self.vs=np.arange
        self.freq=int
        
class medicion:
    def __init__(self):
        self.modvz=float
        self.dmodvz=float
        self.phivz=float
        self.dphivz=float
        self.zl=None
        self.rl=float
        self.drl=float
        self.xcl=float
        self.dxcl=float
        self.vs=float

def leerArchivo(freq):
    with open('data'+str(int(freq))+'.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        T = []
        Vi = []
        Vs = []

        for row in readCSV:
            if(row[0][0]=="0"):
                
                t = float(row[0])
                vi = float(row[1])
                vs = float(row[2])

                T.append(t)
                Vi.append(vi)
                Vs.append(vs)
        
    data=waveform()
    
    data.t=T
    data.vi=Vi
    data.vs=Vs
    data.freq=freq
    
    return data

def impedanciaFreq(data):

    #defino Ri como la resist de entrada medida
    Ri=98646
    
    #antes de procesar, para quitar el posible offset de los datos, les resto su promedio
    viprom=np.average(data.vi)
    vsprom=np.average(data.vs)
    data.vi=data.vi-viprom
    data.vs=data.vs-vsprom

    #defino Vs (amplitud del generador de ondas) como el maximo valor de la señal de excitacion
    Vs=np.amax(data.vs)

    #genero la referencia normalizando la señal de excitacion con su amplitud
    ref=data.vs/Vs
    #para la referencia en cuadratura, uso transformada de Hilbert
    refq=-np.imag(hilbert(ref))

    #proceso de lock-in: multiplico la señal de salida por las referencias...
    y1=data.vi*ref
    y2=data.vi*refq
    #... y filtro pasabajo con un promediador
    y3=np.average(y1)
    y4=np.average(y2)
    
    #errores de y3,y4
    dy3=0.00045*y3
    dy4=0.00045*y4
    
    #el error de Vs es el error del maximo (1,5%)
    dVs=0.015*Vs
    
    med=medicion()
    #obtengo el modulo y fase del voltaje sobre la carga, y por lo tanto el complejo Vz
    med.modvz=2*(y3**2+y4**2)**0.5
    med.phivz=np.arctan(y4/y3)
    
    #saco los errores con propagacion de errores
    med.dmodvz=2*np.sqrt((y3*dy3)**2+(y4*dy4)**2)/np.sqrt(y3**2+y4**2)
    med.dphivz=np.sqrt((y4*dy3)**2+(y3*dy4)**2)/(y3**2+y4**2)
    
    #calculo resistencia, reactancia con sus errores
    A=Ri*med.modvz*np.cos(med.phivz)*Vs
    B=Ri*med.modvz**2
    C=2*Vs*med.modvz*np.cos(med.phivz)
    D=med.modvz**2
    dA=Ri*np.sqrt((Vs*np.cos(med.phivz)*med.dmodvz)**2+(Vs*med.modvz*np.sin(med.phivz)*med.dphivz)**2+
                  (med.modvz*np.cos(med.phivz)*dVs)**2)
    dB=2*B*med.dmodvz/med.modvz
    dD=2*D*med.dmodvz/med.modvz
    dC=2*Vs*np.sqrt((np.cos(med.phivz)*med.dmodvz)**2+(med.modvz*np.sin(med.phivz)*med.dphivz)**2)
    E=A-B
    dE=np.sqrt(dA**2+dB**2)
    H=Vs**2
    dH=2*H*dVs/Vs
    F=H-C+D
    dF=np.sqrt(dC**2+dD**2+dH**2)
    
    med.rl=E/F
    med.drl=med.rl*np.sqrt((dE/E)**2+(dF/F)**2)
    
    G=Ri*med.modvz*Vs*np.sin(med.phivz)
    dG=Ri*np.sqrt((Vs*np.sin(med.phivz)*med.dmodvz)**2+(Vs*med.modvz*np.cos(med.phivz)*med.dphivz)**2+
                 (med.modvz*np.sin(med.phivz)*dVs)**2)
    
    med.xcl=G/F
    med.dxcl=med.xcl*np.sqrt((dG/G)**2+(dF/F)**2)
    return med

outp=open('errores.csv','w')

outp.write("RL,dRL,XCL,dXCL\n")
for i in range(0,100):
    f=1000+i*1000
    raw=leerArchivo(f)
    datos=impedanciaFreq(raw)
    outp.write("%.6f,%.6f,%.6f,%.6f\n" %(datos.rl,datos.drl,datos.xcl,datos.dxcl))
    
outp.close()

print("Success!")
