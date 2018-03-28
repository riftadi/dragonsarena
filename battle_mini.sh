#!/bin/bash

amount=2
if [[ "$1" != "" ]]; then
    amount="$1"
fi

for observer in $(seq $amount)
do
    python -m client.Observer $(($observer-1)) &
done

for run in {1..2}
do
 python -m client.run_client dragon &
done

sleep 3

# let's spawn 4 humans to randomized server

for run in {1..4}
do
 python -m client.run_client &
done
