import argparse
import collections
import datetime
import plotly.graph_objects
import plotly.subplots
import re
from typing import Generator, List, Optional, Text, TextIO

__EVENT_PARSER = re.compile(
    "^(?P<timestamp>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\s+@?hal\s+(?P<player>solene|killruana), the level (?P<level>\d+)(\s[a-zA-Z]+)+, is #\d+! Next level in (?P<remaining_days>\d+) days, (?P<remaining_time>[0-9]{2}:[0-9]{2}:[0-9]{2})\.$"
)


EventData = collections.namedtuple(
    "EventData", ["timestamp", "player", "level", "remaining_time"]
)


def extract_event_data_from_line(line: Text) -> EventData:
    if event_match := __EVENT_PARSER.match(line):
        (
            timestamp_str,
            player,
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
            player=player,
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

def main(args: Optional[List[Text]] = None) -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("data_file", type=argparse.FileType("r"))

    args = arg_parser.parse_args(args)

    players_data = {}
    for event_data in extract_events_data_from_stream(args.data_file):
        try:
            player_data = players_data[event_data.player]
        except KeyError:
            player_data = {"timestamps": [], "levels": [], "remaining_times": []}
            players_data[event_data.player] = player_data

        player_data["timestamps"].append(event_data.timestamp)
        player_data["levels"].append(event_data.level)
        player_data["remaining_times"].append(event_data.remaining_time.total_seconds() / (60 * 60 * 24))

    figure = plotly.subplots.make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        specs=[[{"type": "scatter"}], [{"type": "scatter"}],],
    )
    for player_name, player_data in players_data.items():
        figure.add_trace(
            plotly.graph_objects.Scatter(
                x=player_data["timestamps"],
                y=player_data["levels"],
                name="level  of {}".format(player_name),
                line_shape="linear",
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            plotly.graph_objects.Scatter(
                x=player_data["timestamps"],
                y=player_data["remaining_times"],
                name="remaining time of {}".format(player_name),
                line_shape="linear",
            ),
            row=2,
            col=1,
        )
    figure.show()
