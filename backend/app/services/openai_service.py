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
    Analyze B2B sales conversation using OpenAI API.
    
    Args:
        transcript_text: The transcript text to analyze
        transcript_id: UUID of the transcript
        
    Returns:
        Dictionary containing analysis result and model info
    """
    logger.info(f"Starting B2B sales conversation analysis for transcript: {transcript_id}")
    
    # System prompt for B2B sales conversation intelligence
    system_prompt = """You are an expert B2B sales conversation intelligence analyst.

Analyze the provided call transcript and score sentiment, intent, buying signals, objections, and conversation dynamics.

Rules:
- Evaluate ONLY from transcript evidence. Do not infer facts not supported.
- Score all numeric metrics on a 1-10 scale unless otherwise stated.
- Be strict and calibrated:
  1-3 = weak/negative
  4-6 = moderate/mixed
  7-8 = strong/positive
  9-10 = exceptional/very strong

Return ONLY valid JSON.
No markdown.
No explanations outside JSON.

For each metric provide:
- score
- evidence (short quote snippets)
- rationale (1 sentence)

Analyze these primary dimensions:
1. Live Tone Score
2. Objection & Recovery Arc
3. Champion Signals
4. Buying Commitment Momentum
5. Competitive Mention Sentiment
6. Call Closing Sentiment

Analyze these parameter dimensions:
7. Prospect Tone
8. Pain and Urgency
9. Champion Strength
10. Objection Temperature
11. Buying Commitment
12. Competitive Position
13. Trust and Openness
14. Expansion Potential
15. Decision Friction Indicators
16. Asking to Telling Ratio
17. Transparency Score

Additional derived outputs:
- overall_call_sentiment (Positive/Neutral/Negative)
- lead_temperature (Cold/Warm/Hot)
- meeting_likelihood (0-100)
- follow_up_readiness (0-100)
- next_best_action (array)
- risks_detected (array)
- notable_buying_signals (array)
- objections_detected (array)"""
    
    # User prompt template
    prompt = f"""Analyze this sales call transcript.

Scoring instructions:
- Focus on prospect sentiment more than agent behavior.
- If a metric is absent in transcript, score conservatively and mark low confidence.
- For "Asking to Telling Ratio":
   estimate ratio of discovery questions vs agent-led telling.
- For "Competitive Position":
   score based on brand perception and competitor mentions (if none, neutral 5).
- For "Objection & Recovery Arc":
   detect objections, resistance, and how effectively recovered.
- For "Champion Signals":
   evaluate authority, engagement, influence, willingness to advocate.
- For "Buying Commitment Momentum":
   assess progression toward next-step commitment.

Return this exact JSON structure:

{{
 "summary":{{
   "overall_call_sentiment":"",
   "lead_temperature":"",
   "meeting_likelihood":0,
   "follow_up_readiness":0
 }},
 "primary_metrics":{{
   "live_tone_score":{{"score":0,"evidence":[],"rationale":""}},
   "objection_recovery_arc":{{"score":0,"evidence":[],"rationale":""}},
   "champion_signals":{{"score":0,"evidence":[],"rationale":""}},
   "buying_commitment_momentum":{{"score":0,"evidence":[],"rationale":""}},
   "competitive_mention_sentiment":{{"score":0,"evidence":[],"rationale":""}},
   "call_closing_sentiment":{{"score":0,"evidence":[],"rationale":""}}
 }},
 "parameter_metrics":{{
   "prospect_tone":{{"score":0,"evidence":[],"rationale":""}},
   "pain_urgency":{{"score":0,"evidence":[],"rationale":""}},
   "champion_strength":{{"score":0,"evidence":[],"rationale":""}},
   "objection_temperature":{{"score":0,"evidence":[],"rationale":""}},
   "buying_commitment":{{"score":0,"evidence":[],"rationale":""}},
   "competitive_position":{{"score":0,"evidence":[],"rationale":""}},
   "trust_openness":{{"score":0,"evidence":[],"rationale":""}},
   "expansion_potential":{{"score":0,"evidence":[],"rationale":""}},
   "decision_friction_indicators":{{"score":0,"evidence":[],"rationale":""}},
   "asking_to_telling_ratio":{{
      "score":0,
      "estimated_ratio":"",
      "evidence":[],
      "rationale":""
   }},
   "transparency_score":{{"score":0,"evidence":[],"rationale":""}}
 }},
 "notable_buying_signals":[],
 "objections_detected":[],
 "risks_detected":[],
 "next_best_action":[]
}}

