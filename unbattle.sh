#!/bin/bash

case "$(uname -s)" in

   Darwin)
        # Mac OS
        sudo pkill Python

        sudo kill -9 $(ps aux | grep client.Observer | grep -v grep | awk '{print $2}')
        sudo kill -9 $(ps aux | grep client.run_client | grep -v grep | awk '{print $2}')

        sudo kill -9 $(ps aux | grep battle | grep -v unbattle | grep -v grep | awk '{print $2}')
     ;;

   Linux)
        # Linux

        sudo kill -9 $(ps aux | grep server.run_server | grep -v grep | awk '{print $2}')
        sudo kill -9 $(ps aux | grep client.Observer | grep -v grep | awk '{print $2}')
        sudo kill -9 $(ps aux | grep client.run_client | grep -v grep | awk '{print $2}')

        sudo kill -9 $(ps aux | grep battle | grep -v unbattle | grep -v grep | awk '{print $2}')
     ;;

   CYGWIN*|MINGW32*|MSYS*)
        # Windows

     ;;

   *)
        # Other OS
     ;;

esac
