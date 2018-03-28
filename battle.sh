#!/bin/bash
amount=2
if [[ "$1" != "" ]]; then
    amount="$1"
fi

for observer in $(seq $amount)
do
    python -m client.Observer $(($observer-1)) &
done

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
