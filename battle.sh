#!/bin/bash

python -m client.Observer 127.0.0.1:9191 &

sleep 5

# let's spawn 4 dragons and 20 humans to both server
for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

# wait a bit
sleep 10

for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

sleep 10

# let's spawn 4 dragons and 20 humans to both server
for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

sleep 10

# let's spawn 4 dragons and 20 humans to both server
for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done

for run in {1..2}
do
 python -m client.run_client dragon &
done

for run in {1..10}
do
 python -m client.run_client &
done
