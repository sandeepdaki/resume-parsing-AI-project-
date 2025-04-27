# resume-parsing-AI-project-
# Resume Extractor with Job Description Matching

This project is a web-based **Resume Extractor** application that allows users to upload resumes (PDFs) and a job description (TXT file). The application processes these files to extract key contact information (such as phone numbers and emails), and then computes the similarity between the job description and the resumes using **Sentence Transformers**. It also identifies whether the resume contains mandatory keywords such as skills, experience, and education.

## Features

- **Resume Upload**: Upload multiple PDF resumes for processing.
- **Job Description Upload**: Upload a job description in TXT format.
- **Keyword Matching**: Extracts mandatory keywords from resumes and compares them to the job description.
- **Contact Information Extraction**: Extracts phone numbers and emails from resumes.
- **Similarity Scoring**: Computes a similarity score between the job description and each resume based on their content using **Sentence Transformers**.
- **Result Display**: Displays the results with similarity scores, matched keywords, and extracted contact information.

## Technologies Used

- **Flask**: For creating the web server and handling file uploads.
- **Flask-CORS**: For enabling Cross-Origin Resource Sharing (CORS).
- **Sentence-Transformers**: For computing similarity scores between resumes and the job description.
- **PDFMiner**: For extracting text from PDF resumes.
- **Regular Expressions**: For extracting phone numbers and emails from resumes.
- **Tailwind CSS**: For frontend styling and layout.

## How to Run Locally

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/resume-extractor.git
    cd resume-extractor
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application**:
    ```bash
    python app.py
    ```

5. Open your browser and go to `http://127.0.0.1:5000` to access the application.

## API Endpoints

### `/process` (POST)
- **Purpose**: Processes the uploaded resumes and job description.
- **Parameters**:
  - `resumes`: A list of resume PDF files.
  - `jobDescription`: The job description file in TXT format.
  - `mandatoryFields`: A comma-separated list of keywords to search for in resumes.
- **Response**: A JSON array containing the results for each resume:
  - `filename`: The name of the resume file.
  - `score`: The similarity score between the job description and the resume.
  - `matched_keywords`: The list of keywords matched in the resume.
  - `phone_numbers`: The list of extracted phone numbers from the resume.
  - `emails`: The list of extracted email addresses from the resume.

## Frontend

The frontend allows users to:
- Upload multiple resume files (PDF).
- Upload a job description (TXT).
- Enter mandatory keywords to search for in the resumes.
- View the results with similarity scores, phone numbers, emails, and matched keywords.

## Example Workflow

1. **Upload Resumes and Job Description**: Users upload PDF resumes and a job description TXT file.
2. **Process Files**: The backend processes the uploaded files, extracts contact details, and computes the similarity scores.
3. **Display Results**: Results are displayed with similarity scores, matched keywords, and contact information.

## Contributing

1. Fork this repository.
2. Clone your forked repository to your local machine.
3. Make the changes you want to implement.
4. Commit and push your changes.
5. Create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
