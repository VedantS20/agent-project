from fastapi.middleware.cors import CORSMiddleware
from typing import Union
from fastapi import FastAPI, HTTPException, File, UploadFile, Request, Response
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

from google.cloud import storage
from agno.agent import Agent
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.mistral import MistralChat
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from mistralai import Mistral
from pydantic import BaseModel
from typing import List, Optional, Dict
import time
import json
from textwrap import dedent
from agno.tools import Toolkit

# from openai import OpenAI


mongo_client = MongoClient(
    "mongodb+srv://vedant:test%40123@workshop-bakery.0lshrqn.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client.furniture
products_collection = db.products
cart_collection = db.cart

mistral_small = 'open-mistral-nemo'
mistral_large = 'mistral-large-latest'

load_dotenv()

mistral_api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=mistral_api_key)

app = FastAPI()
storage_client = storage.Client()
BUCKET_NAME = "future-furniture-inventory"
bucket = storage_client.bucket(BUCKET_NAME)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FurnitureStoreTool(Toolkit):
    def __init__(self):
        super().__init__(name="furniture_store_tool")
        self.register(self.get_relevant_items)
        self.register(self.get_all_items)
        self.register(self.add_product_to_cart)

    def get_relevant_items(self, user_input: str, category: Optional[str] = None, price_under: Optional[float] = None) -> str:
        """
        It gets the Relevant Items from the inventory based on the user input

        Args:
            user_input (str): detailed user requirement about the product , what does he want
            category (Optional[str]) : category according to user input it has to in these options sofa , chair , bed , wardrobe or chair
            price_under (Optional[float]) : price in rupee of the product that user wants to search for example if user asks show me sofa under 10000 price_under will be 10000
        """
        print(category, "categoryy")
        if category is None:
            return json.dumps({"error": f"Product Details not found"})
        result = getRecommendations(user_input, category, price_under)
        if len(result) == 0:
            return json.dumps({"error": f"No products found"})
        return json.dumps(result)

    def get_all_items(self) -> List[str]:
        """
        It should show all the products names which are available in the inventory
        """
        products = get_all_products()
        return json.dumps(products)

    def add_product_to_cart(self, id: str):
        """
        It should add the product to the cart with the help of product id

        Args:
            id (str):Id of the product
        """
        print(id, "PRODUCT ID")
        if not id:
            return json.dumps({"error": "Unable to add product to cart"})
        cart_collection.insert_one({"product_id": id})
        return json.dumps({"success": "Product Added to cart successfully"})


@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    """Receives file and uploads it to GCP Bucket"""
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file.file, content_type=file.content_type)

    # fmt: off
    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{file.filename}"
    return {"url": public_url}


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict]] = None
    stream: Optional[bool] = False

@app.post("/chat/completions")
async def chat_completions(request_data: ChatRequest):
    try:
        last_message = request_data.messages[-1].content
        async def stream_agent_response():
            try:
                response_stream = handleAgent().run(last_message, stream=True)
                for chunk in response_stream:
                    # Format each chunk in the expected structure
                    response_data = {
                        "id": f"chatcmpl-{str(hash(time.time()))[:10]}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": request_data.model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": chunk.content
                            },
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(response_data)}\n\n"

                final_data = {
                        "id": f"chatcmpl-{str(hash(time.time()))[:10]}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": request_data.model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": ""
                            },
                            "finish_reason": "stop"
                        }]
                    }
                yield f"data: {json.dumps(final_data)}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                print(f"Error during streaming: {e}")
                error_data = {
                    "error": {
                        "message": str(e),
                        "type": "streaming_error"
                    }
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            stream_agent_response(),
            media_type="text/event-stream"
        )

    except Exception as e:
        print(f"Error in chat completions: {e}")
        error_data = {
            "error": {
                "message": str(e),
                "type": "request_error"
            }
        }
        return StreamingResponse(
            iter([f"data: {json.dumps(error_data)}\n\n"]),
            media_type="text/event-stream"
        )

    except Exception as e:
        print(f"Error in chat completions: {e}")
        error_data = {
            "error": {
                "message": str(e),
                "type": "request_error"
            }
        }
        return StreamingResponse(
            iter([f"data: {json.dumps(error_data)}\n\n"]),
            media_type="text/event-stream"
        )

def generate_embeddings(text):
    model = "mistral-embed"
    mistral_client = Mistral(api_key=mistral_api_key)
    response = mistral_client.embeddings.create(
        model=model,
        inputs=[text]
    )
    return response.data[0].embedding

class Product(BaseModel):
    name: str
    description: str
    price: float
    image: str
    category:str



@app.post("/add_product/")
async def add_product(product: Product):
    print(product.name,"PRODUCT")

    """Stores product details along with embeddings in MongoDB"""
    try:
        embedding = generate_embeddings(product.description)

        product = {
            "name": product.name,
            "description": product.description,
            "image": product.image,
            "price": product.price,
            'category':product.category,
            "embedding": embedding
        }

        products_collection.insert_one(product)
        return {"message": "Product added successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/products")
async def get_products():
    products = list(products_collection.find({}, {"_id": 1, "name": 1, "description": 1, "price": 1, "image": 1,'title':1}))
    for product in products:
        product["_id"] = str(product["_id"])  # Convert ObjectId to string for JSON serialization
    return {"products": products}


def getRecommendations(user_input,category,price_under):
    print(user_input,category,price_under,"vals")
    try:
        embeddings = generate_embeddings(user_input)
        pipeline=[
            {
                    "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": embeddings,
                    "path": "embedding",
                    "exact": True,
                    "limit": 5
                    },
            },
        ]
        if category:
            pipeline.append( {
                "$match":{"category":category}
            })
        if price_under:
            pipeline.append({
                "$match":{"price":{"$lte":price_under}}
            })

        pipeline.append({
                "$project":{
                "embedding":0,
                "_id":0,
                "image":0
                }
            })
        results = products_collection.aggregate(pipeline)
        array_of_results = []
        for doc in results:
            array_of_results.append(doc)
        return array_of_results



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_all_products():
    products = list(products_collection.find({}, {"name": 1,"_id":0}))
    return products



# export async function getRecommendations(userQuery) {
#     const queryEmbedding = await client.embeddings.create({
#         input: userQuery,
#         model: "text-embedding-3-small"
#     });

#     const results = await db.collection("products").aggregate([
#         {
#             $vectorSearch: {
#                 queryVector: queryEmbedding.data[0].embedding,
#                 path: "embedding",
#                 numCandidates: 5,  // Top 5 matches
#                 index: "vector_index" // Make sure to create an index on embedding
#             }
#         }
#     ]).toArray();

#     return results;
# }

def handleAgent():
    return Agent(
    model=MistralChat(
            id=mistral_large,
            api_key=mistral_api_key,
    ),
    storage=SqliteAgentStorage(table_name="agent_sessions", db_file="tmp/data.db"),
    tools=[FurnitureStoreTool()],
    add_history_to_messages=True,
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
7. Keep responses concise, informative, and friendly. """
)


if __name__ == '__main__':
    # handleAgent()
    print(getRecommendations("show me some chairs"))


