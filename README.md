# 👁️ Blind Assist: AI Obstacle Detection System

A streamlined computer vision solution designed to provide **situational awareness** for the visually impaired. This system transforms digital photos into high-level navigation advice by identifying obstacles, estimating their distance, and providing communicative voice feedback.

---

## 🛠️ How it Works

The system operates through a three-stage intelligent pipeline:

1.  **Object Perception (AI)**:
    - Uses the **YOLOv8** deep learning model to identify 80 different types of common objects (people, cars, chairs, stairs, etc.).
    - Every detection is instantly categorized by its pixel coordinates and confidence score.

2.  **Geometric Reasoner**:
    - **Distance Estimation**: Using a pinhole camera model, the system calculates the real-world distance to an object based on its pixel height and known average physical sizes.
    - **Spatial Mapping**: The frame is divided into a 3x3 grid (Left, Center, Right | Top, Middle, Bottom). Objects in the "Center/Center" zone are flagged as high-priority hazards.

3.  **Navigation Decision Engine**:
    - The engine analyzes the density of obstacles in your path.
    - If a hazard is directly ahead (< 2m), it automatically searches for "Safe Gaps" to your left or right and narrates the best action.

---

## � How to Run

### 1. Setup
Ensure you are in the project root and have initialized the environment:
```bash
# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execution
You can process a folder or a single image using the `analyze.py` tool.

**Analyze a Single Photo:**
```bash
python3 src/analyze.py data/samples/sample1.jpg
```

**Analyze All Samples:**
```bash
python3 src/analyze.py
```

---

## � Interpreting Results

The system provides three types of feedback for every analysis:

### 1. Audio Feedback (Communcative)
The system will speak to you in real-time:
- **Status Alerts**: "Vision system online", "Analyzing image..."
- **Direct Advice**: "Stop! Chair ahead. Move to your right."
- **Completion**: "Analysis complete. Reports saved."

### 2. Terminal Summary
A clean breakdown of detected hazards appears in your console:
```text
Detected 3 object(s):
  1. a chair at center/center, approximately 1.2m away
  2. a person at top right, approximately 5.0m away
  
Navigation Recommendation: Stop! A chair is directly in front of you. Path to your right is clear.
```

### 3. Data Reports
Comprehensive logs are automatically generated in `data/output/`:
- **`detection_results.csv`**: A spreadsheet containing coordinates, distances, and descriptions for every object found across all images.

---


