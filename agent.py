from openai import OpenAI
import json

from secrets import API_KEY
from tools.maps import *
from tools.trainline_search import *


class TravelAgent():
    def __init__(self, user_data: dict):
        self.client = OpenAI(api_key=API_KEY)
        self.tools = [google_maps_search_info, trainline_search_info]
        self.user_data = user_data
        self.context = []

    def get_response(self, prompt:str):
        # Inputs
        if self.context == []:
            self.context += [
                {"role": "user", "content": prompt}
            ]
        PROMPT = self.prompt_builder()

        # Get response
        response = self.client.responses.create(model="gpt-5-nano",  instructions=PROMPT, input=self.context, tools=self.tools)

        # Add tool calls to the inputs
        self.context +=  response.output

        # response.output is a list of either reasoning objects or function calling objects.
        # Loop through each one to execute all functions
        for item in response.output:
            if item.type == 'function_call':
                # Need one more step
                finished = False
                print(item)
                # Run the function call if the function exists
                tool_response = None

                match item.name:
                    case 'trainline_search':
                        tool_response = trainline_search(**json.loads(item.arguments))
                    case 'google_maps_search':
                        tool_response = google_maps_search(**json.loads(item.arguments))
                    case _:
                        tool_response = ""

                print(f"Tool response: {tool_response}")
                # Add to list of inputs for next call
                self.context.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        item.name: tool_response
                    })
                })

        return response.output_text

    def run_agent(self):
        user_input = ""
        while True:
            response= self.get_response(user_input)
            print(response)
            user_input = input("User: ")


    def prompt_builder(self):
        # TODO: Change the prompt to be specific of their original address when we have got to it.
        START_PROMPT = f"""You are a helpful travel planner who's goal is to help the user plan their journey. On the first message, introduce yourself and ask only what the travel they need planning is. You should only probe for extra information when you need it.
## User starts at home ##
If the user does not give you a start point, assume they want to start from home.
The user's home address is {self.user_data['home']}

## Process ##
1. Ask the user questions until you have all the info you need
2. Break the journey into 3 parts:
    1. Start point to travel hub (e.g main station or airport)
    2. Travel between travel hubs
    3. Travel hub to destination

3. Find the best travel options between travel hubs

4. Fit travel to and from the travel hubs around this. Make sure these rules apply:
    - I want to arrive at a train station >20 mins before travel

5. Use the outputs of these tools to compile the best journey option.

Once you have gathered all required information, provide an itinery for the journey. Then ask the user if they need help with anything else.
        """

        return START_PROMPT
