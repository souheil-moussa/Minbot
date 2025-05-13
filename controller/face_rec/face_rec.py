import os
import csv
import sys
import cv2
import mediapipe as mp
import face_recognition
import threading
import subprocess
import shlex



def update_csv_value(csv_file_path, search_name):
    """
    Read a CSV file with two columns (name and 0/1 value),
    find the row where name matches search_name,
    and change the value from 0 to 1 if found.
    
    Args:
        csv_file_path (str): Path to the input CSV file
        search_name (str): Name to search for in the first column
        output_file_path (str, optional): Path to save the updated CSV. 
                                          If None, overwrites the input file.
    
    Returns:
        bool: True if a match was found and updated, False otherwise
    """
    output_file_path = csv_file_path
    
    # Read the CSV file
    rows = []
    match_found = False
    
    try:
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:  # Ensure row has at least 2 columns
                    if row[0].strip().lower() == search_name.strip().lower() and row[1] == '0':
                        # Match found and value is 0, update to 1
                        rows.append([row[0], '1'])
                        match_found = True
                        print(f"Match found for '{search_name}'. Value updated from 0 to 1.")
                    else:
                        # No match or value already 1, keep the original row
                        rows.append(row)
                else:
                    # Handle rows with insufficient columns
                    rows.append(row)
                    print(f"Warning: Row does not have enough columns: {row}")
    
        # Write the updated data back to CSV
        with open(output_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
        
        if not match_found:
            print(f"No match found for '{search_name}' with value 0.")
        
        return match_found
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False



# Define the output file and recording duration
output_file = "output.mp4"

# Specify the directory containing known images
KNOWN_FACES_DIR = "./faces_dataset"

# Initialize lists to store known face encodings and names
known_face_encodings = []
known_face_names = []

# Load known faces from the directory
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith((".jpg", ".jpeg", ".png")):  # Check for image files
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)

        # Extract encodings (skip image if encoding fails)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(
                os.path.splitext(filename)[0]
            )  # Use filename as the name

# Initialize MediaPipe Face Detection and Drawing tools
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(output_file)
#cap = cv2.VideoCapture(0)
# Initialize variables for threading
frame_lock = threading.Lock()
frame_to_process = None


def process_frame(frame):
    """Process the video frame for face detection and recognition."""
    global frame_to_process
    with frame_lock:
        frame_to_process = frame.copy()


def main():
    # Initialize Face Detection
    with mp_face_detection.FaceDetection(
        min_detection_confidence=0.8
    ) as face_detection:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Ignoring empty camera frame.")
                continue

            # Reduce frame size for faster processing
            frame = cv2.resize(frame, (640, 480))

            # Start a new thread to process the frame
            process_thread = threading.Thread(target=process_frame, args=(frame,))
            process_thread.start()

            # Wait for processing to finish
            process_thread.join()

            if frame_to_process is not None:
                # Convert the image from BGR to RGB
                image_rgb = cv2.cvtColor(frame_to_process, cv2.COLOR_BGR2RGB)

                # Perform face detection
                results = face_detection.process(image_rgb)

                # Convert the image back to BGR for OpenCV
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                # Process detections for face recognition
                if results.detections:
                    face_locations = []
                    for detection in results.detections:
                        # Extract bounding box and convert to face_recognition format
                        bboxC = detection.location_data.relative_bounding_box
                        h, w, _ = frame.shape
                        x1 = int(bboxC.xmin * w)
                        y1 = int(bboxC.ymin * h)
                        x2 = int((bboxC.xmin + bboxC.width) * w)
                        y2 = int((bboxC.ymin + bboxC.height) * h)

                        # Append face location in top, right, bottom, left format
                        face_locations.append((y1, x2, y2, x1))

                    # Get encodings for detected faces
                    face_encodings = face_recognition.face_encodings(
                        image_rgb, face_locations
                    )

                    for face_encoding, (top, right, bottom, left) in zip(
                        face_encodings, face_locations
                    ):
                        # Compare with known faces
                        matches = face_recognition.compare_faces(
                            known_face_encodings, face_encoding
                        )
                        name = "Unknown"

                        # Use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(
                            known_face_encodings, face_encoding
                        )
                        best_match_index = face_distances.argmin() if matches else None

                        if best_match_index is not None and matches[best_match_index]:
                            name = known_face_names[best_match_index]
                            update_csv_value("at.csv",name)

                        # Draw the bounding box and label
                        cv2.rectangle(
                            image_bgr, (left, top), (right, bottom), (0, 255, 0), 2
                        )
                        cv2.putText(
                            image_bgr,
                            name,
                            (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.75,
                            (0, 255, 0),
                            2,
                        )

                # Display the output
                cv2.imshow("Face Recognition", image_bgr)

            # Break loop on 'q' key press
            if cv2.waitKey(5) & 0xFF == ord("q"):
                break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
