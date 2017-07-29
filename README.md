# pyziabm
Zero Intelligence Agent-Based Model of Modern Limit Order Book

Charles Collver, PhD

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
* Note: for now the price choice set for Provider and Market Maker are hard-coded to improve simulation speed. The user must comment/uncomment the choices for mpi=1 vs. mpi=5 in Provider and MarketMaker. Potential improvements include writing subclasses or specifying the methods at *construction* time (in a dict, maybe).
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

### Written and tested with Python3.6
