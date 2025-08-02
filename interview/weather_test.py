import pytest
from . import weather


def test_single_sample_snapshot():
    """single weather sample"""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    results = list(weather.process_events(events))

    assert len(results) == 1
    assert results[0] == {
        "type": "snapshot",
        "asOf": 1672531200000,
        "stations": {
            "Foster Weather Station": {"high": 37.1, "low": 37.1}
        }
    }


def test_multiple_samples_same_station():
    """multiple samples same station."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531201000,
            "temperature": 32.5
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531202000,
            "temperature": 35.0
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    results = list(weather.process_events(events))
    
    assert len(results) == 1
    assert results[0] == {
        "type": "snapshot",
        "asOf": 1672531202000,
        "stations": {
            "Foster Weather Station": {"high": 37.1, "low": 32.5}
        }
    }


def test_multiple_stations():
    """different weather stations"""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "sample",
            "stationName": "Oak Street Beach",
            "timestamp": 1672531201000,
            "temperature": 40.5
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531202000,
            "temperature": 32.5
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    results = list(weather.process_events(events))
    
    assert len(results) == 1
    assert results[0] == {
        "type": "snapshot",
        "asOf": 1672531202000,
        "stations": {
            "Foster Weather Station": {"high": 37.1, "low": 32.5},
            "Oak Street Beach": {"high": 40.5, "low": 40.5}
        }
    }


def test_reset_command():
    """reset"""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "reset"
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531201000,
            "temperature": 32.5
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    results = list(weather.process_events(events))
    
    assert len(results) == 2
    assert results[0] == {
        "type": "reset",
        "asOf": 1672531200000
    }
    assert results[1] == {
        "type": "snapshot",
        "asOf": 1672531201000,
        "stations": {
            "Foster Weather Station": {"high": 32.5, "low": 32.5}
        }
    }


def test_snapshot_with_no_data():
    """sanpshot no data"""
    events = [
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    results = list(weather.process_events(events))
    assert len(results) == 0


def test_reset_with_no_data():
    """reset command no data"""
    events = [
        {
            "type": "control",
            "command": "reset"
        }
    ]
    
    results = list(weather.process_events(events))
    assert len(results) == 0


def test_unknown_message_type():
    """unknown message raise exception"""
    events = [
        {
            "type": "unknown",
            "data": "something"
        }
    ]
    
    with pytest.raises(ValueError, match="Unknown message type: unknown"):
        list(weather.process_events(events))


def test_unknown_control_command():
    """unknown control commands raise exception."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "unknown"
        }
    ]
    
    with pytest.raises(ValueError, match="Unknown control command: unknown"):
        list(weather.process_events(events))


def test_generator_behavior():
    """process_events behaves as a generator"""
    def event_generator():
        yield {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        }
        yield {
            "type": "control",
            "command": "snapshot"
        }

    gen = weather.process_events(event_generator())
    assert hasattr(gen, '__next__')
    results = list(gen)
    assert len(results) == 1


def test_as_of_timestamp_accuracy():
    """asOf timestamp reflects most recent sample"""
    events = [
        {
            "type": "sample",
            "stationName": "Station A",
            "timestamp": 1000,
            "temperature": 30.0
        },
        {
            "type": "control",
            "command": "snapshot"
        },
        {
            "type": "sample",
            "stationName": "Station B",
            "timestamp": 2000,
            "temperature": 40.0
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    results = list(weather.process_events(events))
    assert len(results) == 2
    assert results[0]["asOf"] == 1000
    assert results[1]["asOf"] == 2000