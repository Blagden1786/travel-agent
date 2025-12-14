from openai import OpenAI
from secrets import API_KEY
from tools.trainline_search import *
import json

class Agent():
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)
        self.tools = self.get_tools()

    def run(self, prompt:str):
        # Inputs
        input_list = [
            {"role": "user", "content": prompt}
        ]

        response = self.client.responses.create(model="gpt-5-nano", input=input_list, tools=self.tools)

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
        ]

        return tools
