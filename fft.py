from DataAdq import data1,data2
#from time import sleep, time
import numpy as np
from scipy import fftpack
from matplotlib import pyplot as plt

Fs=1000
T=1/Fs
L=1500
t=np.arange(0,L-1)*T
S=0.7*np.sin(2*np.pi*50*t)+np.sin(2*np.pi*120*t)
X= S+ 2*np.random.rand(np.size(t))
Y=fftpack.fft(X)
P2=np.abs(Y/L)
P1= P2[0:750]
f=(Fs/L)*np.arange(0,L/2)
plt.plot(f,P1)
plt.show()

'''
ft1=fftpack.fft(data2)
N=np.size(data2)
P2=np.abs(ft1/N)
P1=P2[1:N/2+1]
P1[2:np.size(P1)-1]=2*P1[2:np.size(P1)-1]
f=10000/N*(np.arange(0,N/2))
xf=np.arange(0,1,(2/N))

plt.figure()
plt.plot(f,P1)
plt.show()
'''