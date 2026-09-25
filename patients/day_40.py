import math
import cv2
import mediapipe as mp
import time

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="pose_landmarker_lite.task"
    ),
    running_mode=RunningMode.VIDEO
)

pose = PoseLandmarker.create_from_options(options)

camera = cv2.VideoCapture(0)

start_time = time.monotonic()


def calculate_angle(shoulder, elbow, wrist):
    angle = math.degrees(
        math.atan2(wrist.y - elbow.y,
                   wrist.x - elbow.x)
        -
        math.atan2(shoulder.y - elbow.y,
                   shoulder.x - elbow.x)
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle
    return angle


rep_count = 0
stage = None
while True:
    success, frame = camera.read()

    if not success:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp_ms = int((time.monotonic() - start_time) * 1000)

    results = pose.detect_for_video(mp_image, timestamp_ms)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks[0]

        right_shoulder = landmarks[12]
        right_elbow = landmarks[14]
        right_wrist = landmarks[16]

        angle = calculate_angle(
            right_shoulder,
            right_elbow,
            right_wrist)

        if angle > 160:
            status = "Arm Straight"
            stage = "straight"
        elif angle < 70:
            status = "Arm Bent"

            if stage == "straight":
                stage = "bent"
                rep_count += 1
        else:
            status = "moving"

        print(angle)

        left_elbow = landmarks[13]

        height, width, _ = frame.shape

        right_elbow_x = int(right_elbow.x * width)
        right_elbow_y = int(right_elbow.y * height)

        left_elbow_x = int(left_elbow.x * width)
        left_elbow_y = int(left_elbow.y * height)

        cv2.putText(
            frame,
            status,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Reps: {rep_count}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{int(angle)} degrees",
            (right_elbow_x, right_elbow_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.circle(
            frame,
            (right_elbow_x, right_elbow_y),
            12,
            (0, 0, 255),
            -1)
        cv2.circle(
            frame,
            (left_elbow_x, left_elbow_y),
            12,
            (0, 255, 0),
            -1)

    cv2.imshow("Pose detection", frame)

    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
pose.close()
cv2.destroyAllWindows()
