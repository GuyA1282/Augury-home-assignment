# signal processing answers

A. the difference between the two graphs is in the X axis.
Graph 1 measures the amplitude over time, showing how the vibration is changing over time.
And graph 2 shows the amplitude over frequency, it is calculated from the time samples, usually with an FFT.

B. I would calculate the FFT of graph 1's data and compare it to graph 2.
If it is the same data set, the peaks should be at the same frequencies
with the same amplitudes.

C. In graph 2 we see the frequency and amplitude of each component of the
vibration which is about 40 Hz and 4000 Hz, both at 1G.
In graph 1 the 4000 Hz component can't be seen, because it is too fast and is
mixed with the slow wave.