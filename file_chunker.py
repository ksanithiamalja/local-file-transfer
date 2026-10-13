import os
import time

def copy_file_in_chunks(source_path, destination_path, chunk_size=64 * 1024):
    """
    Copies a file from source_path to destination_path in binary chunks.
    chunk_size = 64 KB (65,536 bytes) by default.
    """
    if not os.path.exists(source_path):
        print(f"Error: Source file '{source_path}' does not exist.")
        return

    # Get total file size in bytes
    total_bytes = os.path.getsize(source_path)
    copied_bytes = 0

    print(f"Starting transfer for: {os.path.basename(source_path)}")
    print(f"Total Size: {total_bytes / (1024 * 1024):.2f} MB\n")

    start_time = time.time()

    # Open source in 'rb' (read binary) and destination in 'wb' (write binary)
    with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
        while True:
            # Read 64 KB chunk from source
            chunk = src.read(chunk_size)
            
            # If chunk is empty, we reached End-Of-File (EOF)
            if not chunk:
                break
            
            # Write the binary chunk to destination
            dst.write(chunk)
            
            # Update progress
            copied_bytes += len(chunk)
            progress = (copied_bytes / total_bytes) * 100
            print(f"Progress: {progress:.2f}% ({copied_bytes}/{total_bytes} bytes)", end='\r')

    elapsed_time = time.time() - start_time
    print(f"\n\nTransfer complete in {elapsed_time:.2f} seconds!")

if __name__ == "__main__":
    # Test file paths
    SOURCE_FILE = "sample_input.txt"
    DEST_FILE = "sample_output.txt"

    # Create a test file if it doesn't exist
    if not os.path.exists(SOURCE_FILE):
        with open(SOURCE_FILE, "w") as f:
            f.write("Hello World! " * 100000) # Creates a ~1.2 MB file

    copy_file_in_chunks(SOURCE_FILE, DEST_FILE)