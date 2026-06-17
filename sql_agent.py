import os
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

# Configure the Gemini API
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)

def generate_sql(question):
    """
    Uses Gemini to translate a natural language question into a SQLite query
    based on the database schema defined in the SYSTEM_PROMPT.
    """
    prompt = f"{SYSTEM_PROMPT}\n\nUser Question:\n{question}\n"
    
    # Use gemini-2.5-flash as default
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    response = model.generate_content(prompt)
    sql = response.text.strip()
    
    # Clean up any potential markdown code blocks
    if "```sql" in sql:
        sql = sql.split("```sql")[1].split("```")[0].strip()
    elif "```" in sql:
        sql = sql.split("```")[1].split("```")[0].strip()
        
    return sql

def explain_results(question, sql, df_results):
    """
    Uses Gemini to analyze the query results and generate business insights
    communicated in executive language.
    """
    if df_results.empty:
        return "The query returned no data. Please refine your question or check if the requested items exist in the database."
        
    results_str = df_results.head(30).to_string()
    
    summary_prompt = f"""
You are an expert FMCG Business Intelligence Analyst.
Analyze the following query results and explain them in clear, executive business language.

User Question: {question}
SQL Executed: {sql}

Query Results (Preview):
{results_str}

Please include:
1. A direct answer to the user's question.
2. Key takeaways and business insights (trends, regional performance, promotion efficiency, stockout patterns, etc.).
3. Actionable recommendations if appropriate.

Write in a professional, clear, and engaging style. Avoid tech jargon about the database or tables; talk about products, sales, and stores.
"""
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(summary_prompt)
    return response.text.strip()
