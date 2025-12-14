import trainline as t

# Dummy train first
def trainline_search(start: str, end: str, date: str):
    return t.search(start, end, date, date)

trainline_search_info = {
                "type": "function",
                "name": "trainline_search",
                "description": "Get the departure and journey time between start and destinaton",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "description": "Start City. e.g London",
                        },
                        "end": {
                            "type": "string",
                            "description": "End City. e.g Edinburgh",
                        },
                        "date": {
                            "type": "string",
                            "description": "Date of travel in the format: dd/mm/yyyy hh:mm (eg 15/10/2018 08:00)",
                        }

                    },
                    "required": ["start", "end", "date"],
                    "additionalProperties": False,
                },
                "strict": True,
            }

print(trainline_search("Edinburgh Waverley", "London", "15/12/2025 08:00").csv())
