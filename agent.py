from openai import OpenAI
from secrets import API_KEY
from tools.google_maps_search import google_maps_search
from tools.trainline_search import *
import json

class TravelAgent():
    def __init__(self, user_data: dict):
        self.client = OpenAI(api_key=API_KEY)
        self.tools = self.get_tools()
        self.user_data = user_data

    def run(self, prompt:str):
        # Inputs
        input_list = [
            {"role": "user", "content": prompt}
        ]

        response = self.client.responses.create(model="gpt-5-nano",  instructions=self.prompt_builder(), input=input_list, tools=self.tools)

        # Add tool calls to the inputs
        input_list +=  response.output

        # response.output is a list of either reasoning objects or function calling objects.
        # Loop through each one to execute all functions
        for item in response.output:
            if item.type == 'function_call':
                # Match function call to the function needed
                match item.name:
                    case 'trainline_search':
                        args = json.loads(item.arguments)
                        tool_response = trainline_search(args['start'], args['end'], args['date'])
                    case 'google_maps_search':
                        args = json.loads(item.arguments)
                        tool_response = google_maps_search(args['start'], args['finish'], args['date'])
                    case _:
                        tool_response = "Tool Not Found"

                # Add to list of inputs for next call
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        item.name: tool_response
                    })
                })

        response = self.client.responses.create(
            model="gpt-5-nano",
            instructions="Respond only with the full journey itinery",
            tools=self.tools,
            input=input_list,
        )

        return response.output_text

    def get_tools(self):
        tools = [
            {
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
                            "description": "Date of travel in ISO format: yyyy:mm:dd",
                        }

                    },
                    "required": ["start", "end", "date"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
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
                        "date": {
                            "type": "string",
                            "description": "Date of travel in ISO format: yyyy:mm:dd",
                        }

                    },
                    "required": ["start", "finish", "date"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        ]

        return tools

    def prompt_builder(self):
        # TODO: Change the prompt to be specific of their original address when we have got to it.
        START_PROMPT = f"""You are a helpful travel planner who's goal is to help the user plan their journey.
## User starts at home ##
If the user does not give you a start point, assume they want to start from home.
The user's home address is {self.user_data['home']}

## Plan ##
1. Break the journey into 3 (or more parts) and use the correct tool for each one:
    1. Start point to travel hub (e.g main station or airport): Use google maps
    2. Travel between travel hubs: Use trainline
    3. Travel hub to destination: Use google maps

2. Use the outputs of these tools to compile the best journey option
        """

        return START_PROMPT
