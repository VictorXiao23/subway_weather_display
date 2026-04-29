"""Custom messages shown in the display header.

Date overrides take priority over day-of-week messages.
Date format: "MM-DD" (no year, repeats annually).
"""

DATE_MESSAGES: dict[str, str] = {
    "01-01": "Happy New Year!",
    "03-14": "Pi Day!",
    "06-23": "Happy Birthday to Victor LOL!",
    "12-25": "Merry Christmas!",
    "11-27": "Happy Thanksgiving!",
    "07-04": "Happy 4th of July!"
}


def get_message(timestamp) -> str:
    date_key = timestamp.strftime("%m-%d")
    if date_key in DATE_MESSAGES:
        return DATE_MESSAGES[date_key]
