#!/bin/bash
first_block=0
gap=100


for i in 0 1 2 3 4 5 6 7 8 9
do
  start=$((first_block + i * gap))
  end=$((start + gap - 1))
  nohup python task_manager.py ${start} ${end} > "../logs/${start}_${end}" 2>&1 &
  echo "Welcome $i times, $start, $end, ${start}_${end}"
done