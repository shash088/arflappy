import cv2
import math

from hand_tracker import HandTracker
from bird_game import BirdGame


def distance(point1, point2):

    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )


cap = cv2.VideoCapture(0)

tracker = HandTracker()
game = BirdGame()

was_pinching = False


while True:

    ret, frame = cap.read()

    if not ret:
        print("Camera not found")
        break

    frame = cv2.flip(frame, 1)

    results = tracker.process(frame)

    pinching = False

    # Detect hand
    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]

        thumb = hand.landmark[4]
        index = hand.landmark[8]

        pinch_distance = distance(
            thumb,
            index
        )

        # Smaller = fingers closer
        if pinch_distance < 0.035:
            pinching = True

    # FLAP ONLY WHEN PINCH STARTS
    if pinching and not was_pinching:

        game.flap()

    was_pinching = pinching

    # Update bird and pipes
    game.update()

    # Draw game
    frame = game.draw(frame)

    # Gesture indicator
    if pinching:

        cv2.putText(
            frame,
            "FLAP!",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

    cv2.imshow(
        "AR Bird Game",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    # Q = quit
    if key == ord("q"):
        break

    # R = restart
    if key == ord("r"):
        game.restart()


cap.release()
cv2.destroyAllWindows()