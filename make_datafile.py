import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys


# def read_block_from_datafile(block_id, filename):
#     # Parse the datafile.xml
#     tree = ET.parse(filename)
#     root = tree.getroot()
#
#     # Find the specified block with the given block_id
#     block_to_read = None
#     for block_elem in root.findall(".//Block[@id='" + str(block_id) + "']"):
#         block_to_read = block_elem
#         break
#
#     if block_to_read is None:
#         return []  # Block with the specified block_id not found
#
#     # Extract and return the records within the block
#     records = []
#     for record_elem in block_to_read.findall(".//Record"):
#         record_id = int(record_elem.find(".//record_id").text)
#         name = record_elem.find(".//name").text
#         coordinates = record_elem.find(".//coordinates").text.split()
#         lat, lon = map(float, coordinates)
#         records.append([record_id, name, lat, lon])
#
#     return records


def read_all_blocks_from_datafile(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    # read data from block0
    block0 = None
    for block_elem in root.findall(".//Block[@id='" + str(0) + "']"):
        block0 = block_elem
        break

    # get the number of blocks from block0
    num_of_blocks = int(block0.find(".//num_of_blocks").text)

    blocks = []
    for block_id in range(1, num_of_blocks):
        block_data = read_block_from_datafile(block_id, filename)
        blocks.append(block_data)

    return blocks


def read_block_from_datafile(block_id, filename):
    # parse the datafile.xml
    tree = ET.parse(filename)
    root = tree.getroot()

    # find the block with the given block_id
    block_to_read = None
    for block_elem in root.findall(".//Block[@id='" + str(block_id) + "']"):
        block_to_read = block_elem
        break

    if block_to_read is None:
        return []  # if there is no block with the specified block_id returns empty list

    # extract and return the records within the block as [block_id, slot_in_block, lat, lon] (no name or record_id)
    records = []
    for record_elem in block_to_read.findall(".//Record"):
        block_id = int(block_to_read.get("id"))
        slot_in_block = int(record_elem.get("id"))
        coordinates = record_elem.find(".//coordinates").text.split()
        coordinates_float = list(map(float, coordinates))
        records.append([block_id, slot_in_block, *coordinates_float])

    return records


def split_data_into_blocks(data, block_size):
    blocks = []
    current_block = []
    current_block_size = 0

    for record in data:
        record_size = sys.getsizeof(record)  # find size of record
        # if the record fits in the current block append it
        if current_block_size + record_size <= block_size:
            current_block.append(record)
            current_block_size += record_size
        # else save the block and create a new one that contains the record
        else:
            blocks.append(current_block)
            current_block = [record]
            current_block_size = record_size

    # if the last block isn't empty save it
    if current_block:
        blocks.append(current_block)

    # return the list with the filled blocks
    return blocks


def save_blocks_to_xml(blocks, num_of_records, filename):
    root_elem = ET.Element("Blocks")

    # create block0 which contains the overall number of records and number of blocks in the datafile
    block0_elem = ET.SubElement(root_elem, "Block", id=str(0))
    ET.SubElement(block0_elem, "num_of_records").text = str(num_of_records)
    ET.SubElement(block0_elem, "num_of_blocks").text = str(len(blocks) + 1)  # +1 = block0

    # create Block elements
    for i, block in enumerate(blocks):
        block_elem = ET.SubElement(root_elem, "Block", id=str(i+1))

        # create Record elements in each Block element
        for j, record in enumerate(block):
            record_elem = ET.SubElement(block_elem, "Record", id=str(j))

            # create sub-elements for each field for each record element
            ET.SubElement(record_elem, "record_id").text = str(record[0])
            ET.SubElement(record_elem, "name").text = str(record[1])
            coordinates_elem = ET.SubElement(record_elem, "coordinates")
            coordinates_elem.text = " ".join(map(str, record[2:]))

    # create the ElementTree
    tree = ET.ElementTree(root_elem)

    # save it the datafile with 'utf-8' encoding
    tree.write(filename, encoding="utf-8", xml_declaration=True)

    # load the saved XML file and format it so that it's easier to read
    xml_content = minidom.parse(filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_content.toprettyxml(indent="    "))


input_file = "map.osm"
block_size = 32 * 1024  # 32KB

# parse the .osm XML file
tree = ET.parse(input_file)
root = tree.getroot()

# list to store the points only (node data)
node_data = []

# access only the "node" elements in the .osm
for element in root:
    if element.tag == "node":
        node_id = element.attrib["id"]
        latitude = element.attrib["lat"]
        longitude = element.attrib["lon"]
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in element.findall("tag")}
        name = tags.get("name", "unknown")  # get the "name" tag value or use "unknown" if it doesn't exist

        # add node data to the list
        node_data.append([node_id, name, latitude, longitude])

# split data into blocks
blocks = split_data_into_blocks(node_data, block_size)
save_blocks_to_xml(blocks, len(node_data), "datafile.xml")
blocks = read_all_blocks_from_datafile("datafile.xml")
print(blocks)
