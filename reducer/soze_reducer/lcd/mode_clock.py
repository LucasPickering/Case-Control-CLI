from datetime import datetime

from soze_reducer.core.mode import register
from . import helper
from .mode import LcdMode


@register("clock", LcdMode.MODES)
class ClockMode(LcdMode):

    # This won't work for any other size LCD so fuck it just hardcode it
    _LCD_WIDTH = 20
    _LONG_DAY_FORMAT = "{d:%A}, {d:%B} {d.day}"
    _SHORT_DAY_FORMAT = "{d:%A}, {d:%b} {d.day}"
    _SECONDS_FORMAT = " {d:%S}"
    _TIME_FORMAT = "{d:%-I}:{d:%M}"

    def __init__(self):
        super().__init__("clock")

    def get_text(self, settings):
        lines = []  # This will we populated as we go along

        now = datetime.now()
        day_str = __class__._LONG_DAY_FORMAT.format(d=now)
        seconds_str = __class__._SECONDS_FORMAT.format(d=now)

        # If the line is too long, shorten the day name
        if len(day_str) + len(seconds_str) > __class__._LCD_WIDTH:
            day_str = __class__._SHORT_DAY_FORMAT.format(d=now)

        # Pad the day string with spaces to make it the right length
        day_str = day_str.ljust(__class__._LCD_WIDTH - len(seconds_str))
        lines.append(day_str + seconds_str)  # First line

        time_str = __class__._TIME_FORMAT.format(d=now).rjust(5)
        time_lines = helper.make_big_text(time_str)  # Rest of the fucking lines
        # Pad each line with a space then add it to the list of lines
        lines += (f" {line}" for line in time_lines)

        return "\n".join(lines)
