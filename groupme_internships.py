import os
import json
import urllib.request
import ssl
import time
import uuid
from dotenv import load_dotenv
import re
import requests
from datetime import date, timedelta

# POST TO GROUPME LOGIC
load_dotenv()
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")
API_URL = "https://api.groupme.com/v3/bots/post"
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
CS_ID = os.environ.get("CS_ID")
ENGINEERING_ID = os.environ.get("ENGINEERING_ID")
MED_ID = os.environ.get("MED_ID")
LAW_ID = os.environ.get("LAW_ID")
BUSINESS_ID = os.environ.get("BUSINESS_ID")
HUMANITIES_ID = os.environ.get("HUMANITIES_ID")

def get_week_date_range():
    """Get the 7-day date range ending with today in MM/DD - MM/DD format"""
    today = date.today()
    # Start date is 7 days ago, end date is today
    start_date = today - timedelta(days=7)
    
    return f"{start_date.strftime('%m/%d')} - {today.strftime('%m/%d')}"

def chunk_jobs(jobs, chunk_size=10):
    """Split jobs into chunks of specified size"""
    for i in range(0, len(jobs), chunk_size):
        yield jobs[i:i + chunk_size]

def post_to_subgroup(text: str, subgroup_id: str):
    """Post a message directly to a subgroup using the GroupMe API"""
    if not ACCESS_TOKEN:
        print("Error: ACCESS_TOKEN must be set in .env file")
        return
    
    # Use the direct messages API for subgroups
    subgroup_api_url = f"https://api.groupme.com/v3/groups/{subgroup_id}/messages"
    
    # Generate a unique source_guid for each message to avoid conflicts
    unique_guid = str(uuid.uuid4())
    
    payload = {
        "message": {
            "source_guid": unique_guid,
            "text": text
        }
    }
    
    payload_json = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{subgroup_api_url}?token={ACCESS_TOKEN}",
        data=payload_json,
        headers={"Content-Type": "application/json"}
    )
    
    # Create SSL context to handle certificate verification issues
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            if resp.status == 201:
                print(f"Message posted successfully to subgroup {subgroup_id}!")
            else:
                print(f"Subgroup post error: {resp.status} - {resp.read().decode()}")
    except Exception as e:
        print(f"Error posting to subgroup: {e}")

# INTERNSHIP LOGIC
def get_internship_info():

    data = get_internships_data()
    if not data:
        return "No internship data available at the moment."
    data = classify_data(data)

    return data

def topic_handler(category: str, data):
    # Placeholder function to get internship information
    match category:
        case "CS/IT":
            return cs_opportunities(data)
        case "Engineering":
            return engineering_opportunities(data)
        case "Health Sciences":
            return health_sciences_opportunities(data)
        case "Social Sciences/Law":
            return social_sciences_opportunities(data)
        case "Business":
            return business_opportunities(data)
        case "Humanities":
            return humanities_opportunities(data)
        case _:
            return None

# Positive signals (strict)
CS_TOKENS = [
    r"software", r"swe", r"developer", r"programmer", r"engineer",
    r"backend", r"front[-\s]?end", r"full[-\s]?stack", r"mobile", r"ios", r"android",
    r"devops", r"sre", r"site reliability", r"platform engineer",
    r"systems engineer", r"systems administrator", r"sysadmin",
    r"cloud", r"aws", r"azure", r"gcp",
    r"data (?:engineer|scientist|platform|infrastructure)",  # NOT plain "data"
    r"ml", r"machine learning", r"artificial intelligence", r"ai",
    r"nlp", r"computer vision", r"robotics",
    r"security engineer", r"application security", r"appsec", r"product security",
    r"penetration tester", r"red team", r"blue team", r"soc analyst",
    r"network engineer", r"site reliability", r"infra(?:structure)?"
]

