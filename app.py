from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx
import re
import io
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# In-memory storage (replace with database in production)
users_db = {}
internships_db = []
candidates_db = []

# NLP Keywords for skills extraction
SKILLS_KEYWORDS = [
    'python', 'java', 'javascript', 'react', 'node', 'angular', 'vue',
    'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
    'html', 'css', 'sql', 'mongodb', 'postgresql', 'mysql',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git',
    'machine learning', 'deep learning', 'data science', 'ai',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'flask', 'django', 'spring boot', 'express',
    'agile', 'scrum', 'devops', 'ci/cd',
    'communication', 'teamwork', 'leadership', 'problem solving'
]

EDUCATION_KEYWORDS = ['bachelor', 'master', 'phd', 'diploma', 'degree', 'b.tech', 'm.tech', 'bca', 'mca', 'bba', 'mba']
EXPERIENCE_KEYWORDS = ['intern', 'developer', 'engineer', 'analyst', 'manager', 'consultant', 'designer']


class ResumeAnalyzer:
    """Analyzes resumes using NLP techniques"""
    
    def __init__(self):
        self.skills_keywords = SKILLS_KEYWORDS
        self.education_keywords = EDUCATION_KEYWORDS
        
    def extract_text_from_pdf(self, file_stream):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def extract_text_from_docx(self, file_stream):
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_stream)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"
    
    def extract_text_from_txt(self, file_stream):
        """Extract text from TXT file"""
        try:
            return file_stream.read().decode('utf-8')
        except Exception as e:
            return f"Error extracting TXT: {str(e)}"
    
    def extract_email(self, text):
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "Not found"
    
    def extract_phone(self, text):
        """Extract phone number from text"""
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else "Not found"
    
    def extract_skills(self, text):
        """Extract skills from text using keyword matching"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def extract_education(self, text):
        """Extract education information"""
        text_lower = text.lower()
        education = []
        
        for edu in self.education_keywords:
            if edu.lower() in text_lower:
                education.append(edu.upper())
        
        return list(set(education)) if education else ["Not specified"]
    
    def calculate_resume_score(self, text, skills, experience_years=0):
        """Calculate resume quality score"""
        score = 0
        
        # Skills score (40 points)
        if len(skills) > 0:
            score += min(len(skills) * 4, 40)
        
        # Length score (20 points)
        word_count = len(text.split())
        if word_count > 100:
            score += min(word_count / 50, 20)
        
        # Contact info score (20 points)
        if self.extract_email(text) != "Not found":
            score += 10
        if self.extract_phone(text) != "Not found":
            score += 10
        
        # Education score (10 points)
        education = self.extract_education(text)
        if len(education) > 0 and "Not specified" not in education:
            score += 10
        
        # Experience score (10 points)
        score += min(experience_years * 2, 10)
        
        return min(int(score), 100)
    
    def analyze_resume(self, file_stream, filename):
        """Complete resume analysis"""
        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_stream)
        elif filename.endswith('.docx'):
            text = self.extract_text_from_docx(file_stream)
        elif filename.endswith('.txt'):
            text = self.extract_text_from_txt(file_stream)
        else:
            return {"error": "Unsupported file format"}
        
        # Extract information
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        skills = self.extract_skills(text)
        education = self.extract_education(text)
        
        # Calculate score
        score = self.calculate_resume_score(text, skills)
        
        return {
            "text": text,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "score": score,
            "word_count": len(text.split())
        }


class HybridMatcher:
    """Hybrid matching using TF-IDF and Cosine Similarity"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
    
    def create_profile_text(self, profile, user_type='candidate'):
        """Create text representation of profile for vectorization"""
        if user_type == 'candidate':
            text_parts = [
                profile.get('skills', ''),
                profile.get('education', ''),
                profile.get('experience', ''),
                profile.get('interests', ''),
                profile.get('certifications', '')
            ]
        else:  # internship/job
            text_parts = [
                profile.get('requiredSkills', ''),
                profile.get('description', ''),
                profile.get('requirements', ''),
                profile.get('department', ''),
                profile.get('title', '')
            ]
        
        return ' '.join([str(part) for part in text_parts if part])
    
    def calculate_skill_match(self, candidate_skills, required_skills):
        """Calculate percentage of skill match"""
        if not candidate_skills or not required_skills:
            return 0
        
        candidate_set = set([s.lower().strip() for s in candidate_skills.split(',')])
        required_set = set([s.lower().strip() for s in required_skills.split(',')])
        
        if len(required_set) == 0:
            return 0
        
        matched = candidate_set.intersection(required_set)
        return (len(matched) / len(required_set)) * 100
    
    def hybrid_match(self, candidates, internships, top_n=10):
        """
        Perform hybrid matching using:
        1. TF-IDF Cosine Similarity (60% weight)
        2. Direct Skill Matching (40% weight)
        """
        results = []
        
        # Create text representations
        candidate_texts = [self.create_profile_text(c, 'candidate') for c in candidates]
        internship_texts = [self.create_profile_text(i, 'internship') for i in internships]
        
        # Combine for TF-IDF fitting
        all_texts = candidate_texts + internship_texts
        
        if len(all_texts) < 2:
            return []
        
        # Fit and transform
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Split back into candidates and internships
            candidate_vectors = tfidf_matrix[:len(candidates)]
            internship_vectors = tfidf_matrix[len(candidates):]
            
            # Calculate cosine similarities
            for i, candidate in enumerate(candidates):
                for j, internship in enumerate(internships):
                    # TF-IDF Cosine Similarity (60%)
                    cosine_sim = cosine_similarity(
                        candidate_vectors[i:i+1],
                        internship_vectors[j:j+1]
                    )[0][0]
                    tfidf_score = cosine_sim * 60
                    
                    # Direct Skill Match (40%)
                    skill_match = self.calculate_skill_match(
                        candidate.get('skills', ''),
                        internship.get('requiredSkills', '')
                    )
                    skill_score = (skill_match / 100) * 40
                    
                    # Combined score
                    total_score = tfidf_score + skill_score
                    
                    # Get matched skills
                    candidate_skills = set([s.lower().strip() for s in candidate.get('skills', '').split(',')])
                    required_skills = set([s.lower().strip() for s in internship.get('requiredSkills', '').split(',')])
                    matched_skills = list(candidate_skills.intersection(required_skills))
                    
                    results.append({
                        'candidate': candidate,
                        'internship': internship,
                        'match_score': round(total_score, 2),
                        'tfidf_score': round(tfidf_score, 2),
                        'skill_score': round(skill_score, 2),
                        'matched_skills': [s.title() for s in matched_skills]
                    })
            
            # Sort by match score
            results.sort(key=lambda x: x['match_score'], reverse=True)
            return results[:top_n]
            
        except Exception as e:
            print(f"Error in hybrid matching: {str(e)}")
            return []
    
    def find_matches_for_candidate(self, candidate_profile, internships, top_n=10):
        """Find top internship matches for a candidate"""
        matches = self.hybrid_match([candidate_profile], internships, top_n * 2)
        
        results = []
        for match in matches[:top_n]:
            internship = match['internship'].copy()
            internship['matchScore'] = match['match_score']
            internship['matchedSkills'] = match['matched_skills']
            results.append(internship)
        
        return results
    
    def find_matches_for_internship(self, internship_profile, candidates, top_n=10):
        """Find top candidate matches for an internship"""
        matches = self.hybrid_match(candidates, [internship_profile], top_n * 2)
        
        results = []
        for match in matches[:top_n]:
            candidate = match['candidate'].copy()
            candidate['matchScore'] = match['match_score']
            candidate['matchedSkills'] = match['matched_skills']
            results.append(candidate)
        
        return results


