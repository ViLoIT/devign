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
OUTPUT_FILE="$OUTPUT_FOLDER/dataset.json"

# Create an empty JSON array
json_array="[]"

# Read up to X C# files into an array (or all if X_FILES is 0)
if [ "$X_FILES" -gt 0 ]; then
    mapfile -t cs_files < <(find "$INPUT_FOLDER" -type f -name "*.cs" ! -name "*.csproj" | head -n "$X_FILES")
else
    mapfile -t cs_files < <(find "$INPUT_FOLDER" -type f -name "*.cs" ! -name "*.csproj")
fi

echo "Found ${#cs_files[@]} C# files to process."

# Initialize a counter
count=0

# Process each C# file
for file in "${cs_files[@]}"; do
    filename=$(basename -- "$file")
    echo "Parse file $filename at position" 
    content=$(jq -Rs . < "$file") # Read file content and escape it for JSON
    
    json_object="{
        \"project\": \"$filename\", 
        \"target\": 1,
        \"commit_id\": \"$COMMIT_ID\",
        \"func\": $content
    }"
    
    # Append JSON object to array
    json_array=$(echo "$json_array" | jq --argjson obj "$json_object" '. + [$obj]')

    ((count++))
    if ((count % 10 == 0)); then
        echo "Processed $count files..."
    fi
done

# Save the final JSON array to output file
echo "$json_array" > "$OUTPUT_FILE"

echo "Combined JSON file created at $OUTPUT_FILE"
