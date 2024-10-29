# LinkedIn Profile Photo Scraper

A Python-based automation tool for extracting profile photos from LinkedIn profiles with built-in CAPTCHA handling capabilities.

## Features

- Automated LinkedIn login with anti-detection measures
- Multiple CAPTCHA handling strategies
- Human-like behavior simulation
- Comprehensive logging
- Cookie management for session persistence
- Configurable delays and timeouts

## Prerequisites

- Python 3.7+
- Chrome browser installed
- LinkedIn account credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-photo-scraper.git
cd linkedin-photo-scraper
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your LinkedIn credentials:
```
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
```

## Usage

Run the script:
```bash
python linkedin_scraper.py
```

The script will:
1. Log in to LinkedIn using provided credentials
2. Navigate to the specified profile
3. Extract the profile photo URL
4. Save the results to `out.log`

## CAPTCHA Handling

The scraper implements multiple strategies for handling CAPTCHA:
1. Cookie Authentication
2. Stealth Mode (human-like behavior)
3. Manual Solving (with configurable timeout)

## Configuration

Key timeouts and delays can be configured by modifying the constants at the top of the script:
- `CAPTCHA_TIMEOUT`: Maximum time to wait for manual CAPTCHA solving
- `LOGIN_WAIT_TIMEOUT`: Time to wait for login elements
- `TYPE_DELAY_MIN/MAX`: Delays between keystrokes
- `PAGE_LOAD_DELAY_MIN/MAX`: Delays after page loads

## Logging

All operations are logged to `out.log` with timestamps and severity levels.

## Security Notes

- Store LinkedIn credentials in the `.env` file (not included in version control)
- Regularly update cookies to maintain session validity
- Use responsibly and in accordance with LinkedIn's terms of service

## Disclaimer

This tool is for educational purposes only. Use it responsibly and in accordance with LinkedIn's terms of service and robots.txt directives.