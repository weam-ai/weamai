from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from src.crypto_hub.utils.crypto_utils import crypto_service
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL
from src.chatflow_langchain.service.config.model_config_anthropic import ANTHROPICMODEL
import os
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from dotenv import load_dotenv
from src.custom_lib.langchain.chat_models.anthropic.chatanthropic_cache import MyChatAnthropic as ChatAnthropic

def chain_summary(api_key:str):
    question_prompt_template = """
                    Please provide a summary of the following text, focusing on brand, company, or product information. Maintain the contact information and basic details, including the company's location and industry. Emphasize detailed information about their products and services, and provide details about their clients. Additionally, include any latest news, future plans, and service plans of the company. Avoid details about the hiring process. Note that information about the company's clients may be stored in images from web scraping.
                    Note:Do not provide summary in markdown format.It should be strictly in string format
                    TEXT: {text}
                    SUMMARY:
                    """

    question_prompt = PromptTemplate(
        template=question_prompt_template, input_variables=["text"]
    )

    refine_prompt_template = """
                Maintain all this details Strictly:-
                Please provide a summary of the following text, focusing on brand, company, or product information. Maintain the contact information and basic details. Include the company's location and industry. Emphasize detailed information about their products and services, and provide details about their clients. Additionally, include any latest news and future plans for the company.Give details about how many service plans and pricing they have.Avoid details about the hiring process.
                Note that information about the company's clients may be stored in images from web scraping.
                Note:Do not provide summary in markdown format.It should be strictly in string format
                ```{text}```
                Summary(In String):
                """

    refine_prompt = PromptTemplate(
        template=refine_prompt_template, input_variables=["text"]
    )

    llm = ChatOpenAI(temperature=0, model_name=OPENAIMODEL.GPT_4_1_MINI,api_key=crypto_service.decrypt(api_key),use_responses_api=True)

    refine_chain = load_summarize_chain(
    llm,
    chain_type="refine",
    question_prompt=question_prompt,
    refine_prompt=refine_prompt,
    return_intermediate_steps=True,
    )   
 

    return refine_chain


def chain_summary_HF(api_key:str,endpoint_url:str):
    question_prompt_template = """
                    Please provide a summary of the following text, focusing on brand, company, or product information. Maintain the contact information and basic details, including the company's location and industry. Emphasize detailed information about their products and services, and provide details about their clients. Additionally, include any latest news, future plans, and service plans of the company. Avoid details about the hiring process. Note that information about the company's clients may be stored in images from web scraping.
                    Note:Do not provide summary in markdown format.It should be strictly in string format
                    TEXT: {text}
                    SUMMARY:
                    """

    question_prompt = PromptTemplate(
        template=question_prompt_template, input_variables=["text"]
    )

    refine_prompt_template = """
                Maintain all this details Strictly:-
                Please provide a summary of the following text, focusing on brand, company, or product information. Maintain the contact information and basic details. Include the company's location and industry. Emphasize detailed information about their products and services, and provide details about their clients. Additionally, include any latest news and future plans for the company.Give details about how many service plans and pricing they have.Avoid details about the hiring process.
                Note that information about the company's clients may be stored in images from web scraping.
                Note:Do not provide summary in markdown format.It should be strictly in string format
                ```{text}```
                Summary(In String):
                """

    refine_prompt = PromptTemplate(
        template=refine_prompt_template, input_variables=["text"]
    )

    llm_huggingface = HuggingFaceEndpoint(
                        endpoint_url=endpoint_url,
                        temperature=0.0,
                        streaming=False,
                        huggingfacehub_api_token=crypto_service.decrypt(api_key),
                        stop_sequences=['<|eot_id|>']
                    )
    llm=ChatHuggingFace(llm=llm_huggingface,stop_sequences=['<|eot_id|>'])
    refine_chain = load_summarize_chain(
    llm,
    chain_type="refine",
    question_prompt=question_prompt,
    refine_prompt=refine_prompt,
    return_intermediate_steps=True,
    )   
 

    return refine_chain

def chain_summary_ANT(api_key:str):
    question_prompt_template = """
                    Please provide a summary of the following text, focusing on brand, company, or product information. Maintain the contact information and basic details, including the company's location and industry. Emphasize detailed information about their products and services, and provide details about their clients. Additionally, include any latest news, future plans, and service plans of the company. Avoid details about the hiring process. Note that information about the company's clients may be stored in images from web scraping.
                    Note:Do not provide summary in markdown format.It should be strictly in string format
                    TEXT: {text}
                    SUMMARY:
                    """

    question_prompt = PromptTemplate(
        template=question_prompt_template, input_variables=["text"]
    )

    refine_prompt_template = """
                Maintain all this details Strictly:-
                Please provide a summary of the following text, focusing on brand, company, or product information. Maintain the contact information and basic details. Include the company's location and industry. Emphasize detailed information about their products and services, and provide details about their clients. Additionally, include any latest news and future plans for the company.Give details about how many service plans and pricing they have.Avoid details about the hiring process.
                Note that information about the company's clients may be stored in images from web scraping.
                Note:Do not provide summary in markdown format.It should be strictly in string format
                ```{text}```
                Summary(In String):
                """

    refine_prompt = PromptTemplate(
        template=refine_prompt_template, input_variables=["text"]
    )

    llm = ChatAnthropic(temperature=0, model_name=ANTHROPICMODEL.CLAUDE_SONNET_3_7,api_key=crypto_service.decrypt(api_key))
    refine_chain = load_summarize_chain(
    llm,
    chain_type="refine",
    question_prompt=question_prompt,
    refine_prompt=refine_prompt,
    return_intermediate_steps=True,
    )   
 

    return refine_chain