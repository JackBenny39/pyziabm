# pyziabm
Zero Intelligence Agent-Based Model of Modern Limit Order Book

Charles Collver, PhD

<<<<<<< HEAD
=======
See the [Project Website](https://jackbenny39.github.io/pyziabm/) for more details.

>>>>>>> branch 'master' of https://github.com/JackBenny39/pyziabm.git
If you just want to install and run a quick simulation:
conda install -c dennycrane pyziabm

In A Jupyter Notebook or iPython command line:

from pyziabm.runner2017mpi_r4 import Runner

Runner() 

will call the simulation with the defaults. To change the defaults and run several in a loop see the runwrapper files detailed below.

There are five files:
1. orderbook3.py
2. trader2017_r3.py
3. runner2017mpi_r3.py
4. runwrapper2017mpi_r3.py
5. runwrapper2017mpi_r3x.py

### orderbook3.py
* Contains the Orderbook class.
* Instances track, process and match orders.
* Imported by runner2017mpi_r3.py.

### trader2017_r3.py
* Contains the base ZITrader class and four subclasses: PennyJumper, Taker, Provider, MarketMaker.
* Imported by runner2017mpi_r3.py.

### runner2017mpi_r3.py
* Contains the Runner class.
* Instances set up and run 1 simulation.
* Note: the __init__() uses all keywords - these are the defaults. User can change them here or override them when instantiating in __main__().
* Note: User should specify proper paths for saving output.
* Imported by runwrapper2017mpi_r3.py.

### runwrapper2017mpi_r3.py
* Runs the simulations in a loop, does some summary output bookkeeping.
* Note: User should specify proper paths for saving output.

### runwrapper2017mpi_r3x.py
* Unix executable version of runwrapper2017mpi_r3.py.
* Note: User should specify proper paths for the python executable and saving output.

There are two test files:
1. testOrderbook3.py
2. testTrader2017_r3.p7

There are several Jupyter Notebooks that should work with minimal changes to the directories.

### Written and tested with Python3.6