# False positives to exclude from CS
CS_BLOCKLIST = [
    r"security (?:officer|guard|operations|patrol|loss prevention)",
    r"physical security", r"facilities", r"custodian|janitor",
    r"warehouse|driver|courier|logistics coordinator",
    r"retail|cashier|barista|server|host|cook",
    r"event(?:s)? (?:staff|assistant|coordinator)",
    r"data entry", r"records clerk",
    r"networking (?:event|mixer)",  # social networking, not networks
]

# Helper to compile with word boundaries
def wb(patterns):
    return [re.compile(rf"\b{p}\b", re.I) for p in patterns]

CS_ALLOWED = wb(CS_TOKENS)
CS_BLOCK   = wb(CS_BLOCKLIST)


FILTERS = {
    "CS/IT": re.compile(
        r"(software|developer|programmer|coder|swe|"
        r"computer|information technology|it support|systems|sysadmin|"
        r"network|cyber|security|infosec|cloud|aws|azure|gcp|"
        r"devops|sre|full[-\s]?stack|backend|frontend|mobile|ios|android|"
        r"data|analytics|machine learning|ml|artificial intelligence|ai|"
        r"nlp|vision|robotics|blockchain|crypto)", re.I),

    "Engineering": re.compile(
        r"(mechanical|civil|structural|electrical|electronics|embedded|"
        r"biomedical|chemical|materials|aerospace|nuclear|industrial|"
        r"manufacturing|systems engineering|automotive|energy|petroleum|mining)", re.I),

    "Business": re.compile(
        r"(finance|financial|accounting|audit|tax|assurance|investment|banking|"
        r"consult|advisory|strategy|ops|operations|supply chain|logistics|"
        r"management|human resources|hr|people|talent|marketing|brand|"
        r"advertising|sales|business analyst|product manager|pm|"
        r"entrepreneurship|economics|e\-?commerce)", re.I),

    "Humanities": re.compile(
        r"(english|literature|writing|editor|publishing|communications|comm|media|"
        r"film|theater|theatre|drama|music|visual arts|fine arts|design|graphic|ux|ui|"
        r"museum|curator|history|philosophy|religion|languages|linguistics|anthropology|"
        r"cultural studies|gender studies|ethnic studies|art history)", re.I),

    "Social Sciences / Law": re.compile(
        r"(policy|public policy|government|politics|political science|international relations|"
        r"law|legal|paralegal|justice|criminology|public admin|sociology|psychology|"
        r"social work|economics|demography|urban studies|education policy)", re.I),

    "Health Sciences": re.compile(
        r"(lab|laboratory|clinical|pre[-\s]?med|medicine|medical|nursing|pharmacy|pharmacology|"
        r"public health|epidemiology|biostatistics|healthcare|dental|dentistry|veterinary|vet|"
        r"physician assistant|pa|allied health|occupational therapy|ot|physical therapy|pt|"
        r"nutrition|dietetic|kinesiology|neuroscience|immunology|oncology|pathology|"
        r"biotech|pharma|biopharma|biomedical research)", re.I),
}

def classify_data(jobs):
    classified_jobs = {
        "CS/IT": [],
        "Engineering": [],
        "Business": [],
        "Humanities": [],
        "Social Sciences / Law": [],
        "Health Sciences": [],
        # Removed "Other" category - jobs that don't fit will be skipped
    }
    
    for job in jobs:
        field = classify_job(job)
        
        # Skip jobs that don't fit into any specific category
        if field == "Other":
            continue
            
        company = job.get('organization', 'Unknown Company')  # Changed from 'company' to 'organization'
        title = job.get('title', 'Unknown Title')
        broken_link = job.get('url', 'No Link Provided')
        application_link = extract_fixed_link(broken_link)
        classified_jobs[field].append((company, title, application_link))
    
    return classified_jobs

