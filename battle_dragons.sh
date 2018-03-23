#!/bin/bash

python -m client.Observer 127.0.0.1:8181 &
python -m client.Observer 127.0.0.1:9191 &
# python -m client.Observer 127.0.0.1:7191 &

for run in {1..20}
do
 python -m client.run_client dragon &
done
