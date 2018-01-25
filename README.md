# pyziabm
Zero Intelligence Agent-Based Model of Modern Limit Order Book

Charles Collver, PhD

See the [Project Website](https://jackbenny39.github.io/pyziabm/) for more details.

If you just want to install and run a quick simulation:
conda install -c dennycrane pyziabm

In a Jupyter Notebook or iPython command line:

import pyziabm as pzi
pzi.Runner()

will call the simulation with the defaults. To change the defaults and run several in a loop see the runwrapper files detailed below.

There are seven files:
1. orderbook3.py
2. trader2017_r3.py
3. runner2017mpi_r3.py
4. runner2017mpi_r4.py
5. runwrapper2017mpi_r3.py
6. runwrapper2017mpi_r3x.py
7. runwrapper2017mpi_r4.py

### orderbook3.py
* Contains the Orderbook class.
* Instances track, process and match orders.
* Imported by runner2017mpi_r3.py.

### trader2017_r3.py
* Contains the base ZITrader class and six subclasses: PennyJumper, Taker, Provider, Provider5, MarketMaker, MarketMaker5.
* There is also an InformedTrader, but it is yet unimplemented. See [pyziabmc](https://github.com/jackbenny39/pyziabmc) for more details.
* Imported by runner2017mpi_r3.py and runner2017mpi_r4.py.

### runner2017mpi_r3.py and runner2017mpi_r4.py
* Contains the Runner class.
* Instances set up and run 1 simulation.
* Note: the \_\_init\_\_() in runner2017mpi_r3.py uses all keywords - these are the defaults. User can change them here or override them when instantiating in \_\_main\_\_().
* Note: User should specify proper paths for saving output.
* Imported by runwrapper2017mpi_r3.py or runwrapper2017mpi_r4.py.

### runwrapper2017mpi_r3.py and runwrapper2017mpi_r4.py
* Runs the simulations in a loop, does some summary output bookkeeping.
* Note: User should specify proper paths for saving output.

### runwrapper2017mpi_r3x.py
* An example of a Unix executable version of runwrapper2017mpi_r3.py.
* Note: User should specify proper paths for the python executable and saving output.

There are two test files:
1. testOrderbook3.py
2. testTrader2017_r3.py

There are several Jupyter Notebooks that should work with minimal changes to the directories.

### Written and tested with Python3.6
