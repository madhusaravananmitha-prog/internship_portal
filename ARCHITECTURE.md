# National Internship Portal - Technical Architecture

## 📐 System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface Layer                    │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │  Candidate UI   │         │   Company UI    │           │
│  │  (React)        │         │   (React)       │           │
│  └────────┬────────┘         └────────┬────────┘           │
└───────────┼──────────────────────────┼─────────────────────┘
            │                          │
            └──────────┬───────────────┘
                       │ HTTP/REST
┌──────────────────────┼─────────────────────────────────────┐
│                      ▼                                       │
│              Flask REST API Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Authentication  │  Profile Mgmt  │  Matching Engine │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Core Processing Layer                        │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Resume Analyzer│  │  NLP Engine  │  │ TF-IDF Engine  │  │
│  │  - PDF Parse   │  │  - Tokenize  │  │  - Vectorize   │  │
│  │  - DOCX Parse  │  │  - Extract   │  │  - Similarity  │  │
│  │  - Text Parse  │  │  - Skills    │  │  - Ranking     │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Storage Layer                         │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Users DB      │  │  Candidates  │  │  Internships   │  │
│  │  (In-Memory)   │  │  (In-Memory) │  │  (In-Memory)   │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Component Architecture

### 1. Resume Analyzer Module

#### Purpose
Extract structured information from unstructured resume documents

#### Components
```python
class ResumeAnalyzer:
    - extract_text_from_pdf()      # PDF → Text
    - extract_text_from_docx()     # DOCX → Text
    - extract_text_from_txt()      # TXT → Text
    - extract_email()              # Regex-based email extraction
    - extract_phone()              # Regex-based phone extraction
    - extract_skills()             # Keyword matching for skills
    - extract_education()          # Education qualification extraction
    - calculate_resume_score()     # Quality scoring algorithm
    - analyze_resume()             # Main orchestrator
```

#### Data Flow
```
Resume File (PDF/DOCX/TXT)
        ↓
Text Extraction
        ↓
Information Extraction (Parallel Processing)
    ├── Email Detection (Regex)
    ├── Phone Detection (Regex)
    ├── Skills Extraction (Keyword Matching)
    └── Education Extraction (Keyword Matching)
        ↓
Resume Scoring Algorithm
        ↓
Structured Output (JSON)
```

#### Scoring Algorithm
```python
Total Score (0-100) = Skills Score (40) + 
                      Length Score (20) + 
                      Contact Score (20) + 
                      Education Score (10) + 
                      Experience Score (10)

Skills Score:
- 4 points per skill identified
- Maximum 40 points (10 skills)

Length Score:
- Based on word count
- word_count / 50 (capped at 20)

Contact Score:
- Email present: 10 points
- Phone present: 10 points

Education Score:
- Valid degree found: 10 points

Experience Score:
- 2 points per year of experience
- Maximum 10 points (5 years)
```

### 2. Hybrid Matching Engine

#### Purpose
Match candidates with internships using dual-algorithm approach

#### Architecture
```
┌─────────────────────────────────────────────────┐
│            Hybrid Matcher                       │
│                                                 │
│  ┌───────────────┐      ┌──────────────────┐  │
│  │   TF-IDF      │      │  Direct Skill    │  │
│  │   Matching    │      │    Matching      │  │
│  │   (60%)       │      │    (40%)         │  │
│  └───────┬───────┘      └────────┬─────────┘  │
│          │                       │             │
│          └───────────┬───────────┘             │
│                      ▼                         │
│              Combined Score                     │
│                 (0-100)                        │
└─────────────────────────────────────────────────┘
```

#### TF-IDF Component (60% weight)

**Purpose**: Semantic similarity between profiles

**Process**:
1. **Text Preparation**
   ```python
   Candidate Text = skills + education + experience + interests + certs
   Internship Text = required_skills + description + requirements + title
   ```

2. **TF-IDF Vectorization**
   ```python
   TfidfVectorizer(
       max_features=500,      # Top 500 terms
       ngram_range=(1, 2),    # 1-word and 2-word phrases
       stop_words='english'   # Remove common words
   )
   ```

3. **Vector Representation**
   ```
   Document → [0.43, 0.12, 0.0, 0.67, ..., 0.21] (500 dimensions)
   ```

4. **Cosine Similarity**
   ```
   similarity = cos(θ) = (A · B) / (||A|| × ||B||)
   
   Where:
   A = Candidate vector
   B = Internship vector
   θ = Angle between vectors
   
   Result range: 0.0 (orthogonal) to 1.0 (identical)
   ```

5. **Score Calculation**
   ```
   TF-IDF Score = Cosine Similarity × 60
   ```

