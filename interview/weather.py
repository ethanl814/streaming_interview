from typing import Any, Iterable, Generator

def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    """
    Processes weather station events and control messages
    
    Maintains state of weather stations and responds to control messages
    """
    stations = {} 
    last_timestamp = None 
    
    for event in events:
        message_type = event.get("type")

        if message_type == "sample":
            station_name = event["stationName"]
            timestamp = event["timestamp"]
            temperature = event["temperature"]
            last_timestamp = timestamp 
            
            # update station data
            if station_name not in stations:
                stations[station_name] = {"high": temperature, "low": temperature}
            else:
                stations[station_name]["high"] = max(stations[station_name]["high"], temperature)
                stations[station_name]["low"] = min(stations[station_name]["low"], temperature)
                
        elif message_type == "control":
            command = event.get("command")
            
            if command == "snapshot":
                if last_timestamp is not None:
                    yield {
                        "type": "snapshot",
                        "asOf": last_timestamp,
                        "stations": dict(stations)  # copy
                    }
                    
            elif command == "reset":
                if last_timestamp is not None:
                    yield {
                        "type": "reset",
                        "asOf": last_timestamp
                    }
                    stations.clear() 
                    
            else:
                raise ValueError(f"Unknown control command: {command}")
                
        else:
            raise ValueError(f"Unknown message type: {message_type}")