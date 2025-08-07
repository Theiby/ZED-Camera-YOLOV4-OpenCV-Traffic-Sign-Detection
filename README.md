# Real-Time Traffic Sign Detection with ZED Camera, YOLOv4, and OpenCV

This project aims to detect and classify traffic signs in real-time and measure the distance to them using a ZED stereo camera. The project combines the **YOLOv4-tiny** object detection model with the **OpenCV** library, leveraging the depth perception capabilities of the ZED camera.



## 📝 Project Goal and Capabilities

The main objectives of this project are:

* **Real-Time Detection:** Instantly detect traffic signs from the video stream of a ZED camera.
* **Depth and Distance Measurement:** Calculate the distance from the camera to each detected traffic sign in centimeters using the ZED camera's stereo vision capabilities.
* **High Performance:** Achieve smooth and fluid detection by using the fast and efficient **YOLOv4-tiny** model.
* **Modular Design:** Provide a modular structure that can be easily adapted to detect different objects and integrated into various platforms.

## 🛠️ Technologies and Libraries Used

* **Camera:** ZED Stereo Camera
* **Object Detection Model:** `YOLOv4-tiny` (with custom `yolov4-tiny-custom.cfg` and `yolov4-tiny-custom_last.weights` files)
* **Programming Language:** Python 3
* **Core Libraries:**
    * `OpenCV`: For image processing and running the YOLO model.
    * `ZED Python API (pyzed)`: For acquiring image and depth data from the ZED camera.
    * `NumPy`: For data manipulation and mathematical operations.

## ⚙️ How the Project Works

The project follows a pipeline consisting of several key steps:

1.  **Camera Initialization and Configuration:**
    * A ZED camera object is created and configured with parameters such as `HD1080` resolution and `30 FPS`.
    * RGB image, depth map, and point cloud data are retrieved from the camera.

2.  **Loading the YOLOv4 Model:**
    * The pre-trained custom YOLOv4-tiny model's configuration (`.cfg`) and weight (`.weights`) files are loaded using the `cv2.dnn.readNetFromDarknet` function.
    * The `obj.names` file, which contains the class labels for the objects to be detected, is read.

3.  **Real-Time Detection Loop:**
    * A new frame is continuously captured from the ZED camera inside a `while` loop.
    * Each captured frame is converted into a `blob` format that the YOLO model can process. During this step, the image is normalized by `1/255.0` and resized to `(416, 416)`.
    * The `blob` is set as the input to the network, and object detection is performed via a forward pass.

4.  **Processing Detection Results:**
    * The outputs from the network's final layers (containing class probabilities and bounding box coordinates) are scanned.
    * Detections with a probability higher than a predefined confidence threshold (`probability_minimum = 0.5`) are considered valid.
    * **Non-Maximum Suppression (NMS)** is applied to eliminate overlapping and redundant bounding boxes.

5.  **Distance Calculation and Visualization:**
    * For each valid detection, the center coordinates (`x_center`, `y_center`) of its bounding box are used.
    * These coordinates are used to look up the object's 3D position in space from the ZED camera's point cloud data (`point_cloud`).
    * The **true distance** to the object is calculated using the Pythagorean theorem (`sqrt(x² + y² + z²)`) and printed to the console.
    * The final results are visualized by drawing bounding boxes around the detected objects and overlaying the class label and confidence score on the output frame.

## 🚀 How to Run the Project

1.  **Prerequisites:**
    * ZED SDK and its Python API must be installed.
    * The required Python libraries must be installed:
        ```bash
        pip install opencv-python numpy
        ```

2.  **File Structure:**
    * Create a folder named `detector` in the same directory where you run the project script.
    * Place the `yolov4-tiny-custom.cfg`, `yolov4-tiny-custom_last.weights`, and `obj.names` files inside this `detector` folder.

3.  **Execution:**
    * Make sure your ZED camera is connected to your computer.
    * Run the Python script with the following command:
        ```bash
        python your_script_name.py
        ```

Once the project is running, a window will open showing the live feed from the ZED camera with detected traffic signs. Simultaneously, the distance information for each detected object will be displayed in the terminal.
