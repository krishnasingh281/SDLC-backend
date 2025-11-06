import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

# 2. Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")

genai.configure(api_key=GEMINI_API_KEY)


def perform_tradeoff_analysis(option1, option2, criteria):
    """
    Calls the Gemini API to perform a trade-off analysis for PS-01.
    
    Args:
        option1 (str): Description of the first design option.
        option2 (str): Description of the second design option.
        criteria (str): Comma-separated string of criteria.

    Returns:
        str: The AI-generated analysis in Markdown format.
    """
    
    # --- FIX 1: Define the System Prompt First ---
    system_prompt = """
    You are an expert systems architect and senior project manager. 
    Your job is to perform a detailed trade-off analysis.

    You will be given two design alternatives and a set of criteria.
    Your response MUST be in Markdown and follow this exact structure:

    1.  **Quantitative Trade-off Matrix**: A Markdown table comparing both options against each specified criterion (e.g., cost, performance, risk).
    2.  **Detailed Pros and Cons**: A separate "Pros" and "Cons" bulleted list for *each* of the two options.
    3.  **Final Recommendation**: A concluding paragraph starting with "**Recommendation:**" that suggests which option is better and provides a brief justification.
    """
    
    # --- FIX 1 (continued): Initialize the model WITH the system prompt ---
    # --- THIS IS THE FIX: 'genAI' changed to 'genai' ---
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash-preview-09-2025',
        system_instruction={"parts": [{"text": system_prompt}]}
    )
    
    # --- This is the user's specific request ---
    user_query = f"""
    Here is the analysis I need:

    **Criteria:**
    {criteria}

    **Design Option 1:**
    {option1}

    **Design Option 2:**
    {option2}
    """
    
    print("---------------------------------")
    print(f"Calling Gemini API for trade-off analysis...")
    
    try:
        # --- FIX 1 (continued): Call generate_content with ONLY the user query ---
        response = model.generate_content(
            contents=[{"parts": [{"text": user_query}]}]
        )
        
        # 5. Extract the text response
        text_response = response.candidates[0].content.parts[0].text
        print("Gemini API call successful.")
        print("---------------------------------")
        return text_response
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # In a real app, you would have more robust error handling
        if hasattr(e, 'response'):
             # Handle API-specific errors
            print(f"API Error details: {e.response.text}")
        
        # --- FIX 2: RE-RAISE THE EXCEPTION ---
        # This stops this function and sends the error
        # back to app.py, which will return a 500 error.
        raise e

def perform_design_review(document_text):
    """
    Calls the Gemini API to perform a design review for PS-02.
    
    Args:
        document_text (str): The full text of the design document to be reviewed.

    Returns:
        str: The AI-generated review in Markdown format.
    """
    
    # 1. Define the System Prompt for PS-02
    # This prompt is custom-built for your PDF's requirements
    system_prompt = """
    You are a meticulous Senior Systems Engineer and a subject matter expert 
    conducting a Preliminary Design Review (PDR). 
    Your task is to analyze the provided design document.

    Your response MUST be in Markdown and follow this exact structure:

    1.  **Executive Summary**: A single, concise paragraph summarizing the design's purpose and key components.
    2.  **Compliance & Requirements Check**: A bulleted list identifying how the design meets (or fails to meet) its implied requirements.
    3.  **Potential Gaps & Risks**: A critical, bulleted list identifying potential design flaws, gaps, unaddressed edge cases, or risks.
    4.  **Action Item Checklist**: A checklist (using `- [ ]`) of actionable items or questions that need to be addressed before the next review (e.g., CDR).
    """
    
    # 2. Initialize the model WITH the system prompt
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash-preview-09-2025',
        system_instruction={"parts": [{"text": system_prompt}]}
    )
    
    # 3. Define the user's query
    user_query = f"""
    Please perform a PDR review on the following design document:

    ---
    {document_text}
    ---
    """
    
    print("---------------------------------")
    print(f"Calling Gemini API for design review (PS-02)...")
    
    try:
        # 4. Call the API
        response = model.generate_content(
            contents=[{"parts": [{"text": user_query}]}]
        )
        
        text_response = response.candidates[0].content.parts[0].text
        print("Gemini API call successful.")
        print("---------------------------------")
        return text_response
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        if hasattr(e, 'response'):
            print(f"API Error details: {e.response.text}")
        raise e