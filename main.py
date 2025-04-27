from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
import os
import tempfile
import re

# Define regex patterns for phone numbers and email addresses
phone_pattern = r'\+?[0-9\-\(\)\s]{7,15}'  # Matches international and local phone numbers
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # Matches email addresses

app = Flask(__name__)
CORS(app)
model = SentenceTransformer('all-MiniLM-L6-v2', trust_remote_code=True, token='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')

# HTML template for frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Extractor</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-2xl">
        <h1 class="text-2xl font-bold mb-6 text-center">Resume Extractor</h1>

        <!-- Resume Files Upload -->
        <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Resumes (PDFs)</label>
            <input type="file" id="resumeFiles" multiple accept=".pdf" 
                   class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
        </div>

        <!-- Job Description Upload -->
        <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Job Description (TXT)</label>
            <input type="file" id="jobDescription" accept=".txt" 
                   class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
        </div>

        <!-- Submit Button -->
        <button id="submitButton" 
                class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition disabled:bg-gray-400"
                disabled>
            Process Files
        </button>

        <!-- Results Section -->
        <div id="results" class="mt-6 hidden">
            <h2 class="text-lg font-semibold mb-4">Similarity Scores</h2>
            <ul id="resultsList" class="space-y-2"></ul>
        </div>

        <!-- Mandatory Fields -->
        <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Mandatory Keywords (Comma separated)</label>
            <input type="text" id="mandatoryFields" 
                placeholder="e.g skills, experience, education"
            class="w-full border border-gray-300 p-2 rounded">
        </div>
    </div>

    <script>
        const resumeFilesInput = document.getElementById('resumeFiles');
        const jobDescriptionInput = document.getElementById('jobDescription');
        const submitButton = document.getElementById('submitButton');
        const resultsSection = document.getElementById('results');
        const resultsList = document.getElementById('resultsList');

        // Enable submit button when both inputs have files
        function checkInputs() {
            const hasResumes = resumeFilesInput.files.length > 0;
            const hasJobDesc = jobDescriptionInput.files.length > 0;
            submitButton.disabled = !(hasResumes && hasJobDesc);
        }

        resumeFilesInput.addEventListener('change', checkInputs);
        jobDescriptionInput.addEventListener('change', checkInputs);

        // Handle form submission
        submitButton.addEventListener('click', async () => {
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';
            resultsSection.classList.add('hidden');
            resultsList.innerHTML = '';

            const formData = new FormData();
            Array.from(resumeFilesInput.files).forEach(file => {
                formData.append('resumes', file);
            });
            formData.append('jobDescription', jobDescriptionInput.files[0]);

            // Capture mandatory fields entered by the user
            const mandatoryFields = document.getElementById('mandatoryFields').value;
            formData.append('mandatoryFields', mandatoryFields);

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Processing failed');

                const results = await response.json();

                // Display results
                resultsSection.classList.remove('hidden');
                results.forEach(({ filename, score, phone_numbers, emails, matched_keywords, matched_keywords_count, total_keywords }) => {
                    const li = document.createElement('li');
                    li.className = 'p-4 bg-gray-50 rounded mb-2';

                    // Create HTML content for each resume
                    let content = `<strong>${filename}</strong>: ${score.toFixed(2)}% match<br>`;
                    content += `<div class="mt-2">`;
                    
                    // Display phone numbers
                    if (phone_numbers && phone_numbers.length > 0) {
                        content += `<strong>Phone Numbers:</strong> ${phone_numbers.join(', ')}<br>`;
                    } else {
                        content += `<strong>Phone Numbers:</strong> None<br>`;
                    }

                    // Display emails
                    if (emails && emails.length > 0) {
                        content += `<strong>Emails:</strong> ${emails.join(', ')}<br>`;
                    } else {
                        content += `<strong>Emails:</strong> None<br>`;
                    }

                    // Display matched keywords
                    if (matched_keywords && matched_keywords.length > 0) {
                        content += `<strong>Matched Keywords:</strong> ${matched_keywords.join(', ')} (${matched_keywords_count}/${total_keywords})<br>`;
                    } else {
                        content += `<strong>Matched Keywords:</strong> None (0/${total_keywords})<br>`;
                    }

                    content += `</div>`;
                    li.innerHTML = content;
                    resultsList.appendChild(li);
                });
            } catch (error) {
                alert('Error processing files: ' + error.message);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Process Files';
            }
        });
    </script>
</body>
</html>
"""

# Convert PDF to text
def extract_text_from_pdf(pdf_path):
    try:
        return extract_text(pdf_path)
    except PDFSyntaxError:
        return None
    except Exception as e:
        print(f"[✗] Error processing {pdf_path}: {e}")
        return None

# Read text file
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Serve frontend
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def extract_contact_info(text):
    """Extract phone numbers and email addresses from the given text."""
    phone_numbers = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    return phone_numbers, emails

# Process uploaded files
@app.route('/process', methods=['POST'])
def process_files():
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)

        # Save uploaded files
        resumes = request.files.getlist('resumes')
        job_description = request.files['jobDescription']
        
        # Save job description
        jd_path = os.path.join(temp_dir, 'job_description.txt')
        job_description.save(jd_path)
        job_description_text = read_file(jd_path)

        mandatory_fields_raw = request.form.get('mandatoryFields', '')
        mandatory_fields = [field.strip().lower() for field in mandatory_fields_raw.split(',') if field.strip()]


        # Process resumes
        resume_texts = []
        resume_files = []
        resume_infos = []
        
        for resume in resumes:
            if resume.filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(temp_dir, resume.filename)
                resume.save(pdf_path)
                
                text = extract_text_from_pdf(pdf_path)
                if text:
                    text_path = os.path.join(output_dir, os.path.splitext(resume.filename)[0] + '.txt')
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    resume_files.append(resume.filename)
                    resume_texts.append(text)


                    text_lower = text.lower()
                    matched_keywords = [field for field in mandatory_fields if field in text_lower]
                    phone_numbers, emails = extract_contact_info(text)
                    resume_infos.append({
                        'filename': resume.filename,
                        'text': text,
                        'matched_keywords': matched_keywords,
                        'total_keywords': len(mandatory_fields),
                        'phone_numbers': phone_numbers,
                        'emails': emails
                    })

        # Encode and compute similarities
        jd_embedding = model.encode(job_description_text, convert_to_tensor=True)
        resume_embeddings = model.encode([info['text'] for info in resume_infos], convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(jd_embedding, resume_embeddings)[0]

        # Prepare results
        results = []
        for idx, score in enumerate(similarities):
            info = resume_infos[idx]
            results.append({
                'filename': info['filename'],
                'score': round(float(score) * 100, 2),
                'matched_keywords_count': len(info['matched_keywords']),
                'total_keywords': info['total_keywords'],
                'matched_keywords': info['matched_keywords'],
                'phone_numbers': info['phone_numbers'],
                'emails': info['emails']
            })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)