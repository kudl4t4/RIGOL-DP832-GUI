# RIGOL-DP832-GUI

> Python based RIGOL DP832 GUI

Simple Python-based application to give a visual remote control interface for the [Rigol DP832](https://www.rigolna.com/products/dc-power-loads/dp800/).

### Main Features ###
  * Supports direct control of all three channels. 
  * Supports graphing view with data logging to csv. 
  * Supports both NI VISA and Python VISA (through PyVISA) 
### Screenshots ###
<img src="https://raw.githubusercontent.com/dretay/RIGOL-DP832-GUI/master/img/screenshot1.png" width="640">
<img src="https://raw.githubusercontent.com/dretay/RIGOL-DP832-GUI/master/img/screenshot2.png" width="640">
### Build Instructions ###
#### Basic Build Setup
1. [install poetry](https://python-poetry.org/docs/) 
2. install any missing dependencies for poetry and or the dependent python librar
  ```
  $ sudo apt-get install python3-matplotlib python3-qtpy python3-venv
  ```
3. install python packages
  ```
  $ poetry install
  ```
#### Running the Application
You can choose to run with either the default NI VISA backend or the python-based pyvisa-py backend by invoking the application as follows:
  ```
  $ poetry run python RIGOL_DP832_GUI.py --pyvisapy
  ```
