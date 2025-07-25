#!/usr/bin/python3
# feed.py
# Print a simple RSS feed into a terminal

import feedparser
import dateutil.parser
from datetime import datetime, timedelta
import pytz
import time
import os
from urllib.parse import urlparse
import signal
import sys
from colorama import Fore, Style

# CTRL+C
def handle_sigint(signal, frame):
    print("\nProgram stopped.")
    sys.exit(0)

# Important keywords
keywords = ["Debian","MongoDB","Ubuntu","MySQL","PostgreSQL","Veeam","ClamAV","VMware","ElasticSearch","Elasticsearch","Apache","Grafana","OpenVPN","Amazon","Google","OpenSSL","OpenSSH","Cloudflare","Nginx"]

signal.signal(signal.SIGINT, handle_sigint)

rss_urls = [
    'https://www.lemondeinformatique.fr/flux-rss/thematique/toutes-les-actualites/rss.xml',
    'https://www.cert.ssi.gouv.fr/feed/',
    'https://securite.developpez.com/index/rss',
    'https://www.it-connect.fr/actualites/actu-securite/feed/',
    'https://www.programmez.com/taxonomy/term/104/feed',
    'https://www.datasecuritybreach.fr/feed/',
    'https://www.lemonde.fr/piratage/rss_full.xml',
    'https://www.cnil.fr/fr/rss.xml',
    'https://feeds.feedburner.com/zataz/lhOa',
    'https://www.alliancy.fr/cybersecurite/feed',
    'https://www.presse-citron.net/category/cybersecurite/feed/',
    'https://www.zdnet.fr/feeds/rss/actualites/cyberattaque-4000237415q.htm',
    'https://www.archimag.com/taxonomy/term/2625/feed',
    'https://feed.infoq.com',
    'https://blog.ovhcloud.com/feed/',
    'https://www.nolimitsecu.fr/feed/',
    'https://feeds.acast.com/public/shows/radio-devops',
    'https://www.percona.com/blog/feed/',
    'https://www.nolimitsecu.fr/feed/',
    'https://azure.microsoft.com/en-us/blog/feed/',
    ]

refresh_rate = 600
# Infinite loop with a refresh every x seconds
while True:
    try:
        entries = []

        for url in rss_urls:
            feed = feedparser.parse(url)
            entries.extend(feed.entries)

        # Determine the start and end dates of the X-day period
        today = datetime.now(pytz.utc)
        start_date = today - timedelta(days=4)
        end_date = today

        # Sort entries by publication date and display only entries from the last 7 days
        sorted_entries = sorted([entry for entry in entries if hasattr(entry, 'published') and dateutil.parser.parse(entry.published).replace(tzinfo=pytz.utc) >= start_date and dateutil.parser.parse(entry.published).replace(tzinfo=pytz.utc) <= end_date], key=lambda entry: dateutil.parser.parse(entry.published).timestamp(), reverse=True)

        os.system('clear')  # Clean the term

        # Display entries sorted by publication date
        for entry in sorted_entries:
            published_date = dateutil.parser.parse(entry.published)
            formatted_date = published_date.strftime('%Y-%m-%d')
            # OK
            domain = urlparse(entry.link).netloc
            # Check Keywords
            if any(keyword in entry.title for keyword in keywords):
                title_text = Fore.YELLOW + entry.title + Style.RESET_ALL
            else:
                title_text = entry.title

            print(f"{formatted_date} [{domain}] {title_text}")
        time.sleep(refresh_rate)
        pass
    except KeyboardInterrupt:
        handle_sigint(None, None)
