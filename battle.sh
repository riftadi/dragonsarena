#!/bin/bash

python -m client.Observer &

sleep 5

for run in {1..4}
do
 python -m client.run_client dragon &
done

for run in {1..20}
do
 python -m client.run_client &
done

sleep 10

for run in {1..4}
do
 python -m client.run_client dragon &
done

for run in {1..20}
do
 python -m client.run_client &
done

sleep 10

for run in {1..4}
do
 python -m client.run_client dragon &
done

for run in {1..20}
do
 python -m client.run_client &
done

sleep 10

for run in {1..4}
do
 python -m client.run_client dragon &
done

for run in {1..20}
do
 python -m client.run_client &
done