#### Direct Skill Matching (40% weight)

**Purpose**: Exact keyword matching for transparency

**Process**:
1. **Skill Extraction**
   ```python
   Candidate Skills = ["Python", "ML", "React"]
   Required Skills = ["Python", "ML", "Data Science"]
   ```

2. **Set Intersection**
   ```python
   Matched = {Python, ML}
   Match Percentage = len(Matched) / len(Required) = 2/3 = 66.7%
   ```

3. **Score Calculation**
   ```python
   Skill Score = Match Percentage × 40 = 66.7% × 40 = 26.68
   ```

#### Combined Scoring
```python
Final Score = TF-IDF Score + Skill Score

Example:
- TF-IDF Cosine Similarity: 0.72
- TF-IDF Score: 0.72 × 60 = 43.2
- Skill Match: 66.7%
- Skill Score: 0.667 × 40 = 26.68
- Final Score: 43.2 + 26.68 = 69.88
```

### 3. REST API Layer

#### Endpoints Structure

```
Authentication
├── POST /api/register          # User registration
└── POST /api/login             # User authentication

Resume Processing
└── POST /api/analyze-resume    # Resume upload & analysis

Profile Management
├── POST /api/save-candidate-profile    # Save candidate data
└── POST /api/save-internship           # Save internship posting

Matching Engine
├── POST /api/find-matches-for-candidate    # Find internships
└── POST /api/find-matches-for-internship   # Find candidates

Monitoring
├── GET /api/stats              # Platform statistics
└── GET /api/health             # Health check
```

#### API Request/Response Flow

**Example: Resume Analysis**
```
Request:
POST /api/analyze-resume
Content-Type: multipart/form-data
Body: {resume: <file>}

Processing:
1. Validate file (size, type)
2. Extract text based on format
3. Run information extraction
4. Calculate quality score
5. Structure output

Response:
{
  "success": true,
  "analysis": {
    "email": "john@example.com",
    "phone": "+91 9876543210",
    "skills": ["Python", "ML", "React"],
    "education": ["B.TECH", "CS"],
    "score": 85,
    "wordCount": 450
  }
}
```

**Example: Matching Request**
```
Request:
POST /api/find-matches-for-candidate
Content-Type: application/json
Body: {
  "skills": "Python, ML, Data Science",
  "education": "B.Tech CS",
  "experience": "1 year"
}

Processing:
1. Create candidate profile text
2. Retrieve all internships
3. Create internship profile texts
4. Run TF-IDF vectorization
5. Calculate cosine similarities
6. Calculate direct skill matches
7. Combine scores (60-40 split)
8. Sort by score (descending)
9. Return top N matches

Response:
{
  "success": true,
  "matches": [
    {
      "id": 1,
      "title": "ML Intern",
      "company": "TechCorp",
      "matchScore": 87.5,
      "matchedSkills": ["Python", "ML"],
      ...
    }
  ],
  "totalMatches": 10
}
```

## 📊 Data Models

### User Model
```python
{
    "email": str,           # Unique identifier
    "password": str,        # Hashed (⚠️ currently plain)
    "userType": str,        # "candidate" | "company"
    "createdAt": datetime
}
```

### Candidate Profile Model
```python
{
    "id": int,
    "name": str,
    "email": str,
    "phone": str,
    "education": str,
    "institution": str,
    "graduationYear": int,
    "skills": str,              # Comma-separated
    "experience": str,
    "interests": str,
    "availability": str,
    "workMode": str,
    "certifications": list,
    "portfolio": str,
    "linkedin": str,
    "github": str,
    "resumeScore": int,         # 0-100
    "createdAt": datetime
}
```

### Internship Model
```python
{
    "id": int,
    "title": str,
    "company": str,
    "location": str,
    "department": str,
    "duration": str,
    "stipend": str,
    "workMode": str,
    "description": str,
    "requiredSkills": str,      # Comma-separated
    "requirements": str,
    "benefits": list,
    "deadline": str,
    "interviewProcess": str,
    "mentorship": str,
    "createdAt": datetime
}
```

## 🔄 Algorithm Deep Dive

### TF-IDF Algorithm

#### 1. Term Frequency (TF)
```
TF(term, document) = (Number of times term appears in document) / 
                     (Total number of terms in document)

Example:
Document: "Python Python Java"
TF(Python) = 2/3 = 0.667
TF(Java) = 1/3 = 0.333
```

#### 2. Inverse Document Frequency (IDF)
```
IDF(term) = log(Total number of documents / 
                Number of documents containing term)

Example:
3 documents, "Python" appears in 2
IDF(Python) = log(3/2) = 0.176

Common words → low IDF (less important)
Rare words → high IDF (more important)
```

