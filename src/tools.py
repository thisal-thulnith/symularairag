import os
import httpx


def create_calendly_link() -> str:
    """Create a one-time Calendly scheduling link. Returns URL or error message."""
    token = os.environ.get("CALENDLY_TOKEN")
    event_type = os.environ.get("CALENDLY_EVENT_TYPE")

    if not token or not event_type:
        return (
            "Booking is not configured. Set CALENDLY_TOKEN and "
            "CALENDLY_EVENT_TYPE in the .env file."
        )

    try:
        resp = httpx.post(
            "https://api.calendly.com/scheduling_links",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "max_event_count": 1,
                "owner": event_type,
                "owner_type": "EventType",
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["resource"]["booking_url"]
    except httpx.HTTPError as e:
        return f"Failed to create booking link: {e}"
