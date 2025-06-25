import json
import os

# Path to your metadata file
SOURCES_METADATA_PATH = "sources_metadata.json" # Adjust if it's in a subfolder like "data/"

# Directory where you want to create the empty transcript files
# The script will create this directory if it doesn't exist.
TRANSCRIPTS_DIR = "interview_transcripts" 

def create_empty_transcript_files(metadata_path, output_dir):
    """
    Reads source_doc_ids from the metadata file and creates an empty .txt file
    for each in the specified output directory.
    """
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            sources_metadata = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Sources metadata file not found at '{metadata_path}'. Cannot create transcript files.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from '{metadata_path}'.")
        return

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created directory: '{output_dir}'")
        except OSError as e:
            print(f"ERROR: Could not create directory '{output_dir}': {e}")
            return
    else:
        print(f"Directory '{output_dir}' already exists.")

    count = 0
    for source_doc_id in sources_metadata.keys():
        filename = os.path.join(output_dir, f"{source_doc_id}.txt")
        try:
            # 'w' mode will create the file if it doesn't exist,
            # or overwrite it if it does (which is fine for empty files).
            # Using 'a' (append) would also create it if it doesn't exist
            # and do nothing if it exists and is empty.
            with open(filename, 'w', encoding='utf-8') as f:
                # File is created empty, no need to write anything
                pass 
            print(f"Created empty file: '{filename}'")
            count += 1
        except IOError as e:
            print(f"ERROR: Could not create file '{filename}': {e}")
    
    print(f"\nSuccessfully created {count} empty transcript files in '{output_dir}'.")

if __name__ == "__main__":
    # Make sure your sources_metadata.json is in the same directory as this script,
    # or provide the correct path.
    create_empty_transcript_files(SOURCES_METADATA_PATH, TRANSCRIPTS_DIR)