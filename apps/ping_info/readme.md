# Overview
Script to check ping to specific machine.  
Store result in csv file in `data` folder  
# Installation
1. Install python
2. cd to folder with script
3. run below code
```python
pip install -r r.txt
```
4. fill config.json with proper values. `Duration` is in hours
5. run script
```python
python main.py
```
# Tools
1. **converter.py** script used to delete proper ping and save only timeouts (+ and - one row of timeout for better analise).
2. **analysis.py** script used to analise `timeouts.csv` file (Work in progress, right now shows only max,min and avarage of ping)