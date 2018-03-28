#!/bin/bash

for run in {1..20}
do
 python -m client.run_client dragon &
done

sleep 3

# let's spawn all humans to randomized server

for run in {1..200}
do
 python -m client.run_client &
done
