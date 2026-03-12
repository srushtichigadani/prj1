import json
import itertools
import random
import uuid
from typing import Dict, List, Set, Tuple

import cv2
import numpy as np

from app.core.config import CAPTCHA_VIDEO_DIR

SESSIONS: Dict[str, List[str]] = {}
USED_CONFIGS: Set[tuple] = set()


def generate_captcha_video_and_qa() -> Tuple[str, List[dict], List[str], str]:
    width, height = 640, 360
    fps = 24
    duration = random.randint(4, 5)
    total_frames = fps * duration

    session_id = str(uuid.uuid4())
    video_filename = CAPTCHA_VIDEO_DIR / f"captcha_{session_id}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    video = cv2.VideoWriter(str(video_filename), fourcc, fps, (width, height))

    shape_list = [
        "circle",
        "square",
        "triangle",
        "star",
        "pentagon",
        "hexagon",
        "diamond",
        "cross",
        "arrow",
        "ellipse",
    ]

    colors = [
        (0, 0, 255),
        (255, 0, 0),
        (0, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
        (0, 165, 255),
    ]
    color_names = ["red", "blue", "green", "yellow", "purple", "orange"]

    movements = [
        "left_right",
        "right_left",
        "diagonal",
        "zigzag",
        "circle",
        "bounce",
    ]

    sizes = [20, 40, 60]

    # Keep picking random attributes until we find a configuration
    # that has not been used before in this process.
    while True:
        shape_combo = random.sample(shape_list, 3)

        color_indices = [random.randint(0, 5) for _ in range(3)]
        color_combo = [colors[i] for i in color_indices]
        color_name_combo = [color_names[i] for i in color_indices]

        movement_combo = [random.choice(movements) for _ in range(3)]

        numbers = [str(random.randint(0, 9)) for _ in range(3)]
        size_combo = [random.choice(sizes) for _ in range(3)]

        timing = list(itertools.permutations([0, fps * 1, fps * 2], 3))
        start_frames = random.choice(timing)

        config_signature = (
            tuple(shape_combo),
            tuple(color_name_combo),
            tuple(movement_combo),
            tuple(numbers),
            tuple(size_combo),
            tuple(start_frames),
        )

        if config_signature not in USED_CONFIGS:
            USED_CONFIGS.add(config_signature)
            break

    def draw_shape(frame, shape, x, y, size, color):
        if shape == "circle":
            cv2.circle(frame, (x, y), size, color, -1)
        elif shape == "square":
            cv2.rectangle(frame, (x - size, y - size), (x + size, y + size), color, -1)
        elif shape == "triangle":
            pts = np.array([[x, y - size], [x - size, y + size], [x + size, y + size]])
            cv2.fillPoly(frame, [pts], color)
        elif shape == "star":
            pts = np.array(
                [
                    [x, y - size],
                    [x + size // 2, y - size // 3],
                    [x + size, y - size // 3],
                    [x + size // 3, y + size // 6],
                    [x + size // 2, y + size],
                    [x, y + size // 3],
                    [x - size // 2, y + size],
                    [x - size // 3, y + size // 6],
                    [x - size, y - size // 3],
                    [x - size // 2, y - size // 3],
                ]
            )
            cv2.fillPoly(frame, [pts], color)
        else:
            cv2.circle(frame, (x, y), size, color, -1)

    objects = []
    for i in range(3):
        obj = {
            "shape": shape_combo[i],
            "color": color_combo[i],
            "color_name": color_name_combo[i],
            "movement": movement_combo[i],
            "number": numbers[i],
            "size": size_combo[i],
            "start": start_frames[i],
        }
        objects.append(obj)

    for frame_no in range(total_frames):
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255

        for obj in objects:
            if frame_no >= obj["start"]:
                t = frame_no - obj["start"]

                if obj["movement"] == "left_right":
                    x = (t * 6) % width
                    y = height // 2
                elif obj["movement"] == "right_left":
                    x = width - (t * 6) % width
                    y = height // 2
                elif obj["movement"] == "diagonal":
                    x = (t * 5) % width
                    y = (t * 3) % height
                elif obj["movement"] == "zigzag":
                    x = (t * 6) % width
                    y = int(abs(np.sin(t / 5)) * height)
                elif obj["movement"] == "circle":
                    x = int(width / 2 + 100 * np.cos(t / 10))
                    y = int(height / 2 + 100 * np.sin(t / 10))
                elif obj["movement"] == "bounce":
                    x = (t * 6) % width
                    y = abs((t * 6) % height - height // 2) + height // 4
                else:
                    x = width // 2
                    y = height // 2

                draw_shape(frame, obj["shape"], x, y, obj["size"], obj["color"])
                cv2.putText(
                    frame,
                    obj["number"],
                    (x - 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

        video.write(frame)

    video.release()

    q1 = f"What number was on the {objects[0]['shape']}?"
    a1 = objects[0]["number"]

    q2 = f"What color was the shape with number {objects[1]['number']}?"
    a2 = objects[1]["color_name"]

    q3 = f"Which shape moved in {objects[2]['movement']} motion?"
    a3 = objects[2]["shape"]

    largest = max(objects, key=lambda x: x["size"])
    q4 = "Which shape was the largest in the video?"
    a4 = largest["shape"]

    questions_text = [q1, q2, q3, q4]
    answers = [a1, a2, a3, a4]

    questions_payload = [
        {"id": i + 1, "text": questions_text[i]} for i in range(len(questions_text))
    ]

    SESSIONS[session_id] = answers

    return str(video_filename), questions_payload, answers, session_id


def get_questions_header_value(questions_payload: List[dict]) -> str:
    return json.dumps(questions_payload)


def get_session_answers(session_id: str) -> List[str] | None:
    return SESSIONS.get(session_id)

