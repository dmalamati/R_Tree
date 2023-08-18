import xml.etree.ElementTree as ET
import csv
import pandas as pd

input_file = "map.osm"
output_file = "datafile.csv"
block_size = 32 * 1024  # 32KB in bytes


# Function to calculate the size of a CSV row, including block_id
def calculate_entry_size(block_id, node_data):
    csv_row = f"{block_id}," + ",".join(node_data)
    return len(csv_row.encode("utf-8"))


# Function to write data to blocks
def write_data_to_blocks(node_data, block_size):
    current_block_id = 1  # variable that helps to take into consideration the block_id size
    current_block_size = 0  # variable to count the size of each block while filling it with data
    current_block_data = []  # list that will contain each blocks data
    blocks_data = []  # list that will contain the blocks

    for entry in node_data:
        entry_size = calculate_entry_size(current_block_id, entry)
        if current_block_size + entry_size <= block_size:  # if entry fits in the existing block
            current_block_data.append(entry)  # insert entry to current block
            current_block_size += entry_size  # update current block size
        else:
            blocks_data.append((current_block_id, current_block_data))  # if block is full insert it to blocks_data
            current_block_id += 1
            current_block_size = entry_size  # initialize new block size
            current_block_data = [entry]  # initialize new block data by inserting the entry

    if current_block_data:
        blocks_data.append((current_block_id, current_block_data))

    return blocks_data


# Parse the .osm XML file
tree = ET.parse(input_file)
root = tree.getroot()

# List to store the points only (node data)
node_data = []

# Access only the "node" elements
for element in root:
    if element.tag == "node":
        node_id = element.attrib["id"]
        latitude = element.attrib["lat"]
        longitude = element.attrib["lon"]
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in element.findall("tag")}
        name = tags.get("name", "unknown")  # Get the "name" tag value or use "unknown" if it doesn't exist

        # Add node data to the list
        node_data.append([node_id, latitude, longitude, name])


# Write data to blocks
blocks_data = write_data_to_blocks(node_data, block_size)

# Write blocks data to CSV file
with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["block_id", "id", "lat", "lon", "name"])

    # Write metadata in block0
    csv_writer.writerow([0, len(node_data), len(blocks_data), block_size])

    # Write data for each block starting from block_id = 1
    for block_id, block_data in blocks_data:
        for entry in block_data:
            csv_writer.writerow([block_id] + entry)


# Step 3: Print all the columns
data = pd.read_csv(output_file)

# Optional: Set some display options to see all the columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)

# Print the DataFrame
print(data)





#   Node = []
#   d dimentions
#   n entries per node
#
# tree =[ [<mbr,index> , , , ] -> [<point,record_id> , , ] -> [] [] ]

