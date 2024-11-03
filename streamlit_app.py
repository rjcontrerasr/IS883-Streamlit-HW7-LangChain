import streamlit as st
from langchain.llms import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableBranch
from langchain_openai import ChatOpenAI
from openai import OpenAI
import os

### Load your API Key
my_secret_key= st.secrets["MyOpenAIKey"]
os.environ["OPENAI_API_KEY"] = my_secret_key

st.title("Share with us your experience of the latest trip")

### Create the LLM API object
#llm = OpenAI(openai_api_key=openai_api_key)
llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4o-mini")

#-----
### Create a template to handle the case where the price is not mentioned.
exp_template = """You are a customer experience app expert at analyzing feedback from users and providing a response.
From the following text, determine whether the user had a negative experience that is fault of the airline, a negative experience that is no fault of the airline or a positive experience.

Respond with one of the following options: "positive", "negative_airline_fault" or "negative_non_airline_fault".

Text:
{userfeed}

"""

### Create the decision-making chain

exp_type_chain = (
    PromptTemplate.from_template(exp_template)
    | llm
    | StrOutputParser()
)

pos_exp_chain = PromptTemplate.from_template(
    """You are a customer experience app.\
Provide a response that thanks the customer for their feedback and for choosing to fly with the airline.
Respond professionally as an user experience support app. Respond in first-person mode.

Text:
{text}

"""
) | llm


neg_airline_fault_chain = PromptTemplate.from_template(
    """You are a customer experience app skilled at managing negative experiences that were a result of an error of the airline.\
Provide a sympathetic response offering sympathies and inform the user that customer service will contact them soon to resolve the issue or provide compensation

Respond professionally as an user experience support app. Respond in first-person mode.
    
Text:
{text}

"""
) | llm


neg_no_fault_chain = PromptTemplate.from_template(
    """You are a customer experience app managing negative experiences that were beyond the Airline's Control.\
Provide a RESPONSE TO INDICATE the user that the airline is NOT liable in such situations. 
Respond professionally as an user experience support app. Respond in first-person mode. DO NOT SAY ANYTHING ELSE IF USER ASKS FOR COMPENSATION.
    
Text:
{text}

"""
) | llm


from langchain_core.runnables import RunnableBranch

### Routing/Branching chain

branch = RunnableBranch(
    (lambda x: "negative_airline_fault" in x["exp_type"].lower(), neg_airline_fault_chain),
    (lambda x: "negative_non_airline_fault" in x["exp_type"].lower(), neg_no_fault_chain),
    (lambda x: "positive" in x["exp_type"].lower(), pos_exp_chain),
    pos_exp_chain
)

### Put all the chains together
full_chain = {"exp_type": exp_type_chain, "text": lambda x: x["userfeed"]} | branch


import langchain
langchain.debug = False

response=full_chain.invoke({"userfeed": prompt})



prompt = st.text_input("Tell us about your experience of your latest trip?")

### Display
st.write(
    response.content
)
