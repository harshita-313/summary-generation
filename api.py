from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os
from openai import OpenAI
from mysql_database import insert_text
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Text(BaseModel):
    text: str

class Get_items(BaseModel):
    # text: str
    summary: str = Field(description="")
    language: str = Field(description="Give the language code")
   
@app.post('/summary')   
async def get_summary(data: Text):

    openai_api = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL")
    client = OpenAI(api_key=openai_api)

    if data.text:   
        response = client.responses.parse(
            model = openai_model,
            instructions=open('prompt.md', 'r', encoding='utf-8').read(),
            input=f"Text: {data.text}",
            text_format=Get_items, 
        ) 
        
        summary_text = response.output_parsed

        insert_text(
            text = data.text, 
            summary = summary_text.summary,
            language=summary_text.language
        )

        return summary_text
      
    else:
        return ("Text not Found!")

