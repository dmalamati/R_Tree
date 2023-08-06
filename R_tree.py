import csv
import pandas as pd

input_file = "datafile.csv"


# Function to read data from a specific block
def read_block_data(csv_reader, block_id):
    block_data = []

    slot = 0  # Initialize slot for each block
    for row in csv_reader:
        row_block_id = int(row[0])
        if row_block_id == block_id:
            block_data.append([block_id, slot, row[2], row[3]])  # Include block_id, slot, lat, lon
            slot += 1  # Increment slot for each record in the block
        elif row_block_id > block_id:
            break  # Stop reading when the next block is reached

    return block_data


# main ------------------------------------------------------------------------------

# Read data from the CSV file
with open(input_file, "r", newline="", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file)

    # Skip the header row
    next(csv_reader)

    # Read and store the metadata from the second row
    metadata = next(csv_reader)

    # Parse metadata
    total_entries = int(metadata[1])
    total_blocks = int(metadata[2])
    block_size = int(metadata[3])

    # Read and process each data block
    for block_id in range(1, total_blocks + 1):
        csv_file.seek(0)  # Reset the reader position to the beginning
        next(csv_reader)  # Skip the header row
        next(csv_reader)  # Skip the metadata row

        block_data = read_block_data(csv_reader, block_id)

        # Create a DataFrame for the block data
        columns = ["block_id", "slot", "lat", "lon"]
        df = pd.DataFrame(block_data, columns=columns)

        print(f"Block {block_id}:")
        print(df)
        # print(block_data)

        print("\n")  # Separate blocks with an empty line


