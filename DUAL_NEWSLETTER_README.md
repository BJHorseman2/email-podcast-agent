# Dual Newsletter Automation Setup

## ✅ What's Been Set Up

You now have automation for **TWO COMPLETELY SEPARATE** newsletters:

### 1. 📧 Mando Minutes
- **Sender**: `hello@www.mandominutes.com`
- **Arrives**: ~7:30 AM daily
- **Processed**: 7:45 AM
- **Features**: Link following to fetch full article content
- **Style**: Fast-paced crypto/markets briefing

### 2. 📧 Puck News (Jon Kelly)
- **Sender**: `jonkelly@puck.news`
- **Arrives**: Variable (6-11 AM)
- **Processed**: 8:30 AM
- **Features**: Standard processing
- **Style**: In-depth analysis and commentary

## 🚀 How to Use

### Process Today's Mando Minutes Right Now:
```bash
python3 process_mando_now.py
```

### Process Both Newsletters:
```bash
python3 dual_newsletter_automation.py
```

### Enable Daily Automation:
```bash
chmod +x setup_dual_automation.sh
./setup_dual_automation.sh
# Follow the crontab instructions
```

## 📁 Files Created

- `dual_newsletter_automation.py` - Main automation that handles both newsletters
- `multi_newsletter_config.json` - Configuration for both newsletters
- `process_mando_now.py` - Quick script to process today's Mando
- `setup_dual_automation.sh` - Setup script for cron jobs

## ⚙️ Configuration

The system is configured to:
1. Check for Mando Minutes at 7:45 AM
2. Check for Puck News at 8:30 AM
3. Create separate podcasts for each
4. Send separate emails with appropriate subjects
5. Use link following for Mando (to get article content)

## 🔧 Customization

Edit `multi_newsletter_config.json` to:
- Adjust check times
- Change email subjects
- Add more newsletters
- Modify podcast styles

## 📊 What Happens Each Day

1. **7:45 AM**: System checks for Mando Minutes
   - Finds email from `hello@www.mandominutes.com`
   - Extracts links and fetches article content
   - Creates 3-5 minute podcast
   - Sends "Your Mando Minutes Podcast" email

2. **8:30 AM**: System checks for Puck News
   - Finds email from `jonkelly@puck.news`
   - Processes newsletter content
   - Creates podcast
   - Sends "Your Puck News Podcast" email

Both run independently - if one fails, the other still processes!
