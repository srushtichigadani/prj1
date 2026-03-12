from pydantic import BaseModel


class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str


class AnswerResult(BaseModel):
    correct: bool
    correct_answer: str
    message: str

