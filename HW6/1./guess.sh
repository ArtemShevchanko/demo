#!/bin/bash

number=$((RANDOM % 100 + 1))
attempts=0
max_attempts=5

echo "Guess the number from 1 to 100"

while [ $attempts -lt $max_attempts ]
do
    read -p "Enter number: " guess

    attempts=$((attempts + 1))

    if [ "$guess" -eq "$number" ]; then
        echo "Congratulations! You guessed correctly."
        exit 0
    elif [ "$guess" -lt "$number" ]; then
        echo "Too low."
    else
        echo "Too high."
    fi

    echo "Attempts left: $((max_attempts - attempts))"
done

echo "Sorry, you are out of attempts."
echo "Correct number was: $number"