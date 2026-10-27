import math
import cv2
import mediapipe as mp
import time
import csv
from datetime import date


# -----------------------------
# MEDIAPIPE SETUP
# -----------------------------

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


# -----------------------------
# 2D ANGLE FUNCTION
# -----------------------------

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


# -----------------------------
# 3D ANGLE FUNCTION
# -----------------------------

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
        vector1[0] * vector2[0]
        + vector1[1] * vector2[1]
        + vector1[2] * vector2[2]
    )

    length1 = math.sqrt(
        vector1[0] ** 2
        + vector1[1] ** 2
        + vector1[2] ** 2
    )

    length2 = math.sqrt(
        vector2[0] ** 2
        + vector2[1] ** 2
        + vector2[2] ** 2
    )

    if length1 == 0 or length2 == 0:
        return 180

    cosine_angle = dot_product / (
        length1 * length2
    )

    cosine_angle = max(
        -1,
        min(1, cosine_angle)
    )

    return math.degrees(
        math.acos(cosine_angle)
    )


# -----------------------------
# DISTANCE FUNCTION
# -----------------------------

def calculate_distance(point1, point2):

    distance = math.sqrt(
        (point1.x - point2.x) ** 2
        + (point1.y - point2.y) ** 2
        + (point1.z - point2.z) ** 2
    )

    return distance


# -----------------------------
# SAVE SESSION
# -----------------------------

