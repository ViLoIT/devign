#!/bin/bash

# Check if correct number of arguments is provided
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 <input_folder> <output_folder> [num_files]"
    exit 1
fi

INPUT_FOLDER="$1"
OUTPUT_FOLDER="$2"
X_FILES="${3:-0}" # Use provided number or default to 0 (process all files)
COMMIT_ID="8ec824c0903f4ab0c52ea5d8898abc8331a66e9a"

# Ensure output folder exists
mkdir -p "$OUTPUT_FOLDER"

# Define output file path
OUTPUT_FILE="$OUTPUT_FOLDER/$(echo "$INPUT_FOLDER" | sed 's|/|-|g').json"

# Find all C# files
mapfile -t cs_files < <(find "$INPUT_FOLDER" -type f -name "*.cs" ! -name "*.csproj")

# Shuffle and pick X_FILES if specified
if [ "$X_FILES" -gt 0 ] && [ "${#cs_files[@]}" -gt "$X_FILES" ]; then
    mapfile -t cs_files < <(printf "%s\n" "${cs_files[@]}" | shuf -n "$X_FILES")
fi

echo "Found ${#cs_files[@]} C# files to process."

# Initialize an empty JSON array in a file buffer
echo "[" > "$OUTPUT_FILE"
first_file=true
count=0

# Process each C# file efficiently
for file in "${cs_files[@]}"; do
    filename=$(basename -- "$file")
    content=$(jq -Rs . < "$file")  # Read and escape file content for JSON

    json_object="{
        \"project\": \"$filename\", 
        \"target\": 0,
        \"commit_id\": \"$COMMIT_ID\",
        \"func\": $content
    }"

    # Add a comma separator for all but the first entry
    if [ "$first_file" = true ]; then
        first_file=false
    else
        echo "," >> "$OUTPUT_FILE"
    fi

    echo "$json_object" >> "$OUTPUT_FILE"

    ((count++))
    if ((count % 1000 == 0)); then
        echo "Processed $count files..."
    fi
done

# Close JSON array
echo "]" >> "$OUTPUT_FILE"

echo "Combined JSON file created at $OUTPUT_FILE"
