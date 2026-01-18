<h1 align="center">AI Social Media Caption Creator</h1>

---

## Table of Contents
- Overview  
- Features  
- Tech Stack  
- How the System Works  
- Prompt Design  
- Challenges and Edge Cases  
- How to Run the Project  
- Environment Variables  
- Sample Files  
- Deployment Notes  

---

## Overview
This project is a minimal full-stack web application built as part of an internship task. The application allows users to upload a product image or provide a short text brief and instantly receive AI-generated social media content. The focus of the project is fast response time, creative and relevant captions, clean UI, and easy deployment.

The backend is implemented using FastAPI, while the frontend is a lightweight HTML, CSS, and JavaScript interface. The AI generation is powered by the Gemini AI API.

---

## Features
The application generates three creative caption ideas, three sets of relevant hashtags, and a suggested best posting time based on the content type. Users can copy the generated captions directly from the UI or export them for later use.

---

## Tech Stack
The backend uses Python with FastAPI for API development and request handling. Gemini AI is used for caption and hashtag generation. The frontend is built with vanilla HTML, CSS, and JavaScript to keep the UI clean and lightweight. The project uses a Python virtual environment to ensure dependency isolation.

---

## How the System Works
The frontend sends either an uploaded image or a text brief to the FastAPI backend. The backend processes the input, extracts relevant context, and constructs a prompt for the Gemini AI model. The AI response is parsed into captions, hashtags, and posting time suggestions, which are then returned to the frontend and displayed to the user.

---

## Prompt Design
The prompt is designed to clearly instruct the AI to generate exactly three captions, three hashtag sets, and one posting time suggestion. Constraints are included to ensure creativity while keeping outputs concise, platform-appropriate, and relevant to marketing use cases.

---

## Challenges and Edge Cases
One challenge was maintaining consistent output formatting from the AI model, especially when handling both image-based and text-based inputs. Another challenge was ensuring fast responses while avoiding overly long or generic captions. These were addressed through prompt tuning and response validation in the backend.

---

## How to Run the Project
First, navigate to the backend directory and create a Python virtual environment. This isolates dependencies and avoids conflicts with global packages.

```bash
cd backend
python -m venv venv

```

Activate the virtual environment depending on your operating system.

```bash
venv\Scripts\activate
```

Once the virtual environment is active, install all required dependencies from the requirements file.

```bash
pip install -r requirements.txt
```

Start the FastAPI backend server.

```bash
python main.py
```

Open a new terminal window for the frontend, navigate to the frontend directory, and start a simple local server.

```bash
cd frontend
python -m http.server 8000
```

Finally, open your browser and go to:

```bash
http://localhost:8000
```

---

## Environment Variables

The Gemini AI API key is stored in a .env file inside the backend directory. This file is loaded by the application at runtime and should not be committed to version control.

---

## Sample Files
The repository includes sample product images and text briefs that can be used to quickly test the application and validate the AI-generated outputs.

---

## Deployment Notes

The application is designed to be easily deployable. The backend can be deployed on any platform that supports Python and FastAPI, while the frontend can be served as static files. The clean separation between frontend and backend allows flexible scaling and integration.
