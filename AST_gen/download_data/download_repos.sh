#!/bin/bash

echo $1
if [ -z "$1" ]
then
    echo "No argument supplied"
    exit 1
fi

mkdir -p data_repos
cd data_repos

while IFS= read -r line
do
    echo "$line"
    git clone --depth=1 $line
done < "$1"

find . -type f ! -name "*.py" -exec rm {} \;
find . -type d -empty -delete

#Remove symbolic links
find . -type l -delete