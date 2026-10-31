import random
import cv2
import numpy as np


class BirdGame:

    def __init__(self, width=640, height=480):

        self.width = width
        self.height = height

        # =========================
        # BIRD
        # =========================

        self.bird_x = 150
        self.bird_y = height // 2
        self.bird_velocity = 0

        self.gravity = 0.55
        self.flap_strength = -9

        self.bird_size = 18

        # =========================
        # PIPES
        # =========================

        self.pipe_width = 70
        self.pipe_gap = 175

        # Faster
        self.pipe_speed = 4.5

        # Distance between pipes
        self.pipe_distance = 260

        # Multiple pipes
        self.pipes = []

        # Start with 3 pipes
        for i in range(3):

            x = width + i * self.pipe_distance

            self.pipes.append({
                "x": x,
                "gap_y": self.random_gap(),
                "passed": False
            })

        # =========================
        # SCORE
        # =========================

        self.score = 0
        self.game_over = False

        # =========================
        # MILESTONES
        # =========================

        self.milestones = [
            5,
            10,
            20,
            50,
            100,
            150,
            200,
            250,
            300
        ]

        self.celebration_timer = 0
        self.celebration_text = ""

    # ==================================================
    # RANDOM GAP
    # ==================================================

    def random_gap(self):

        return random.randint(
            70,
            self.height - self.pipe_gap - 70
        )

    # ==================================================
    # FLAP
    # ==================================================

    def flap(self):

        if not self.game_over:

            self.bird_velocity = self.flap_strength

    # ==================================================
    # CREATE NEW PIPE
    # ==================================================

    def create_new_pipe(self):

        if len(self.pipes) == 0:

            x = self.width

        else:

            last_pipe = self.pipes[-1]

            x = (
                last_pipe["x"] +
                self.pipe_distance
            )

        self.pipes.append({
            "x": x,
            "gap_y": self.random_gap(),
            "passed": False
        })

    # ==================================================
    # UPDATE
    # ==================================================

    def update(self):

        if self.game_over:
            return

        # -------------------------
        # BIRD PHYSICS
        # -------------------------

        self.bird_velocity += self.gravity

        self.bird_y += self.bird_velocity

        # -------------------------
        # MOVE PIPES
        # -------------------------

        for pipe in self.pipes:

            pipe["x"] -= self.pipe_speed

        # -------------------------
        # SCORE
        # -------------------------

        for pipe in self.pipes:

            if (
                not pipe["passed"]
                and
                pipe["x"] +
                self.pipe_width <
                self.bird_x
            ):

                pipe["passed"] = True

                self.score += 1

                self.check_milestone()

                # Gradually increase speed
                self.pipe_speed += 0.08

                # Make gap smaller
                if self.score % 5 == 0:

                    if self.pipe_gap > 120:

                        self.pipe_gap -= 4

        # -------------------------
        # REMOVE OLD PIPES
        # -------------------------

        self.pipes = [
            pipe
            for pipe in self.pipes
            if pipe["x"] > -self.pipe_width - 20
        ]

        # -------------------------
        # KEEP 3 PIPES AHEAD
        # -------------------------

        while len(self.pipes) < 3:

            self.create_new_pipe()

        # -------------------------
        # CELEBRATION
        # -------------------------

        if self.celebration_timer > 0:

            self.celebration_timer -= 1

        # -------------------------
        # COLLISION
        # -------------------------

        self.check_collision()

    # ==================================================
    # MILESTONE
    # ==================================================

    def check_milestone(self):

        if self.score in self.milestones:

            self.celebration_text = (
                str(self.score) + "!"
            )

            self.celebration_timer = 75

        elif (
            self.score > 300
            and
            self.score % 50 == 0
        ):

            self.celebration_text = (
                str(self.score) + "!"
            )

            self.celebration_timer = 75

    # ==================================================
    # COLLISION
    # ==================================================

    def check_collision(self):

        # Ceiling
        if (
            self.bird_y -
            self.bird_size <
            0
        ):

            self.game_over = True
            return

        # Ground
        if (
            self.bird_y +
            self.bird_size >
            self.height
        ):

            self.game_over = True
            return

        # Bird rectangle

        bird_left = (
            self.bird_x -
            self.bird_size
        )

        bird_right = (
            self.bird_x +
            self.bird_size
        )

        bird_top = (
            self.bird_y -
            self.bird_size
        )

        bird_bottom = (
            self.bird_y +
            self.bird_size
        )

        # Check every pipe

        for pipe in self.pipes:

            pipe_left = pipe["x"]

            pipe_right = (
                pipe["x"] +
                self.pipe_width
            )

            # Horizontal overlap

            if (
                bird_right > pipe_left
                and
                bird_left < pipe_right
            ):

                gap_top = pipe["gap_y"]

                gap_bottom = (
                    pipe["gap_y"] +
                    self.pipe_gap
                )

                # Hit top pipe

                if bird_top < gap_top:

                    self.game_over = True
                    return

                # Hit bottom pipe

                if bird_bottom > gap_bottom:

                    self.game_over = True
                    return

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self, frame):

        # =========================
        # LIGHT AR OVERLAY
        # =========================

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (
                self.width,
                self.height
            ),
            (100, 190, 255),
            -1
        )

        frame = cv2.addWeighted(
            overlay,
            0.15,
            frame,
            0.85,
            0
        )

        # =========================
        # PIPES
        # =========================

        for pipe in self.pipes:

            x = int(pipe["x"])
            gap_y = int(pipe["gap_y"])

            # Top pipe

            cv2.rectangle(
                frame,
                (x, 0),
                (
                    x + self.pipe_width,
                    gap_y
                ),
                (0, 180, 0),
                -1
            )

            # Bottom pipe

            bottom_start = (
                gap_y +
                self.pipe_gap
            )

            cv2.rectangle(
                frame,
                (x, bottom_start),
                (
                    x + self.pipe_width,
                    self.height
                ),
                (0, 180, 0),
                -1
            )

            # Top cap

            cv2.rectangle(
                frame,
                (
                    x - 6,
                    gap_y - 18
                ),
                (
                    x +
                    self.pipe_width +
                    6,
                    gap_y
                ),
                (0, 230, 0),
                -1
            )

            # Bottom cap

            cv2.rectangle(
                frame,
                (
                    x - 6,
                    bottom_start
                ),
                (
                    x +
                    self.pipe_width +
                    6,
                    bottom_start + 18
                ),
                (0, 230, 0),
                -1
            )

        # =========================
        # BIRD
        # =========================

        bird_x = self.bird_x
        bird_y = int(self.bird_y)

        # Wing animation
        wing_offset = int(
            np.sin(
                cv2.getTickCount()
                /
                cv2.getTickFrequency()
                * 12
            )
            * 4
        )

        # Body

        cv2.circle(
            frame,
            (
                bird_x,
                bird_y
            ),
            self.bird_size,
            (0, 200, 255),
            -1
        )

        # Wing

        cv2.ellipse(
            frame,
            (
                bird_x - 5,
                bird_y +
                5 +
                wing_offset
            ),
            (12, 7),
            20,
            0,
            360,
            (0, 150, 220),
            -1
        )

        # Eye

        cv2.circle(
            frame,
            (
                bird_x + 7,
                bird_y - 7
            ),
            5,
            (255, 255, 255),
            -1
        )

        cv2.circle(
            frame,
            (
                bird_x + 8,
                bird_y - 7
            ),
            2,
            (0, 0, 0),
            -1
        )

        # Beak

        points = np.array([
            [
                bird_x +
                self.bird_size,
                bird_y
            ],
            [
                bird_x +
                self.bird_size +
                12,
                bird_y + 5
            ],
            [
                bird_x +
                self.bird_size,
                bird_y + 10
            ]
        ])

        cv2.fillPoly(
            frame,
            [points],
            (0, 140, 255)
        )

        # =========================
        # SCORE
        # =========================

        cv2.putText(
            frame,
            str(self.score),
            (
                self.width // 2 - 20,
                60
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (255, 255, 255),
            4
        )

        # =========================
        # MILESTONE
        # =========================

        if self.celebration_timer > 0:

            progress = (
                75 -
                self.celebration_timer
            )

            scale = (
                1.0 +
                progress /
                100
            )

            text = self.celebration_text

            font = cv2.FONT_HERSHEY_SIMPLEX

            size = cv2.getTextSize(
                text,
                font,
                scale,
                5
            )[0]

            text_x = (
                self.width -
                size[0]
            ) // 2

            text_y = (
                self.height // 2
            )

            cv2.putText(
                frame,
                text,
                (
                    text_x,
                    text_y
                ),
                font,
                scale,
                (0, 255, 255),
                5
            )

            cv2.putText(
                frame,
                "MILESTONE!",
                (
                    190,
                    text_y + 65
                ),
                font,
                0.9,
                (255, 255, 255),
                3
            )

            # Particles

            for i in range(14):

                angle = (
                    i * 25 +
                    progress * 5
                )

                radius = (
                    70 +
                    progress
                )

                px = int(
                    self.width // 2 +
                    np.cos(
                        np.radians(angle)
                    ) *
                    radius
                )

                py = int(
                    self.height // 2 +
                    np.sin(
                        np.radians(angle)
                    ) *
                    radius
                )

                cv2.circle(
                    frame,
                    (px, py),
                    4,
                    (0, 255, 255),
                    -1
                )

        # =========================
        # GAME OVER
        # =========================

        if self.game_over:

            cv2.rectangle(
                frame,
                (80, 150),
                (560, 330),
                (0, 0, 0),
                -1
            )

            cv2.putText(
                frame,
                "GAME OVER",
                (150, 215),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.4,
                (0, 0, 255),
                4
            )

            cv2.putText(
                frame,
                f"Score: {self.score}",
                (220, 255),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press R to restart",
                (170, 295),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        return frame

    # ==================================================
    # RESTART
    # ==================================================

    def restart(self):

        self.bird_y = self.height // 2
        self.bird_velocity = 0

        self.pipe_speed = 4.5
        self.pipe_gap = 175

        self.score = 0
        self.game_over = False

        self.celebration_timer = 0
        self.celebration_text = ""

        self.pipes = []

        for i in range(3):

            x = (
                self.width +
                i * self.pipe_distance
            )

            self.pipes.append({
                "x": x,
                "gap_y": self.random_gap(),
                "passed": False
            })