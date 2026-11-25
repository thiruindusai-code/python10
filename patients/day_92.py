import math
import os
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

# Camera/tracking tolerances
# These are NOT medical limits
SHOULDER_DOWN = 30
SHOULDER_DIFF_MAX = 40
TORSO_SHIFT_MAX = 0.15
ELBOW_STRAIGHT_MIN = 105
VISIBILITY_MIN = 0.4


# =============================
# MEDIAPIPE SETUP
# =============================

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "pose_landmarker_lite.task",
        )
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
    final_time,
    shoulder_target,
    shoulder_max,
    rejected_reps
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
            "status",
            "shoulder_target",
            "shoulder_max",
            "rejected_reps"
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
            "status": session_status,
            "shoulder_target": shoulder_target,
            "shoulder_max": shoulder_max,
            "rejected_reps": rejected_reps
        })
    print("Saving session...")


def show_patient_history(patient_name):

    if not os.path.exists("rehab_history.csv"):
        print("No previous sessions found.")
        return

    with open(
        "rehab_history.csv",
        "r",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        sessions = [
            row for row in reader
            if row.get("patient", "").strip().lower()
            == patient_name.strip().lower()
        ]

    if not sessions:
        print("No previous sessions found.")
        return

    print()
    print("Recent sessions:")

    for row in sessions[-3:]:

        print(
            f"{row.get('date', '?')} | "
            f"{row.get('exercise', '?')} | "
            f"{row.get('completed_reps', '0')}/"
            f"{row.get('target_reps', '0')} reps | "
            f"{row.get('status', '?')}"
        )

    print()


# =============================
# PATIENT INFORMATION
# =============================

while True:

    patient_name = input(
        "Enter your name: "
    ).strip().title()

    if patient_name:
        break

    print("Patient name cannot be empty.")

show_patient_history(patient_name)

print("Choose an exercise:")
print("1. Bicep Curl")
print("2. Shoulder Raise")

while True:

    exercise_choice = input("Enter 1 or 2:")

    if exercise_choice == "1":

        exercise_name = "Bicep Curl"
        break

    elif exercise_choice == "2":

        exercise_name = "Shoulder Raise"
        break

    else:
        print("Invalid choice. Please enter 1 or 2.")
# =============================
# TARGET REPS
# DAY 77
# =============================

while True:

    try:

        target_reps = int(
            input(
                "How many reps do you want to do?: "
            )
        )

        if target_reps > 0:
            break

        print("Please enter at least 1 rep.")

    except ValueError:

        print("Please enter a whole number only.")

# =============================
# PATIENT SHOULDER SETTINGS
# DAY 73 + 74 + 76
# =============================
shoulder_target = ""
shoulder_max = ""
if exercise_name == "Shoulder Raise":

    while True:

        try:

            SHOULDER_UP = float(
                input(
                    "Enter therapist-approved target shoulder angle: "
                )
            )

            SHOULDER_MAX_ALLOWED = float(
                input(
                    "Enter therapist-approved maximum shoulder angle: "
                )
            )

        except ValueError:

            print()
            print("Please enter numbers only.")
            print()

            continue

        if (
            SHOULDER_UP > SHOULDER_DOWN
            and SHOULDER_MAX_ALLOWED > 0
            and SHOULDER_UP < SHOULDER_MAX_ALLOWED
            and SHOULDER_MAX_ALLOWED <= 180
        ):

            break

        print()
        print("Invalid shoulder settings.")
        print(f"Target must be above {SHOULDER_DOWN} degrees.")
        print("Maximum must be greater than target.")
        print("Maximum cannot be above 180 degrees.")
        print()
    shoulder_target = SHOULDER_UP
    shoulder_max = SHOULDER_MAX_ALLOWED

# =============================
# CAMERA
# =============================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("Error: Could not open webcam.")

    pose.close()

    raise SystemExit

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

exercise_start_time = None

session_date = date.today()

rep_count = 0

stage = None

bent_frames = 0

session_saved = False

final_time = None

raised_frames = 0

shoulder_rep_invalid = False

rejected_reps = 0

# =============================
# CAMERA LOOP
# =============================

while True:

    success, frame = camera.read()

    if not success:
        break

    # =========================
    # TIMER
    # =========================

    if exercise_start_time is None:

        elapsed_time = 0.0

    else:

        elapsed_time = (
            time.monotonic()
            - exercise_start_time
        )

    # =========================
    # FRAME CONVERSION
    # =========================

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

    if (
        results.pose_landmarks
        and results.pose_world_landmarks
    ):

        landmarks = results.pose_landmarks[0]

        world = results.pose_world_landmarks[0]

        # =====================
        # NORMAL LANDMARKS
        # =====================

        right_shoulder = landmarks[12]

        right_elbow = landmarks[14]

        right_wrist = landmarks[16]

        right_hip = landmarks[24]

        left_shoulder = landmarks[11]

        left_elbow = landmarks[13]

        left_wrist = landmarks[15]

        left_hip = landmarks[23]

        # =====================
        # WORLD LANDMARKS
        # =====================

        world_right_shoulder = world[12]

        world_right_elbow = world[14]

        world_right_wrist = world[16]

        world_left_shoulder = world[11]

        world_left_elbow = world[13]

        world_left_wrist = world[15]

        world_right_hip = world[24]

        world_left_hip = world[23]

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
        # ELBOW ANGLES
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

        # =====================
        # SHOULDER 2D ANGLES
        # DEBUG ONLY
        # =====================

        right_shoulder_angle_2d = calculate_angle(

            right_hip,

            right_shoulder,

            right_elbow

        )

        left_shoulder_angle_2d = calculate_angle(

            left_hip,

            left_shoulder,

            left_elbow

        )

        # =====================
        # SHOULDER 3D ANGLES
        # ACTUAL SHOULDER LOGIC
        # =====================

        shoulder_angle = calculate_3d_angle(

            world_right_hip,

            world_right_shoulder,

            world_right_elbow

        )

        left_shoulder_angle = calculate_3d_angle(

            world_left_hip,

            world_left_shoulder,

            world_left_elbow

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

            "R shoulder 3D:",
            int(shoulder_angle),

            "L shoulder 3D:",
            int(left_shoulder_angle),

            "R shoulder 2D:",
            int(right_shoulder_angle_2d),

            "L shoulder 2D:",
            int(left_shoulder_angle_2d),

            "Difference:",
            int(shoulder_difference),

            "R elbow:",
            int(angle_3d),

            "L elbow:",
            int(left_elbow_angle_3d),

            "Torso:",
            round(torso_shift, 3),

            "Stage:",
            stage,

            "Raised frames:",
            raised_frames,

            "Invalid:",
            shoulder_rep_invalid

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

            raised_frames = 0

            shoulder_rep_invalid = True

        # =====================
        # BICEP CURL
        # =====================

        elif exercise_name == "Bicep Curl":

            # ARM STRAIGHT

            if angle_3d > BICEP_STRAIGHT:

                status = "Arm Straight"

                feedback = "Bend your arm"

                stage = "straight"

                bent_frames = 0

            # ARM BENT

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

                    if (

                        rep_count == 1

                        and exercise_start_time is None

                    ):

                        exercise_start_time = time.monotonic()

                    stage = "bent"

                feedback = "Straighten your arm"

            # ARM MOVING

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

            # =====================
            # TOO HIGH
            # =====================

            if (

                max(
                    shoulder_angle,
                    left_shoulder_angle
                )

                > SHOULDER_MAX_ALLOWED

            ):

                status = "Too High"

                feedback = (
                    "Lower your arms - rep will not count"
                )

                shoulder_rep_invalid = True

                raised_frames = 0

            # =====================
            # ARMS DOWN
            # =====================

            elif (

                shoulder_angle < SHOULDER_DOWN

                and left_shoulder_angle < SHOULDER_DOWN

            ):

                status = "Arm Down"

                # COMPLETE VALID REP

                if (

                    stage == "up"

                    and not shoulder_rep_invalid

                    and rep_count < target_reps

                ):

                    rep_count += 1

                    # Start timer after first
                    # completed valid rep

                    if (

                        rep_count == 1

                        and exercise_start_time is None

                    ):

                        exercise_start_time = time.monotonic()

                    feedback = (
                        "Good rep! Raise your arms"
                    )

                # INVALID REP

                elif shoulder_rep_invalid:

                    rejected_reps += 1

                    feedback = (
                        "Rep rejected. Raise again"
                    )

                else:

                    feedback = "Raise your arms"

                stage = "down"

                raised_frames = 0

                shoulder_rep_invalid = False

            # =====================
            # ARMS RAISED
            # =====================

            elif (

                shoulder_angle > SHOULDER_UP

                and left_shoulder_angle > SHOULDER_UP

            ):

                status = "Arm Raised"

                if (

                    stage == "down"

                    and not shoulder_rep_invalid

                    and shoulder_difference
                    <= SHOULDER_DIFF_MAX

                    and torso_shift
                    <= TORSO_SHIFT_MAX

                    and angle_3d
                    >= ELBOW_STRAIGHT_MIN

                    and left_elbow_angle_3d
                    >= ELBOW_STRAIGHT_MIN

                    and rep_count < target_reps

                ):

                    raised_frames += 1

                    feedback = "Hold your arms up"

                    if raised_frames >= 2:

                        stage = "up"

                        raised_frames = 0

                        feedback = (
                            "Good height! Lower your arms"
                        )

                elif (

                    shoulder_difference
                    > SHOULDER_DIFF_MAX

                ):

                    raised_frames = 0

                    feedback = (
                        "Raise both arms evenly"
                    )

                elif (

                    torso_shift
                    > TORSO_SHIFT_MAX

                ):

                    raised_frames = 0

                    feedback = (
                        "Keep your body straight"
                    )

                elif (

                    angle_3d < ELBOW_STRAIGHT_MIN

                    or left_elbow_angle_3d
                    < ELBOW_STRAIGHT_MIN

                ):

                    raised_frames = 0

                    feedback = (
                        "Keep your elbows straighter"
                    )

                elif stage == "up":

                    raised_frames = 0

                    feedback = "Lower your arms"

                else:

                    raised_frames = 0

                    feedback = (
                        "Hold steady and keep good form"
                    )

            # =====================
            # ARM MOVING
            # =====================

            else:

                status = "Moving"

                raised_frames = 0

                if shoulder_rep_invalid:

                    feedback = (
                        "Lower both arms to restart"
                    )

                elif stage == "down":

                    if (

                        shoulder_difference
                        > SHOULDER_DIFF_MAX

                    ):

                        feedback = (
                            "Raise both arms evenly"
                        )

                    else:

                        feedback = (
                            "Keep raising your arms"
                        )

                elif stage == "up":

                    feedback = (
                        "Keep lowering your arms"
                    )

                else:

                    feedback = (
                        "Lower both arms to start"
                    )

        # =====================
        # GOAL
        # =====================

        if rep_count >= target_reps:

            feedback = "Goal reached!"

            if final_time is None:

                final_time = int(

                    time.monotonic()

                    - exercise_start_time

                )

            if not session_saved:

                save_session(
                    patient_name,
                    exercise_name,
                    session_date,
                    target_reps,
                    rep_count,
                    final_time,
                    shoulder_target,
                    shoulder_max,
                    rejected_reps

                )
                session_saved = True

        # =====================
        # SCREEN COORDINATES
        # =====================

        height, width, _ = frame.shape

        progress_percent = min(

            100,

            (
                rep_count
                / target_reps
            ) * 100

        )

        bar_x = 30

        bar_y = 340

        bar_width = 300

        bar_height = 25

        filled_width = int(

            bar_width

            * progress_percent

            / 100

        )

        right_elbow_x = int(

            right_elbow.x

            * width

        )

        right_elbow_y = int(

            right_elbow.y

            * height

        )

        left_elbow_x = int(

            left_elbow.x

            * width

        )

        left_elbow_y = int(

            left_elbow.y

            * height

        )

        # =====================
        # DISPLAY VALUES
        # =====================

        if exercise_name == "Bicep Curl":

            display_angle = angle_3d

            display_form = form

        else:

            display_angle = (

                shoulder_angle

                + left_shoulder_angle

            ) / 2

            if (

                max(
                    shoulder_angle,
                    left_shoulder_angle
                )

                > SHOULDER_MAX_ALLOWED

            ):

                display_form = "Arms too high"

            elif (

                shoulder_difference
                > SHOULDER_DIFF_MAX

            ):

                display_form = "Arms uneven"

            elif (

                torso_shift
                > TORSO_SHIFT_MAX

            ):

                display_form = "Keep body straight"

            elif (

                angle_3d < ELBOW_STRAIGHT_MIN

                or left_elbow_angle_3d
                < ELBOW_STRAIGHT_MIN

            ):

                display_form = "Straighten elbows"

            else:

                display_form = "Good form"

        # =====================
        # PROGRESS BAR
        # =====================

        cv2.rectangle(

            frame,

            (
                bar_x,
                bar_y
            ),

            (
                bar_x + filled_width,
                bar_y + bar_height
            ),

            (0, 255, 0),

            -1

        )

        cv2.rectangle(

            frame,

            (
                bar_x,
                bar_y
            ),

            (
                bar_x + bar_width,
                bar_y + bar_height
            ),

            (255, 255, 255),

            2

        )

        cv2.putText(

            frame,

            f"Progress: {int(progress_percent)}%",

            (30, 390),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 255, 255),

            2

        )

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

        # =====================
        # TIMER DISPLAY
        # =====================

        if final_time is not None:

            display_time = final_time

        else:

            display_time = elapsed_time

        cv2.putText(

            frame,

            f"Time: {display_time:.1f} sec",

            (30, 430),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 255, 255),

            2

        )
        if exercise_name == "Shoulder Raise":

            cv2.putText(
                frame,
                f"Target: {int(SHOULDER_UP)} deg | Max: {int(SHOULDER_MAX_ALLOWED)} deg",
                (30, 480),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Right shoulder: {int(shoulder_angle)} deg",
                (400, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Left shoulder: {int(left_shoulder_angle)} deg",
                (400, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Difference: {int(shoulder_difference)} deg",
                (400, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            if shoulder_difference > SHOULDER_DIFF_MAX:

                if shoulder_angle < left_shoulder_angle:
                    balance_text = "Raise right arm more"
                else:
                    balance_text = "Raise left arm more"

            else:
                balance_text = "Arms balanced"

            cv2.putText(
                frame,
                balance_text,
                (400, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Rejected reps: {rejected_reps}",
                (400, 210),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
        # =====================
        # ANGLE DISPLAY
        # =====================

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
        if final_time is not None:

            cv2.putText(
                frame,
                "SESSION COMPLETE",
                (30, 540),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"{rep_count}/{target_reps} reps | Time: {final_time} sec",
                (30, 580),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )
            if exercise_name == "Shoulder Raise":
                total_attempts = rep_count + rejected_reps

                if total_attempts > 0:
                    valid_rep_rate = (
                        rep_count / total_attempts
                    ) * 100
                else:
                    valid_rep_rate = 0

                cv2.putText(
                    frame,
                    f"Valid rep rate: {valid_rep_rate:.0f}% | Rejected: {rejected_reps}",
                    (30, 620),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
        # =====================
        # ELBOW DOTS
        # =====================

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

    else:

        cv2.putText(
            frame,
            "Move into camera view",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Make sure your upper body is visible",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
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
                elapsed_time,
                shoulder_target,
                shoulder_max,
                rejected_reps
            )

            session_saved = True

        break


# =============================
# CLEANUP
# =============================

camera.release()

pose.close()

cv2.destroyAllWindows()
