# ... existing code ...
def _calculate_day_length(sunrise: str, sunset: str) -> str:
    """Calculate hours of daylight from sunrise/sunset times."""
    try:
        from datetime import datetime
        # Parse times (format: "6:45 AM" or "7:30 PM")
        def parse_time(time_str: str) -> datetime:
            time_str = time_str.strip().upper()
            is_pm = "PM" in time_str
            time_str = time_str.replace("AM", "").replace("PM", "").strip()
            hour, minute = map(int, time_str.split(":"))
            if is_pm and hour != 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
            return datetime(1900, 1, 1, hour, minute)
        
        sunrise_dt = parse_time(sunrise)
        sunset_dt = parse_time(sunset)
        
        # Calculate difference
        diff = sunset_dt - sunrise_dt
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if minutes == 0:
            return f"{hours}h"
        return f"{hours}h {minutes}m"
    except Exception:
        return "--"

# ... existing code in render_template section ...
        # Calculate day length if we have sunrise/sunset
        day_length = None
        if weather and weather.get("sunrise") and weather.get("sunset"):
            day_length = _calculate_day_length(weather["sunrise"], weather["sunset"])
        
        # Get current month for climate normals
        current_month = now.strftime("%B").lower()
        climate_normal = None
        if almanac_facts and almanac_facts.get("climate_normals"):
            climate_normal = almanac_facts["climate_normals"].get(current_month)
        
        # Get upcoming annual events
        upcoming_annual_events = []
        if almanac_facts and almanac_facts.get("annual_events"):
            current_month_num = now.month
            for event in almanac_facts["annual_events"]:
                event_month = event.get("month", 0)
                if event_month >= current_month_num:
                    upcoming_annual_events.append(event)
            upcoming_annual_events = sorted(upcoming_annual_events, key=lambda x: x.get("month", 0))[:3]
        
        html = render_template(
            "index.html",
            app_name=app.config["APP_NAME"],
            date_str=date_str,
            center_lat=lat,
            center_lon=lon,
            weather=weather,
            nws_alerts=nws_alerts[:3],
            air_quality=air_quality,
            tax_info=tax_info,
            agg=agg,
            cal_upcoming=cal_upcoming,
            legis_upcoming=legis_upcoming,
            boards_upcoming=boards_upcoming,
            week_grid=week_grid,
            week_start_date=week_start_date,
            hours_all=hours_all,
            trivia_items=trivia_items,
            legislation_stats=legislation_stats,
            almanac_facts=almanac_facts,
            daily_info=daily_info,
            city_reference=city_reference,
            road_closures=results.get("road_closures", []),
            current_season=current_season,
            upcoming_holidays=upcoming_holidays,
            on_this_date=on_this_date,
            day_length=day_length,
            climate_normal=climate_normal,
            upcoming_annual_events=upcoming_annual_events,
        )
