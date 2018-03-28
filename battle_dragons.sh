#!/bin/bash

# python -m client.Observer 127.0.0.1:8181 &
# python -m client.Observer 127.0.0.1:9191 &
# python -m client.Observer 127.0.0.1:7191 &

python -m client.Observer 34.245.150.134:8181 &
python -m client.Observer 34.244.251.145:8181 &

for run in {1..20}
do
 python -m client.run_client dragon &
done
