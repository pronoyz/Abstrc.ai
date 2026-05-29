from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import json
import re
import os


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    return splitter.split_text(transcript)


def summarize(transcript: str) -> dict:
    llm = get_llm()

    
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of the video transcript concisely."),
        ("human", "{text}"),
    ])
    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)
    chunk_summaries = [map_chain.invoke({"text": chunk}) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)

   
    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert video summarizer. Combine these partial summaries into a final structured report.

You MUST respond with ONLY a valid JSON object — no markdown, no code fences, no extra text before or after.

Use this exact structure:
{{
  "summary": "A concise paragraph summarizing the overall content.",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "action_items": ["Task 1", "Task 2"]
}}

Rules:
- "summary" must be a plain string paragraph.
- "key_points" must be a JSON array of at least 3 strings.
- "action_items" must be a JSON array of strings. If none exist, use [].
- Output raw JSON only — no ```json fences, no intro sentence.""",
        ),
        ("human", "{text}"),
    ])

    combined_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | combined_prompt
        | llm
        | StrOutputParser()
    )

    raw = combined_chain.invoke(combined)
    return parse_summary_output(raw)


def parse_summary_output(text: str) -> dict:
    """Parse JSON output from the LLM into a structured dict."""
    
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

    try:
        data = json.loads(cleaned)
        return {
            "summary": str(data.get("summary", "")).strip(),
            "key_points": [str(p) for p in data.get("key_points", [])],
            "action_items": [str(a) for a in data.get("action_items", [])],
        }
    except json.JSONDecodeError:
       
        return {
            "summary": text.strip(),
            "key_points": [],
            "action_items": [],
        }


def generate_title(transcript: str) -> str:
    llm = get_llm()

    title_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            (
                "system",
                "Based on the video transcript, generate a short professional video title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    return title_chain.invoke(transcript[:2000])