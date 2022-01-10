# Corona

Script to visualize the current pandemic situation in Belgium.

Based on the visualization provided by [sciensano](https://covid-19.sciensano.be/sites/default/files/Covid19/Meest%20recente%20update.pdf) with a few improvements:
* Logarithmic scale: visualizes trends more clearly for a virus that behaves exponentially
* Customizable date range
* Option to visualize situation in specific province only

The images below compare the script and sciensano visualization of the number of Covid cases in the same period (01/03/2020 - 29/12/2021). While the Sciensano visualization gives the impression of a comfortable downward trend, the script visualization already shows the beginning of an upward trend, caused by the Omicron variant. In the sciensano visualization, the peaks seem to come out of nowhere, but in the script visualization their buildup is visualized more clearly.

## Installation

```shell
pip install git+https://github.com/quintenroets/school
```
Developed for Linux OS

# Script 

![Alt text](examples/out.png?raw=true)

# Sciensano 

taken from [here](http://covid-19.sciensano.be/sites/default/files/Covid19/COVID-19_Daily%20report_20211229%20-%20NL.pdf)

![Alt text](examples/sciensano.png?raw=true)
