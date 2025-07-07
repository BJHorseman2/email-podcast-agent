#!/bin/bash
# Setup Daily Automation for BOTH Newsletters

echo "🎯 Setting up dual newsletter automation..."
echo ""
echo "This will process:"
echo "   📧 Mando Minutes - arrives ~7:30 AM, processed at 7:45 AM"
echo "   📧 Puck News - arrives variable time, processed at 8:30 AM"
echo ""
echo "Both are completely separate newsletters with their own podcasts!"
echo ""

# Make scripts executable
chmod +x dual_newsletter_automation.py
chmod +x process_mando_now.py

# Show cron setup
echo "To enable daily automation, add these lines to your crontab:"
echo ""
echo "# Mando Minutes - Check at 7:45 AM"
echo "45 7 * * * cd /Users/markbaumrind/Desktop/email_podcast_agent && /usr/bin/python3 -c 'from dual_newsletter_automation import DualNewsletterAutomation; a = DualNewsletterAutomation(); a.process_newsletter(a.config[\"newsletters\"][0])' >> cron_mando.log 2>&1"
echo ""
echo "# Puck News - Check at 8:30 AM"
echo "30 8 * * * cd /Users/markbaumrind/Desktop/email_podcast_agent && /usr/bin/python3 -c 'from dual_newsletter_automation import DualNewsletterAutomation; a = DualNewsletterAutomation(); a.process_newsletter(a.config[\"newsletters\"][1])' >> cron_puck.log 2>&1"
echo ""
echo "To edit crontab: crontab -e"
echo ""
echo "Or run continuously with scheduling:"
echo "python3 dual_newsletter_automation.py --schedule"
