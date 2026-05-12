#!/bin/bash

WATCH_DIR="$HOME/demo/HW5/ex10watch"

inotifywait -m -e create "$WATCH_DIR" --format "%f" | while read FILE
do
FULL_PATH="$WATCH_DIR/$FILE"

sleep 1
if [ -f "$FULL_PATH" ]; then
echo "new file detected: $FILE"

echo "_____FILE CONTENT_____"
cat "$FULL_PATH"
echo "______________________"

mv "$FULL_PATH" "$FULL_PATH.back"

echo "File renamed to: $FILE.back"
fi
done