#### 3. TF-IDF Score
```
TF-IDF(term, document) = TF(term, document) × IDF(term)

Example:
TF-IDF(Python) = 0.667 × 0.176 = 0.117
```

### Cosine Similarity Algorithm

#### Mathematical Foundation
```
Given two vectors A and B:

cos(θ) = (A · B) / (||A|| × ||B||)

Where:
A · B = Dot product = Σ(Ai × Bi)
||A|| = Magnitude = √(Σ(Ai²))
||B|| = Magnitude = √(Σ(Bi²))
```

#### Example Calculation
```
Candidate Vector:  [0.5, 0.3, 0.0, 0.8]
Internship Vector: [0.4, 0.5, 0.1, 0.6]

Dot Product = (0.5×0.4) + (0.3×0.5) + (0.0×0.1) + (0.8×0.6)
            = 0.2 + 0.15 + 0 + 0.48
            = 0.83

||Candidate|| = √(0.5² + 0.3² + 0.0² + 0.8²)
              = √(0.25 + 0.09 + 0 + 0.64)
              = √0.98 = 0.99

||Internship|| = √(0.4² + 0.5² + 0.1² + 0.6²)
               = √(0.16 + 0.25 + 0.01 + 0.36)
               = √0.78 = 0.88

Cosine Similarity = 0.83 / (0.99 × 0.88)
                  = 0.83 / 0.87
                  = 0.95 (95% similar)
```

## 🚀 Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Resume Analysis | O(n) | n = document length |
| TF-IDF Vectorization | O(m × d) | m = docs, d = vocab size |
| Cosine Similarity | O(d) | d = vector dimensions |
| Matching (1 candidate, k internships) | O(k × d) | For all comparisons |
| Sorting Results | O(n log n) | n = number of matches |

### Space Complexity

| Component | Complexity | Notes |
|-----------|-----------|-------|
| TF-IDF Matrix | O(m × d) | m = docs, d = features (500) |
| Document Storage | O(n × l) | n = docs, l = avg length |
| User Database | O(u) | u = number of users |

### Scalability Considerations

**Current Limitations:**
- In-memory storage (volatile)
- Synchronous processing
- Single-threaded execution
- No caching

**Scaling Recommendations:**
1. **Horizontal Scaling**: Multiple Flask workers with Gunicorn
2. **Database**: PostgreSQL/MongoDB for persistence
3. **Caching**: Redis for TF-IDF vectors
4. **Async Processing**: Celery for background jobs
5. **Load Balancing**: Nginx reverse proxy
6. **Microservices**: Separate matching engine service

## 🔒 Security Considerations

### Current Security Issues (⚠️ Production)
1. **Plain Text Passwords**: Use bcrypt/argon2
2. **No Authentication**: Implement JWT tokens
3. **No Input Validation**: Add comprehensive validation
4. **CORS Open**: Restrict origins in production
5. **No Rate Limiting**: Implement API throttling
6. **File Upload Risks**: Validate file types & sizes

### Recommended Security Measures
```python
# Password Hashing
from werkzeug.security import generate_password_hash, check_password_hash

# JWT Authentication
from flask_jwt_extended import create_access_token, jwt_required

# Input Validation
from marshmallow import Schema, fields, validate

# Rate Limiting
from flask_limiter import Limiter
```

## 📈 Future Enhancements

### Phase 2: Advanced Features
1. **Deep Learning Models**: BERT/GPT for semantic matching
2. **Skill Taxonomy**: Hierarchical skill relationships
3. **Collaborative Filtering**: User behavior-based recommendations
4. **Real-time Matching**: WebSocket notifications
5. **Analytics Dashboard**: Matching insights & trends

### Phase 3: Enterprise Features
1. **Multi-tenancy**: Support for multiple organizations
2. **Advanced Filters**: Salary, location radius, visa status
3. **Application Tracking**: End-to-end hiring pipeline
4. **Interview Scheduling**: Calendar integration
5. **Video Assessments**: Integrated video interviews

## 📚 References

### Academic Papers
- Salton & McGill (1986): "Introduction to Modern Information Retrieval"
- Ramos (2003): "Using TF-IDF to Determine Word Relevance"

### Libraries Documentation
- Scikit-learn: https://scikit-learn.org/
- Flask: https://flask.palletsprojects.com/
- PyPDF2: https://pypdf2.readthedocs.io/

### Related Work
- LinkedIn's Talent Matching Engine
- Indeed's Job Search Algorithm
- Google Cloud Talent Solution

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Author**: National Internship Portal Team
