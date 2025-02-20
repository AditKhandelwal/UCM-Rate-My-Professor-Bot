import json
import requests
from bs4 import BeautifulSoup

# -------------------------------------------
# 1) LOAD LEGACY IDS FROM JSON
# -------------------------------------------
def load_legacy_ids(json_file="legacyIds.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    name_to_id = {}
    for entry in data:
        for prof_name, legacy_id in entry.items():
            key = prof_name.lower()
            name_to_id[key] = legacy_id
    return name_to_id


# -------------------------------------------
# 2) SCRAPE PROFESSOR PAGE
# -------------------------------------------
import requests
from bs4 import BeautifulSoup

def scrape_professor_page(legacy_id):
    url = f"https://www.ratemyprofessors.com/professor/{legacy_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
        # Possibly add a Cookie if get "Unauthorized"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) Department
    dept_elem = soup.select_one("span.TeacherTitles__StyledDepartmentName-new3kl-2.fPrYfD")
    department = dept_elem.get_text(strip=True) if dept_elem else "N/A"

    # 2) Would Take Again & Difficulty
    feedback_items = soup.select("div.TeacherFeedback__StyledTeacherFeedback-gzhlj7-0.cTOmHU > div.FeedbackItem__StyledFeedbackItem-uof32n-0.dTFbKx")
    would_take_again = "N/A"
    difficulty = "N/A"
    if len(feedback_items) >= 2:
        wta_elem = feedback_items[0].select_one(".FeedbackItem__FeedbackNumber-uof32n-1.kkESWs")
        if wta_elem:
            would_take_again = wta_elem.get_text(strip=True)

        diff_elem = feedback_items[1].select_one(".FeedbackItem__FeedbackNumber-uof32n-1.kkESWs")
        if diff_elem:
            difficulty = diff_elem.get_text(strip=True)

    # 3) Top Tags
    tags_container = soup.select_one("div.TeacherTags__TagsContainer-sc-16vmh1y-0.cgUwDc")
    top_tags = []
    if tags_container:
        tag_spans = tags_container.select("span.Tag-bs9vf4-0.hHOVKF")
        top_tags = [t.get_text(strip=True) for t in tag_spans]

    # 4) Latest 3 Ratings
    ratings_list = soup.select("li .Rating__StyledRating-sc-1rhvpxz-1.jcIQzP")
    latest_ratings = []
    for rating in ratings_list[:3]:
        comment_elem = rating.select_one("div.Comments__StyledComments-dzzyvm-0.gRjWel")
        comment_text = comment_elem.get_text(strip=True) if comment_elem else ""

        quality_elem = rating.select_one(".CardNumRating__CardNumRatingNumber-sc-17t4b9u-2.bUneqk")
        quality = quality_elem.get_text(strip=True) if quality_elem else "N/A"

        diff_elem = rating.select_one(".CardNumRating__CardNumRatingNumber-sc-17t4b9u-2.cDKJcc")
        diff = diff_elem.get_text(strip=True) if diff_elem else "N/A"

        date_elem = rating.select_one(".TimeStamp__StyledTimeStamp-sc-9q2r30-0.bXQmMr")
        date_text = date_elem.get_text(strip=True) if date_elem else ""

        course_elem = rating.select_one(".RatingHeader__StyledClass-sc-1dlkqw1-3.eXfReS")
        course_code = course_elem.get_text(strip=True) if course_elem else ""

        latest_ratings.append({
            "date": date_text,
            "course": course_code,
            "quality": quality,
            "difficulty": diff,
            "comment": comment_text
        })

    return {
        "legacyId": legacy_id,
        "department": department,
        "wouldTakeAgain": would_take_again,
        "difficulty": difficulty,
        "topTags": top_tags,
        "latestRatings": latest_ratings
    }


# -------------------------------------------
# 3) MAIN: QUERY BY NAME, PRINT RESULTS
# -------------------------------------------
def getProfessorInfo(prof_name):
    name_to_id = load_legacy_ids("legacyIds.json")
    # Make it so name is NOT case sensitive
    key = prof_name.lower()
    # Look up the legacy ID
    if key not in name_to_id:
        return "invalid"
    legacy_id = name_to_id[key]
    # Scrape the professor's page
    details = scrape_professor_page(legacy_id)
    return (json.dumps(details, indent=2))