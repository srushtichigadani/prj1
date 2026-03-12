import os

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.models.schemas import AnswerRequest, AnswerResult
from app.services.captcha_service import (
    generate_captcha_video_and_qa,
    get_questions_header_value,
    get_session_answers,
)

router = APIRouter(prefix="/captcha", tags=["captcha"])


def _remove_file(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


@router.get("")
def get_captcha(background_tasks: BackgroundTasks):
    video_path, questions_payload, _, session_id = generate_captcha_video_and_qa()

    headers = {
        "X-Session-Id": session_id,
        "X-Questions": get_questions_header_value(questions_payload),
    }

    # Schedule deletion of the generated video after the response is sent
    background_tasks.add_task(_remove_file, video_path)

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="captcha_video.mp4",
        headers=headers,
    )


@router.post("/check", response_model=AnswerResult)
def check_answer(payload: AnswerRequest):
    session_id = payload.session_id
    question_id = payload.question_id
    user_answer = payload.answer.strip().lower()

    answers = get_session_answers(session_id)
    if answers is None:
        raise HTTPException(status_code=404, detail="Invalid or expired session_id")

    if not (1 <= question_id <= len(answers)):
        raise HTTPException(status_code=400, detail="Invalid question_id")

    correct_answer = str(answers[question_id - 1])
    is_correct = user_answer == correct_answer.strip().lower()
    message = "Correct answer!" if is_correct else "Incorrect answer."

    return AnswerResult(
        correct=is_correct,
        correct_answer=correct_answer,
        message=message,
    )

