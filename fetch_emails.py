# Misc
import os
from datetime import datetime, timedelta
from typing import List

# Guard railing
from pydantic import BaseModel, Field
import llm

# Langchain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

# pydantic output which is supposed to be generated by the LLM
# Content to be extracted: date,time,amount,merchant,status
class InvoiceData(BaseModel):
    date: str = Field(description="The exact date of when the transaction occured")
    time: str = Field(description="The exact time the transaction occur")
    amount: float = Field(description="The total cost of the transaction")
    merchant: str = Field(description="The person who the transaction occured between")
    status: str = Field(description="Whether or not the transaction was approved or declined") 
    type: str = Field(description="The type of transaction")

# function which fetches the emails from the user based on a specific query
def fetch_emails() -> List[dict]:
    """Gets emails from a user after a certain date.

    This function uses the GMail API to fetch emails based on a
    given query. The query is used to get emails from a specific
    sender and with a specific subject after a certain date.

    The function returns a list of dictionaries containing the email
    data. Each dictionary has a single key-value pair where the key
    is "body" and the value is the email body.

    Args:
        None

    Returns:
        List[dict]: List of dictionaries containing email data.
    """

    # Gathering the google data
    credentials = get_gmail_credentials(
        client_secrets_file='CREDENTIALS.json',
        token_file='TOKEN.json',
        scopes=["https://mail.google.com/"],
    )

    # Building a api resource service for GMail
    api_resource = build_resource_service(credentials=credentials)

    # Initializes the search object
    search = GmailSearch(api_resource=api_resource)

    # Searches for emails based on a given query
    query = "from:no-reply-ncbcardalerts@jncb.com subject:TRANSACTION APPROVED after:{}".format(
        (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d"))
    
    # a list of dictionaries containing the transaction email data
    emails: List[dict] = search(query)

    if emails:
        # if there are emails, return a list of dictionaries containing the transaction email data
        print(f"{len(emails)} new email(s) found!")
        return [{ "body": email["body"] } for email in emails]
    else:
        print("No new emails found!")
        return []



# Function that takes the prompt as a string and returns the LLM output
def extract_email_tx_data() -> List[str]:
    """Custom LLM API wrapper.

    This function is a wrapper for the LLM API, which extracts
    transaction data from a list of emails. The LLM is provided with
    instructions to extract the following data from each email:

    - date
    - time
    - amount
    - merchant
    - status
    - type

    The function returns the output of the LLM API for each email in
    the list.

    Args:
        None

    Returns:
        List[str]: The output of the LLM API for each email in the list.
    """

    # Instructions sent to the LLM
    template = """
    # Context
    Below are bodies of text which contain transaction data.
    # Goal
    Without commenting, adding comments or notes, extract the following from EMAIL TRANSACTION DATA: date, time, amount, merchant, status, type
    # EMAIL TRANSACTION DATA
    {mail_list}
    # Format
    {format_instructions}
    """

    # How the message received from the LLM should be formatted
    output_parser = PydanticOutputParser(pydantic_object=InvoiceData)

    # Create a prompt for the LLM
    prompt = PromptTemplate(
        template=template,
        input_variables=["mail_list"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
        )

    # Create the chain for the LLM call
    chain = prompt | llm.LLMs.mistral | output_parser

    # Fetch emails
    mail_list = fetch_emails()

    results = [chain.invoke({"mail_list": eachEmail}) for eachEmail in mail_list]

    return results