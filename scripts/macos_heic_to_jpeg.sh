#!/bin/zsh

# macos_heic_to_jpeg.sh
# Converts all HEIC files in a given folder to JPEG using sips.
# Case-insensitive - matches .heic, .HEIC, etc.
#
# Usage: macos_heic_to_jpeg.sh <folder>
# Example: macos_heic_to_jpeg.sh ~/Photos

# Use $1 if set; otherwise print the error message and exit.
# This uses the ${parameter:?word} form of shell parameter expansion.
# See: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
WORK_DIR="${1:?Usage: macos_heic_to_jpeg.sh <folder>}"

# nocaseglob handles the case-insensitive matching natively, so you only need one glob pattern
setopt nocaseglob

for f in "$WORK_DIR"/*.heic; do
  output="${f%.*}.jpg"
  echo "Converting $f -> $output"
  
  # sips: scriptable image processing system (MacOS-specific)
  sips -s format jpeg "$f" --out "$output"
done

echo "Done."
