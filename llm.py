# Navigation
import os 
# LLM
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

# LLM model logic

class FormattedResponse(BaseModel): # Format for response
    source: str = Field(description = "Individual source of each piece of information. For example, book title, year of publication, and author name. " \
                                      "Should be in plain text with no quotation marks, brackets, markdown, unicode formatting or hidden characters.")
    source_details: str | None = Field(default=None, description = "Optional reference to chapter, page, or section if known.")
    info: str = Field(description = "Summary of how this source answers the question or presents relevant information.")

class AstrologyResponses(BaseModel):
    responses: list[FormattedResponse] # List the previous responses (if multiple)

load_dotenv() # Load the .env file with environmental variables
API_KEY = os.environ.get("GROQ_API_KEY") 

PROMPT_ASTROLOGY_INFO = """ 
    You are AstroScholar, an Agentic LLM Research Assistant for Historical Astrology Sources. 
    Answer {question} as it relates to planetary correspondences from historical astrology texts. 
    {format_instructions} inside a JSON object with key 'responses', 
    where 'responses' is a list of sources and info entries. 
    These sources may provide conflicting information, this is fine, present all information.
    """

def get_llm_response(question: str): 
    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        groq_api_key=API_KEY)
    parser = PydanticOutputParser(pydantic_object = AstrologyResponses)

    message = HumanMessagePromptTemplate.from_template(template=PROMPT_ASTROLOGY_INFO)
    chat_prompt = ChatPromptTemplate.from_messages(messages=[message])
    chat_prompt_with_values = chat_prompt.format_prompt(
        question = question,
        format_instructions = parser.get_format_instructions())
    
    response = llm.invoke(chat_prompt_with_values.to_messages())
    data = parser.parse(response.content)

    return data

