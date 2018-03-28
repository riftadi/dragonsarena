#!/bin/bash

amount=2
if [[ "$1" != "" ]]; then
    amount="$1"
fi

for observer in $(seq $amount)
do
    python -m client.Observer $(($observer-1)) &
done