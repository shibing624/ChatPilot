#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

KEY_FILE=.webui_secret_key

PORT="${PORT:-8080}"
if test "$WEBUI_SECRET_KEY $WEBUI_JWT_SECRET_KEY" = " "; then
  echo No WEBUI_SECRET_KEY provided

  if ! [ -e "$KEY_FILE" ]; then
    echo Generating WEBUI_SECRET_KEY
    # Generate a random value to use as a WEBUI_SECRET_KEY in case the user didn't provide one.
    echo $(head -c 12 /dev/random | base64) > $KEY_FILE
  fi

  echo Loading WEBUI_SECRET_KEY from $KEY_FILE
  WEBUI_SECRET_KEY=`cat $KEY_FILE`
fi

export WEBUI_SECRET_KEY="$WEBUI_SECRET_KEY"
ps -ef | grep "chatpilot" | grep -v "grep" | awk '{print $2}' | xargs kill -9
gunicorn -k uvicorn.workers.UvicornWorker chatpilot.server:app --bind 0.0.0.0:$PORT --forwarded-allow-ips '*' -w 2