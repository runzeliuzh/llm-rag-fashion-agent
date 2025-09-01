# Fashion Assistant with RAG integration
from app.vector_store import cost_optimized_vector_store as vector_store
import logging
from typing import Optional
import os
import requests
import json

logger = logging.getLogger(__name__)

# Use DeepSeek API (Paid but very affordable and high quality)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Set this in Railway environment variables
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Fallback option

def validate_response_format(text: str) -> str:
    """
    Validates and ensures the response follows the required format structure
    """
    if not text:
        return text
    
    # Check if response has the required sections
    required_sections = ["**Style Overview:**", "**Key Pieces:**", "**Styling Tips:**"]
    missing_sections = [section for section in required_sections if section not in text]
    
    if missing_sections:
        # If format is completely wrong, try to restructure it
        return restructure_response(text)
    
    # Ensure each section ends properly
    lines = text.split('\n')
    cleaned_lines = []
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            cleaned_lines.append("")
            continue
            
        # Check if it's a section header
        if line.startswith("**") and line.endswith(":**"):
            current_section = line
            cleaned_lines.append(line)
        elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
            # Bullet point - ensure it ends properly
            if not line.rstrip().endswith(('.', '!', '?', ')')):
                line = line.rstrip() + '.'
            cleaned_lines.append(line)
        else:
            # Regular text - ensure it ends properly
            if line and not line.rstrip().endswith(('.', '!', '?', ':', ')')):
                line = line.rstrip() + '.'
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

def restructure_response(text: str) -> str:
    """
    Attempts to restructure a response that doesn't follow the format
    """
    # Basic restructuring - split into overview and details
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if len(paragraphs) >= 2:
        overview = paragraphs[0]
        if not overview.endswith(('.', '!', '?')):
            overview += '.'
            
        details = paragraphs[1] if len(paragraphs) > 1 else "Consider classic pieces that suit your style."
        if not details.endswith(('.', '!', '?')):
            details += '.'
            
        tips = paragraphs[2] if len(paragraphs) > 2 else "Focus on fit, comfort, and personal expression."
        if not tips.endswith(('.', '!', '?')):
            tips += '.'
        
        return f"""**Style Overview:** {overview}

**Key Pieces:**
• {details}

**Styling Tips:** {tips}"""
    
    # Fallback
    if not text.endswith(('.', '!', '?')):
        text += '.'
    return f"""**Style Overview:** {text}

**Key Pieces:**
• Focus on well-fitted basics and quality pieces.

**Styling Tips:** Consider your lifestyle and personal preferences when choosing outfits."""

def ensure_complete_response(text: str, max_length: int = 800) -> str:
    """
    Ensures the response ends with complete sentences and is within reasonable length
    """
    if not text:
        return text
    
    # If text is short enough, return as is
    if len(text) <= max_length:
        # Check if it ends properly
        if text.rstrip().endswith(('.', '!', '?', ':', ')')):
            return text.rstrip()
        else:
            # Find the last complete sentence
            text = text.rstrip()
            for i in range(len(text) - 1, -1, -1):
                if text[i] in '.!?':
                    return text[:i + 1]
            return text  # If no sentence ending found, return as is
    
    # Text is too long, find a good cutoff point
    cutoff_text = text[:max_length]
    
    # Find the last complete sentence within the limit
    for i in range(len(cutoff_text) - 1, -1, -1):
        if cutoff_text[i] in '.!?':
            # Check if we're not cutting off mid-word or important context
            remaining_text = cutoff_text[:i + 1].rstrip()
            if len(remaining_text) > max_length * 0.7:  # At least 70% of desired length
                return remaining_text
    
    # If no good sentence break found, find last complete word
    words = cutoff_text.split()
    if len(words) > 1:
        # Remove the last word (likely incomplete)
        complete_text = ' '.join(words[:-1])
        if complete_text.endswith(('.', '!', '?')):
            return complete_text
        else:
            return complete_text + '.'
    
    return text[:max_length].rstrip() + '.'