def classify_job(job):
    text = f"{job['title']} {job.get('description','')}"
    
    # Special handling for CS/IT with stricter filtering
    if FILTERS["CS/IT"].search(text):
        # Check if any CS_ALLOWED patterns match
        has_cs_signal = any(pattern.search(text) for pattern in CS_ALLOWED)
        
        # Check if any CS_BLOCK patterns match (false positives)
        has_block_signal = any(pattern.search(text) for pattern in CS_BLOCK)
        
        # Only classify as CS/IT if we have positive signals AND no blocking signals
        if has_cs_signal and not has_block_signal:
            return "CS/IT"
        # If it matches the general CS filter but fails the strict check, 
        # continue to check other categories
    
    # Check other categories with existing filters
    for field, pat in FILTERS.items():
        if field != "CS/IT" and pat.search(text):  # Skip CS/IT since we handled it above
            return field
            
    return "Other"

def extract_fixed_link(broken_link):
    """
    Fix LinkedIn job URLs to use clean format with just the job ID.
    Convert from: https://www.linkedin.com/jobs/view/equipment-engineering-trainee-at-vestas-4302691296
    To: https://www.linkedin.com/jobs/view/4302691296
    """
    if not broken_link or broken_link == 'No Link Provided':
        return 'No Link Provided'
    
    # Check if it's a LinkedIn job URL
    if 'linkedin.com/jobs/view/' in broken_link:
        # Extract the last 10 digits (job ID) from the URL
        # Use regex to find the job ID at the end of the URL
        import re
        job_id_match = re.search(r'(\d{10})$', broken_link)
        
        if job_id_match:
            job_id = job_id_match.group(1)
            return f"https://www.linkedin.com/jobs/view/{job_id}"
    
    # If it's not a LinkedIn URL or we can't extract the ID, return original
    return broken_link

def get_internships_data():
    """Fetch internship data from the RapidAPI internships API - get ~300 jobs"""
    all_internships = []
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "internships-api.p.rapidapi.com"
    }
    
    try:
        # Make 40 requests to get approximately 400 jobs (40 * 10 = 400)
        for page in range(40):
            # Add pagination using offset parameter and location filter for United States
            url = f"https://internships-api.p.rapidapi.com/active-jb-7d?offset={page * 10}&location_filter=United States"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                internships = response.json()
                
                if internships:
                    all_internships.extend(internships)
                    print(f"Fetched page {page + 1}/40: {len(internships)} jobs (Total: {len(all_internships)})")
                else:
                    print(f"No data returned for page {page + 1}, stopping...")
                    break
            else:
                print(f"Error fetching page {page + 1}: {response.status_code} - {response.text}")
                break
            
            # Add delay between requests to be respectful to the API
            time.sleep(0.5)  # 500ms delay between requests
            
        # Remove duplicates based on similarity, not just exact matches
        unique_jobs = []
        seen = set()
        
        for job in all_internships:
            # Create a more comprehensive similarity key
            company = job.get('organization', '').lower().strip()  # Changed from 'company' to 'organization'
            title = job.get('title', '').lower().strip()
            
            # Remove common words that don't add uniqueness
            title_cleaned = re.sub(r'\b(intern|internship|summer|2024|2025|2026|student|position|role|opportunity)\b', '', title)
            title_cleaned = re.sub(r'\s+', ' ', title_cleaned).strip()  # Remove extra spaces
            
            # Create similarity key with cleaned data
            job_key = (company, title_cleaned)
            
            # Also check for very similar titles at the same company
            is_duplicate = False
            for existing_key in seen:
                existing_company, existing_title = existing_key
                
                # Same company check
                if company == existing_company:
                    # Check if titles are very similar (using basic similarity)
                    title_words = set(title_cleaned.split())
                    existing_words = set(existing_title.split())
                    
                    # If they share most words, consider it a duplicate
                    if title_words and existing_words:
                        common_words = title_words.intersection(existing_words)
                        similarity = len(common_words) / max(len(title_words), len(existing_words))
                        
                        if similarity > 0.7:  # 70% similarity threshold
                            is_duplicate = True
                            break
            
            if not is_duplicate and job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        print(f"Total unique jobs fetched: {len(unique_jobs)} (removed {len(all_internships) - len(unique_jobs)} duplicates)")
        return unique_jobs
    
    except Exception as e:
        print(f"Error fetching internship data: {e}")
        return all_internships  # Return whatever we got before the error

