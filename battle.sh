#!/bin/bash

python -m client.Observer &

sleep 5

for run in {1..2}
do
 python -m client.run_client 1 dragon &
done

for run in {1..10}
do
 python -m client.run_client 1 &
done

for run in {1..2}
do
 python -m client.run_client 2 dragon &
done

for run in {1..10}
do
 python -m client.run_client 2 &
done

sleep 10

for run in {1..2}
do
 python -m client.run_client 1 dragon &
done

for run in {1..10}
do
 python -m client.run_client 1 &
done

for run in {1..2}
do
 python -m client.run_client 2 dragon &
done

for run in {1..10}
do
 python -m client.run_client 2 &
done

sleep 10

for run in {1..2}
do
 python -m client.run_client 1 dragon &
done

for run in {1..10}
do
 python -m client.run_client 1 &
done

for run in {1..2}
do
 python -m client.run_client 2 dragon &
done

for run in {1..10}
do
 python -m client.run_client 2 &
done

sleep 10

for run in {1..2}
do
 python -m client.run_client 1 dragon &
done

for run in {1..10}
do
 python -m client.run_client 1 &
done

for run in {1..2}
do
 python -m client.run_client 2 dragon &
done

for run in {1..10}
do
 python -m client.run_client 2 &
done