def get_response_format(query: str) -> str:
    """
    Determines the best response format based on the query type
    """
    query_lower = query.lower()
    
    # For outfit/styling questions
    if any(word in query_lower for word in ['outfit', 'style', 'wear', 'look', 'dress', 'match', 'combine']):
        return """You MUST provide responses in EXACTLY this format:

**Style Overview:** [1-2 sentences describing the overall style/approach]

**Key Pieces:**
• [Item 1 with specific details]
• [Item 2 with specific details] 
• [Item 3 with specific details]

**Styling Tips:** [2-3 sentences with practical advice]

Always end each section completely. Never cut off mid-sentence."""

    # For trend/shopping questions  
    elif any(word in query_lower for word in ['trend', 'fashion', 'buy', 'shop', 'popular', 'current']):
        return """You MUST provide responses in EXACTLY this format:

**Current Trends:** [2-3 sentences about relevant trends]

**What to Look For:**
• [Trend 1 with specific details]
• [Trend 2 with specific details]
• [Trend 3 with specific details]

**Shopping Tips:** [2-3 sentences with practical buying advice]

Always end each section completely. Never cut off mid-sentence."""

    # Default format for general questions
    else:
        return """You MUST provide responses in EXACTLY this format:

**Overview:** [2-3 sentences explaining the main points]

**Key Points:**
• [Point 1 with specific details]
• [Point 2 with specific details]
• [Point 3 with specific details]

**Recommendations:** [2-3 sentences with actionable advice]

Always end each section completely. Never cut off mid-sentence."""

async def get_rag_response(query: str, session_id: Optional[str] = None):
    """
    LLM-RAG response using multiple cost-effective LLM options
    """
    # Step 1: Get context from vector store
    results = vector_store.query(query, n_results=3)
    
    # Debug logging to see what we get
    print(f"🔍 Query: {query}")
    print(f"📊 Results structure: {type(results)}")
    print(f"📊 Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
    
    # Check if we have documents
    if not results or 'documents' not in results:
        print("❌ No results or no documents key")
        # Still try to get LLM response with general fashion knowledge
        context = "General fashion advice: Focus on timeless pieces, proper fit, and personal style."
    else:
        documents = results['documents']
        if not documents or not isinstance(documents, list) or len(documents) == 0:
            print("❌ Empty documents list")
            context = "General fashion advice: Focus on timeless pieces, proper fit, and personal style."
        else:
            # Get the first list of documents (ChromaDB returns list of lists)
            doc_list = documents[0] if documents else []
            if not doc_list or len(doc_list) == 0:
                print("❌ Empty document list")
                context = "General fashion advice: Focus on timeless pieces, proper fit, and personal style."
            else:
                print(f"✅ Found {len(doc_list)} relevant documents")
                # Get the most relevant context
                context = "\n".join(doc_list[:2])  # Limit context to avoid token limits
                print(f"📝 Context preview: {context[:200]}...")
    
    # Step 2: Try multiple LLM options in order of preference
    llm_functions = [
        query_deepseek_llm,         # Primary: DeepSeek API (high quality, affordable)
        query_huggingface_llm,      # Fallback: Free tier available
        query_openai_compatible_llm, # Fallback: Other cheap/free options
        query_ollama_llm,           # Fallback: If you have access to Ollama server
    ]
    
    for llm_func in llm_functions:
        try:
            response = await llm_func(query, context)
            if response and len(response.strip()) > 20:
                print(f"✅ Got response from {llm_func.__name__}")
                return response
        except Exception as e:
            logger.error(f"LLM error with {llm_func.__name__}: {e}")
            continue
    
    # Step 3: Fallback to intelligent text processing (always responds)
    print("🔄 Using intelligent fashion response generation")
    return create_fashion_response(query, context)

async def query_huggingface_llm(query: str, context: str):
    """
    Query Hugging Face Inference API for LLM response
    """
    if not HF_API_KEY:
        return None
    
    # Create a well-structured prompt for fashion advice
    prompt = f"""You are a fashion expert. Based on the following fashion information, provide helpful advice about the user's question.

Fashion Context:
{context[:800]}

User Question: {query}

Fashion Expert Response:"""

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try multiple free models in order of preference
    models = [
        "microsoft/DialoGPT-medium",
        "google/flan-t5-base", 
        "facebook/blenderbot-400M-distill"
    ]
    
    for model in models:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 400,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '').strip()
                    if generated_text and len(generated_text) > 20:
                        # Clean up the response
                        if "Fashion Expert Response:" in generated_text:
                            generated_text = generated_text.split("Fashion Expert Response:")[-1].strip()
                        return generated_text
                        
        except Exception as e:
            logger.warning(f"Failed to use model {model}: {e}")
            continue
    
    return None