# Initialize analyzers
resume_analyzer = ResumeAnalyzer()
matcher = HybridMatcher()


# ==================== API ROUTES ====================

@app.route('/')
def index():
    """Serve the main HTML page as static file"""
    return send_from_directory('.', 'index.html')


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType')
    
    if not email or not password or not user_type:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    if email in users_db:
        return jsonify({"success": False, "message": "User already exists"}), 400
    
    users_db[email] = {
        "email": email,
        "password": password,  # In production, hash this!
        "userType": user_type,
        "createdAt": datetime.now().isoformat()
    }
    
    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": {"email": email, "userType": user_type}
    })


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    if email not in users_db:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if users_db[email]['password'] != password:
        return jsonify({"success": False, "message": "Invalid password"}), 401
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "email": email,
            "userType": users_db[email]['userType']
        }
    })


@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume_endpoint():
    """Analyze uploaded resume"""
    if 'resume' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    
    # Analyze resume
    result = resume_analyzer.analyze_resume(io.BytesIO(file.read()), file.filename)
    
    if "error" in result:
        return jsonify({"success": False, "message": result["error"]}), 400
    
    return jsonify({
        "success": True,
        "analysis": {
            "email": result['email'],
            "phone": result['phone'],
            "skills": result['skills'],
            "education": result['education'],
            "score": result['score'],
            "wordCount": result['word_count']
        }
    })