def save_session(
    patient_name,
    exercise_name,
    session_date,
    target_reps,
    rep_count,
    final_time
):

    if rep_count >= target_reps:
        session_status = "Completed"

    else:
        session_status = "Incomplete"

    with open(
        "rehab_history.csv",
        "a",
        newline=""
    ) as file:

        fieldnames = [
            "patient",
            "exercise",
            "date",
            "target_reps",
            "completed_reps",
            "time_seconds",
            "status"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow({
            "patient": patient_name,
            "exercise": exercise_name,
            "date": session_date,
            "target_reps": target_reps,
            "completed_reps": rep_count,
            "time_seconds": final_time,
            "status": session_status
        })

    print("Saving session....")


# -----------------------------
# PATIENT INFORMATION
# -----------------------------

patient_name = input(
    "Enter your name: "
).strip().title()

print()
print("Choose an exercise:")
print("1. Bicep Curl")
print("2. Shoulder Raise")

exercise_choice = input(
    "Enter 1 or 2: "
)


if exercise_choice == "1":
    exercise_name = "Bicep Curl"

elif exercise_choice == "2":
    exercise_name = "Shoulder Raise"

else:
    exercise_name = "Bicep Curl"


target_reps = int(
    input(
        "How many reps do you want to do?: "
    )
)

# -----------------------------
# CAMERA SETUP
# -----------------------------

camera = cv2.VideoCapture(0)

cv2.namedWindow(
    "Pose detection",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Pose detection",
    1280,
    720
)

start_time = time.monotonic()

# -----------------------------
# SESSION VARIABLES
# -----------------------------

session_date = date.today()

session_start_time = time.monotonic()

rep_count = 0

stage = None

bent_frames = 0

session_saved = False

final_time = None


# -----------------------------
# MAIN CAMERA LOOP
# -----------------------------

while True:

    success, frame = camera.read()

    elapsed_time = int(
        time.monotonic()
        - session_start_time
    )

    if not success:
        break

    # -------------------------
    # CONVERT FRAME
    # -------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # -------------------------
    # TIMESTAMP
    # -------------------------

    timestamp_ms = int(
        (
            time.monotonic()
            - start_time
        ) * 1000
    )

    # -------------------------
    # POSE DETECTION
    # -------------------------

    results = pose.detect_for_video(
        mp_image,
        timestamp_ms
    )

    if results.pose_landmarks:

        landmarks = (
            results.pose_landmarks[0]
        )

        world_landmarks = (
            results.pose_world_landmarks[0]
        )

        # ---------------------
        # RIGHT LANDMARKS
        # ---------------------

        right_shoulder = landmarks[12]
        right_elbow = landmarks[14]
        right_wrist = landmarks[16]
        right_hip = landmarks[24]

        # ---------------------
        # LEFT LANDMARKS
        # ---------------------

        left_shoulder = landmarks[11]
        left_elbow = landmarks[13]
        left_wrist = landmarks[15]
        left_hip = landmarks[23]

        # ---------------------
        # RIGHT WORLD LANDMARKS
        # ---------------------

        world_right_shoulder = (
            world_landmarks[12]
        )

        world_right_elbow = (
            world_landmarks[14]
        )

        world_right_wrist = (
            world_landmarks[16]
        )

        world_right_hip = (
            world_landmarks[24]
        )

        # ---------------------
        # LEFT WORLD LANDMARKS
        # ---------------------

        world_left_shoulder = (
            world_landmarks[11]
        )

        world_left_elbow = (
            world_landmarks[13]
        )

        world_left_wrist = (
            world_landmarks[15]
        )

        # ---------------------
        # ARM VISIBILITY
        # ---------------------

        arm_visible = (
            right_shoulder.visibility > 0.7
            and right_elbow.visibility > 0.7
            and right_wrist.visibility > 0.7
        )

        both_arms_visible = (
            right_shoulder.visibility > 0.7
            and right_elbow.visibility > 0.7
            and right_wrist.visibility > 0.7
            and left_shoulder.visibility > 0.7
            and left_elbow.visibility > 0.7
            and left_wrist.visibility > 0.7
        )

        # ---------------------
        # BICEP CURL FORM CHECK
        # ---------------------

        elbow_distance = abs(
            right_elbow.x
            - right_shoulder.x
        )

        if elbow_distance < 0.12:
            form = "Good form"

        else:
            form = "Keep elbow close"

        # ---------------------
        # RIGHT ELBOW 2D ANGLE
        # ---------------------

        angle = calculate_angle(
            right_shoulder,
            right_elbow,
            right_wrist
        )

        # ---------------------
        # RIGHT ELBOW 3D ANGLE
        # ---------------------

        angle_3d = calculate_3d_angle(
            world_right_shoulder,
            world_right_elbow,
            world_right_wrist
        )

        # ---------------------
        # LEFT ELBOW 3D ANGLE
        # ---------------------

        left_elbow_angle_3d = (
            calculate_3d_angle(
                world_left_shoulder,
                world_left_elbow,
                world_left_wrist
            )
        )

        # ---------------------
        # RIGHT SHOULDER ANGLE
        # ---------------------

        shoulder_angle = (
            calculate_angle(
                right_hip,
                right_shoulder,
                right_elbow
            )
        )

        # ---------------------
        # LEFT SHOULDER ANGLE
        # ---------------------

        left_shoulder_angle = (
            calculate_angle(
                left_hip,
                left_shoulder,
                left_elbow
            )
        )

        # ---------------------
        # SHOULDER SYMMETRY
        # ---------------------

        shoulder_difference = abs(
            shoulder_angle
            - left_shoulder_angle
        )

        # ---------------------
        # TORSO LEAN CHECK
        # ---------------------

        shoulder_center_x = (
            right_shoulder.x
            + left_shoulder.x
        ) / 2

        hip_center_x = (
            right_hip.x
            + left_hip.x
        ) / 2

        torso_shift = abs(
            shoulder_center_x
            - hip_center_x
        )

        # ---------------------
        # DEBUG PRINTS
        # ---------------------

        print(
            "Right elbow:",
            int(angle_3d),
            "Left elbow:",
            int(left_elbow_angle_3d)
        )

        print(
            "Shoulder difference:",
            int(shoulder_difference)
        )

        print(
            "Torso shift:",
            round(torso_shift, 3)
        )

        print(
            "Shoulder angle:",
            int(shoulder_angle)
        )

        # =====================
        # EXERCISE LOGIC
        # =====================

        if (
            exercise_name == "Bicep Curl"
            and not arm_visible
        ):

            status = "Show your right arm"
            feedback = "Move your right arm into view"

            stage = None
            bent_frames = 0

        elif (
            exercise_name == "Shoulder Raise"
            and not both_arms_visible
        ):

            status = "Show both arms"
            feedback = "Move both arms into view"

            stage = None
            bent_frames = 0

        # =====================
        # BICEP CURL
        # =====================

        elif exercise_name == "Bicep Curl":

            if angle_3d > 150:

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

                feedback = (
                    "Straighten your arm"
                )

            else:

                status = "Moving"

                bent_frames = 0

                if stage == "straight":

                    feedback = (
                        "Keep bending your arm"
                    )

                elif stage == "bent":

                    feedback = (
                        "Keep straightening your arm"
                    )

                else:

                    feedback = (
                        "Straighten your arm to start"
                    )

        # =====================
        # SHOULDER RAISE
        # =====================

        elif exercise_name == "Shoulder Raise":

            # ARM DOWN

            if shoulder_angle < 25:

                status = "Arm Down"

                feedback = "Raise your arm"

                stage = "down"

            # ARM RAISED

            elif shoulder_angle > 65:

                status = "Arm Raised"

                feedback = "Lower your arm"

                # -----------------
                # VALID REP
                # -----------------

                if (
                    stage == "down"
                    and shoulder_difference <= 12
                    and torso_shift <= 0.015
                    and angle_3d >= 145
                    and left_elbow_angle_3d >= 145
                    and rep_count < target_reps
                ):

                    rep_count += 1

                # -----------------
                # UNEVEN ARMS
                # -----------------

                elif shoulder_difference > 12:

                    feedback = (
                        "Raise both arms evenly"
                    )

                # -----------------
                # BODY LEAN
                # -----------------

                elif torso_shift > 0.015:

                    feedback = (
                        "Keep your body straight"
                    )

                # -----------------
                # ELBOWS TOO BENT
                # -----------------

                elif (
                    angle_3d < 145
                    or left_elbow_angle_3d < 145
                ):

                    feedback = (
                        "Keep your elbows straighter"
                    )

                stage = "up"

            # ---------------------
            # ARM BETWEEN DOWN/UP
            # ---------------------

            else:

                status = "Moving"

                if stage == "down":

                    feedback = (
                        "Keep raising your arm"
                    )

                elif stage == "up":

                    feedback = (
                        "Keep lowering your arm"
                    )

                else:

                    feedback = (
                        "Lower your arm to start"
                    )

        # =====================
        # GOAL REACHED
        # =====================

        if rep_count >= target_reps:

            feedback = "Goal reached"
