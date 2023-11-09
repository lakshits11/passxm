import re

def extract_main_website(website_url):
    # Define the regular expression pattern to match the main website domain
    pattern = r"^(?:https?://)?(?:www\.)?([^:/\n?]+)"

    match = re.search(pattern, website_url)
    if match:
        main_website = match.group(1)
        return main_website
    else:
        return None