#!/bin/bash

echo "filenabe:"
read filename

if [ -f "$filename" ]; then
cat "$filename"
else
echo "eror"
fi
