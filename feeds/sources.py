RSS_SOURCES = {
    # InfoNewHaven (working)
    "who_knew": "https://www.infonewhaven.com/category/who-knew-blog/feed/",
    "food_drink": "https://www.infonewhaven.com/food-drink/feed/",
    "music_arts": "https://www.infonewhaven.com/arts-entertainment/music/feed/",
    # Yale Daily News
    "yale_daily_news": "https://yaledailynews.com/feed/",
    # New Haven Independent
    "nh_independent": "https://www.newhavenindependent.org/feed",
    # CT Mirror - New Haven coverage
    "ct_mirror": "https://ctmirror.org/category/cities/new-haven/feed/",
    # NHPR (Connecticut Public Radio)
    "ct_public": "https://www.ctpublic.org/rss.xml",
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
    "who_knew": {"name": "InfoNewHaven", "url": "https://www.infonewhaven.com"},
    "food_drink": {"name": "InfoNewHaven", "url": "https://www.infonewhaven.com"},
    "music_arts": {"name": "InfoNewHaven", "url": "https://www.infonewhaven.com"},
    "events_calendar": {"name": "InfoNewHaven", "url": "https://www.infonewhaven.com"},
    # Yale Daily News
    "yale_daily_news": {"name": "Yale Daily News", "url": "https://yaledailynews.com"},
    # New Haven Independent
    "nh_independent": {"name": "NH Independent", "url": "https://www.newhavenindependent.org"},
    # CT Mirror
    "ct_mirror": {"name": "CT Mirror", "url": "https://ctmirror.org"},
    # CT Public Radio
    "ct_public": {"name": "CT Public", "url": "https://www.ctpublic.org"},
    # City of New Haven
    "city_news": {"name": "City of New Haven", "url": "https://www.newhavenct.gov"},
    "city_events": {"name": "City of New Haven", "url": "https://www.newhavenct.gov"},
    "city_calendar_items": {"name": "City of New Haven", "url": "https://www.newhavenct.gov"},
    # IAFF Local 825
    "iaff_headlines": {"name": "IAFF Local 825", "url": "https://newhavenfire.org"},
}


