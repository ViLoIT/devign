#!/bin/bash

# Ensure correct usage
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <json_file> <output_folder> <num_random>"
    exit 1
fi

JSON_FILE="$1"
OUTPUT_FOLDER="$2"
NUM_RANDOM="$3"

# Validate that the JSON file exists
if [ ! -f "$JSON_FILE" ]; then
    echo "Error: JSON file '$JSON_FILE' not found!"
    exit 1
fi

# Validate that NUM_RANDOM is a positive integer
if ! [[ "$NUM_RANDOM" =~ ^[0-9]+$ ]] || [ "$NUM_RANDOM" -le 0 ]; then
    echo "Error: Number of random elements must be a positive integer."
    exit 1
fi

# Ensure the output directory exists
mkdir -p "$OUTPUT_FOLDER"

# Extract only the filename (without path)
FILE_NAME=$(basename -- "$JSON_FILE")  
BASE_NAME="${FILE_NAME%.json}"        
OUTPUT_FILE="$OUTPUT_FOLDER/${BASE_NAME}-selected.json"

echo "Output file: $OUTPUT_FILE"

# Get jq version
JQ_VERSION=$(jq --version 2>/dev/null | cut -d'-' -f2)
JQ_MAJOR=$(echo "$JQ_VERSION" | cut -d'.' -f1)
JQ_MINOR=$(echo "$JQ_VERSION" | cut -d'.' -f2)

# Check if jq supports shuffle (introduced in jq 1.6)
if [[ -z "$JQ_VERSION" || "$JQ_MAJOR" -lt 1 || ("$JQ_MAJOR" -eq 1 && "$JQ_MINOR" -lt 6) ]]; then
    echo "Warning: jq version < 1.6 detected! Using 'shuf' instead of 'shuffle'."

    # jq <1.6: Use shuf workaround
    jq -c '.[]' "$JSON_FILE" | shuf | head -n "$NUM_RANDOM" | jq -s '.' > "$OUTPUT_FILE"
else
    # jq 1.6+: Use shuffle
    jq -c '.[]' "$JSON_FILE" | shuf | head -n "$NUM_RANDOM" | jq -s '.' > "$OUTPUT_FILE"
fi

# Verify if the output file was created successfully
if [ -f "$OUTPUT_FILE" ]; then
    echo "Selected $NUM_RANDOM random elements from '$JSON_FILE' → '$OUTPUT_FILE'"
else
    echo "Error: Failed to create '$OUTPUT_FILE'!"
    exit 1
fi