# CS LOGIC
def cs_opportunities(data):
    data = data["CS/IT"]
    if not data:
        return ["No new CS/IT Related internship opportunities available at the moment."]

    # Split jobs into chunks of 10
    job_chunks = list(chunk_jobs(data, 10))
    messages = []
    week_range = get_week_date_range()
    
    for chunk_num, chunk in enumerate(job_chunks, 1):
        if len(job_chunks) > 1:
            message = f"🖥️ New CS/IT Related Internships (Part {chunk_num}/{len(job_chunks)}):\n"
            message += f"======== ({week_range}) ========\n\n"
        else:
            message = "🖥️ New CS/IT Related Internships:\n"
            message += f"======== ({week_range}) ========\n\n"
        
        start_num = (chunk_num - 1) * 10 + 1
        for i, job in enumerate(chunk, start_num):
            company, job_title, application_link = job
            message += f"{i}. {company}\n"
            message += f"   Position: {job_title}\n"
            message += f"   Apply: {application_link}\n\n"
        
        messages.append(message)
    
    return messages

# ENGINEERING LOGIC
def engineering_opportunities(data):
    data = data["Engineering"]
    if not data:
        return ["No new Engineering Related internship opportunities available at the moment."]

    # Split jobs into chunks of 10
    job_chunks = list(chunk_jobs(data, 10))
    messages = []
    week_range = get_week_date_range()
    
    for chunk_num, chunk in enumerate(job_chunks, 1):
        if len(job_chunks) > 1:
            message = f"🛠️ New Engineering Related Internships (Part {chunk_num}/{len(job_chunks)}):\n"
            message += f"=========== ({week_range}) ===========\n\n"
        else:
            message = "🛠️ New Engineering Related Internships:\n"
            message += f"=========== ({week_range}) ===========\n\n"
        
        start_num = (chunk_num - 1) * 10 + 1
        for i, job in enumerate(chunk, start_num):
            company, job_title, application_link = job
            message += f"{i}. {company}\n"
            message += f"   Position: {job_title}\n"
            message += f"   Apply: {application_link}\n\n"
        
        messages.append(message)
    
    return messages

# HEALTH SCIENCES LOGIC
def health_sciences_opportunities(data):
    data = data["Health Sciences"]
    if not data:
        return ["No new Health Sciences/Med Related internship opportunities available at the moment."]

    # Split jobs into chunks of 10
    job_chunks = list(chunk_jobs(data, 10))
    messages = []
    week_range = get_week_date_range()
    
    for chunk_num, chunk in enumerate(job_chunks, 1):
        if len(job_chunks) > 1:
            message = f"🩺 New Health Sciences/Med Related Internships (Part {chunk_num}/{len(job_chunks)}):\n"
            message += f"============ ({week_range}) ============\n\n"
        else:
            message = "🩺 New Health Sciences/Med Related Internships:\n"
            message += f"============ ({week_range}) ============\n\n"
        
        start_num = (chunk_num - 1) * 10 + 1
        for i, job in enumerate(chunk, start_num):
            company, job_title, application_link = job
            message += f"{i}. {company}\n"
            message += f"   Position: {job_title}\n"
            message += f"   Apply: {application_link}\n\n"
        
        messages.append(message)
    
    return messages

# SOCIAL SCIENCES/LAW LOGIC
def social_sciences_opportunities(data):
    data = data["Social Sciences / Law"]
    if not data:
        return ["No new Social Sciences/Law Related internship opportunities available at the moment."]

    # Split jobs into chunks of 10
    job_chunks = list(chunk_jobs(data, 10))
    messages = []
    week_range = get_week_date_range()
    
    for chunk_num, chunk in enumerate(job_chunks, 1):
        if len(job_chunks) > 1:
            message = f"⚖️ New Social Sciences/Law Related Internships (Part {chunk_num}/{len(job_chunks)}):\n"
            message += f"============ ({week_range}) ============\n\n"
        else:
            message = "⚖️ New Social Sciences/Law Related Internships:\n"
            message += f"============ ({week_range}) ============\n\n"
        
        start_num = (chunk_num - 1) * 10 + 1
        for i, job in enumerate(chunk, start_num):
            company, job_title, application_link = job
            message += f"{i}. {company}\n"
            message += f"   Position: {job_title}\n"
            message += f"   Apply: {application_link}\n\n"
        
        messages.append(message)
    
    return messages

