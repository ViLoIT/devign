#!/bin/bash

# Ensure correct usage
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_folder> <output_folder>"
    exit 1
fi

INPUT_FOLDER="$1"
OUTPUT_FOLDER="$2"

# Define good and bad output directories
GOOD_DIR="$OUTPUT_FOLDER/good"
BAD_DIR="$OUTPUT_FOLDER/bad"

# Create output directories
mkdir -p "$GOOD_DIR"
mkdir -p "$BAD_DIR"

# Function to process a C# file
process_file() {
    local input_file="$1"
    local relative_path="${input_file#$INPUT_FOLDER/}"  # Get relative path
    local output_bad="$BAD_DIR/${relative_path%.cs}_bad.cs"
    local output_good="$GOOD_DIR/${relative_path%.cs}_good.cs"

    local in_bad=0
    local in_good=0
    local capturing_header=1
    local header=""
    local footer=""

    # Ensure output directories exist for subfolders
    mkdir -p "$(dirname "$output_bad")"
    mkdir -p "$(dirname "$output_good")"

    # Read the file line by line
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Capture header (until #if is found)
        if [[ "$line" == *"#if (!OMITBAD)"* ]]; then
            in_bad=1
            in_good=0
            capturing_header=0
            echo -e "$header" > "$output_bad"  # Write header to bad file
            continue
        elif [[ "$line" == *"#if (!OMITGOOD)"* ]]; then
            in_good=1
            in_bad=0
            capturing_header=0
            echo -e "$header" > "$output_good"  # Write header to good file
            continue
        fi

        # Stop capturing when reaching #endif
        if [[ "$line" == *"#endif"* ]]; then
            in_bad=0
            in_good=0
            continue
        fi

        # Capture the header part (before the first #if)
        if [[ $capturing_header -eq 1 ]]; then
            header+="$line\n"
        fi

        # Ensure class structure remains
        if [[ $in_bad -eq 1 ]]; then
            echo "$line" >> "$output_bad"
        elif [[ $in_good -eq 1 ]]; then
            echo "$line" >> "$output_good"
        fi
    done < "$input_file"

    # Ensure proper closing braces for class and namespace
    footer="}\n}\n"

    # Append the footer to maintain valid C# syntax
    if [[ -s "$output_bad" ]]; then
        echo -e "$footer" >> "$output_bad"
    fi
    if [[ -s "$output_good" ]]; then
        echo -e "$footer" >> "$output_good"
    fi

    echo "Processed: $input_file → $output_bad & $output_good"
}

# Find all C# files in the input folder and process them
find "$INPUT_FOLDER" -type f -name "*.cs" | while read -r file; do
    process_file "$file"
done

echo "All C# files processed. Output in $OUTPUT_FOLDER"
