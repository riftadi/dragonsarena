#!/bin/bash
for run in {1..7}
do
  python Client.py dragon &
done

python Client.py human x &

for run in {1..10}
do
  python Client.py &
done