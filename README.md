# R_Tree: Spatial Indexing and Query Processing in Python

This repository implements an **R-Tree** spatial index in Python, along with auxiliary modules for bulk loading, insertion, deletion, K-nearest neighbor (KNN) queries, range queries, and skyline queries.

---

## 📂 Project Structure

| File / Folder | Description |
|----------------|-------------|
| `Entry.py`         | Implementation of the entry objects (leaf/non-leaf nodes) |
| `Node.py`          | Node representation in the R-Tree (with children, bounding rectangle, etc.) |
| `bulkloading.py`   | Bulk loading algorithm for building a tree from many objects |
| `insert.py`         | Insertion logic for adding individual objects |
| `delete.py`         | Deletion logic for removing objects |
| `KNN.py`            | K-nearest neighbor search implementation |
| `range_query.py`    | Range query support (rectangular region queries) |
| `Skyline.py`        | Skyline query processing over spatial objects |
| `make_datafile.py`  | Utility script to generate example spatial data files |
| `make_indexfile.py` | Utility script to generate example index files |
| `datafile*.xml`     | Sample datasets in XML format |
| `indexfile*.xml`    | Sample index files for experiments |
| `map*.osm`          | Sample map / spatial data files for testing |

---

## 🔍 Features & Functionality

- Implementation of the **R-Tree** spatial index structure in Python  
- Support for **bulk loading**, **insert**, **delete**  
- Query operations:
  - **K-nearest neighbors (KNN)**  
  - **Range queries** (axis-aligned rectangle)  
  - **Skyline queries** on spatial data  
- Utility scripts for generating test data & indexes  
- Sample datasets and maps included for experimentation

---

## 🛠 Requirements

To run and test the code, you will need:

- Python 3.7 or newer  
- Standard Python libraries (no external dependencies assumed)  
- Optionally: `xml` parsers / libraries if you customize input format  
- A command-line or IDE environment to run `.py` scripts

---

## 🚀 Usage Examples

Below are sample commands / usage examples.

### Bulk load and index building
```bash
python bulkloading.py --input datafile4000.xml --output indexfile_bulk.xml
```

### Insertion
```bash
python insert.py --index indexfile_bulk.xml --object new_object.xml
```

### Deletion
```bash
python delete.py --index indexfile_bulk.xml --object object_to_remove.xml
```

### KNN querry
```bash
python KNN.py --index indexfile_bulk.xml --query q_point.xml --k 5
```

### Range querry
```bash
python range_query.py --index indexfile_bulk.xml --xmin x1 --ymin y1 --xmax x2 --ymax y2
```

### Skyline querry
```bash
python Skyline.py --index indexfile_bulk.xml --input datafile4000.xml
```

## 📊 Performance Considerations & Design Choices

- **Node capacity & split strategies:** The choice of maximum entries per node and the splitting policy directly affect tree height and query efficiency.  
- **Bounding rectangle heuristics:** Different heuristics for minimum bounding rectangles influence overlap and coverage, impacting query performance.  
- **Bulk loading:** Typically produces higher-quality trees compared to inserting objects in random order.  
- **Deletion handling:** Must manage node underflow properly, including reinsertion of orphaned entries.  
- **Query performance:** Strongly depends on pruning effectiveness using bounding rectangles.  
- **Skyline queries:** Often require advanced pruning techniques to remain efficient on large datasets.  

---

## 🧪 Testing & Validation

- Use the provided sample data files (`datafile*.xml`) and index files (`indexfile*.xml`) to validate correctness.  
- Compare the results of KNN, range, and skyline queries against a brute-force baseline (if feasible).  
- Experiment with different R-Tree parameters (e.g., node size, split policy) to observe trade-offs in performance and accuracy.  
