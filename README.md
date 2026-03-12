## Captcha API

Python FastAPI service that generates a video-based captcha, returns the video as raw `.mp4`, and validates user answers to dynamic questions.

### Endpoints

- `GET /captcha`  
  - **Body**: raw `.mp4` captcha video  
  - **Headers**:  
    - `X-Session-Id`: session id  
    - `X-Questions`: JSON array of questions (`[{ "id": 1, "text": "..." }, ...]`)

- `POST /captcha/check`  
  - **Body**:
    ```json
    {
      "session_id": "string",
      "question_id": 1,
      "answer": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "correct": true,
      "correct_answer": "3",
      "message": "Correct answer!"
    }
    ```

### Run locally (development)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run in production

- **Uvicorn directly**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **Example Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

