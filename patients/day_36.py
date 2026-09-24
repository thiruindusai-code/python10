import cv2

camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera")
        break

    cv2.putText(
        frame,
        "Exercise Count: 3",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.rectangle(
        frame,
        (100, 100),
        (300, 300),
        (255, 0, 0),
        3
    )
    cv2.circle(
        frame,
        (400, 200),
        50,
        (0, 0, 255),
        3
    )

    cv2.line(
        frame,
        (50, 400),
        (500, 400),
        (255, 255, 0),
        4
    )
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
