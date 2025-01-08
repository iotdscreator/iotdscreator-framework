#!/bin/sh

if [ "$#" -ne 5 ]; then
  echo "Error: incorrect number of arguments"
  echo "Usage: $0 <device name> <server's address> <server's port number> <application (top/atop)> <report time interval (in seconds)>"
  exit 1
fi

NAME=$1
ADDR=$2
PORT=$3
APP=$4
INTERVAL=$5
APP_TIMEOUT=1
NC_TIMEOUT=3
SLEEP_TIME=$((INTERVAL-ATOP_TIMEOUT-NC_TIMEOUT))
TIMEOUT=$((APP_TIMEOUT+NC_TIMEOUT))

if [ "$APP" = "top" ]; then
  echo "The top application is used to report host data"
elif [ "$APP" = "atop" ]; then
  echo "The atop application is used to report host data"
else
  echo "The application (${APP}) is unavailable"
  echo "Please use top or atop for this purpose"
  exit 1
fi

if [ "$SLEEP_TIME" -le 0 ]; then
  echo "Error: the sleep time is less than or equal to 0"
  echo "Please increase the interval time (at least ${TIMEOUT} seconds)"
  exit 1
fi

while true
do
  timeout ${APP_TIMEOUT} ${APP} > test.txt
  ATOP=`cat test.txt`
  TIMESTAMP=$(date +%s)
  MSG="{ \"name\": \"${NAME}\", \"type\": \"${APP}\", \"timestamp\": \"${TIMESTAMP}\", \"data\": \"${ATOP}\" }"

  echo "${MSG}" | timeout ${NC_TIMEOUT} nc -u ${ADDR} ${PORT} 
  sleep ${SLEEP_TIME}
done
