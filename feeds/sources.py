RSS_SOURCES = {
    # InfoNewHaven (working)
    "who_knew": "https://www.infonewhaven.com/category/who-knew-blog/feed/",
    "food_drink": "https://www.infonewhaven.com/food-drink/feed/",
    "music_arts": "https://www.infonewhaven.com/arts-entertainment/music/feed/",
    # City of New Haven feeds are currently disabled due to 403 responses.
    # "city_news": "https://www.newhavenct.gov/Home/Components/News/RSS",
    # "city_events": "https://www.newhavenct.gov/Home/Components/Calendar/Event/RSS",
    # "city_calendar_items": "https://www.newhavenct.gov/Home/Components/Calendar/Item/RSS",
    # IAFF Local 825 (scraped, not RSS)
    "iaff_headlines": "https://newhavenfire.org/index.cfm?zone=/unionactive/iaff_headline_view.cfm",
}

# InfoNewHaven iCal is currently blocked behind a JS challenge (Sucuri),
# which prevents server-side fetching. Disable for now.
ICAL_SOURCES = {
    # "events_calendar": "https://www.infonewhaven.com/things-to-do/new-haven-events-calendar/?ical=1",
}

SOURCE_CREDIT = {
    "site": "InfoNewHaven.com",
    "url": "https://www.infonewhaven.com",
    "note": "All content aggregated for Elm City Daily is provided courtesy of InfoNewHaven.com.",
}

SOURCE_META = {
    # InfoNewHaven
    "who_knew": {"name": "InfoNewHaven.com", "url": "https://www.infonewhaven.com"},
    "food_drink": {"name": "InfoNewHaven.com", "url": "https://www.infonewhaven.com"},
    "music_arts": {"name": "InfoNewHaven.com", "url": "https://www.infonewhaven.com"},
    "events_calendar": {"name": "InfoNewHaven.com", "url": "https://www.infonewhaven.com"},
    # City of New Haven
    "city_news": {"name": "City of New Haven", "url": "https://www.newhavenct.gov"},
    "city_events": {"name": "City of New Haven", "url": "https://www.newhavenct.gov"},
    "city_calendar_items": {"name": "City of New Haven", "url": "https://www.newhavenct.gov"},
    # IAFF Local 825
    "iaff_headlines": {"name": "IAFF Local 825", "url": "https://newhavenfire.org"},
}


