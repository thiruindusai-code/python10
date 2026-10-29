import math
import cv2
import mediapipe as mp
import time
import csv
from datetime import date


# =============================
# SETTINGS / THRESHOLDS
# =============================

BICEP_STRAIGHT = 150
BICEP_BENT = 90

SHOULDER_DOWN = 20
SHOULDER_UP = 55

SHOULDER_DIFF_MAX = 15
TORSO_SHIFT_MAX = 0.020
ELBOW_STRAIGHT_MIN = 130

VISIBILITY_MIN = 0.5


# =============================
# MEDIAPIPE SETUP
# =============================

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


# =============================
# ANGLE FUNCTIONS
# =============================

def calculate_angle(point1, point2, point3):

    angle = math.degrees(
        math.atan2(
            point3.y - point2.y,
            point3.x - point2.x
        )
        -
        math.atan2(
            point1.y - point2.y,
            point1.x - point2.x
        )
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


def calculate_3d_angle(point1, point2, point3):

    vector1 = (
        point1.x - point2.x,
        point1.y - point2.y,
        point1.z - point2.z
    )

    vector2 = (
        point3.x - point2.x,
        point3.y - point2.y,
        point3.z - point2.z
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


# =============================
# SAVE SESSION
# =============================

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

    print("Saving session...")


# =============================
# PATIENT INFORMATION
# =============================

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


# =============================
# CAMERA
# =============================

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
session_start_time = time.monotonic()

session_date = date.today()

rep_count = 0
stage = None
bent_frames = 0
session_saved = False
final_time = None


# =============================
# CAMERA LOOP
# =============================

while True:

    success, frame = camera.read()

    if not success:
        break

    elapsed_time = int(
        time.monotonic()
        - session_start_time
    )

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp_ms = int(
        (
            time.monotonic()
            - start_time
        ) * 1000
    )

    results = pose.detect_for_video(
        mp_image,
        timestamp_ms
    )

    # =========================
    # POSE FOUND
    # =========================

    if results.pose_landmarks:

        landmarks = results.pose_landmarks[0]
        world = results.pose_world_landmarks[0]

        # Normal landmarks
        right_shoulder = landmarks[12]
        right_elbow = landmarks[14]
        right_wrist = landmarks[16]
        right_hip = landmarks[24]

        left_shoulder = landmarks[11]
        left_elbow = landmarks[13]
        left_wrist = landmarks[15]
        left_hip = landmarks[23]

        # World landmarks
        world_right_shoulder = world[12]
        world_right_elbow = world[14]
        world_right_wrist = world[16]

        world_left_shoulder = world[11]
        world_left_elbow = world[13]
        world_left_wrist = world[15]

        # =====================
        # VISIBILITY
        # =====================

        arm_visible = (
            right_shoulder.visibility > VISIBILITY_MIN
            and right_elbow.visibility > VISIBILITY_MIN
            and right_wrist.visibility > VISIBILITY_MIN
        )

        both_arms_visible = (
            right_shoulder.visibility > VISIBILITY_MIN
            and right_elbow.visibility > VISIBILITY_MIN
            and right_wrist.visibility > VISIBILITY_MIN
            and left_shoulder.visibility > VISIBILITY_MIN
            and left_elbow.visibility > VISIBILITY_MIN
            and left_wrist.visibility > VISIBILITY_MIN
        )

        # =====================
        # BICEP FORM
        # =====================

        elbow_distance = abs(
            right_elbow.x
            - right_shoulder.x
        )

        if elbow_distance < 0.12:
            form = "Good form"
        else:
            form = "Keep elbow close"

        # =====================
        # ANGLES
        # =====================

        angle_3d = calculate_3d_angle(
            world_right_shoulder,
            world_right_elbow,
            world_right_wrist
        )

        left_elbow_angle_3d = calculate_3d_angle(
            world_left_shoulder,
            world_left_elbow,
            world_left_wrist
        )

        shoulder_angle = calculate_angle(
            right_hip,
            right_shoulder,
            right_elbow
        )

        left_shoulder_angle = calculate_angle(
            left_hip,
            left_shoulder,
            left_elbow
        )

        # =====================
        # SHOULDER SYMMETRY
        # =====================

        shoulder_difference = abs(
            shoulder_angle
            - left_shoulder_angle
        )

        # =====================
        # TORSO LEAN
        # =====================

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

        # =====================
        # DEBUG
        # =====================

        print(
            "Shoulder:",
            int(shoulder_angle),
            "Left shoulder:",
            int(left_shoulder_angle),
            "Difference:",
            int(shoulder_difference),
            "R elbow:",
            int(angle_3d),
            "L elbow:",
            int(left_elbow_angle_3d),
            "Torso:",
            round(torso_shift, 3),
            "Stage:",
            stage
        )

        # =====================
        # VISIBILITY CHECK
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

        # =====================
        # BICEP CURL
        # =====================

        elif exercise_name == "Bicep Curl":

            if angle_3d > BICEP_STRAIGHT:

                status = "Arm Straight"
                feedback = "Bend your arm"

                stage = "straight"
                bent_frames = 0

            elif angle_3d < BICEP_BENT:

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

        # =====================
        # SHOULDER RAISE
        # =====================

        elif exercise_name == "Shoulder Raise":

            # Your real down position is about 9 degrees.
            if shoulder_angle < SHOULDER_DOWN:

                status = "Arm Down"
                feedback = "Raise your arms"

                stage = "down"

            # Your real raised position is about 65 degrees.
            elif shoulder_angle > SHOULDER_UP:

                status = "Arm Raised"

                if (
                    stage == "down"
                    and shoulder_difference <= SHOULDER_DIFF_MAX
                    and torso_shift <= TORSO_SHIFT_MAX
                    and angle_3d >= ELBOW_STRAIGHT_MIN
                    and left_elbow_angle_3d >= ELBOW_STRAIGHT_MIN
                    and rep_count < target_reps
                ):

                    rep_count += 1

                    feedback = "Good rep! Lower your arms"

                elif shoulder_difference > SHOULDER_DIFF_MAX:

                    feedback = "Raise both arms evenly"

                elif torso_shift > TORSO_SHIFT_MAX:

                    feedback = "Keep your body straight"

                elif (
                    angle_3d < ELBOW_STRAIGHT_MIN
                    or left_elbow_angle_3d < ELBOW_STRAIGHT_MIN
                ):

                    feedback = "Keep your elbows straighter"

                else:

                    feedback = "Lower your arms"

                stage = "up"

            else:

                status = "Moving"

                if stage == "down":
                    feedback = "Keep raising your arms"

                elif stage == "up":
                    feedback = "Keep lowering your arms"

                else:
                    feedback = "Lower your arms to start"

        # =====================
        # GOAL
        # =====================

        if rep_count >= target_reps:

            feedback = "Goal reached!"

            if final_time is None:
                final_time = elapsed_time

            if not session_saved:

                save_session(
                    patient_name,
                    exercise_name,
                    session_date,
                    target_reps,
                    rep_count,
                    final_time
                )

                session_saved = True

        # =====================
        # SCREEN COORDINATES
        # =====================

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

        # =====================
        # DISPLAY VALUES
        # =====================

        if exercise_name == "Bicep Curl":

            display_angle = angle_3d
            display_form = form

        else:

            display_angle = shoulder_angle

            if shoulder_difference > SHOULDER_DIFF_MAX:
                display_form = "Arms uneven"

            elif torso_shift > TORSO_SHIFT_MAX:
                display_form = "Keep body straight"

            elif (
                angle_3d < ELBOW_STRAIGHT_MIN
                or left_elbow_angle_3d < ELBOW_STRAIGHT_MIN
            ):
                display_form = "Straighten elbows"

            else:
                display_form = "Good form"

        # =====================
        # TEXT
        # =====================

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
            f"Reps: {rep_count}/{target_reps}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
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
            display_form,
            (30, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
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
            f"Exercise: {exercise_name}",
            (30, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{int(display_angle)} degrees",
            (
                right_elbow_x,
                right_elbow_y - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Elbow dots
        cv2.circle(
            frame,
            (right_elbow_x, right_elbow_y),
            12,
            (0, 0, 255),
            -1
        )

        cv2.circle(
            frame,
            (left_elbow_x, left_elbow_y),
            12,
            (0, 255, 0),
            -1
        )

    # =========================
    # SHOW CAMERA
    # =========================

    cv2.imshow(
        "Pose detection",
        frame
    )

    # =========================
    # QUIT
    # =========================

    if cv2.waitKey(1) == ord("q"):

        if not session_saved:

            save_session(
                patient_name,
                exercise_name,
                session_date,
                target_reps,
                rep_count,
                elapsed_time
            )

            session_saved = True

        break


# =============================
# CLEANUP
# =============================

camera.release()
pose.close()
cv2.destroyAllWindows()
