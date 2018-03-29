#!/bin/bash

for run in {1..20}
do
    python -m client.run_client dragon &
done