async def query_deepseek_llm(query: str, context: str):
    """
    Query DeepSeek API for LLM response (OpenAI-compatible)
    DeepSeek offers excellent quality at very affordable prices
    """
    if not DEEPSEEK_API_KEY:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # DeepSeek API endpoint
        api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # Get the appropriate response format for this query
        response_format = get_response_format(query)
        
        payload = {
            "model": "deepseek-chat",  # Their main chat model
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a professional fashion expert assistant. {response_format}"
                },
                {
                    "role": "user", 
                    "content": f"Based on this fashion information: {context[:800]}\n\nQuestion: {query}\n\nProvide fashion advice following the exact format specified:"
                }
            ],
            "max_tokens": 800,  # Generous limit for complete format
            "temperature": 0.7,
            "top_p": 0.9,
            "stop": ["**Additional", "**Note:", "**Remember:", "\n\n---", "User:"]  # Stop before extra content
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                generated_text = result['choices'][0]['message']['content'].strip()
                if generated_text and len(generated_text) > 20:
                    # Validate and ensure proper format structure
                    formatted_response = validate_response_format(generated_text)
                    print(f"✅ DeepSeek API response generated successfully")
                    print(f"📝 Response length: {len(formatted_response)} chars")
                    return formatted_response
        else:
            print(f"❌ DeepSeek API error: {response.status_code} - {response.text}")
                    
    except Exception as e:
        logger.warning(f"DeepSeek API error: {e}")
    
    return None

async def query_ollama_llm(query: str, context: str):
    """
    Alternative: Use Ollama API (if you have access to a server with Ollama)
    """
    ollama_url = os.getenv("OLLAMA_URL")  # e.g., "http://your-server:11434"
    if not ollama_url:
        return None
    
    try:
        prompt = f"""You are a fashion expert. Based on the fashion information provided, answer the user's question about fashion trends and styling.

Fashion Information:
{context[:600]}

Question: {query}

Answer:"""

        payload = {
            "model": "llama2:7b-chat",  # or "mistral:7b"
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 600  # Increased for complete responses
            }
        }
        
        response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '').strip()
            if generated_text and len(generated_text) > 20:
                # Ensure complete response
                complete_response = ensure_complete_response(generated_text)
                return complete_response
                
    except Exception as e:
        logger.warning(f"Ollama API error: {e}")
    
    return None

async def query_openai_compatible_llm(query: str, context: str):
    """
    Alternative: Use any OpenAI-compatible API (like OpenRouter, Together AI, etc.)
    Many offer free tiers or very cheap rates
    """
    api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
    api_url = os.getenv("OPENAI_COMPATIBLE_URL", "https://api.openai.com/v1/chat/completions")
    
    if not api_key:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": os.getenv("OPENAI_COMPATIBLE_MODEL", "gpt-3.5-turbo"),
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful fashion expert assistant. Provide concise, practical fashion advice based on the given context."
                },
                {
                    "role": "user", 
                    "content": f"Fashion Context: {context[:600]}\n\nQuestion: {query}\n\nProvide helpful fashion advice:"
                }
            ],
            "max_tokens": 700,  # Increased for complete responses
            "temperature": 0.7
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                generated_text = result['choices'][0]['message']['content'].strip()
                if generated_text and len(generated_text) > 20:
                    # Ensure complete response
                    complete_response = ensure_complete_response(generated_text)
                    return complete_response
                    
    except Exception as e:
        logger.warning(f"OpenAI-compatible API error: {e}")
    
    return None

