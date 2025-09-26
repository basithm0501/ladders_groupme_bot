# GroupMe Internship Bot

An automated bot that fetches internship opportunities from RapidAPI and posts them to categorized GroupMe subgroups.

## Features

- 🔍 **Smart Categorization**: Automatically classifies internships into 6 categories:
  - 🖥️ CS/IT (with advanced filtering to reduce false positives)
  - 🛠️ Engineering 
  - 🩺 Health Sciences/Medical
  - ⚖️ Social Sciences/Law
  - 💼 Business
  - 🎨 Humanities

- 📱 **Multi-Message Support**: Splits large categories into multiple messages (10 jobs per message)
- 🔗 **Mobile-Friendly URLs**: Cleans LinkedIn URLs for better mobile compatibility
- 🗓️ **Date Ranges**: Shows 7-day date ranges in message headers
- 🌎 **US-Focused**: Filters for United States locations only
- 🔄 **Duplicate Removal**: Advanced similarity-based deduplication (70% threshold)

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/groupme-internship-bot.git
   cd groupme-internship-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install python-dotenv requests
   ```

3. **Create `.env` file** with your API credentials:
   ```env
   ACCESS_TOKEN=your_groupme_access_token
   GROUP_ID=your_groupme_group_id
   RAPIDAPI_KEY=your_rapidapi_key
   CS_ID=cs_subgroup_id
   ENGINEERING_ID=engineering_subgroup_id
   MED_ID=medical_subgroup_id
   LAW_ID=law_subgroup_id
   BUSINESS_ID=business_subgroup_id
   HUMANITIES_ID=humanities_subgroup_id
   ```

4. **Run the bot**:
   ```bash
   python3 groupme_internships.py
   ```

## API Requirements

- **GroupMe API**: Personal access token for posting to subgroups
- **RapidAPI Internships API**: For fetching job data

## How It Works

1. **Data Fetching**: Retrieves ~250 internship opportunities from RapidAPI
2. **Smart Filtering**: Uses regex patterns and blocklists to ensure quality categorization
3. **URL Cleaning**: Converts long LinkedIn URLs to clean format (`/jobs/view/XXXXXXXXXX`)
4. **Message Chunking**: Splits categories with >10 jobs into multiple messages
5. **GroupMe Posting**: Posts to appropriate subgroups with 1-second delays

## Configuration

### CS/IT Filtering
The bot uses advanced filtering for CS/IT roles to reduce false positives:
- **Allowed terms**: software, developer, engineer, devops, cloud, etc.
- **Blocked terms**: security guard, data entry, networking events, etc.

### Message Format
```
🖥️ New CS/IT Related Internships (Part 1/3):
======== (09/17 - 09/24) ========

1. Company Name
   Position: Software Engineer Intern
   Apply: https://www.linkedin.com/jobs/view/1234567890

2. Another Company
   Position: Frontend Developer Intern
   Apply: https://www.linkedin.com/jobs/view/0987654321
```

## Contributing

Feel free to submit issues and pull requests to improve the bot's functionality!

## License

MIT License - feel free to use and modify as needed.
