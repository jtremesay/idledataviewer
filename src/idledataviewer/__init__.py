import argparse
import collections
import datetime
import flask
from pathlib import Path
import re
from typing import Generator, List, Optional, Text, TextIO

__EVENT_PARSER = re.compile(
    "^(?P<timestamp>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\s+@?hal\s+(?P<player>solene|killruana), the level (?P<level>\d+)(\s[a-zA-Z]+)+, is #\d+! Next level in (?P<remaining_days>\d+) days, (?P<remaining_time>[0-9]{2}:[0-9]{2}:[0-9]{2})\.$"
)


EventData = collections.namedtuple(
    "EventData", ["timestamp", "player_name", "level", "remaining_time"]
)


def extract_event_data_from_line(line: Text) -> EventData:
    if event_match := __EVENT_PARSER.match(line):
        (
            timestamp_str,
            player_name,
            level_str,
            remaining_days_str,
            remaining_time_str,
        ) = event_match.group(
            "timestamp", "player", "level", "remaining_days", "remaining_time"
        )

        timestamp = datetime.datetime.fromisoformat(timestamp_str)
        level = int(level_str)

        remaining_time_days = int(remaining_days_str)
        remaining_time_time = datetime.time.fromisoformat(remaining_time_str)
        remaining_time = datetime.timedelta(
            days=remaining_time_days,
            hours=remaining_time_time.hour,
            minutes=remaining_time_time.minute,
            seconds=remaining_time_time.second,
        )
        event_data = EventData(
            timestamp=timestamp,
            player_name=player_name,
            level=level,
            remaining_time=remaining_time,
        )

        return event_data

    raise ValueError


def extract_events_data_from_stream(stream: TextIO) -> Generator[EventData, None, None]:
    for line in stream:
        try:
            event_data = extract_event_data_from_line(line)
        except ValueError:
            continue

        yield event_data

data_file_path = Path() / "data" / "idle.txt"
assert data_file_path.exists()

app = flask.Flask(__name__)


@app.route("/api/players")
def api_get_players():
    players_data = {}
    with data_file_path.open() as f:
        for event_data in extract_events_data_from_stream(f):
                try:
                    player_data = players_data[event_data.player_name]
                except KeyError:
                    player_data = {"events": []}
                    players_data[event_data.player_name] = player_data

                player_data["events"].append({
                    "timestamp": event_data.timestamp,
                    "level": event_data.level,
                    "remaining_time": event_data.remaining_time.total_seconds()
                })

    return flask.jsonify(players_data)


@app.route("/")
def index():
    return flask.render_template("index.html")