Transcript:
{transcript_text}"""
    
    try:
        # Call OpenAI API with GPT-4o-mini for B2B sales intelligence
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model with strong performance
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower temperature for consistent, focused analysis
            max_tokens=4000,  # Increased for comprehensive analysis
            response_format={"type": "json_object"}
        )
        
        # Extract response
        content = response.choices[0].message.content
        
        # Parse the JSON response
        result_data = json.loads(content)
        
        # Calculate tokens and cost
        tokens_used = response.usage.total_tokens
        # Approximate cost: gpt-4o-mini is ~$0.00015 input + $0.0006 output per 1K tokens
        # Simplified average: ~$0.0004 per 1K tokens
        cost = (tokens_used / 1000) * 0.0004
        
        logger.info(f"B2B sales analysis completed for {transcript_id}. Tokens used: {tokens_used}")
        
        # Return the full analysis result with new schema
        return {
            "result": result_data,  # Contains summary, primary_metrics, parameter_metrics, etc.
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


def analyze_digital_journey(transcript_text: str, transcript_id: str) -> Dict[str, Any]:
    """
    Analyze digital user journey using OpenAI API.
    
    Args:
        transcript_text: The digital journey transcript to analyze
        transcript_id: UUID of the transcript
        
    Returns:
        Dictionary containing analysis result and model info
    """
    logger.info(f"Starting digital journey analysis for transcript: {transcript_id}")
    
    # System prompt for digital journey intelligence
    system_prompt = """You are an expert digital marketing and conversion optimization analyst.

Analyze the provided digital user journey transcript and evaluate engagement depth, content consumption, time investment, and conversion readiness.

Rules:
- Evaluate ONLY from journey evidence. Do not infer facts not supported.
- Score all numeric metrics on a 1-10 scale unless otherwise stated.
- Be strict and calibrated:
  1-3 = weak/low engagement
  4-6 = moderate/mixed engagement
  7-8 = strong/high engagement
  9-10 = exceptional/very high engagement

Return ONLY valid JSON.
No markdown.
No explanations outside JSON.

Analyze these dimensions:
1. Engagement Depth - Overall engagement intensity based on actions and time
2. Content Consumption - Quality and quantity of content consumed
3. Time Investment - Total time, high-value content time, depth
4. Conversion Readiness - Likelihood of conversion (0-100%)
5. Session Temperature - Cold/Warm/Hot
6. Journey Stage - Research/Comparison/Decision
7. Drop-off Signals - Where engagement declined
8. Conversion Signals - Positive indicators
9. Friction Points - Hesitation or struggle points
10. Next Best Action - Recommended follow-ups"""
    
    # User prompt template
    prompt = f"""Analyze this digital user journey transcript.

Focus on:
- Time spent on different content types
- High-intent actions (downloads, pricing views, form fills, extended video watches)
- Content progression and depth
- Drop-off or abandonment patterns
- Re-engagement signals (returns to site)
- Form completion vs abandonment

Return this exact JSON structure:

{{
  "summary": {{
    "session_temperature": "",
    "conversion_readiness": 0,
    "journey_stage": "",
    "content_pieces_consumed": 0,
    "high_intent_actions": []
  }},
  "engagement_depth": {{
    "score": 0,
    "key_actions": [],
    "rationale": ""
  }},
  "content_consumption": {{
    "score": 0,
    "key_actions": [],
    "rationale": ""
  }},
  "time_investment": {{
    "total_session_time": "",
    "high_value_content_time": "",
    "average_time_per_content": "",
    "depth_score": 0
  }},
  "drop_off_signals": [],
  "conversion_signals": [],
  "friction_points": [],
  "next_best_action": []
}}

Digital Journey Transcript:
{transcript_text}"""
    
    try:
        # Call OpenAI API with GPT-4o-mini for digital journey intelligence
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        # Extract response
        content = response.choices[0].message.content
        
        # Parse the JSON response
        result_data = json.loads(content)
        
        # Calculate tokens and cost
        tokens_used = response.usage.total_tokens
        cost = (tokens_used / 1000) * 0.0004
        
        logger.info(f"Digital journey analysis completed for {transcript_id}. Tokens used: {tokens_used}")
        
        # Return the full analysis result
        return {
            "result": result_data,
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
