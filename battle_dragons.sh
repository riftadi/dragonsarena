#!/bin/bash

for run in {1..4}
do
    python -m client.run_client dragon &
done
