from DataAdq import data1, data2, freq
from scipy.signal import hilbert
import numpy as np
import matplotlib.pyplot as plt 

Ri=99500
v1prom=np.average(data1.v)
v2prom=np.average(data2.v)
data1.v=data1.v-v1prom
data2.v=data2.v-v2prom
Vs=np.amax(data2.v)
ref=data2.v/Vs
refq=-np.imag(hilbert(ref))
v1prom=np.average(data1.v)
v2prom=np.average(data2.v)

y1=data1.v*ref
y2=data1.v*refq

y3=np.average(y1)
y4=np.average(y2)

modVz=2*(y3**2+y4**2)**0.5
Phi=np.arctan(y4/y3)


print("|Vz|=",modVz)
print("Phi=",180*Phi/(np.pi))

Vz=modVz*(np.cos(Phi)+1j*np.sin(Phi))
print("Vz=",Vz)
ZL=(-Vz*Ri)/(Vz-Vs)

print("ZL= ",ZL)
print("RL=",np.real(ZL)," ohm")
print("C=",(-1/(np.imag(ZL)*2*np.pi*freq))*10**9,"nF")