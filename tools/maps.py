
# Dummy maps
def google_maps_search(start, finish, start_time):
    return "30 minutes by taking the X18 bus leaving in 5 minutes"

google_maps_search_info = {
                "type": "function",
                "name": "google_maps_search",
                "description": "Plan a journey between places",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "description": "Start City. e.g London",
                        },
                        "finish": {
                            "type": "string",
                            "description": "End City. e.g Edinburgh",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Time for journey to start",
                        }

                    },
                    "required": ["start", "finish", "start_time"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
