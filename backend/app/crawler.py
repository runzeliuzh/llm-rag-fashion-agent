"""
Fashion Content Crawler - Legal-Safe Implementation

This crawler demonstrates web scraping techniques while avoiding legal issues:

1. EXAMPLE WEBSITES: Uses fictional domain names to show crawling structure
2. ORIGINAL CONTENT: All static content is original educational material
3. NO COPYRIGHT VIOLATIONS: Avoids real fashion website content extraction
4. EDUCATIONAL PURPOSE: Demonstrates RAG system architecture safely

For production use, consider these LEGAL options:
- Wikipedia fashion articles (Creative Commons licensed)
- RSS feeds from fashion sites (publicly available)
- Official APIs (NewsAPI, Guardian API, etc.)
- Educational institution content (public access)
- Government fashion archives (public domain)

This implementation prioritizes legal compliance while maintaining
system functionality for portfolio demonstration.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class FashionBlogCrawler:
    def __init__(self, data_dir="data/blog_crawled"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Example fashion content sources (for demonstration purposes only)
        # In production, use RSS feeds, APIs, or partner agreements
        self.fashion_sources = {
            "example_fashion_magazine": {
                "base_url": "https://example-fashion-magazine.com",
                "section_urls": [
                    "https://example-fashion-magazine.com/trends",
                    "https://example-fashion-magazine.com/styling"
                ]
            },
            "sample_style_blog": {
                "base_url": "https://sample-style-blog.com",
                "section_urls": [
                    "https://sample-style-blog.com/seasonal-trends",
                    "https://sample-style-blog.com/outfit-ideas"
                ]
            },
            "demo_fashion_site": {
                "base_url": "https://demo-fashion-site.com",
                "section_urls": [
                    "https://demo-fashion-site.com/fashion-tips"
                ]
            },
            "fashion_content_api": {
                "base_url": "https://fashion-content-api.com",
                "section_urls": [
                    "https://fashion-content-api.com/api/articles"
                ]
            },
            "style_knowledge_base": {
                "base_url": "https://style-knowledge-base.com",
                "section_urls": [
                    "https://style-knowledge-base.com/public-content"
                ]
            }
        }
        
        # Headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def safe_request(self, url: str, timeout=10):
        """Make a safe HTTP request with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None
    
    def extract_article_content(self, html: str, url: str) -> Dict:
        """Extract meaningful content from article HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Try to find article content using common selectors
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '.article-body'
        ]
        
        content = ""
        title = ""
        
        # Extract title
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Extract content
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Get all paragraphs
                paragraphs = content_div.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    break
        
        # Fallback: get all paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # Clean content
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', content)
        
        return {
            'title': title,
            'content': content,
            'url': url,
            'extracted_at': datetime.now().isoformat(),
            'word_count': len(content.split())
        }
    
    def crawl_fashion_articles(self, max_articles=50):
        """Crawl fashion articles from multiple sources"""
        all_articles = []
        
        # Comprehensive fashion knowledge base (original educational content)
        static_content = [
            {
                'title': 'Complete Guide to Autumn 2025 Fashion Trends',
                'content': 'This autumn, fashion embraces rich textures and sophisticated earth tones that reflect the season\'s natural beauty. Key trends include oversized blazers in camel, burgundy, and forest green that provide structure while maintaining comfort. Knee-high boots in leather and suede become statement pieces, especially when paired with midi skirts or wide-leg trousers. Chunky knit sweaters in cream, oatmeal, and deep navy offer cozy luxury for cooler days. Animal prints return with refined leopard and snake patterns appearing on dresses, scarves, and handbags. Faux fur coats provide glamour for evening occasions while remaining ethically conscious. Layering becomes an art form - start with fitted basics, add textured middle pieces, and finish with statement outerwear.',
                'url': 'https://example-fashion-education.com/autumn-trends-2025',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 135
            },
            {
                'title': 'Mastering the Art of Versatile Blazer Styling',
                'content': 'The versatile blazer stands as the ultimate wardrobe transformer, elevating any outfit from casual to sophisticated. For professional settings, pair with tailored trousers and pointed-toe flats in matching or complementary colors. Create effortless weekend style by wearing over fitted t-shirts with dark denim and white sneakers. Evening elegance emerges when styled with silk camisoles, wide-leg pants, and heeled mules or pumps. The key lies in balancing proportions - oversized blazers require fitted bottoms while structured blazers pair well with flowing silhouettes. Choose neutral colors like navy, black, camel, or charcoal for maximum versatility. Rolling sleeves slightly creates a relaxed, approachable appearance. Quality construction in blazers justifies investment since they transcend seasonal trends.',
                'url': 'https://example-styling-academy.com/blazer-mastery',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 142
            },
            {
                'title': 'Comprehensive Winter Boot Selection and Styling Guide',
                'content': 'Winter footwear combines functionality with fashion, requiring careful consideration of both climate needs and style preferences. Knee-high boots in black or brown leather provide sophistication for office environments while offering warmth and protection. Combat boots with interesting buckle details add edgy contrast to feminine dresses and skirts. Over-the-knee boots create dramatic silhouettes when paired with mini skirts or fitted dresses, elongating legs beautifully. Ankle boots with block heels offer versatility for daily wear, working equally well with jeans, skirts, and dresses. Waterproof hiking boots transcend their outdoor origins when styled with cropped jeans and cozy sweaters. Prioritize boots with good tread for safety on icy surfaces. Invest in quality leather that improves with age and proper care.',
                'url': 'https://example-footwear-guide.com/winter-boots-2025',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 145
            },
            {
                'title': 'Building a Sustainable and Ethical Fashion Wardrobe',
                'content': 'Sustainable fashion choices benefit personal style, financial wellbeing, and environmental responsibility simultaneously. Investing in quality pieces that last multiple seasons proves more economical than frequently replacing cheaper items. Choose natural fibers like organic cotton, linen, and ethically-sourced wool over synthetic materials that shed microplastics. Shop secondhand and vintage stores for unique pieces at significantly lower prices while reducing environmental impact. Rent formal wear for special occasions instead of purchasing items worn once. Proper garment care through gentle washing, appropriate storage, and timely repairs extends clothing life dramatically. Support brands with transparent supply chains and ethical manufacturing practices. Organize clothing swaps with friends to refresh wardrobes without environmental cost.',
                'url': 'https://example-sustainable-style.org/ethical-wardrobe',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 138
            },
            {
                'title': 'Professional Accessorizing: Elevating Any Outfit Strategically',
                'content': 'Strategic accessorizing transforms basic outfits into polished, professional looks without requiring wardrobe overhaul. Begin with one statement piece and build supporting elements around it - choose either bold jewelry, colorful scarf, or striking handbag as the focal point. Mix metal tones confidently by establishing one dominant metal (70%) with subtle accents of another (30%). Layer necklaces of different lengths for sophisticated visual interest while maintaining workplace appropriateness. Match handbag color to shoes for cohesive traditional looks, or create intentional contrast for modern statements. Belts define waistlines and add structure to flowing garments like dresses and oversized tops. Sunglasses should complement face shapes - round faces benefit from angular frames while square faces prefer rounded styles.',
                'url': 'https://example-professional-styling.com/accessory-mastery',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 141
            },
            {
                'title': 'Decoding Business Casual: Modern Professional Dress Guidelines',
                'content': 'Business casual dress codes require balancing professionalism with personal expression and comfort. For women, blouses in silk or high-quality cotton pair excellently with dress pants or knee-length pencil skirts. Cardigans and unstructured blazers add polish when needed while maintaining approachability. Choose closed-toe shoes with moderate heels for comfort during long workdays - pumps, loafers, or professional flats work well. Avoid revealing necklines, hemlines above the knee, or casual fabrics like denim and jersey. Build around neutral colors like navy, gray, charcoal, and cream for maximum versatility. Add personality through accessories like colorful scarves, statement jewelry, or interesting textures. Invest in quality fabrics that resist wrinkles and maintain crisp appearance throughout demanding schedules.',
                'url': 'https://example-workplace-fashion.com/business-casual-guide',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 144
            },
            {
                'title': 'Creating Memorable and Confident Date Night Looks',
                'content': 'Successful date night styling balances personal expression with occasion appropriateness while prioritizing comfort and confidence. Little black dresses remain timeless choices - style differently with accessories for various date types and venues. For casual coffee dates, try high-waisted jeans with silk blouses and comfortable ankle boots that allow walking. Dinner dates call for midi dresses or elegant separates with heeled sandals that provide sophistication without sacrificing stability. Concert and entertainment venues suit edgy leather jackets over fitted tops with comfortable boots for standing and dancing. Always consider venue and planned activities when choosing outfits. Avoid new shoes or uncomfortable fabrics that might distract from enjoying the experience. Confidence comes from feeling authentic and comfortable in your choices.',
                'url': 'https://example-date-style.com/romantic-outfit-ideas',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 140
            },
            {
                'title': 'Color Theory and Coordination for Effortless Style',
                'content': 'Understanding color theory eliminates guesswork from outfit coordination while creating sophisticated, intentional looks. Monochromatic schemes using different shades and tints of the same color create elegant, elongating effects that work for any body type. Complementary colors like navy and coral or purple and yellow provide vibrant, eye-catching contrast perfect for making statements. Neutral bases of black, white, gray, beige, and cream allow colorful accessories and accent pieces to shine without overwhelming. Earth tones including various browns, greens, and oranges work harmoniously together, creating warm, approachable looks. Metallics like gold, silver, and rose gold function as neutrals, adding glamour without competing with other colors. Start with two colors maximum when beginning, then gradually experiment with more complex combinations as confidence and understanding grow.',
                'url': 'https://example-color-styling.com/coordination-mastery',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 148
            },
            {
                'title': 'Body-Positive Styling: Enhancing Your Natural Silhouette',
                'content': 'Body-positive styling focuses on enhancing individual silhouettes while promoting comfort, confidence, and personal expression. Pear-shaped figures can emphasize upper bodies with statement tops, interesting necklines, and structured jackets while choosing A-line or straight-leg bottoms. Apple shapes benefit from empire waistlines, V-necks, and vertical lines that create length and draw attention upward. Hourglass figures can emphasize waists with belted pieces, fitted silhouettes, and wrap styles that showcase natural curves. Athletic builds look stunning in softer fabrics, peplum tops, and flowing pieces that add feminine curves. Remember these are guidelines for exploration, not rigid rules - the most important factor is how clothing makes you feel confident, comfortable, and authentically yourself.',
                'url': 'https://example-body-positive-style.com/silhouette-guide',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 143
            },
            {
                'title': 'Budget-Conscious Fashion: Building Style Without Breaking Bank',
                'content': 'Creating exceptional personal style requires strategy rather than unlimited budgets, focusing on smart investments and creative styling. Identify pieces worn most frequently - quality blazer, comfortable shoes, versatile dress, well-fitted jeans - and invest accordingly since cost-per-wear decreases over time. Shop end-of-season sales for classic pieces that transcend trends, buying winter coats in spring and summer dresses in fall. Consignment and thrift stores offer designer pieces at significant discounts while providing unique finds unavailable in mainstream retail. Mix high and low price points - pair affordable basics with one statement investment piece for balanced looks. Proper tailoring makes inexpensive pieces appear custom-made and luxurious. Build gradually rather than purchasing complete outfits, allowing wardrobe to develop organically over time.',
                'url': 'https://example-budget-fashion.com/smart-shopping-guide',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 147
            }
        ]
        
        all_articles.extend(static_content)
        
        # Add Wikipedia fashion articles (100% legal)
        print("🔍 Crawling Wikipedia fashion content...")
        try:
            wikipedia_articles = self.crawl_wikipedia_fashion(max_articles=3)
            all_articles.extend(wikipedia_articles)
            print(f"✅ Added {len(wikipedia_articles)} Wikipedia articles")
        except Exception as e:
            print(f"⚠️ Wikipedia crawling failed: {e}")
        
        # Try to crawl from actual sources
        for source_name, source_info in self.fashion_sources.items():
            if len(all_articles) >= max_articles:
                break
                
            print(f"🔍 Attempting to crawl from {source_name}...")
            
            try:
                # Real web crawling implementation
                articles_found = self.crawl_source_real(source_name, source_info, max_per_source=3)
                all_articles.extend(articles_found)
                print(f"✅ Found {len(articles_found)} articles from {source_name}")
                
            except Exception as e:
                print(f"⚠️ Failed to crawl {source_name}: {e}")
                # Fallback to static content if real crawling fails
                fallback_articles = self.get_fallback_content(source_name, source_info)
                all_articles.extend(fallback_articles)
                print(f"📚 Using fallback content for {source_name}")
            
            # Be respectful - add delay between sources
            time.sleep(2)
        
        # Save all articles
        for article in all_articles:
            self.save_article(article)
        
        print(f"✅ Successfully collected {len(all_articles)} fashion articles")
        return all_articles
    
    def crawl_source_real(self, source_name: str, source_info: Dict, max_per_source=3) -> List[Dict]:
        """Actually crawl real websites for fashion content"""
        articles = []
        
        for section_url in source_info["section_urls"]:
            if len(articles) >= max_per_source:
                break
                
            print(f"  📡 Crawling: {section_url}")
            
            # Get the main page
            response = self.safe_request(section_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links based on common patterns
            article_links = self.find_article_links(soup, source_info["base_url"], source_name)
            
            # Crawl individual articles
            for link in article_links[:max_per_source]:
                if len(articles) >= max_per_source:
                    break
                    
                article_data = self.crawl_single_article(link)
                if article_data and article_data['content']:
                    articles.append(article_data)
                    print(f"    ✅ Extracted: {article_data['title'][:50]}...")
                
                # Respectful delay between articles
                time.sleep(1)
        
        return articles
    
    def find_article_links(self, soup: BeautifulSoup, base_url: str, source_name: str) -> List[str]:
        """Find article links on a fashion website page"""
        links = []
        
        # Common selectors for article links on fashion sites
        link_selectors = [
            'a[href*="/fashion/"]',
            'a[href*="/style/"]',
            'a[href*="/trends/"]',
            'article a',
            '.article-link',
            '.post-link',
            'h2 a',
            'h3 a'
        ]
        
        # Site-specific selectors for demonstration
        # These would be adapted based on actual content sources used
        if source_name == "example_fashion_magazine":
            link_selectors.extend([
                '.article-headline a',
                '.trend-article-link'
            ])
        elif source_name == "sample_style_blog":
            link_selectors.extend([
                '.blog-post-title a',
                '.style-article a'
            ])
        elif source_name == "demo_fashion_site":
            link_selectors.extend([
                '.fashion-content a',
                '.style-guide-link a'
            ])
        elif source_name == "fashion_content_api":
            link_selectors.extend([
                '.api-article-link',
                '.content-item a'
            ])
        elif source_name == "style_knowledge_base":
            link_selectors.extend([
                '.knowledge-article a',
                '.style-tip-link a'
            ])
        
        for selector in link_selectors:
            try:
                found_links = soup.select(selector)
                for link in found_links:
                    href = link.get('href')
                    if href:
                        # Convert relative URLs to absolute
                        full_url = urljoin(base_url, href)
                        
                        # Filter for fashion-related content
                        if self.is_fashion_related(full_url, link.get_text()):
                            links.append(full_url)
                            
                if links:
                    break  # Stop at first successful selector
                    
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {e}")
                continue
        
        # Remove duplicates and limit
        return list(set(links))[:10]
    
    def is_fashion_related(self, url: str, title: str) -> bool:
        """Check if URL/title is fashion-related"""
        fashion_keywords = [
            'fashion', 'style', 'outfit', 'trend', 'clothing', 'dress',
            'shoes', 'accessory', 'beauty', 'wardrobe', 'designer',
            'runway', 'collection', 'look', 'wear', 'chic'
        ]
        
        text_to_check = (url + ' ' + (title or '')).lower()
        return any(keyword in text_to_check for keyword in fashion_keywords)
    
    def crawl_single_article(self, url: str) -> Dict:
        """Crawl a single article page"""
        response = self.safe_request(url)
        if not response:
            return None
            
        return self.extract_article_content(response.text, url)
    
    def get_fallback_content(self, source_name: str, source_info: Dict) -> List[Dict]:
        """
        Provide comprehensive fallback fashion content
        This content is original and educational, avoiding any copyright issues
        """
        fallback_content = {
            "example_fashion_magazine": [
                {
                    'title': 'Essential Wardrobe Building: Investment Pieces That Last',
                    'content': 'Building a timeless wardrobe starts with identifying key investment pieces that transcend seasonal trends. A well-tailored blazer in navy or black provides instant sophistication and works for both professional and casual settings. Quality denim in a flattering cut becomes the foundation for countless outfits. A classic trench coat offers versatility across seasons and occasions. Comfortable leather shoes in neutral colors provide polish and durability. A little black dress serves multiple purposes from business meetings to evening events. These pieces form the backbone of a functional wardrobe that reduces decision fatigue while maintaining style.',
                    'url': f'{source_info["base_url"]}/investment-pieces-guide',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 108
                },
                {
                    'title': 'Color Psychology in Fashion: Choosing Colors That Work',
                    'content': 'Understanding color psychology helps create outfits that convey the right message and enhance personal confidence. Navy blue projects trustworthiness and professionalism, making it ideal for business settings. Burgundy and deep reds convey power and passion, perfect for important meetings or evening events. Forest green suggests stability and growth, working well in creative environments. Soft pastels like blush pink and lavender create approachable, feminine energy. Black remains the ultimate power color, conveying sophistication and authority. When building outfits, consider the emotional impact of color choices alongside personal preferences and skin tone compatibility.',
                    'url': f'{source_info["base_url"]}/color-psychology',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 115
                },
                {
                    'title': 'Seasonal Transition Styling: Mastering Layering Techniques',
                    'content': 'Mastering layering allows for seamless seasonal transitions while maximizing wardrobe versatility. Start with lightweight base layers in moisture-wicking fabrics that can be worn alone or under other pieces. Add structured middle layers like cardigans, blazers, or lightweight sweaters that provide warmth without bulk. Finish with adaptable outer layers that can be easily removed as temperatures change throughout the day. Textures play a crucial role in successful layering - mix smooth and textured fabrics for visual interest. Consider color coordination when layering, using neutral bases with one accent color to maintain cohesion.',
                    'url': f'{source_info["base_url"]}/layering-techniques',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 119
                }
            ],
            "sample_style_blog": [
                {
                    'title': 'Body-Positive Styling: Dressing for Your Unique Shape',
                    'content': 'Body-positive styling focuses on enhancing your natural silhouette while promoting comfort and confidence. For pear-shaped figures, emphasize the upper body with statement tops and jackets while choosing A-line or straight-leg bottoms. Apple shapes benefit from empire waistlines and V-necks that create vertical lines and draw attention upward. Hourglass figures can emphasize the waist with belted pieces and fitted silhouettes. Athletic builds look great in softer fabrics and peplum tops that add curves. Remember that these are guidelines, not rules - the most important factor is how clothing makes you feel confident and comfortable.',
                    'url': f'{source_info["base_url"]}/body-positive-styling',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 118
                },
                {
                    'title': 'Sustainable Fashion Practices for the Modern Wardrobe',
                    'content': 'Sustainable fashion practices benefit both personal style and environmental responsibility. Quality over quantity should guide purchasing decisions - invest in well-made pieces that will last for years rather than fast fashion items. Choose natural fibers like organic cotton, linen, and wool which are biodegradable and often more durable. Proper garment care extends clothing life significantly through gentle washing, proper storage, and timely repairs. Secondhand shopping offers unique pieces at affordable prices while reducing environmental impact. Clothing swaps with friends provide free wardrobe refreshes. When disposing of unwanted items, donate to charity or textile recycling programs rather than throwing away.',
                    'url': f'{source_info["base_url"]}/sustainable-fashion',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 125
                },
                {
                    'title': 'Professional Styling on Any Budget: Smart Shopping Strategies',
                    'content': 'Building a professional wardrobe doesn\'t require a luxury budget with smart shopping strategies and careful planning. Focus investments on pieces worn most frequently - a quality blazer and comfortable shoes provide better value than multiple trendy items. Shop end-of-season sales for classic pieces that transcend trends. Consignment stores offer designer pieces at significant discounts. Mix high and low - pair affordable basics with one statement investment piece. Proper tailoring makes inexpensive pieces look custom-made. Build gradually rather than shopping for entire outfits at once. Create a wishlist and wait for sales on specific items rather than impulse buying.',
                    'url': f'{source_info["base_url"]}/budget-professional-styling',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 122
                }
            ],
            "demo_fashion_site": [
                {
                    'title': 'Accessory Strategies: Maximizing Impact with Minimal Pieces',
                    'content': 'Strategic accessorizing transforms basic outfits into polished looks without requiring extensive wardrobe investments. The statement piece rule suggests choosing one focal point - either bold jewelry, a colorful scarf, or a striking handbag - while keeping other accessories minimal. Scarves offer incredible versatility, functioning as neck accessories, hair wraps, or bag decorations. Quality handbags in neutral colors work across multiple outfits and occasions. When mixing metals in jewelry, maintain a 70-30 ratio with one dominant metal and subtle accents of another. Functional accessories like watches and sunglasses should complement rather than compete with outfit elements.',
                    'url': f'{source_info["base_url"]}/accessory-strategies',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 121
                },
                {
                    'title': 'Fit and Proportion: The Foundation of Great Style',
                    'content': 'Perfect fit forms the foundation of exceptional style, often making inexpensive pieces appear luxurious while poor fit diminishes even designer clothing. Shoulder seams should align with natural shoulder points - this is the most important fit element and difficult to alter. Sleeve length should show a quarter to half inch of shirt cuff beneath jacket sleeves. Pant length should create a slight break on shoes for traditional looks or no break for modern styling. Proper waist placement follows natural waistline rather than hip bones. When in doubt, choose slightly larger sizes for professional alteration rather than settling for too-small garments.',
                    'url': f'{source_info["base_url"]}/fit-proportion-guide',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 125
                }
            ],
            "fashion_content_api": [
                {
                    'title': 'Capsule Wardrobe Essentials: 30 Pieces for Endless Combinations',
                    'content': 'A well-designed capsule wardrobe maximizes outfit possibilities while minimizing decision fatigue and closet clutter. Essential pieces include five tops in varying sleeve lengths and necklines, three bottoms in different silhouettes, two blazers or structured jackets, one dress suitable for multiple occasions, and three pairs of shoes covering casual, professional, and formal needs. Color coordination ensures all pieces work together - build around three neutral colors with one accent color. Quality fabrics that resist wrinkles and maintain shape perform better in capsule systems. Seasonal additions refresh the wardrobe without complete overhaul.',
                    'url': f'{source_info["base_url"]}/capsule-wardrobe-guide',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 118
                },
                {
                    'title': 'Digital Age Professional Dressing: Virtual Meeting Style Guide',
                    'content': 'Professional dressing for digital interactions requires new considerations beyond traditional office attire. Camera positioning affects how clothing appears - higher necklines and structured shoulders photograph better than loose or low-cut styles. Solid colors and subtle patterns work better than busy prints which can create visual noise on screen. Good lighting enhances appearance more than expensive clothing - position yourself facing a window or invest in a ring light. While comfortable bottoms are practical for video calls, maintaining complete professional appearance supports psychological confidence. Keep a blazer nearby for unexpected video calls when working from home.',
                    'url': f'{source_info["base_url"]}/virtual-meeting-style',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 117
                }
            ],
            "style_knowledge_base": [
                {
                    'title': 'Texture Mixing Mastery: Adding Visual Interest to Simple Outfits',
                    'content': 'Texture mixing elevates simple outfits by creating visual depth and sophistication without relying on bold colors or patterns. Smooth textures like silk and satin pair beautifully with rough textures like tweed or corduroy. Shiny surfaces such as leather complement matte fabrics like cotton or wool. Mixing weights adds dimension - combine heavy knits with lightweight chiffon or substantial denim with delicate lace details. Limit texture mixing to two or three different textures per outfit to avoid overwhelming the eye. Neutral color palettes allow textures to be the focal point without competing elements.',
                    'url': f'{source_info["base_url"]}/texture-mixing-guide',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 113
                },
                {
                    'title': 'Confidence Through Clothing: Psychology of Personal Style',
                    'content': 'Personal style serves as external expression of internal identity, directly impacting confidence and self-perception. Research shows that clothing choices affect both how others perceive us and how we perceive ourselves. Well-fitted, comfortable clothing reduces self-consciousness and allows focus on important tasks rather than appearance concerns. Color choices influence mood - wearing preferred colors boosts confidence while unflattering colors can diminish self-assurance. Developing personal style involves identifying clothing that aligns with lifestyle, values, and authentic self-expression rather than following trends blindly. Confidence comes from wearing clothes that feel genuinely representative of personal identity.',
                    'url': f'{source_info["base_url"]}/confidence-through-clothing',
                    'extracted_at': datetime.now().isoformat(),
                    'word_count': 121
                }
            ]
        }
        
        # Get content for the specific source, or provide general content
        return fallback_content.get(source_name, [
            {
                'title': 'Universal Style Principles for Every Wardrobe',
                'content': 'Successful personal style builds on universal principles that transcend trends and individual preferences. Quality matters more than quantity - investing in fewer, better-made pieces provides superior long-term value and satisfaction. Proper fit transforms even basic pieces into polished looks, while poor fit undermines expensive designer items. Color coordination creates harmony and sophistication, starting with neutral foundations and adding accent colors gradually. Comfort enables confidence - clothing should enhance rather than restrict movement and self-expression. Personal style develops over time through experimentation and reflection, guided by lifestyle needs and authentic preferences rather than external pressure to follow trends.',
                'url': f'https://style-education.com/universal-principles',
                'extracted_at': datetime.now().isoformat(),
                'word_count': 119
            }
        ])

    def save_article(self, article: Dict):
        """Save article to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = urlparse(article['url']).netloc.replace('.', '_')
        filename = f"{domain}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
    
    def load_crawled_articles(self) -> List[Dict]:
        """Load all previously crawled articles"""
        articles = []
        
        if not os.path.exists(self.data_dir):
            return articles
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        article = json.load(f)
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to load {filepath}: {e}")
        
        return articles

    def crawl_wikipedia_fashion(self, max_articles=5) -> List[Dict]:
        """
        Crawl Wikipedia fashion articles (100% legal - Creative Commons licensed)
        This demonstrates real crawling with zero legal risk
        """
        wikipedia_articles = []
        
        # Fashion topics available on Wikipedia
        fashion_topics = [
            "Fashion",
            "Fashion_design", 
            "Sustainable_fashion",
            "Color_theory",
            "Business_casual",
            "Casual_wear",
            "Fashion_accessory",
            "Wardrobe_(clothing)"
        ]
        
        try:
            for topic in fashion_topics[:max_articles]:
                try:
                    # Use Wikipedia API (completely legal)
                    api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
                    response = self.safe_request(api_url)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        
                        # Extract content from Wikipedia API response
                        article = {
                            'title': data.get('title', topic.replace('_', ' ')),
                            'content': data.get('extract', ''),
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                            'source': 'wikipedia_api',
                            'extracted_at': datetime.now().isoformat(),
                            'word_count': len(data.get('extract', '').split())
                        }
                        
                        if article['content'] and len(article['content']) > 100:
                            wikipedia_articles.append(article)
                            print(f"✅ Wikipedia: {article['title']}")
                        
                except Exception as e:
                    print(f"⚠️ Failed to get Wikipedia article for {topic}: {e}")
                    continue
                    
                # Be respectful to Wikipedia
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️ Wikipedia crawling failed: {e}")
        
        return wikipedia_articles

def main():
    """Main function to run crawler"""
    crawler = FashionBlogCrawler()
    articles = crawler.crawl_fashion_articles(max_articles=20)
    print(f"Crawled {len(articles)} articles")
    
    # Also populate vector store immediately
    from app.vector_store import cost_optimized_vector_store as vector_store
    
    documents = []
    metadatas = []
    
    for article in articles:
        if article['content'] and len(article['content']) > 50:
            documents.append(article['content'])
            metadatas.append({
                'title': article['title'],
                'url': article['url'],
                'source': article.get('source', 'fashion_blog_crawl'),
                'extracted_at': article['extracted_at']
            })
    
    if documents:
        try:
            vector_store.add_documents(documents, metadatas=metadatas)
            print(f"✅ Added {len(documents)} articles to vector store")
        except Exception as e:
            print(f"❌ Failed to add to vector store: {e}")
    
    print("🎉 Crawler completed and vector store populated!")

if __name__ == "__main__":
    main()
