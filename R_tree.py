import csv
import pandas as pd

input_file = "datafile.csv"


# Function to read data from a specific block
def read_block_data(csv_reader, block_id):
    block_data = []

    for row in csv_reader:
        row_block_id = int(row[0])
        if row_block_id == block_id:
            # block_data.append(row[1:])  # Exclude the block_id from the data
            block_data.append(row)
        elif row_block_id > block_id:
            break  # Stop reading when the next block is reached

    return block_data


# Read data from the CSV file
with open(input_file, "r", newline="", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file)

    # Skip the header row
    next(csv_reader)

    # Read and store the metadata from the second row aka first block
    metadata = next(csv_reader)

    # Save the metadata
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
        columns = ["block_id", "id", "lat", "lon", "name"]
        df = pd.DataFrame(block_data, columns=columns)

        print(f"Block {block_id}:")
        print(df)
        # print(block_data)

        print("\n")  # Separate blocks with an empty line
