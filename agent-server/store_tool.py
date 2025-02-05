from main import getRecommendations, get_all_products
from pydantic import BaseModel

from agno.utils.log import logger
from agno.tools import Toolkit
from agno.agent import Agent
from agno.models.mistral import MistralChat
from textwrap import dedent
from typing import List
import os
import json

mistral_api_key = os.getenv("MISTRAL_API_KEY")


class FurnitureStoreTool(Toolkit):
    def __init__(self):
        super().__init__(name="furniture_store_tool")
        self.register(self.get_relevant_items)
        self.register(self.get_all_items)

    def get_relevant_items(self, user_input: str) -> str:
        """
        It gets the Relevant Items from the inventory based on the user input

        Args:
            user_input (str): user input

        """

        return json.dumps(getRecommendations(user_input))

    def get_all_items(self) -> List[str]:
        """
        It should show all the products names which are available in the inventory
        """
        products = get_all_products()
        return json.dumps(products)


agent = Agent(tools=[FurnitureStoreTool()],
              model=MistralChat(
    id="mistral-large-latest",
    api_key=mistral_api_key,
),
    show_tool_calls=True,
    markdown=True,
    description=dedent("""I am a smart AI-powered sales assistant for a furniture store. 
                        I help customers find the best furniture based on their preferences, budget, and requirements. 
                        I provide product recommendations, explain features like a salesperson, assist with adding items to the cart, and track order status."""))

instructions = dedent("""You are a helpful AI sales assistant for an online furniture store. Your job is to help customers find the best furniture based on their needs. 

Guidelines:
1. Ask clarifying questions if the user's request is vague.
2. Recommend products based on user input and their preferences.
3. Use engaging and persuasive language, like a real salesperson.
4. Provide a summary of each recommended product, including its price, features, and image URL.
5. Allow users to add products to their cart.
6. If a user asks about their order status, ask for the order ID and retrieve the information.
7. Keep responses concise, informative, and friendly. """)

agent.print_response("what do you have ?")
