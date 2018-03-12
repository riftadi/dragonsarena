#!/bin/bash

python -m client.Observer 127.0.0.1:9191 &

sleep 5

# let's spawn 4 dragons and 20 humans to both server
for run in {1..2}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 &
done

for run in {1..2}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 &
done

# wait a bit
sleep 10

for run in {1..2}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 &
done

for run in {1..2}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 &
done

sleep 10

# let's spawn 4 dragons and 20 humans to both server
for run in {1..2}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 &
done

for run in {1..2}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 &
done

sleep 10

# let's spawn 4 dragons and 20 humans to both server
for run in {1..2}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282 &
done

for run in {1..2}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 dragon &
done

for run in {1..10}
do
 python -m client.run_client 127.0.0.1:9191 127.0.0.1:9292 &
done
