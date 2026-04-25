"""
OpenAI API service for sentiment analysis.
"""
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from openai import RateLimitError, APIError, APIConnectionError, APITimeoutError

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


def analyze_sentiment(transcript_text: str, transcript_id: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a transcript using OpenAI API.
    
    Args:
        transcript_text: The transcript text to analyze
        transcript_id: UUID of the transcript
        
    Returns:
        Dictionary containing analysis result and model info
    """
    logger.info(f"Starting sentiment analysis for transcript: {transcript_id}")
    
    # Create the prompt for sentiment analysis
    prompt = f"""Analyze the following customer service transcript and provide a detailed sentiment analysis.

Transcript:
{transcript_text}

Please provide:
1. Overall sentiment (positive, negative, or neutral)
2. Confidence score (0.0 to 1.0)
3. Key phrases that indicate the sentiment
4. Emotions detected in the conversation
5. A brief summary of the interaction
6. Detailed feedback on the conversation quality and customer satisfaction

Format your response as JSON with these fields:
- sentiment: string
- confidence: float
- key_phrases: array of strings
- emotions: array of strings
- summary: string
- detailed_feedback: string
"""
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Can be configured or upgraded to gpt-4
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing customer service conversations and determining sentiment. Provide accurate, detailed analysis in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Extract response
        content = response.choices[0].message.content
        
        # Parse the JSON response
        result_data = json.loads(content)
        
        # Calculate tokens and cost
        tokens_used = response.usage.total_tokens
        # Approximate cost: gpt-3.5-turbo is ~$0.002 per 1K tokens
        cost = (tokens_used / 1000) * 0.002
        
        logger.info(f"Analysis completed for {transcript_id}. Tokens used: {tokens_used}")
        
        return {
            "result": {
                "sentiment": result_data.get("sentiment", "unknown"),
                "confidence": float(result_data.get("confidence", 0.0)),
                "key_phrases": result_data.get("key_phrases", []),
                "emotions": result_data.get("emotions", []),
                "summary": result_data.get("summary", ""),
                "detailed_feedback": result_data.get("detailed_feedback", ""),
                "raw_response": result_data
            },
            "model_info": {
                "model": response.model,
                "tokens_used": tokens_used,
                "cost": round(cost, 6)
            }
        }
        
    except RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded for {transcript_id}: {str(e)}")
        raise ValueError(f"Rate limit exceeded. Please try again later: {str(e)}")
    
    except APIConnectionError as e:
        logger.error(f"OpenAI connection error for {transcript_id}: {str(e)}")
        raise ValueError(f"Failed to connect to OpenAI API: {str(e)}")
    
    except APITimeoutError as e:
        logger.error(f"OpenAI timeout error for {transcript_id}: {str(e)}")
        raise ValueError(f"OpenAI API request timed out: {str(e)}")
    
    except APIError as e:
        logger.error(f"OpenAI API error for {transcript_id}: {str(e)}")
        raise ValueError(f"OpenAI API error: {str(e)}")
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response for {transcript_id}: {str(e)}")
        raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error calling OpenAI API for {transcript_id}: {str(e)}")
        raise


def test_openai_connection() -> bool:
    """
    Test OpenAI API connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        logger.info("✅ OpenAI API connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI API connection failed: {str(e)}")
        return False
