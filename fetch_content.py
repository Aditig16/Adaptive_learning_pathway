import json
import os
from google import genai
from collections import defaultdict
from googleapiclient.discovery import build
from dotenv import load_dotenv
from google.genai import types


load_dotenv()
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=youtube_api_key)


MAX_VIDEOS_PER_SKILL = 3
MAX_TITLE_LEN = 80
MAX_DESC_LEN = 120
TOKEN_LIMIT_SOFT = 12000

TIMELINE_MAP = {
    "1-3 months": 8,
    "3–6 months": 12,
    "6–12 months": 20,
    "< 1 months": 3,
    "1+ year": 24
}
def content_generation(user):
    skills=load_skills()
    weak_skills_score=calculate_weak_skills(skills)
    roadmap={}
    for skill,score in weak_skills_score.items():
        videos = fetch_youtube_videos(skill)
        roadmap[skill] = {
            "score": score,
            "videos": videos
        }
    prompt=build_prompt(user['target_role'],TIMELINE_MAP.get(str(user['timelines']).strip(), 8), roadmap)
    return prompt
    
def calculate_weak_skills(gap):
    weak_skills_scores={}
    for skill, score in gap.items():
        if(score<75):
            weak_skills_scores[skill]=score        
    return weak_skills_scores

def fetch_youtube_videos(skill,maxResults=3):
    request = youtube.search().list(
        q=f"{skill} tutorial",
        part="snippet",
        maxResults= maxResults,
        type="video"
    )

    response = request.execute()

    videos = []
    for item in response.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "url": f"https://youtube.com/watch?v={item['id']['videoId']}"
        })
    return videos

##############################################
    # TO DO : Should load weak skills from DB
##############################################  
     
def load_skills(path="weak_skills.json"):
    with open(path, "r") as f:
        return json.load(f)

def estimate_tokens(text: str) -> int:
    return len(text) // 4


def trim(text, limit):
    if not text:
        return ""
    text = str(text).strip()
    return text[:limit]


def compress_data(weak_skills_data):
    """
    Input:
    {
      "SQL": {"score": 40, "videos": [...]}
    }
    """

    compressed = {}

    for skill, data in list(weak_skills_data.items()):

        videos = data.get("videos", [])[:MAX_VIDEOS_PER_SKILL]

        seen = set()
        clean_videos = []

        for v in videos:
            title = trim(v.get("title"), MAX_TITLE_LEN)
            desc = trim(v.get("description"), MAX_DESC_LEN)
            url = v.get("url", "")

            if title.lower() in seen:
                continue
            seen.add(title.lower())

            clean_videos.append({
                "t": title,
                "d": desc,
                "u": url
            })

        compressed[skill] = {
            "score": data.get("score", 0),
            "videos": clean_videos
        }

    return compressed


def build_prompt(role, timeline_weeks, weak_skills_data):
    """
    timeline_weeks → user goal duration (VERY IMPORTANT CONTROL SIGNAL)
    """

    compressed = compress_data(weak_skills_data)

    payload = {
        "role": role,
        "timeline_weeks": timeline_weeks,
        "skills": compressed
    }

    prompt = f"""
You are an expert adaptive learning system.

INPUT JSON:
{json.dumps(payload, indent=2)}

────────────────────────
TASK:
────────────────────────

────────────────────
STRICT RULES:
────────────────────
1. timeline_weeks is FIXED = {timeline_weeks}
2. Create ONE unified learning plan across ALL skills
3. Weeks MUST be sequential from 1 to {timeline_weeks}
4. DO NOT skip, merge, or add extra weeks
5. DO NOT create separate timelines per skill

────────────────────
CRITICAL RESOURCE RULE:
────────────────────
- Each skill contains "videos" with URLs
- You MUST use ONLY these provided videos
- DO NOT generate new links
- Every week MUST include at least 1 video link from input

────────────────────
TASK RULES:
────────────────────
- tasks MUST include video links inside text
- format each task like:
  "Watch: TITLE (URL)"
- do NOT separate links into another field

────────────────────
OTHER RULES
────────────────────

1. Adjust learning depth based on timeline:
   - short timeline → focus only fundamentals
   - medium timeline → balanced theory + practice
   - long timeline → deep mastery + projects

2. Summarize provided learning resources briefly
3. The reason should explain why the user is suggested to learn the skill, based on the score he received
4. RESOURCE SUMMARY Should briefly summarize the contents of the videos using the descriptions provided

────────────────────────
OUTPUT RULES:
────────────────────────
- Return ONLY valid JSON
- Keep explanation short
- No markdown
- No extra text

────────────────────────
OUTPUT FORMAT:
────────────────────────
{{
  "timeline_weeks": {timeline_weeks},
  "learning_path": [
    {{
      "skill": "",
      "reason": "",
      "resource_summary": "",
      "weekly_plan": [
        {{
          "week": 1,
          "focus": "",
          "TASK": []
        }}
      ]
    }}
  ]
}}
"""

    if estimate_tokens(prompt) > TOKEN_LIMIT_SOFT:
        print("Warning: prompt may exceed token limit")

    return prompt