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


MAX_VIDEOS_PER_SKILL = 1
MAX_TITLE_LEN = 80
MAX_DESC_LEN = 120
TOKEN_LIMIT_SOFT = 12000

TIMELINE_MAP = {
    "1-3 months": 8,
    "3-6 months": 12,
    "6-12 months": 20,
    "< 1 months": 3,
    "1+ year": 24
}

def content_generation(user, assessment_report,missing_skills, mode):
    weak_skills_score = calculate_weak_skills(
        assessment_report
    )
    all_skills = {}
    for skill, score in weak_skills_score.items():
        all_skills[skill] = {
        "score": score,
        "attempted": True
    }
    if missing_skills:
        for skill in missing_skills:
            if skill not in all_skills:
                all_skills[skill] = {
                "score": 0,
                "attempted":False
            }
    roadmap={}
    for skill,score in all_skills.items():
        videos = fetch_youtube_videos(skill)
        roadmap[skill] = {
            "score": score,
            "videos": videos
        }
    prompt=build_prompt(user['target_role'],TIMELINE_MAP.get(str(user['timelines']).strip(), 8), roadmap, mode)
    return prompt
    
def calculate_weak_skills(gap):
   weak_skills_scores={}
   for skill, score in gap.items():
       if(score<75):
           weak_skills_scores[skill]=score        
   return weak_skills_scores

def fetch_youtube_videos(skill,maxResults=1):
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


def build_prompt(role, timeline_weeks, weak_skills_data, mode):
    """
    timeline_weeks → user goal duration (VERY IMPORTANT CONTROL SIGNAL)
    """

    compressed = compress_data(weak_skills_data)

    payload = {
        "role": role,
        "timeline_weeks": timeline_weeks,
        "skills": compressed,
        "mode":mode
    }

    prompt = f"""
You are an expert adaptive learning system.

INPUT JSON:
{json.dumps(payload, indent=2)}


TASK:-

STRICT RULES:-

WEEK STRUCTURE RULES:-

- Weeks are fixed from 1 to timeline_weeks
- Each week must contain at least 1 TASK
- Tasks must be distributed evenly across all weeks
- A week may contain multiple skills and multiple tasks
- Avoid clustering too much content in early weeks
- Ensure no week is empty or overloaded

MODE:-
If mode = "initial":
- Assume user is starting fresh
- Teach from fundamentals => advanced
- Build complete progression for all skills

If mode = "reassessment":
- User already followed a previous roadmap
- DO NOT restart basics unless score < 30

SKILL RULES:-
Each skill has:
- attempted (boolean)
- score (0-100)

If attempted = False:
- no prior knowledge => teach basics first (foundation)

If attempted = True:
- some knowledge => focus on gaps, reinforcement and improvement

CRITICAL RESOURCE RULE:-

- Each skill contains "videos" with URLs
- You MUST use ONLY these provided videos
- DO NOT generate new links
- Every week MUST include at least 1 video link from input

TASK RULES:-

- tasks MUST include video links inside text
- format each task like:
  "Watch: TITLE (URL)"
- do NOT separate links into another field

OTHER RULES:-

1. Adjust learning depth based on timeline:
   - short timeline => focus only fundamentals
   - medium timeline => balanced theory + practice
   - long timeline => deep mastery + projects
2. Summarize provided learning resources briefly
3. RESOURCE SUMMARY Should briefly summarize the contents of the videos using the descriptions provided


OUTPUT RULES:-

- Return ONLY valid JSON
- Keep explanation short
- No markdown
- No extra text


OUTPUT FORMAT:-

{{
  "timeline_weeks": {timeline_weeks},
  "reason": ""3-4 line summary of overall skill gaps"",
  "learning_path": [
    {{
      "skill": "",
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