"""
Comprehensive testing script for Career Compass backend.
Tests all endpoints: health, extract-skills, match-jobs, analyze-gaps, extract-from-pdf
"""

import requests
import json
import sys
from pathlib import Path

API_URL = "http://localhost:8000"

def print_result(test_name: str, passed: bool, message: str = ""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status} | {test_name}")
    if message:
        print(f"       {message}")


def test_health():
    """Test GET /health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result("Health Check", True, f"Status: ok, Jobs in DB: {data.get('job_count')}")
            return True
        else:
            print_result("Health Check", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False


def test_extract_skills():
    """Test POST /api/extract-skills endpoint"""
    try:
        text = "I have worked with Python, SQL, and Power BI. I also know Azure and have used pandas for data analysis."
        response = requests.post(
            f"{API_URL}/api/extract-skills",
            json={"text": text},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            skills = data.get("skills", [])
            if len(skills) > 0:
                print_result("Extract Skills", True, f"Found {len(skills)} skills: {', '.join(skills[:5])}")
                return True
            else:
                print_result("Extract Skills", False, "No skills extracted")
                return False
        else:
            print_result("Extract Skills", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("Extract Skills", False, str(e))
        return False


def test_match_jobs():
    """Test POST /api/match-jobs endpoint"""
    try:
        skills = ["python", "sql", "power bi", "azure"]
        response = requests.post(
            f"{API_URL}/api/match-jobs",
            json={"skills": skills},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            if len(matches) > 0:
                top_match = matches[0]
                score = top_match.get("score", 0)
                title = top_match.get("title", "Unknown")
                print_result(
                    "Match Jobs",
                    True,
                    f"Found {len(matches)} matches. Top: {title} ({int(score*100)}%)"
                )
                return True
            else:
                print_result("Match Jobs", False, "No matches found")
                return False
        else:
            print_result("Match Jobs", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("Match Jobs", False, str(e))
        return False


def test_analyze_gaps():
    """Test POST /api/analyze-gaps endpoint"""
    try:
        job = {
            "title": "Data Analyst",
            "skills_required": "Python, SQL, Power BI, Tableau",
            "raw_description": "We are looking for a Data Analyst with 2+ years experience in SQL, Python, and data visualization tools like Power BI or Tableau."
        }
        student_skills = ["python", "sql"]
        response = requests.post(
            f"{API_URL}/api/analyze-gaps",
            json={"job": job, "student_skills": student_skills},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            missing = data.get("missing_skills", [])
            week1 = data.get("week1", "")
            if missing and week1:
                print_result(
                    "Analyze Gaps",
                    True,
                    f"Missing skills: {', '.join(missing)}. Week 1 plan available."
                )
                return True
            else:
                print_result("Analyze Gaps", False, "Incomplete response")
                return False
        else:
            print_result("Analyze Gaps", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("Analyze Gaps", False, str(e))
        return False


def test_extract_from_pdf():
    """Test POST /api/extract-from-pdf endpoint"""
    try:
        # Create a simple test PDF (requires reportlab)
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io

        # Create PDF in memory
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, "I have 5 years experience with Python and SQL.")
        c.drawString(100, 730, "I am skilled in Data Analysis, Machine Learning, and Azure Cloud.")
        c.drawString(100, 710, "I have worked with Pandas, NumPy, and scikit-learn.")
        c.save()
        pdf_buffer.seek(0)

        # Send PDF to API
        files = {"file": ("test_resume.pdf", pdf_buffer, "application/pdf")}
        response = requests.post(
            f"{API_URL}/api/extract-from-pdf",
            files=files,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            text = data.get("text", "")
            skills = data.get("skills", [])
            if text and len(skills) > 0:
                print_result(
                    "Extract From PDF",
                    True,
                    f"Extracted {len(skills)} skills from PDF: {', '.join(skills[:5])}"
                )
                return True
            else:
                print_result("Extract From PDF", False, "No skills extracted from PDF")
                return False
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_result("Extract From PDF", False, f"Status {response.status_code}: {error_detail}")
            return False
    except ImportError:
        print_result("Extract From PDF", False, "reportlab not installed (optional for testing)")
        return None
    except Exception as e:
        print_result("Extract From PDF", False, str(e))
        return False


def main():
    print("=" * 70)
    print("CAREER COMPASS — BACKEND TESTING SUITE")
    print("=" * 70)
    print(f"\nTarget API: {API_URL}")
    print("\nMake sure FastAPI is running: uvicorn main:app --reload\n")

    results = {}

    print("\n--- TESTING ENDPOINTS ---")
    results["health"] = test_health()
    results["extract_skills"] = test_extract_skills()
    results["match_jobs"] = test_match_jobs()
    results["analyze_gaps"] = test_analyze_gaps()
    results["extract_pdf"] = test_extract_from_pdf()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)

    for test_name, result in results.items():
        status = "✓" if result is True else ("✗" if result is False else "⊘")
        print(f"{status} {test_name}")

    print("\n" + "-" * 70)
    print(f"Passed: {passed}/{total} | Failed: {failed}/{total} | Skipped: {skipped}/{total}")
    print("=" * 70)

    if failed == 0:
        print("\n✓ All tests passed! Your backend is ready.")
        sys.exit(0)
    else:
        print(f"\n✗ {failed} test(s) failed. Check your backend setup.")
        sys.exit(1)


if __name__ == "__main__":
    main()
