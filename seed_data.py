"""
Sample Data Seeder
Populates the database with sample internships and candidates for testing
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

# Sample Internships
sample_internships = [
    {
        "title": "Data Science Intern",
        "company": "TechCorp India",
        "location": "Bangalore, Karnataka",
        "department": "Analytics",
        "duration": "6 months",
        "stipend": "₹25,000/month",
        "workMode": "Hybrid",
        "description": "Work on cutting-edge ML projects with real-world datasets",
        "requiredSkills": "Python, Machine Learning, Pandas, NumPy, Scikit-learn",
        "requirements": "Currently pursuing B.Tech/M.Tech in CS/related field",
        "benefits": "Mentorship, Certificate, Pre-placement offer",
        "deadline": "30 days",
        "interviewProcess": "Resume Screening → Coding Test → 2 Technical Rounds",
        "mentorship": "1-on-1 mentorship with senior data scientists"
    },
    {
        "title": "Full Stack Developer Intern",
        "company": "StartupXYZ",
        "location": "Mumbai, Maharashtra",
        "department": "Engineering",
        "duration": "3 months",
        "stipend": "₹20,000/month",
        "workMode": "Remote",
        "description": "Build scalable web applications using modern tech stack",
        "requiredSkills": "React, Node.js, JavaScript, MongoDB, Express",
        "requirements": "Strong understanding of web development fundamentals",
        "benefits": "Flexible hours, Learning budget, Team outings",
        "deadline": "15 days",
        "interviewProcess": "Resume Screening → Assignment → Technical Interview",
        "mentorship": "Weekly code reviews and pairing sessions"
    },
    {
        "title": "AI Research Intern",
        "company": "IIT Bombay Research Lab",
        "location": "Mumbai, Maharashtra",
        "department": "Computer Vision Lab",
        "duration": "6 months",
        "stipend": "₹30,000/month",
        "workMode": "On-site",
        "description": "Research on computer vision and deep learning applications",
        "requiredSkills": "Python, TensorFlow, PyTorch, Deep Learning, Computer Vision",
        "requirements": "Master's student or final year B.Tech with research interest",
        "benefits": "Research paper publication, Conference opportunities, Academic credit",
        "deadline": "45 days",
        "interviewProcess": "Resume Screening → Research presentation → Faculty interview",
        "mentorship": "Direct guidance from PhD students and professors"
    },
    {
        "title": "Product Management Intern",
        "company": "Flipkart",
        "location": "Bangalore, Karnataka",
        "department": "Product",
        "duration": "4 months",
        "stipend": "₹35,000/month",
        "workMode": "On-site",
        "description": "Drive product initiatives for India's largest e-commerce platform",
        "requiredSkills": "Product Analytics, SQL, User Research, Agile, Communication",
        "requirements": "MBA/B.Tech final year, strong analytical skills",
        "benefits": "PPO, Networking, Product launch experience",
        "deadline": "20 days",
        "interviewProcess": "Resume Screening → Case study → Product rounds",
        "mentorship": "Shadow senior PMs and lead mini-projects"
    },
    {
        "title": "DevOps Intern",
        "company": "Infosys",
        "location": "Pune, Maharashtra",
        "department": "Cloud Infrastructure",
        "duration": "6 months",
        "stipend": "₹18,000/month",
        "workMode": "Hybrid",
        "description": "Automate deployment pipelines and manage cloud infrastructure",
        "requiredSkills": "AWS, Docker, Kubernetes, CI/CD, Linux, Python",
        "requirements": "Understanding of cloud computing and automation",
        "benefits": "AWS certification, Training programs, Full-time offer",
        "deadline": "60 days",
        "interviewProcess": "Resume Screening → Technical test → HR round",
        "mentorship": "Training program with hands-on projects"
    },
    {
        "title": "UI/UX Design Intern",
        "company": "Zomato",
        "location": "Gurgaon, Haryana",
        "department": "Design",
        "duration": "3 months",
        "stipend": "₹22,000/month",
        "workMode": "Remote",
        "description": "Design delightful user experiences for millions of users",
        "requiredSkills": "Figma, Adobe XD, User Research, Prototyping, Design Thinking",
        "requirements": "Portfolio showcasing UX/UI projects",
        "benefits": "Design mentorship, Portfolio building, Stipend",
        "deadline": "25 days",
        "interviewProcess": "Portfolio review → Design challenge → Team interview",
        "mentorship": "Work directly with senior designers on live projects"
    }
]

# Sample Candidates
sample_candidates = [
    {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "phone": "+91 98765 43210",
        "education": "B.Tech Computer Science",
        "institution": "IIT Delhi",
        "graduationYear": "2026",
        "skills": "Python, Machine Learning, TensorFlow, Data Analysis, SQL",
        "experience": "Completed ML course from Coursera, worked on 3 projects",
        "interests": "Deep Learning, Computer Vision, AI Research",
        "availability": "Immediate",
        "workMode": "Hybrid",
        "certifications": "Google Machine Learning Crash Course, AWS Cloud Practitioner",
        "portfolio": "https://rahulsharma.dev",
        "linkedin": "linkedin.com/in/rahulsharma",
        "github": "github.com/rahulsharma",
        "resumeScore": 88
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "+91 87654 32109",
        "education": "B.Tech Information Technology",
        "institution": "NIT Trichy",
        "graduationYear": "2025",
        "skills": "React, JavaScript, Node.js, MongoDB, HTML, CSS",
        "experience": "Built 5 full-stack projects, freelanced for 2 startups",
        "interests": "Web Development, Cloud Computing, Open Source",
        "availability": "From June 2025",
        "workMode": "Remote",
        "certifications": "Meta React Developer, Full Stack Development - Udemy",
        "portfolio": "https://priyapatel.com",
        "linkedin": "linkedin.com/in/priyapatel",
        "github": "github.com/priyapatel",
        "resumeScore": 92
    },
    {
        "name": "Arjun Reddy",
        "email": "arjun.reddy@example.com",
        "phone": "+91 76543 21098",
        "education": "MBA (Marketing)",
        "institution": "IIM Ahmedabad",
        "graduationYear": "2026",
        "skills": "Product Management, SQL, Data Analytics, Market Research, Agile",
        "experience": "Summer internship at Paytm, led 2 product launches",
        "interests": "Product Strategy, User Experience, Growth Hacking",
        "availability": "Immediate",
        "workMode": "On-site",
        "certifications": "Product Management - Product School, Google Analytics",
        "portfolio": "https://arjunreddy.in",
        "linkedin": "linkedin.com/in/arjunreddy",
        "github": "github.com/arjunreddy",
        "resumeScore": 85
    }
]

def seed_internships():
    """Seed sample internships"""
    print("🌱 Seeding internships...")
    for internship in sample_internships:
        try:
            response = requests.post(f"{BASE_URL}/save-internship", json=internship)
            if response.status_code == 200:
                print(f"✅ Added: {internship['title']} at {internship['company']}")
            else:
                print(f"❌ Failed: {internship['title']}")
        except Exception as e:
            print(f"❌ Error adding {internship['title']}: {str(e)}")

def seed_candidates():
    """Seed sample candidates"""
    print("\n🌱 Seeding candidates...")
    for candidate in sample_candidates:
        try:
            response = requests.post(f"{BASE_URL}/save-candidate-profile", json=candidate)
            if response.status_code == 200:
                print(f"✅ Added: {candidate['name']}")
            else:
                print(f"❌ Failed: {candidate['name']}")
        except Exception as e:
            print(f"❌ Error adding {candidate['name']}: {str(e)}")

def check_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy and running\n")
            return True
        return False
    except:
        print("❌ Server is not running!")
        print("Please start the Flask server first: python app.py\n")
        return False

def main():
    print("=" * 60)
    print("   National Internship Portal - Data Seeder")
    print("=" * 60)
    print()
    
    if not check_health():
        return
    
    seed_internships()
    seed_candidates()
    
    print("\n" + "=" * 60)
    print("✅ Data seeding completed successfully!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   - {len(sample_internships)} internships added")
    print(f"   - {len(sample_candidates)} candidates added")
    print("\n🎯 You can now test the matching algorithm!")
    print("   Visit: http://localhost:5000\n")

if __name__ == "__main__":
    main()
