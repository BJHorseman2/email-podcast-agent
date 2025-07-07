# AOL Email to Podcast Agent - Setup Guide

## 🎯 CUSTOMIZED FOR YOUR AOL.COM EMAIL

This agent is specifically configured to work with AOL.com email accounts and process your specific morning email into a podcast.

## 📧 AOL Email Setup Required

### 1. Enable AOL App Password
Since AOL requires secure authentication, you need to create an app password:

1. **Sign in to your AOL Account**:
   - Go to https://login.aol.com
   - Sign in with your AOL email and password

2. **Generate App Password**:
   - Go to Account Security settings
   - Click "Generate app password"
   - Choose "Other app" and name it "Email Podcast Agent"
   - **Copy the generated password** (you'll need this for config.json)

3. **Enable IMAP Access**:
   - In AOL Mail settings, ensure IMAP access is enabled
   - This allows external applications to read your email

### 2. Configure Your Specific Email

Edit `config.json` with your details:

```json
{
  "email": {
    "username": "yourname@aol.com",
    "password": "your_app_password_here"
  },
  "target_email": {
    "sender": "newsletter@company.com",
    "subject_contains": ["daily", "morning"],
    "subject_exact": "Daily Newsletter"
  }
}
```

### 3. Email Targeting Options

Choose how to identify your specific email:

**Option A - By Sender:**
```json
"target_email": {
  "sender": "dailynews@company.com"
}
```

**Option B - By Subject Keywords:**
```json
"target_email": {
  "subject_contains": ["morning brief", "daily digest"]
}
```

**Option C - Exact Subject:**
```json
"target_email": {
  "subject_exact": "Your Daily Newsletter"
}
```

**Option D - Time Window:**
```json
"target_email": {
  "time_window": {
    "start_hour": 6,
    "end_hour": 10
  }
}
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install schedule
```

### 2. Update Configuration
1. Open `config.json`
2. Add your AOL email and app password
3. Specify your target email details

### 3. Test Connection
```bash
python3 aol_email_agent.py
```

### 4. Enable Daily Automation
```bash
python3 aol_email_agent.py --schedule
```

## 📋 Example Configuration

Here's a complete example for a daily newsletter:

```json
{
  "email": {
    "username": "john@aol.com",
    "password": "abcd-efgh-ijkl-mnop"
  },
  "target_email": {
    "sender": "newsletter@techcrunch.com",
    "subject_contains": ["daily"],
    "time_window": {
      "start_hour": 7,
      "end_hour": 9
    }
  },
  "podcast": {
    "max_length_minutes": 5,
    "intro_text": "Good morning! Here's your TechCrunch daily digest.",
    "outro_text": "Stay updated with tech news. Have a great day!"
  }
}
```

## 🔧 Advanced Features

### Email Processing
- ✅ **HTML Email Support**: Converts HTML emails to clean text
- ✅ **Smart Content Extraction**: Removes headers, footers, unsubscribe links
- ✅ **Key Point Identification**: Automatically finds bullet points and highlights
- ✅ **Content Validation**: Ensures minimum content length

### Podcast Customization
- ✅ **Custom Intro/Outro**: Personalize your podcast opening and closing
- ✅ **Duration Control**: Set maximum podcast length
- ✅ **Summary Generation**: Automatic email summarization
- ✅ **Key Points Extraction**: Highlights important information

### Automation Features
- ✅ **Daily Scheduling**: Runs automatically every morning
- ✅ **Error Handling**: Retries failed attempts
- ✅ **File Management**: Organizes and cleans up old files
- ✅ **Email Marking**: Marks processed emails as read

## 🎙️ Workflow

1. **Morning Trigger**: Agent runs at 8 AM (configurable)
2. **AOL Connection**: Securely connects to your AOL email
3. **Email Search**: Finds your specific morning email
4. **Content Processing**: Extracts and cleans email content
5. **Script Generation**: Creates engaging podcast script
6. **File Creation**: Saves content and NotebookLM instructions
7. **Podcast Ready**: Follow instructions to generate audio

## 🎯 Daily Usage

Each morning, the agent will:
1. ✅ Check your AOL inbox for the target email
2. ✅ Process the content into a podcast script
3. ✅ Create step-by-step NotebookLM instructions
4. ✅ Save everything to organized files
5. ✅ Mark the email as processed

You then simply:
1. Open the generated instruction file
2. Follow the steps to create your podcast in NotebookLM
3. Download and enjoy your personalized morning podcast!

## 🛠️ Troubleshooting

### Common Issues:

**"Authentication failed"**
- Verify your AOL app password (not regular password)
- Check username format: must include @aol.com

**"No emails found"**
- Check your target email filters
- Verify the sender/subject criteria
- Ensure the email arrived in the time window

**"Content too short"**
- Email might be mostly images or links
- Adjust minimum_content_length in config

### Support:
- Check `aol_podcast_agent.log` for detailed error messages
- Test connection first before enabling automation
- Start with broad filters, then narrow down

## ✅ Ready to Go!

Your AOL email-to-podcast agent is configured and ready. Just update the config.json with your specific email details and you'll have automated morning podcasts from your favorite newsletter!
