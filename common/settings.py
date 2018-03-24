# This file holds all settings in the game

# Are we running on AWS?
AWS_MODE_FLAG = False

# How many servers should be running
N_SERVERS = 2

# Which servers (in server_ID) should the client connect to?
CLIENTSIDE_SERVER_LIST = [1, 2]

# Duration of gta game in seconds
GTA_DURATION = 2 * 60

# The addresses of the servers
SERVERS_LOCAL = [
            { # server 1
                "server_id"     :  1,
                "server2client" :  "127.0.0.1:8181",
                "client2server" :  "127.0.0.1:8282",
                "server2server" :  "127.0.0.1:8383",
            },

            { # server 2
                "server_id"     :  2,
                "server2client" :  "127.0.0.1:9191",
                "client2server" :  "127.0.0.1:9292",
                "server2server" :  "127.0.0.1:9393",
            },
            
            { # server 3
                "server_id"     :  3,
                "server2client" :  "127.0.0.1:7191",
                "client2server" :  "127.0.0.1:7292",
                "server2server" :  "127.0.0.1:7393",
            },
            
            { # server 4
                "server_id"     :  4,
                "client2server" :  "127.0.0.1:10101",
                "server2client" :  "127.0.0.1:10202",
                "server2server" :  "127.0.0.1:10303",
            },
            
            { # server 5
                "server_id"     :  5,
                "client2server" :  "127.0.0.1:11101",
                "server2client" :  "127.0.0.1:11202",
                "server2server" :  "127.0.0.1:11303",
            },
          ]

SERVERS_AWS_PRIVATE = [
            { # server 1
                "server_id"     :  1,
                "server2client" :  "172.16.17.1:8181",
                "client2server" :  "172.16.17.1:8282",
                "server2server" :  "172.16.17.1:8383",
            },

            { # server 2
                "server_id"     :  2,
                "server2client" :  "172.16.17.2:9191",
                "client2server" :  "172.16.17.2:9292",
                "server2server" :  "172.16.17.2:9393",
            },
            
            { # server 3
                "server_id"     :  3,
                "server2client" :  "172.16.17.3:7191",
                "client2server" :  "172.16.17.3:7292",
                "server2server" :  "172.16.17.3:7393",
            },
            
            { # server 4
                "server_id"     :  4,
                "client2server" :  "172.16.17.4:10101",
                "server2client" :  "172.16.17.4:10202",
                "server2server" :  "172.16.17.4:10303",
            },
            
            { # server 5
                "server_id"     :  5,
                "client2server" :  "172.16.17.5:11101",
                "server2client" :  "172.16.17.5:11202",
                "server2server" :  "172.16.17.5:11303",
            },
          ]

SERVERS_AWS_PUBLIC = [
            { # server 1
                "server_id"     :  1,
                "server2client" :  "52.50.157.142:8181",
                "client2server" :  "52.50.157.142:8282",
                "server2server" :  "52.50.157.142:8383",
            },

            { # server 2
                "server_id"     :  2,
                "server2client" :  "54.154.152.152:9191",
                "client2server" :  "54.154.152.152:9292",
                "server2server" :  "54.154.152.152:9393",
            },
            
            { # server 3
                "server_id"     :  3,
                "server2client" :  "172.16.17.3:7191",
                "client2server" :  "172.16.17.3:7292",
                "server2server" :  "172.16.17.3:7393",
            },
            
            { # server 4
                "server_id"     :  4,
                "client2server" :  "172.16.17.4:10101",
                "server2client" :  "172.16.17.4:10202",
                "server2server" :  "172.16.17.4:10303",
            },
            
            { # server 5
                "server_id"     :  5,
                "client2server" :  "172.16.17.5:11101",
                "server2client" :  "172.16.17.5:11202",
                "server2server" :  "172.16.17.5:11303",
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
TRAILING_01_DELAY = 800
RELAX_TSS_ORDER_CHECKING = False
MSG_LATE_DELAY_BUDGET = 100

# various delays in ms
GAMESTATE_PUBLISH_DELAY = 500.0
SERVERSIDE_CLIENT_TIMEOUT = 3000
CLIENTSIDE_UPDATE_TIMEOUT = 2000
GAMECLOCK_UPDATE_DELAY = 10.0
SERVER_MAIN_LOOP_DELAY = 500.0
WAIT_DELAY_AFTER_GAME_END = 5000
GAME_WINNING_CONDITION_CHECK_DELAY = 300
