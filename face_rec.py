import os
import cv2
import mediapipe as mp
import face_recognition
import threading

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

# Set up the webcam
cap = cv2.VideoCapture(0)

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
        min_detection_confidence=0.5
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
