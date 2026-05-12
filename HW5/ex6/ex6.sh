#!/bin/bash

echo "you sentence:"
read sentence
echo $sentence | awk '{for(i=NF;i>=1;i--) printf $i" "; print ""}'
