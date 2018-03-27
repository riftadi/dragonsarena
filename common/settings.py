# This file holds all settings in the game

# Are we running on AWS?
AWS_MODE_FLAG = False

# How many servers should be running
N_SERVERS = 2

# Which servers (in server_ID) should the client connect to?
CLIENTSIDE_SERVER_LIST = [1, 2]

# Duration of gta game in seconds
GTA_DURATION = 2 * 60

LOCAL_IP = ["127.0.0.1", "127.0.0.1", "127.0.0.1", "127.0.0.1", "127.0.0.1"]

# The addresses of the servers
SERVERS_LOCAL = [
            { # server 1
                "server_id"     :  1,
                "server2client" :  "%s:8181" % LOCAL_IP[0],
                "client2server" :  "%s:8282" % LOCAL_IP[0],
                "server2server" :  "%s:8383" % LOCAL_IP[0],
            },

            { # server 2
                "server_id"     :  2,
                "server2client" :  "%s:9191" % LOCAL_IP[1],
                "client2server" :  "%s:9292" % LOCAL_IP[1],
                "server2server" :  "%s:9393" % LOCAL_IP[1],
            },
            
            { # server 3
                "server_id"     :  3,
                "server2client" :  "%s:10101" % LOCAL_IP[2],
                "client2server" :  "%s:10202" % LOCAL_IP[2],
                "server2server" :  "%s:10303" % LOCAL_IP[2],
            },
            
            { # server 4
                "server_id"     :  4,
                "server2client" :  "%s:11111" % LOCAL_IP[3],
                "client2server" :  "%s:11212" % LOCAL_IP[3],
                "server2server" :  "%s:11313" % LOCAL_IP[3],
            },
            
            { # server 5
                "server_id"     :  5,
                "server2client" :  "%s:12121" % LOCAL_IP[4],
                "client2server" :  "%s:12222" % LOCAL_IP[4],
                "server2server" :  "%s:12323" % LOCAL_IP[4],
            },
          ]

PRIVATE_AWS_IP = ["172.16.17.1", "172.16.17.1", "172.16.17.1", "172.16.17.1", "172.16.17.1"]

SERVERS_AWS_PRIVATE = [
            { # server 1
                "server_id"     :  1,
                "server2client" :  "%s:8181" % PRIVATE_AWS_IP[0],
                "client2server" :  "%s:8282" % PRIVATE_AWS_IP[0],
                "server2server" :  "%s:8383" % PRIVATE_AWS_IP[0],
            },

            { # server 2
                "server_id"     :  2,
                "server2client" :  "%s:8181" % PRIVATE_AWS_IP[1],
                "client2server" :  "%s:8282" % PRIVATE_AWS_IP[1],
                "server2server" :  "%s:8383" % PRIVATE_AWS_IP[1],
            },
            
            { # server 3
                "server_id"     :  3,
                "server2client" :  "%s:8181" % PRIVATE_AWS_IP[2],
                "client2server" :  "%s:8282" % PRIVATE_AWS_IP[2],
                "server2server" :  "%s:8383" % PRIVATE_AWS_IP[2],
            },
            
            { # server 4
                "server_id"     :  4,
                "server2client" :  "%s:8181" % PRIVATE_AWS_IP[3],
                "client2server" :  "%s:8282" % PRIVATE_AWS_IP[3],
                "server2server" :  "%s:8383" % PRIVATE_AWS_IP[3],
            },
            
            { # server 5
                "server_id"     :  5,
                "server2client" :  "%s:8181" % PRIVATE_AWS_IP[4],
                "client2server" :  "%s:8282" % PRIVATE_AWS_IP[4],
                "server2server" :  "%s:8383" % PRIVATE_AWS_IP[4],
            },
          ]

PUBLIC_AWS_IP = ["52.50.157.142", "54.154.152.152", "52.50.157.142", "54.154.152.152", "52.50.157.142"]

SERVERS_AWS_PUBLIC = [
            { # server 1
                "server_id"     :  1,
                "server2client" :  "%s:8181" % PUBLIC_AWS_IP[0],
                "client2server" :  "%s:8282" % PUBLIC_AWS_IP[0],
                "server2server" :  "%s:8383" % PUBLIC_AWS_IP[0],
            },

            { # server 2
                "server_id"     :  2,
                "server2client" :  "%s:8181" % PUBLIC_AWS_IP[1],
                "client2server" :  "%s:8282" % PUBLIC_AWS_IP[1],
                "server2server" :  "%s:8383" % PUBLIC_AWS_IP[1],
            },
            
            { # server 3
                "server_id"     :  3,
                "server2client" :  "%s:8181" % PUBLIC_AWS_IP[2],
                "client2server" :  "%s:8282" % PUBLIC_AWS_IP[2],
                "server2server" :  "%s:8383" % PUBLIC_AWS_IP[2],
            },
            
            { # server 4
                "server_id"     :  4,
                "server2client" :  "%s:8181" % PUBLIC_AWS_IP[3],
                "client2server" :  "%s:8282" % PUBLIC_AWS_IP[3],
                "server2server" :  "%s:8383" % PUBLIC_AWS_IP[3],
            },
            
            { # server 5
                "server_id"     :  5,
                "server2client" :  "%s:8181" % PUBLIC_AWS_IP[4],
                "client2server" :  "%s:8282" % PUBLIC_AWS_IP[4],
                "server2server" :  "%s:8383" % PUBLIC_AWS_IP[4],
            },
          ]

# Delays setting for the characters
CHAR_MIN_DELAY = 1000
CHAR_MAX_DELAY = 2000
BOT_CLOSING_WAIT_TIME = 15

# TSS Gamestate ID
LEADING_STATE = 0
TRAILING_01_STATE = 1
TEMP_STATE = 9

# TSS Delay
TRAILING_01_DELAY = 500
RELAX_TSS_ORDER_CHECKING = True
MSG_LATE_DELAY_BUDGET = 50

# various delays in ms
GAMESTATE_PUBLISH_DELAY = 500.0
SERVERSIDE_CLIENT_TIMEOUT = 3000
CLIENTSIDE_UPDATE_TIMEOUT = 5000
GAMECLOCK_UPDATE_DELAY = 10.0
SERVER_MAIN_LOOP_DELAY = 500.0
WAIT_DELAY_AFTER_GAME_END = 5000
GAME_WINNING_CONDITION_CHECK_DELAY = 300