@app.route('/api/save-candidate-profile', methods=['POST'])
def save_candidate_profile():
    """Save candidate profile"""
    data = request.json
    
    # Add to candidates database
    candidate = {
        "id": len(candidates_db) + 1,
        "name": data.get('name'),
        "email": data.get('email'),
        "phone": data.get('phone'),
        "education": data.get('education'),
        "institution": data.get('institution'),
        "graduationYear": data.get('graduationYear'),
        "skills": data.get('skills'),
        "experience": data.get('experience'),
        "interests": data.get('interests'),
        "availability": data.get('availability'),
        "workMode": data.get('workMode'),
        "certifications": data.get('certifications', '').split(',') if data.get('certifications') else [],
        "portfolio": data.get('portfolio', ''),
        "linkedin": data.get('linkedin', ''),
        "github": data.get('github', ''),
        "resumeScore": data.get('resumeScore', 0),
        "createdAt": datetime.now().isoformat()
    }
    
    candidates_db.append(candidate)
    
    return jsonify({
        "success": True,
        "message": "Profile saved successfully",
        "candidate": candidate
    })


@app.route('/api/save-internship', methods=['POST'])
def save_internship():
    """Save internship posting"""
    data = request.json
    
    internship = {
        "id": len(internships_db) + 1,
        "title": data.get('title'),
        "company": data.get('company'),
        "location": data.get('location'),
        "department": data.get('department'),
        "duration": data.get('duration'),
        "stipend": data.get('stipend'),
        "workMode": data.get('workMode'),
        "description": data.get('description'),
        "requiredSkills": data.get('requiredSkills'),
        "requirements": data.get('requirements'),
        "benefits": data.get('benefits', '').split(',') if data.get('benefits') else [],
        "deadline": data.get('deadline'),
        "interviewProcess": data.get('interviewProcess', ''),
        "mentorship": data.get('mentorship', ''),
        "createdAt": datetime.now().isoformat()
    }
    
    internships_db.append(internship)
    
    return jsonify({
        "success": True,
        "message": "Internship posted successfully",
        "internship": internship
    })


@app.route('/api/find-matches-for-candidate', methods=['POST'])
def find_matches_for_candidate():
    """Find matching internships for a candidate using hybrid NLP matching"""
    data = request.json
    
    candidate_profile = {
        "skills": data.get('skills', ''),
        "education": data.get('education', ''),
        "experience": data.get('experience', ''),
        "interests": data.get('interests', ''),
        "certifications": data.get('certifications', '')
    }
    
    if not internships_db:
        return jsonify({
            "success": True,
            "matches": [],
            "message": "No internships available"
        })
    
    # Find matches
    matches = matcher.find_matches_for_candidate(candidate_profile, internships_db, top_n=10)
    
    return jsonify({
        "success": True,
        "matches": matches,
        "totalMatches": len(matches)
    })


@app.route('/api/find-matches-for-internship', methods=['POST'])
def find_matches_for_internship():
    """Find matching candidates for an internship using hybrid NLP matching"""
    data = request.json
    
    internship_profile = {
        "requiredSkills": data.get('requiredSkills', ''),
        "description": data.get('description', ''),
        "requirements": data.get('requirements', ''),
        "department": data.get('department', ''),
        "title": data.get('title', '')
    }
    
    if not candidates_db:
        return jsonify({
            "success": True,
            "matches": [],
            "message": "No candidates available"
        })
    
    # Find matches
    matches = matcher.find_matches_for_internship(internship_profile, candidates_db, top_n=10)
    
    return jsonify({
        "success": True,
        "matches": matches,
        "totalMatches": len(matches)
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    return jsonify({
        "success": True,
        "stats": {
            "totalUsers": len(users_db),
            "totalCandidates": len(candidates_db),
            "totalInternships": len(internships_db),
            "totalMatches": len(candidates_db) * len(internships_db)
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "resume_analyzer": "active",
            "hybrid_matcher": "active",
            "database": "active"
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  National Internship Portal - Flask Backend")
    print("=" * 60)
    print()
    print("✅ NLP Resume Analyzer: Active")
    print("✅ TF-IDF Matching Engine: Active")
    print("✅ Hybrid Algorithm: 60% TF-IDF + 40% Skills")
    print()
    print("Server starting at: http://localhost:5000")
    print("Press CTRL+C to stop")
    print("=" * 60)
    print()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
