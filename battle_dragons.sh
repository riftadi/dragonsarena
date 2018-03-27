#!/bin/bash

python -m client.Observer 127.0.0.1:8181 &
python -m client.Observer 127.0.0.1:9191 &
# python -m client.Observer 127.0.0.1:7191 &

# python -m client.Observer 52.50.157.142:8181 &
# python -m client.Observer 54.154.152.152:9191 &

for run in {1..20}
do
 python -m client.run_client dragon &
done
