# National Internship Portal - Flask Backend with NLP Matching

## 🚀 Features

### Backend (Flask)
- **Resume Analyzer**: Extracts text from PDF, DOCX, TXT files
- **NLP Skills Extraction**: Identifies technical and soft skills using keyword matching
- **TF-IDF Vectorization**: Converts text to numerical vectors for similarity matching
- **Cosine Similarity**: Calculates semantic similarity between profiles
- **Hybrid Matching Algorithm**:
  - 60% TF-IDF Cosine Similarity
  - 40% Direct Skill Matching
- **REST API**: Full CRUD operations for candidates and internships
- **Resume Scoring**: Automated quality assessment (0-100%)

### Frontend (React)
- **Responsive Design**: Mobile-first government portal styling
- **Real-time Resume Analysis**: Upload and get instant feedback
- **Smart Recommendations**: AI-powered matching results
- **Dual Interface**: Separate views for candidates and companies
- **Filters & Sorting**: Location, work mode, match score sorting

## 📋 Tech Stack

### Backend
- Flask 3.0.0
- NumPy 1.26.2
- Pandas 2.1.4
- Scikit-learn 1.3.2 (TF-IDF, Cosine Similarity)
- PyPDF2 3.0.1 (PDF parsing)
- python-docx 1.1.0 (DOCX parsing)
- Flask-CORS (Cross-origin requests)

### Frontend
- React 18
- Vanilla CSS (No external UI library)
- Government of India design standards

## 🛠️ Installation & Setup

### Prerequisites
```bash
Python 3.8 or higher
pip (Python package manager)
```

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Flask Server
```bash
python app.py
```

Server will start at: `http://localhost:5000`

### Step 3: Access the Portal
Open your browser and navigate to: `http://localhost:5000`

## 📁 Project Structure

```
national-internship-portal/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── ARCHITECTURE.md            # Detailed architecture docs
│
└── templates/
    └── index.html            # React frontend (single page)
```

## 🔧 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login

### Resume Analysis
- `POST /api/analyze-resume` - Upload and analyze resume
  - Accepts: PDF, DOCX, TXT
  - Returns: Skills, Education, Email, Phone, Score

### Profile Management
- `POST /api/save-candidate-profile` - Save candidate profile
- `POST /api/save-internship` - Post internship opportunity

### Matching Engine
- `POST /api/find-matches-for-candidate` - Find matching internships
- `POST /api/find-matches-for-internship` - Find matching candidates

### Statistics
- `GET /api/stats` - Platform statistics
- `GET /api/health` - Health check endpoint

## 🧠 NLP & Matching Algorithm

### Resume Analysis Pipeline
1. **Text Extraction**
   - PDF: PyPDF2
   - DOCX: python-docx
   - TXT: Direct read

2. **Information Extraction**
   - Email: Regex pattern matching
   - Phone: Regex pattern matching
   - Skills: Keyword matching against 40+ skill database
   - Education: Keyword matching for degrees

3. **Resume Scoring** (0-100%)
   - Skills: 40 points (4 per skill, max 40)
   - Content Length: 20 points (based on word count)
   - Contact Info: 20 points (email + phone)
   - Education: 10 points
   - Experience: 10 points

### Hybrid Matching Algorithm

#### Step 1: TF-IDF Vectorization
```python
TfidfVectorizer(
    max_features=500,      # Top 500 important terms
    ngram_range=(1, 2),    # Unigrams and bigrams
    stop_words='english'   # Remove common words
)
```

#### Step 2: Profile Text Creation
- **Candidate**: Skills + Education + Experience + Interests + Certifications
- **Internship**: Required Skills + Description + Requirements + Department + Title

#### Step 3: Similarity Calculation
```
Total Match Score = (TF-IDF Cosine Similarity × 60%) + (Direct Skill Match × 40%)
```

**TF-IDF Cosine Similarity (60%)**
- Measures semantic similarity between entire profiles
- Captures contextual relationships
- Handles synonyms and related terms

**Direct Skill Match (40%)**
- Exact keyword matching
- Percentage of required skills possessed
- Clear, interpretable results

#### Step 4: Result Ranking
- Sort by total match score (descending)
- Return top N matches
- Include matched skills list

## 📊 Example Usage

### 1. Upload Resume
```bash
curl -X POST http://localhost:5000/api/analyze-resume \
  -F "resume=@my_resume.pdf"
```

Response:
```json
{
  "success": true,
  "analysis": {
    "email": "candidate@example.com",
    "phone": "+91 98765 43210",
    "skills": ["Python", "Machine Learning", "Flask", "React"],
    "education": ["B.TECH", "COMPUTER SCIENCE"],
    "score": 85,
    "wordCount": 450
  }
}
```

