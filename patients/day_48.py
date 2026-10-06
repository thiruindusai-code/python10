import math
import cv2
import mediapipe as mp
import time
import csv


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
        math.atan2(
            wrist.y - elbow.y,
            wrist.x - elbow.x
        )
        -
        math.atan2(
            shoulder.y - elbow.y,
            shoulder.x - elbow.x
        )
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


def calculate_3d_angle(shoulder, elbow, wrist):
    vector1 = (
        shoulder.x - elbow.x,
        shoulder.y - elbow.y,
        shoulder.z - elbow.z
    )

    vector2 = (
        wrist.x - elbow.x,
        wrist.y - elbow.y,
        wrist.z - elbow.z
    )

    dot_product = (
        vector1[0] * vector2[0] +
        vector1[1] * vector2[1] +
        vector1[2] * vector2[2]
    )

    length1 = math.sqrt(
        vector1[0] ** 2 +
        vector1[1] ** 2 +
        vector1[2] ** 2
    )

    length2 = math.sqrt(
        vector2[0] ** 2 +
        vector2[1] ** 2 +
        vector2[2] ** 2
    )

    if length1 == 0 or length2 == 0:
        return 180

    cosine_angle = dot_product / (length1 * length2)

    cosine_angle = max(
        -1,
        min(1, cosine_angle)
    )

    return math.degrees(
        math.acos(cosine_angle)
    )


def calculate_distance(point1, point2):
    distance = math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2 +
        (point1.z - point2.z) ** 2
    )

    return distance


patient_name = input("Enter your name: ").strip().title()
target_reps = int(input("How many reps do you want to do?: "))

rep_count = 0
stage = None
bent_frames = 0
session_saved = False

while True:
    success, frame = camera.read()

    if not success:
        break

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp_ms = int(
        (time.monotonic() - start_time) * 1000
    )

    results = pose.detect_for_video(
        mp_image,
        timestamp_ms
    )

    if results.pose_landmarks:

        landmarks = results.pose_landmarks[0]

        world_landmarks = results.pose_world_landmarks[0]

        right_shoulder = landmarks[12]
        right_elbow = landmarks[14]
        right_wrist = landmarks[16]

        left_elbow = landmarks[13]

        world_right_shoulder = world_landmarks[12]
        world_right_elbow = world_landmarks[14]
        world_right_wrist = world_landmarks[16]

        # Check if right arm is visible
        arm_visible = (
            right_shoulder.visibility > 0.7 and
            right_elbow.visibility > 0.7 and
            right_wrist.visibility > 0.7
        )

        # Simple form check
        elbow_distance = abs(
            right_elbow.x - right_shoulder.x
        )

        if elbow_distance < 0.12:
            form = "Good form"
        else:
            form = "Keep elbow close"

        # 2D angle
        angle = calculate_angle(
            right_shoulder,
            right_elbow,
            right_wrist
        )

        # 3D angle
        angle_3d = calculate_3d_angle(
            world_right_shoulder,
            world_right_elbow,
            world_right_wrist
        )

        print(
            "3D angle:",
            int(angle_3d),
            "Visible:",
            arm_visible,
            "Bent frames:",
            bent_frames,
            "Form:",
            form
        )

        # Exercise logic
        if not arm_visible:
            status = "Show your right arm"
            feedback = "Move your arm into view"

            stage = None
            bent_frames = 0

        elif angle_3d > 150:
            status = "Arm Straight"
            feedback = "Bend your arm"

            stage = "straight"
            bent_frames = 0

        elif angle_3d < 90:
            status = "Arm Bent"

            bent_frames += 1

            if (
                bent_frames >= 2
                and stage == "straight"
                and form == "Good form"
                and rep_count < target_reps

            ):
                rep_count += 1
                stage = "bent"

            feedback = "Straighten your arm"

        else:
            status = "Moving"

            bent_frames = 0

            if stage == "straight":
                feedback = "Keep bending your arm"

            elif stage == "bent":
                feedback = "Keep straightening your arm"

            else:
                feedback = "Straighten your arm to start"

        if rep_count >= target_reps:
            feedback = "Goal reached!"

            if not session_saved:
                with open("rehab_session.csv", "a", newline="")as file:

                    fieldnames = [
                        "patient",
                        "target_reps",
                        "completed_reps"
                    ]

                    writer = csv.DictWriter(
                        file,
                        fieldnames=fieldnames
                    )

                    if file.tell() == 0:
                        writer.writeheader()

                    writer.writerow({
                        "patient": patient_name,
                        "target_reps": target_reps,
                        "completed_reps": rep_count
                    })
                session_saved = True

        height, width, _ = frame.shape

        right_elbow_x = int(
            right_elbow.x * width
        )

        right_elbow_y = int(
            right_elbow.y * height
        )

        left_elbow_x = int(
            left_elbow.x * width
        )

        left_elbow_y = int(
            left_elbow.y * height
        )

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
            f"Patient: {patient_name}",
            (30, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2


        )

        cv2.putText(
            frame,
            f"Reps: {rep_count}/{target_reps}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{int(angle_3d)} degrees",
            (
                right_elbow_x,
                right_elbow_y - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            feedback,
            (30, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            form,
            (30, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.circle(
            frame,
            (
                right_elbow_x,
                right_elbow_y
            ),
            12,
            (0, 0, 255),
            -1
        )

        cv2.circle(
            frame,
            (
                left_elbow_x,
                left_elbow_y
            ),
            12,
            (0, 255, 0),
            -1
        )

    cv2.imshow(
        "Pose detection",
        frame
    )

    if cv2.waitKey(1) == ord("q"):
        break


camera.release()

pose.close()

cv2.destroyAllWindows()
