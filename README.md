# Active Learning Demo
Active Learning clustering of flight data

## Dependencies
This repository requires the following packages:

 - Python 3
 - matplotlib
 - numpy
 - scikit-learn
 - pandas
 - PyQt5

 # Compiling UI
 To generate the code for the UI, use the `pyuic5` tool:

 ```zsh
 for ui_file in $(find demo/ui -name "*.ui")
 do
    pyuic5 $ui_file -o ${ui_file:r}.py
 done
 ```

 # Running
 The main file is `demo.py`. In this file you can specify the path to the input
 data dir, with all the flight data, as well as to the csv file that has the
 features obtained by using DTW.

`python run_demo.py`

# Report
An explanation of the research and the experiments carried out can be observed in report.pdf file. Unfortunately the data used in this project is private.

# Authors
This demo has been developed by Leonardo Vilela Teixeira and Miguel Mendez Perez at Purdue University