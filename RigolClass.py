##Funciones de control y adquisicion de datos para instrumentos Rigol
##Lucas M. Grigolato - Jose I. Quinteros
##Laboratorio II
##Instituto Balseiro - 2018

import visa
from time import sleep
import numpy as np

#Si se trabaja con NI-VISA, setear en ''
#Si se trabaja con PyVISA-py, setear en '@py'
system=''

class waveform:
    ##estructura para contener los datos relativos a una waveform
    def __init__(self):
        self.points=int
        self.yref=int
        self.yinc=float
        self.yor=float
        self.xinc=float
        self.pre=str
        self.t=np.arange
        self.v=np.arange

class RigolDS2000(object):
    #Funciones de control y adquisicion de un osciloscopio
    #Rigol DS2000 Series
    def __init__(self):
        #reemplazar la dirección por la propia del instrumento
        self.instr=visa.ResourceManager(system).open_resource('USB0::0x1AB1::0x04B0::DS2D163351641::INSTR')
    def ID(self):
        #devuelve el identificador del dispositivo
        return(self.instr.query("*IDN?"))

    def autoSet(self):
        #realiza un autoset en el osciloscopio
        self.instr.write(":AUT")
        sleep(3)

    def setMemDepth(self,x):
        #fija la resolucion de memoria en el nivel x
        self.instr.write("RUN")
        self.instr.write(":ACQuire:MDEPth "+str(int(x)))
        sleep(1)

    def runAndStop(self):
        #deja correr al osciloscopio por 2 segundos
        self.instr.write("RUN")
        sleep(1)
        self.instr.write("STOP")

    def setRead(self,CH,MODE,FORM,START,STOP):
        #configura parametros necesarios para la lectura
        self.instr.write(":WAV:SOUR CHAN"+str(CH))
        self.instr.write(":WAV:MODE "+str(MODE))
        self.instr.write(":WAV:FORM "+str(FORM))
        self.instr.write(":WAV:STAR "+str(START))
        self.instr.write(":WAV:STOP "+str(STOP))
        self.instr.write(":WAV:RES")
        self.instr.write(":WAV:BEG")

    def getWaveformData(self):
        #retorna un objeto de tipo waveform, conteniendo parametros de
        #la lectura y dos np.array con los datos de t y amplitud
        wav=waveform()

        #extraigo los parametros
        wav.pre=self.instr.query(":WAV:PRE?")+"\n\n"
        wav.points=int(self.instr.query(":WAV:POIN?"))
        wav.yref=int(self.instr.query(":WAV:YREF?"))
        wav.yinc=float(self.instr.query(":WAV:YINC?"))
        wav.yor=float(self.instr.query(":WAV:YOR?"))
        wav.xinc=float(self.instr.query(":WAV:XINC?"))

        #inicializo la variable donde voy a almacenar los datos crudos
        raw=None

        #antes de obtener los datos crudos, tengo que asegurarme que el osciloscopio
        #haya terminado de almacenar las waveform en su memoria (que salga del estado
        #READ)
        status=str(self.instr.query(":WAV:STAT?"))
        while(status[0:4]=="READ"):
            status=str(self.instr.query(":WAV:STAT?"))
        
        #almaceno los datos crudos
        self.instr.write(":WAV:DATA?")
        sleep(0.5)
        raw=self.instr.read_raw()
        
        #creo los vectores para t y amplitud en wav
        wav.t=np.zeros(wav.points)
        wav.v=np.zeros(wav.points)

        #proceso los datos crudos y los almaceno en los vectores de wav
        for i in range(12,wav.points+12): #ciclo empieza en 12 para omitir el header
            wav.t[i-12]=float((i-12)*wav.xinc)
            wav.v[i-12]=float((raw[i]-wav.yref))*wav.yinc-wav.yor

        #cierro la lectura
        self.instr.write(":WAV:END")

        return wav

    def setScalePeriod(self,n,freq):
        #setea la escala horizontal para mostrar exactamente n periodos en pantalla,
        #conocida la frecuencia de trabajo freq
        T=1./freq
        sc=(n*T)/14.
        self.instr.write(":TIM:SCAL "+str(sc)) 

    def setTriggerSourceIE(self,MODE):
        #setea el origen del trigger del osciloscopio, para que sea INT o EXT
        self.instr.write("TRIG:EDG:SOUR "+str(MODE))

    def setTriggerSource(self,CH):
        #setea el origen del trigger del osciloscopio, en modo Edge, en el canal CH
        self.instr.write("TRIG:EDG:SOUR CHAN"+str(CH))

    def setOffset(self,CH,offset):
        #setea el offset del canal Ch
        self.instr.write(":CHAN"+str(CH)+":OFFS "+str(offset))
        
    def setVerticalScale(self,CH,scale):
        #setea la escala vertical del canal CH
        self.instr.write(":CHAN"+str(CH)+":SCAL "+str(scale))
        sleep(0.2)

    def measureAmp(self,CH):
        #mide la amplitud de la señal del canal CH
        self.instr.write(":MEAS:VAMP? CHAN"+str(CH))
        return float(self.instr.read())

class RigolDG4000(object):
    #Funciones de control de un generador de señales
    #Rigol DG4000 Series
    def __init__(self):
        #reemplazar la dirección por la propia del instrumento
        self.instr=visa.ResourceManager(system).open_resource('USB0::0x1AB1::0x0641::DG4E163251558::INSTR')

    def ID(self):
        #devuelve el identificador del dispositivo
        return self.instr.query("*IDN?")

    def turnOutput(self,CH,status):
        #cambia el output del canal CH a ON|OFF
        self.instr.write(":OUTPUT"+str(CH)+" "+str(status))
        sleep(0.5)

    def setFunc(self,CH,func):
        #setea la funcion del canal CH a SIN|SQU, etc
        self.instr.write(":SOUR"+str(CH)+":FUNC "+str(func))

    def setFreq(self,CH,freq):
        #setea la frecuencia del canal CH a freq Hz
        self.instr.write(":SOUR"+str(CH)+":FREQ "+str(freq))

    def setAmpl(self,CH,amp,unit):
        #setea la amplitud del canal CH a amp VPP|VRMS
        self.instr.write(":SOUR"+str(CH)+":VOLT:UNIT "+str(unit))
        self.instr.write(":SOUR"+str(CH)+":VOLT "+str(amp))
        sleep(0.5)

    def setNoiseLevel(self,CH,level):
        #setea el nivel de ruido del canal CH a level% de su amplitud
        self.instr.write(":OUTP"+str(CH)+":NOIS:SCAL "+str(level)) 

    def turnNoise(self,CH,status):
        #enciende o apaga el ruido del canal CH
        self.instr.write(":OUTP"+str(CH)+":NOIS "+str(status))