# BUSINESS LOGIC
def business_opportunities(data):
    data = data["Business"]
    if not data:
        return ["No new Business Related internship opportunities available at the moment."]

    # Split jobs into chunks of 10
    job_chunks = list(chunk_jobs(data, 10))
    messages = []
    week_range = get_week_date_range()
    
    for chunk_num, chunk in enumerate(job_chunks, 1):
        if len(job_chunks) > 1:
            message = f"💼 New Business Related Internships (Part {chunk_num}/{len(job_chunks)}):\n"
            message += f"========= ({week_range}) =========\n\n"
        else:
            message = "💼 New Business Related Internships:\n"
            message += f"========= ({week_range}) =========\n\n"
        
        start_num = (chunk_num - 1) * 10 + 1
        for i, job in enumerate(chunk, start_num):
            company, job_title, application_link = job
            message += f"{i}. {company}\n"
            message += f"   Position: {job_title}\n"
            message += f"   Apply: {application_link}\n\n"
        
        messages.append(message)
    
    return messages

# HUMANITIES LOGIC
def humanities_opportunities(data):
    data = data["Humanities"]
    if not data:
        return ["No new Humanities Related internship opportunities available at the moment."]

    # Split jobs into chunks of 10
    job_chunks = list(chunk_jobs(data, 10))
    messages = []
    week_range = get_week_date_range()
    
    for chunk_num, chunk in enumerate(job_chunks, 1):
        if len(job_chunks) > 1:
            message = f"🎨 New Humanities Related Internships (Part {chunk_num}/{len(job_chunks)}):\n"
            message += f"========== ({week_range}) ==========\n\n"
        else:
            message = "🎨 New Humanities Related Internships:\n"
            message += f"========== ({week_range}) ==========\n\n"
        
        start_num = (chunk_num - 1) * 10 + 1
        for i, job in enumerate(chunk, start_num):
            company, job_title, application_link = job
            message += f"{i}. {company}\n"
            message += f"   Position: {job_title}\n"
            message += f"   Apply: {application_link}\n\n"
        
        messages.append(message)
    
    return messages

def post_last_week_internships():
    data = get_internship_info()
    if not data:
        print("No internship data available at the moment.")
        exit(0)
    
    # CS/IT Opportunities
    cs_messages = topic_handler("CS/IT", data)
    for message in cs_messages:
        post_to_subgroup(message, CS_ID)
        time.sleep(1)

    # Engineering Opportunities
    eng_messages = topic_handler("Engineering", data)
    for message in eng_messages:
        post_to_subgroup(message, ENGINEERING_ID)
        time.sleep(1)

    # Health Sciences Opportunities
    health_messages = topic_handler("Health Sciences", data)
    for message in health_messages:
        post_to_subgroup(message, MED_ID)
        time.sleep(1)

    # Social Sciences/Law Opportunities
    social_messages = topic_handler("Social Sciences/Law", data)
    for message in social_messages:
        post_to_subgroup(message, LAW_ID)
        time.sleep(1)

    # Business Opportunities
    business_messages = topic_handler("Business", data)
    for message in business_messages:
        post_to_subgroup(message, BUSINESS_ID)
        time.sleep(1)

    # Humanities Opportunties
    humanities_messages = topic_handler("Humanities", data)
    for message in humanities_messages:
        post_to_subgroup(message, HUMANITIES_ID)
        time.sleep(1)

if __name__ == "__main__":
    post_last_week_internships()