### 2. Find Matching Internships
```bash
curl -X POST http://localhost:5000/api/find-matches-for-candidate \
  -H "Content-Type: application/json" \
  -d '{
    "skills": "Python, Machine Learning, Data Science",
    "education": "B.Tech Computer Science",
    "experience": "1 year internship",
    "interests": "AI, Deep Learning"
  }'
```

Response:
```json
{
  "success": true,
  "matches": [
    {
      "id": 1,
      "title": "ML Intern",
      "company": "TechCorp",
      "matchScore": 87.5,
      "matchedSkills": ["Python", "Machine Learning"],
      "location": "Bangalore",
      "stipend": "₹20,000/month"
    }
  ],
  "totalMatches": 10
}
```

## 🎯 Key Algorithms Explained

### TF-IDF (Term Frequency-Inverse Document Frequency)
- **Term Frequency (TF)**: How often a word appears in a document
- **Inverse Document Frequency (IDF)**: How rare/important a word is across all documents
- **TF-IDF**: TF × IDF - gives weight to important, distinctive terms

### Cosine Similarity
- Measures angle between two vectors
- Range: 0 (completely different) to 1 (identical)
- Formula: cos(θ) = (A · B) / (||A|| × ||B||)

### Example Calculation
```
Candidate Profile: "Python Machine Learning Data Science"
Internship Profile: "Python Deep Learning AI Research"

TF-IDF Vectors:
Candidate: [0.5, 0.4, 0.3, 0.6, 0.0, 0.0]
Internship: [0.5, 0.0, 0.0, 0.0, 0.7, 0.6]

Cosine Similarity: 0.45
TF-IDF Score: 0.45 × 60 = 27%

Direct Skill Match:
Common: Python (1 out of 3 required)
Skill Score: (1/3) × 40 = 13.3%

Total Match: 27 + 13.3 = 40.3%
```

## 🔐 Security Notes

**⚠️ Important for Production:**
1. **Password Hashing**: Currently storing plain text - use bcrypt/argon2
2. **Database**: Using in-memory storage - implement PostgreSQL/MongoDB
3. **Authentication**: Add JWT tokens for session management
4. **Input Validation**: Add comprehensive validation
5. **File Upload Security**: Limit file sizes, validate types
6. **HTTPS**: Use SSL certificates in production
7. **Environment Variables**: Store secrets in .env files

## 📈 Performance Optimization

### Current Limitations
- In-memory storage (resets on restart)
- No caching for TF-IDF calculations
- Synchronous processing

### Recommended Improvements
1. **Database**: PostgreSQL with SQLAlchemy ORM
2. **Caching**: Redis for TF-IDF vectors
3. **Background Jobs**: Celery for async processing
4. **Load Balancing**: Nginx + Gunicorn
5. **Monitoring**: Prometheus + Grafana

## 🧪 Testing

### Test Resume Analysis
```bash
# Create a test resume file
echo "Name: John Doe
Email: john@example.com
Phone: +91 9876543210
Skills: Python, Java, Machine Learning, React
Education: B.Tech Computer Science
Experience: 2 years as Software Developer" > test_resume.txt

# Upload to API
curl -X POST http://localhost:5000/api/analyze-resume \
  -F "resume=@test_resume.txt"
```

### Test Matching Algorithm
```bash
# Add sample internship
curl -X POST http://localhost:5000/api/save-internship \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer Intern",
    "company": "TechCorp",
    "requiredSkills": "Python, Flask, React",
    "location": "Bangalore",
    "stipend": "₹20000"
  }'

# Find matches
curl -X POST http://localhost:5000/api/find-matches-for-candidate \
  -H "Content-Type: application/json" \
  -d '{
    "skills": "Python, React, JavaScript"
  }'
```

## 📚 Additional Resources

- [Scikit-learn TF-IDF Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [Cosine Similarity Explained](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer Notes

### Extending the Skill Database
Edit `SKILLS_KEYWORDS` in `app.py`:
```python
SKILLS_KEYWORDS = [
    'python', 'java', 'javascript',  # Add more skills
    'your_new_skill'
]
```

### Customizing Match Weights
Adjust in `HybridMatcher` class:
```python
tfidf_score = cosine_sim * 60  # Change from 60%
skill_score = (skill_match / 100) * 40  # Change from 40%
```

### Adding New File Formats
Implement in `ResumeAnalyzer` class:
```python
def extract_text_from_rtf(self, file_stream):
    # Your RTF parsing logic
    pass
```

## 🐛 Troubleshooting

### Common Issues

**1. Module Not Found Error**
```bash
pip install -r requirements.txt --upgrade
```

**2. Port Already in Use**
```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

**3. CORS Issues**
```bash
# Ensure flask-cors is installed
pip install flask-cors
```

**4. PDF Extraction Fails**
```bash
# Try alternative PDF library
pip install pdfplumber
```

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: [Link to docs]

---

**Built with ❤️ for India's Skill Development Initiative**