def create_fashion_response(query: str, context: str):
    """
    Create intelligent fashion response using comprehensive fashion knowledge
    This ensures high-quality responses even without external LLM APIs
    """
    query_lower = query.lower()
    
    # Comprehensive fashion knowledge base
    fashion_knowledge = {
        'autumn_fall_trends': """
**Autumn 2025 Fashion Trends:**
• **Colors**: Rich burgundy, forest green, burnt orange, deep navy, camel brown
• **Textures**: Chunky knits, corduroy, leather, suede, faux fur
• **Key Pieces**: Oversized blazers, knee-high boots, cozy cardigans, wide-leg trousers
• **Layering**: Start with fitted base layers, add structured middle pieces, finish with statement outerwear
• **Accessories**: Scarves in plaid or solid colors, structured handbags, statement jewelry
        """,
        
        'winter_trends': """
**Winter Style Essentials:**
• **Outerwear**: Wool coats, puffer jackets, trench coats with thermal linings
• **Footwear**: Waterproof boots, thermal insoles, knee-high leather boots
• **Layering Strategy**: Moisture-wicking base, insulating middle layer, windproof outer shell
• **Colors**: Deep jewel tones, classic black, cream, rich browns
• **Accessories**: Wool scarves, leather gloves, warm hats that don't flatten hair
        """,
        
        'spring_trends': """
**Spring Fashion Refresh:**
• **Colors**: Soft pastels, fresh whites, mint green, coral pink, sky blue
• **Fabrics**: Light cotton, linen blends, silk, breathable synthetics
• **Key Pieces**: Midi dresses, light cardigans, white sneakers, cropped jackets
• **Transition**: Layer with pieces you can remove as temperatures rise
• **Footwear**: Ballet flats, low-heeled sandals, clean white sneakers
        """,
        
        'summer_trends': """
**Summer Style Guide:**
• **Colors**: Bright whites, vibrant coral, sunny yellow, ocean blue, tropical prints
• **Fabrics**: Pure cotton, linen, moisture-wicking blends, lightweight silk
• **Key Pieces**: Sundresses, shorts with 4-6 inch inseams, breathable tops
• **Sun Protection**: Wide-brim hats, UV-protective sunglasses, light cover-ups
• **Footwear**: Sandals with arch support, canvas sneakers, comfortable wedges
        """,
        
        'work_professional': """
**Professional Wardrobe Essentials:**
• **Foundation**: Well-fitted blazers in navy, black, and neutral tones
• **Bottoms**: Tailored trousers, knee-length skirts, professional dresses
• **Colors**: Navy, charcoal, cream, soft gray - build on neutral foundations
• **Footwear**: Closed-toe pumps 1-3 inches, professional flats, quality leather
• **Guidelines**: Err on conservative side, invest in quality fabrics, ensure proper fit
• **Accessories**: Minimal jewelry, structured handbags, silk scarves for color
        """,
        
        'casual_weekend': """
**Elevated Casual Style:**
• **Foundation**: Quality jeans in dark wash, comfortable yet polished pieces
• **Tops**: Soft sweaters, fitted t-shirts, button-down shirts
• **Layering**: Cardigans, denim jackets, light blazers for instant polish
• **Footwear**: Clean sneakers, ankle boots, comfortable flats
• **Key Principle**: Choose pieces that look intentional, not thrown together
        """,
        
        'date_night': """
**Date Night Outfit Ideas:**
• **Dinner Dates**: Midi dresses, elegant separates, heeled sandals or pumps
• **Casual Coffee**: High-waisted jeans, silk blouses, ankle boots
• **Activity Dates**: Comfortable yet stylish - think elevated athleisure
• **Evening Events**: Little black dress with statement accessories
• **Comfort Rule**: Never wear anything that makes you fidget or feel self-conscious
        """,
        
        'color_coordination': """
**Color Theory Made Simple:**
• **Monochromatic**: Different shades of same color for sophisticated elegance
• **Complementary**: Navy & coral, purple & yellow for vibrant contrast
• **Neutral Base**: Black, white, gray, beige allow colorful accents to shine
• **Earth Tones**: Browns, greens, oranges work harmoniously together
• **Metallics**: Gold and silver add glamour without competing
• **Starting Point**: Limit to 2-3 colors max, build confidence gradually
        """,
        
        'accessories': """
**Accessorizing Like a Pro:**
• **Statement Rule**: Choose one focal point - bold jewelry OR striking bag OR colorful scarf
• **Metal Mixing**: Pick one dominant metal (70%) with small accents of another (30%)
• **Proportions**: Large accessories with simple outfits, minimal accessories with busy patterns
• **Functionality**: Choose pieces that work with your lifestyle and comfort level
• **Scarves**: Add color and texture, can transform basic outfits instantly
        """,
        
        'sustainable_fashion': """
**Sustainable Style Choices:**
• **Quality Over Quantity**: Invest in well-made pieces that last multiple seasons
• **Versatility**: Choose items that work for multiple occasions and can be styled differently
• **Natural Fibers**: Organic cotton, linen, wool are more sustainable than synthetics
• **Care**: Proper washing, storing, and maintenance extends garment life significantly
• **Secondhand**: Vintage and consignment shopping for unique, affordable pieces
• **Rental**: For special occasion wear you'll only use once
        """,
        
        'body_styling': """
**Flattering Fit Guidelines:**
• **Petite**: Vertical lines, high-waisted bottoms, cropped jackets
• **Tall**: Horizontal elements, wide belts, longer tops and jackets
• **Curvy**: Defined waistlines, V-necks, A-line silhouettes
• **Athletic**: Softer fabrics, peplum tops, bootcut or wide-leg pants
• **Universal**: Proper fit is more important than trends - tailor when needed
        """,
        
        'budget_styling': """
**Budget-Friendly Fashion:**
• **Investment Pieces**: Quality blazer, good jeans, versatile dress, comfortable shoes
• **Trend Shopping**: Buy trendy pieces at lower price points since they're temporary
• **Mix High-Low**: Combine investment pieces with affordable trend items
• **Secondhand Strategy**: Shop consignment for designer pieces at fraction of retail
• **Care**: Proper maintenance makes affordable pieces look more expensive
        """
    }
    
    # Determine the most relevant knowledge category
    knowledge_key = None
    
    # Season-specific queries
    if any(word in query_lower for word in ['autumn', 'fall', 'october', 'november']):
        knowledge_key = 'autumn_fall_trends'
    elif any(word in query_lower for word in ['winter', 'cold', 'december', 'january', 'february']):
        knowledge_key = 'winter_trends'
    elif any(word in query_lower for word in ['spring', 'march', 'april', 'may']):
        knowledge_key = 'spring_trends'
    elif any(word in query_lower for word in ['summer', 'hot', 'june', 'july', 'august']):
        knowledge_key = 'summer_trends'
    
    # Occasion-specific queries
    elif any(word in query_lower for word in ['work', 'office', 'professional', 'business', 'meeting']):
        knowledge_key = 'work_professional'
    elif any(word in query_lower for word in ['casual', 'weekend', 'everyday', 'comfortable']):
        knowledge_key = 'casual_weekend'
    elif any(word in query_lower for word in ['date', 'dinner', 'evening', 'romantic']):
        knowledge_key = 'date_night'
    
    # Style technique queries
    elif any(word in query_lower for word in ['color', 'colours', 'match', 'coordinate']):
        knowledge_key = 'color_coordination'
    elif any(word in query_lower for word in ['accessory', 'accessories', 'jewelry', 'bag', 'scarf']):
        knowledge_key = 'accessories'
    elif any(word in query_lower for word in ['body', 'flattering', 'fit', 'size']):
        knowledge_key = 'body_styling'
    elif any(word in query_lower for word in ['sustainable', 'eco', 'ethical', 'green']):
        knowledge_key = 'sustainable_fashion'
    elif any(word in query_lower for word in ['budget', 'cheap', 'affordable', 'save']):
        knowledge_key = 'budget_styling'
    
    # Build comprehensive response
    response_parts = []
    
    # Add personalized opening based on query
    if any(word in query_lower for word in ['what', 'should', 'wear', 'today']):
        opening = "Here's what I recommend for your styling question:\n\n"
    elif any(word in query_lower for word in ['how', 'style', 'outfit']):
        opening = "Great styling question! Here's how to approach it:\n\n"
    elif any(word in query_lower for word in ['trend', 'fashion', 'latest']):
        opening = "Let me share the latest fashion insights:\n\n"
    else:
        opening = "Here's my fashion advice for you:\n\n"
    
    # Add specific knowledge if found
    if knowledge_key and knowledge_key in fashion_knowledge:
        response_parts.append(fashion_knowledge[knowledge_key])
    
    # Add context from vector store if available
    if context and len(context.strip()) > 50:
        response_parts.append(f"\n**Additional Fashion Insights:**\n{context[:400]}...")
    
    # Add general styling tips if no specific knowledge was found
    if not knowledge_key:
        response_parts.append("""
**Universal Styling Tips:**
• **Fit First**: Proper fit is more important than following every trend
• **Build a Foundation**: Invest in quality basics in neutral colors
• **Personal Style**: Adapt trends to your lifestyle, body type, and preferences
• **Confidence**: The best accessory is confidence in your choices
• **Comfort**: If you don't feel comfortable, it shows - choose what makes you feel great
        """)
    
    # Combine all parts
    full_response = opening + "\n".join(response_parts)
    
    return full_response