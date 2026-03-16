cd backend
pip install -r requirements.txt
export GEMINI_API_KEY="AIzaSyA46TWOZddtEeblufXInAK0Qzctaz_3ekM"
uvicorn main:app --reload
