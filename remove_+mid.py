#Many of the .mid files had mid before the .mid extension so to remove this, run this code
#the main scrape.py code was modified to remove mid but use this if that doesnt work

import os
import re
from pathlib import Path

def clean_mid_filename(filename):
    """Remove 'mid' that appears right before '.mid' extension (case insensitive)"""
    return re.sub(r'mid(?=\.mid$)', '', filename, flags=re.IGNORECASE)

def process_artists_folder(root_folder="Artists"):
    """Process all .mid files in Artists folder and subfolders"""
    root_path = Path(root_folder)
    
    for midi_file in root_path.glob('**/*.mid'):
        original_name = midi_file.name
        cleaned_name = clean_mid_filename(original_name)
        
        if cleaned_name != original_name:
            new_path = midi_file.with_name(cleaned_name)
            midi_file.rename(new_path)
            print(f"Renamed: {original_name} -> {cleaned_name}")

if __name__ == "__main__":
    print("Cleaning .mid filenames in Artists folder...")
    process_artists_folder()
    print("Done!")