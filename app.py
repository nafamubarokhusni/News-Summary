from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import replicate
import os
from dotenv import load_dotenv
import re
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Replicate API token
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
replicate_client = None
if REPLICATE_API_TOKEN:
    replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

class NewsExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_content(self, url):
        """Extract content from news URL"""
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return None, "Invalid URL format"
            
            # Fetch the webpage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract article content
            content = self._extract_article_content(soup)
            
            if not content:
                return None, "Could not extract article content"
            
            return {
                'title': title,
                'content': content,
                'url': url
            }, None
            
        except requests.RequestException as e:
            return None, f"Error fetching URL: {str(e)}"
        except Exception as e:
            return None, f"Error processing content: {str(e)}"
    
    def _is_valid_url(self, url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try various title selectors
        title_selectors = [
            'h1',
            'title',
            '.headline',
            '.article-title',
            '[class*="title"]',
            '[class*="headline"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        
        return "Article Title"
    
    def _extract_article_content(self, soup):
        """Extract main article content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Try various content selectors
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '[class*="article"]',
            '[class*="content"]',
            '.story-body',
            'main'
        ]
        
        content = ""
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if len(text) > len(content):
                    content = text
        
        # If no specific content found, try paragraphs
        if len(content) < 100:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        # Clean up the content
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content

class NewsSummarizer:
    def __init__(self):
        self.client = replicate_client

    def summarize(self, title, content):
        """Summarize news article using Replicate ibm-granite/granite-3.3-8b-instruct"""
        try:
            if not self.client:
                return self._fallback_summarize(content)

            prompt = f"""
            Please provide a clear and concise summary of this news article. Focus on the key facts, main points, and important details.

            Title: {title}

            Article Content: {content[:3000]}

            Summary:"""

            output = self.client.run(
                "ibm-granite/granite-3.3-8b-instruct",
                input={"prompt": prompt}
            )
            # Replicate returns a list of strings, join if needed
            if isinstance(output, list):
                return " ".join([str(o).strip() for o in output if o]).strip()
            return str(output).strip()
        except Exception as e:
            print(f"Replicate API error: {e}")
            return self._fallback_summarize(content)
    
    def _fallback_summarize(self, content):
        """Simple extractive summarization as fallback"""
        sentences = content.replace('\n', ' ').split('. ')
        
        # Take first 3 sentences as summary
        if len(sentences) >= 3:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = content[:500] + '...' if len(content) > 500 else content
        
        return summary

# Initialize components
extractor = NewsExtractor()
summarizer = NewsSummarizer()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize_news():
    """API endpoint to summarize news from URL"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Handle demo case
        if url.startswith('demo://'):
            demo_response = demo_article()
            demo_data = demo_response.get_json()
            
            # Generate summary for demo content
            summary = summarizer.summarize(demo_data['title'], demo_data['content'])
            
            return jsonify({
                'success': True,
                'title': demo_data['title'],
                'summary': summary,
                'url': demo_data['url']
            })
        
        # Extract content from URL
        article_data, error = extractor.extract_content(url)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Generate summary
        summary = summarizer.summarize(article_data['title'], article_data['content'])
        
        return jsonify({
            'success': True,
            'title': article_data['title'],
            'summary': summary,
            'url': url
        })
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/api/demo')
def demo_article():
    """Demo endpoint with sample article data"""
    return jsonify({
        'title': 'Breaking: Scientists Discover New Species in Ocean Depths',
        'content': 'Scientists have discovered a remarkable new species of deep-sea fish in the Mariana Trench, the deepest part of the world\'s oceans. The newly identified species, temporarily named Pseudoliparis marianensis, was found at depths exceeding 8,000 meters below sea level. The discovery was made during a recent expedition using advanced submersible technology. The fish exhibits unique adaptations to extreme pressure environments, including specialized proteins that allow its cells to function under crushing pressure. Researchers believe this discovery could provide insights into how life adapts to extreme conditions and may have implications for understanding life on other planets. The team plans to conduct further studies to better understand the species\' behavior, diet, and ecosystem role.',
        'url': 'demo://sample-news-article'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)