#!/bin/bash
first_block=35400
gap=100


for i in 0
do
  start=$((first_block + i * gap))
  end=$((start + gap - 1))
  nohup python task_manager.py ${start} ${end} > "../logs/${start}_${end}" 2>&1 &
  echo "Welcome $i times, $start, $end, ${start}_${end}"
done