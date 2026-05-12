#!/bin/bash

echo "filename?"
read filename

if [ -f "$filename" ]; then
echo " + "
else
echo " - "
fi
