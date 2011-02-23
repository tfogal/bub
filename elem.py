from __future__ import with_statement
import os
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
import fin
import findir

def floatlist(lst): return [float(i) for i in lst]

f="/home/tfogal/data/bu-biometallomics/BottomLeft/TOPLEFTFIN2/ABC192.FIN2"
header=[]
odd_filename=''
date=''
with open(f, "r") as finf:
  title = finf.readline().strip()
  date = finf.readline().strip()
  odd_filename = finf.readline().strip()
  number = finf.readline().strip()
  zero = finf.readline().strip()
  bunch_of_sixteens = finf.readline().strip()
  cps = finf.readline().strip()
  header = finf.readline().strip().split(",")


fig = plt.figure()

findata = fin.FIN(f)

i,j = 4,5

time = findata.element("Time")
elem0 = findata.element(header[i])
elem1 = findata.element(header[j])

fig = plt.figure(1)
fig.suptitle(odd_filename + " (" + date + ")", fontsize=14)
ax = plt.subplot(311)
ax.set_ylabel(header[i])
plt.plot(time,elem0)
imax = elem0.index(max(elem0))
plt.annotate("max", xy=(time[imax],elem0[imax]),
             xytext=(time[imax]+20, elem0[imax]+100),
             arrowprops=dict(facecolor='black', shrink=0.05))

ax = plt.subplot(312, sharex=ax)
ax.set_ylabel(header[j])
plt.plot(time,elem1)
plt.xlabel(header[0])

def avg(l): return sum(l) / len(l)

v = [(v[0]-avg(elem0))*(v[1]-avg(elem1)) for v in zip(elem0, elem1)]

ax = plt.subplot(313, sharex=ax)
ax.set_ylabel("Covariance: " + header[i] + " " + header[j])
assert(len(time) == len(v))
plt.plot(time, v)

plt.show()
