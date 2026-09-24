import cv2

image = cv2.imread('test.jpg')

if image is None:
    print("Image not found")
else:
    cv2.imshow("My Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
