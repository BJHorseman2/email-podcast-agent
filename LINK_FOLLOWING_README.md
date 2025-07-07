# Link-Following Enhancement for Email to Podcast Agent

## 🎯 Problem Solved
Your Mando Minutes newsletter (and similar link digests) only contain link titles in the email body. The actual news content is on external websites. This enhancement follows those links and includes the actual article content in your podcasts!

## 🚀 New Features

### 1. **Automatic Link Extraction**
- Extracts all URLs from email content (both HTML and plain text)
- Filters out social media, tracking, and unsubscribe links
- Prioritizes trusted news sources (Bloomberg, Reuters, CoinDesk, etc.)

### 2. **Smart Article Fetching**
- Fetches content from up to 10 most relevant links per email
- Uses concurrent processing for faster retrieval
- Handles timeouts and errors gracefully

### 3. **Content Extraction**
- Intelligently extracts article text from various website formats
- Removes ads, navigation, and other non-content elements
- Limits content to 500 words per article for podcast brevity

### 4. **Enhanced Podcast Scripts**
- Includes actual article content, not just link titles
- Groups articles by topic (Crypto, Markets, General News)
- Provides source attribution for each story

## 📁 New Files

- `link_following_agent.py` - Core link-following functionality
- `mando_minutes_agent.py` - Specialized agent for Mando Minutes
- `test_link_following.py` - Test script with examples
- `requirements_enhanced.txt` - Updated dependencies
- `setup_link_following.sh` - Quick setup script

## 🔧 Installation

```bash
# Install dependencies
pip install -r requirements_enhanced.txt

# Run setup script
chmod +x setup_link_following.sh
./setup_link_following.sh
```

## 💡 Usage

### For Mando Minutes specifically:
```bash
python mando_minutes_agent.py
```

### To upgrade existing agents:
Replace your current agent class inheritance from:
```python
class YourAgent:
```

To:
```python
from link_following_agent import LinkFollowingNewsletterAgent

class YourAgent(LinkFollowingNewsletterAgent):
```

## 📊 Example Output

**Before (without link following):**
```
"Today's stories:
- Early BTC whales shed $50b BTC: Bloomberg
- Bessent targets Mid-July for stablecoin law
- Trump's tariff letters set to start today"
```

**After (with link following):**
```
"Story 1: Bitcoin Whales Offload $50 Billion in Historic Selloff
From bloomberg.com

Longtime Bitcoin holders, known as 'whales,' have sold approximately $50 billion worth of the cryptocurrency in recent weeks, marking one of the largest selloffs in Bitcoin's history. According to blockchain analytics data, wallets that have held Bitcoin since 2011-2013 have become active, moving substantial amounts to exchanges. Analysts suggest this could signal profit-taking ahead of potential market volatility...

Story 2: Treasury Nominee Bessent Eyes July Timeline for Stablecoin Legislation
From coindesk.com

Scott Bessent, nominated for Treasury Secretary, indicated during Senate hearings that comprehensive stablecoin regulation could be finalized by mid-July. The proposed framework would establish federal oversight for dollar-backed digital currencies, requiring issuers to hold reserves in cash and short-term Treasuries..."
```

## ⚙️ Configuration

Add these to your email config for better Mando Minutes handling:
```json
{
  "newsletter_name": "mando_minutes",
  "trusted_domains": ["puck.news", "axios.com", "semafor.com"],
  "max_articles_to_fetch": 10,
  "article_word_limit": 500
}
```

## 🎯 Perfect For

- **Mando Minutes** - Crypto and markets link digest
- **Morning Brew** - Business news roundup
- **Axios Newsletters** - Brief news with "Go deeper" links
- **The Hustle** - Tech and business links
- **Any newsletter that's mostly links!**

## 🔒 Respects Paywalls

The agent respects website paywalls and terms of service. It will only fetch publicly accessible content. For paywalled articles, it will include the title and note that full content requires a subscription.

## 📈 Performance

- Fetches 5-10 articles in ~10-15 seconds
- Concurrent processing for efficiency
- Caches results to avoid refetching
- Handles failures gracefully

## 🐛 Troubleshooting

If links aren't being fetched:
1. Check internet connection
2. Verify the links are accessible in a browser
3. Some sites may block automated requests
4. Check the log files for specific errors

## 🚀 Next Steps

1. Run the Mando Minutes agent to test with your actual emails
2. Listen to the enhanced podcasts with full article content
3. Customize the article selection and length to your preferences
4. Add more trusted domains for your specific newsletters
