#!/bin/bash

python -m client.Observer 127.0.0.1:8181 &
python -m client.Observer 127.0.0.1:9191 &

for run in {1..20}
do
 python -m client.run_client dragon &
done

sleep 5

# let's spawn 20 humans to randomized server

for run in {1..20}
do
 python -m client.run_client &
done

sleep 5

# let's spawn 20 humans to randomized server

for run in {1..20}
do
 python -m client.run_client &
done

sleep 5

# let's spawn 20 humans to randomized server

for run in {1..20}
do
 python -m client.run_client &
done

sleep 5

# let's spawn 20 humans to randomized server

for run in {1..20}
do
 python -m client.run_client &
done
