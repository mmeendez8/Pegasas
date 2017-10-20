#!/usr/bin/env bash

for ui_file in $(find demo/ui -name "*.ui")
do
   echo ${ui_file:r}
   echo "${ui_file%%.*}"
   pyuic5 $ui_file -o $"${ui_file%%.*}".py
done



