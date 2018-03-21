#!/bin/bash

python -m client.Observer 127.0.0.1:8181 &
python -m client.Observer 127.0.0.1:9191 &
python -m client.Observer 127.0.0.1:7191 &

for run in {1..20}
do
 python -m client.run_client dragon &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done

sleep 3

# let's spawn 10 humans to randomized server

for run in {1..5}
do
 python -m client.run_client &
done

sleep 2

for run in {1..5}
do
 python -m client.run_client &
done
