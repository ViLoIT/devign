#!/bin/bash

# Check if an input file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 input.json"
    exit 1
fi

input_file="$1"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found!"
    exit 1
fi

# Extract the directory and filename
input_dir=$(dirname "$input_file")
input_filename=$(basename "$input_file")
output_file="$input_dir/shuffled_$input_filename"

# Shuffle JSON array using jq and shuf
jq -c '.[]' "$input_file" | shuf | jq -s '.' > "$output_file"

echo "Shuffled JSON saved to $output_file"
