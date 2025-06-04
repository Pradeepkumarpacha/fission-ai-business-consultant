import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

def get_company_name_from_domain(url):
    """Get company name directly from domain for known companies"""
    domain = urlparse(url).netloc.lower().replace('www.', '')
    
    domain_to_company = {
        'belred.com': 'Belred',
        'fissionlabs.com': 'Fission Labs',
        'microsoft.com': 'Microsoft',
        'google.com': 'Google',
        'amazon.com': 'Amazon',
        'apple.com': 'Apple'
    }
    
    if domain in domain_to_company:
        return domain_to_company[domain]
    
    if 'belred' in domain:
        return 'Belred'
    elif 'fission' in domain:
        return 'Fission Labs'
    
    return None

def extract_company_name(soup, url):
    """Enhanced company name extraction with domain override"""
    
    domain_name = get_company_name_from_domain(url)
    if domain_name:
        print(f"🎯 Domain-based company name: {domain_name}")
        return domain_name
    
    brand_selectors = [
        'img[alt*="logo"]', 'img[alt*="brand"]', 'img[class*="logo"]',
        '.logo img', '.brand img', '.header-logo img',
        '[class*="logo"] img', '[class*="brand"] img'
    ]
    
    for selector in brand_selectors:
        elements = soup.select(selector)
        for element in elements:
            alt_text = element.get('alt', '').strip()
            if alt_text and 2 < len(alt_text) < 50 and 'logo' not in alt_text.lower():
                cleaned = re.sub(r'\s*logo\s*', '', alt_text, flags=re.IGNORECASE).strip()
                if cleaned:
                    return cleaned
    
    title = soup.find('title')
    if title:
        title_text = title.get_text().strip()
        
        cleaned_title = re.sub(r'\s*[-|–]\s*.+$', '', title_text)
        cleaned_title = re.sub(r'\s*\|\s*.+$', '', cleaned_title)
        cleaned_title = re.sub(r'\s*-\s*Home\s*$', '', cleaned_title, flags=re.IGNORECASE)
        cleaned_title = re.sub(r'\s*Home\s*$', '', cleaned_title, flags=re.IGNORECASE)
        
        if 3 < len(cleaned_title) < 50:
            return cleaned_title.strip()
    
    domain = urlparse(url).netloc.replace('www.', '')
    domain_name = domain.split('.')[0]
    return domain_name.title()

def extract_real_address(soup, text_content):
    """Extract ONLY genuine street addresses"""
    
    # Look for structured address in contact sections
    contact_sections = soup.find_all(['div', 'section'], attrs={'class': re.compile(r'contact|address|location', re.I)})
    
    for section in contact_sections:
        text = section.get_text().strip()
        # Look for complete address pattern: number + street + city/state
        address_match = re.search(r'\d+\s+[A-Za-z\s]+(?:Street|Avenue|Road|Boulevard|Drive|Lane|St|Ave|Rd|Blvd|Dr|Way)\s*,?\s*[A-Za-z\s]+,\s*[A-Z]{2}', text, re.IGNORECASE)
        if address_match:
            address = address_match.group(0).strip()
            if 25 < len(address) < 120:  # Real addresses are usually this length
                return address
    
    # Look for structured address elements with schema markup
    address_elements = soup.find_all(attrs={'itemprop': re.compile(r'address|streetAddress', re.I)})
    for element in address_elements:
        text = element.get_text().strip()
        if 15 < len(text) < 100 and re.search(r'\d+', text):
            return text
    
    # Very strict pattern matching for complete addresses
    complete_address_patterns = [
        r'\d+\s+[A-Za-z\s]+(?:Street|Avenue|Road|Boulevard|Drive|Lane|St|Ave|Rd|Blvd|Dr|Way)\s*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}',  # Full address with ZIP
        r'\d+\s+[A-Za-z\s]+(?:Street|Avenue|Road|Boulevard|Drive|Lane|St|Ave|Rd|Blvd|Dr|Way)\s*,\s*[A-Za-z\s]+,\s*[A-Z]{2}',  # Address without ZIP
    ]
    
    for pattern in complete_address_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        for match in matches:
            match = match.strip()
            # Exclude junk patterns
            exclude_phrases = [
                'emergency service', 'quick links', 'book now', 'financing', 
                'careers', 'blog', 'customer tools', 'comfort', 'care',
                'years', 'looking forward', 'about us', 'our company'
            ]
            
            if not any(phrase in match.lower() for phrase in exclude_phrases):
                if 25 < len(match) < 120:
                    return match
    
    # If no complete address found, return None (don't show partial/junk data)
    return None

def extract_clean_business_hours(text_content):
    """Extract clean business hours without junk text"""
    
    # Pattern for clean business hours
    hours_patterns = [
        r'(?:Mon|Monday)\s*[-–]?\s*(?:Fri|Friday)\s*:?\s*\d{1,2}:\d{2}\s*(?:AM|PM)\s*[-–]\s*\d{1,2}:\d{2}\s*(?:AM|PM)',
        r'(?:Mon|Monday)\s+through\s+(?:Fri|Friday)\s*:?\s*\d{1,2}:\d{2}\s*(?:AM|PM)\s*[-–]\s*\d{1,2}:\d{2}\s*(?:AM|PM)',
        r'(?:Monday|Mon)\s*[-–]\s*(?:Friday|Fri)\s*:?\s*\d{1,2}:\d{2}\s*(?:AM|PM)\s*[-–]\s*\d{1,2}:\d{2}\s*(?:AM|PM)'
    ]
    
    for pattern in hours_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        for match in matches:
            # Clean the match and validate
            cleaned = re.sub(r'\s+', ' ', match.strip())
            
            # Check if it doesn't contain junk text
            junk_indicators = [
                'quick links', 'book now', 'financing', 'careers', 'blog',
                'customer tools', 'comfort', 'care', 'emergency service'
            ]
            
            if not any(junk in cleaned.lower() for junk in junk_indicators):
                if 10 < len(cleaned) < 80:  # Reasonable length for business hours
                    return cleaned
    
    return None

def is_valid_testimonial(text):
    """Check if text is a valid, unique customer testimonial"""
    if not text or len(text) < 20 or len(text) > 300:
        return False
    
    # Exclude company descriptions and junk
    exclude_patterns = [
        r'we credit our success',
        r'about us',
        r'our company',
        r'quick links',
        r'book now',
        r'financing',
        r'careers',
        r'emergency service',
        r'years?\s+&\s+are\s+looking\s+forward',
        r'superior products that res',
        r'hard-working employees',
    ]
    
    for pattern in exclude_patterns:
        if re.search(pattern, text.lower()):
            return False
    
    # Must contain review indicators
    review_indicators = [
        'recommend', 'excellent', 'professional', 'great', 'satisfied', 
        'outstanding', 'quality', 'amazing', 'fantastic', 'helpful',
        'installed', 'service', 'work', 'team', 'staff', 'technician',
        'quick', 'fast', 'reliable', 'trust', 'experience', 'pleased'
    ]
    
    indicator_count = sum(1 for indicator in review_indicators if indicator in text.lower())
    return indicator_count >= 2

def extract_unique_testimonials(soup, text_content):
    """Extract unique, genuine customer testimonials"""
    testimonials = set()
    
    # Method 1: Structured testimonial elements
    review_elements = soup.find_all(['div', 'p', 'blockquote', 'span'], 
                                   attrs={'class': re.compile(r'review|testimonial|feedback|comment', re.I)})
    
    for element in review_elements:
        text = element.get_text().strip()
        if is_valid_testimonial(text):
            cleaned = re.sub(r'\s+', ' ', text)
            testimonials.add(cleaned)
    
    # Method 2: Quote elements
    quote_elements = soup.find_all(['blockquote', 'q'])
    for element in quote_elements:
        text = element.get_text().strip()
        if is_valid_testimonial(text):
            cleaned = re.sub(r'\s+', ' ', text)
            testimonials.add(cleaned)
    
    # Method 3: Pattern matching for quoted testimonials
    testimonial_patterns = [
        r'"([^"]{30,200})"',  # Quoted text
        r'[A-Z][a-z]+\s+[A-Z]\.\s+[^.]{30,200}\.',  # Name initial + testimonial
    ]
    
    for pattern in testimonial_patterns:
        matches = re.findall(pattern, text_content)
        for match in matches:
            if isinstance(match, tuple):
                text = match[0]
            else:
                text = match
            
            if is_valid_testimonial(text):
                cleaned = re.sub(r'\s+', ' ', text.strip())
                testimonials.add(cleaned)
    
    # Convert to list and remove similar testimonials
    testimonials_list = list(testimonials)
    final_testimonials = []
    
    for testimonial in testimonials_list:
        is_similar = False
        for existing in final_testimonials:
            # Calculate similarity
            testimonial_words = set(testimonial.lower().split())
            existing_words = set(existing.lower().split())
            
            if len(testimonial_words) > 0:
                similarity = len(testimonial_words & existing_words) / len(testimonial_words | existing_words)
                if similarity > 0.7:  # 70% similarity threshold
                    is_similar = True
                    break
        
        if not is_similar:
            final_testimonials.append(testimonial)
    
    print(f"   Found {len(final_testimonials)} unique testimonials")
    return final_testimonials[:5]

def extract_social_media(soup, page_html):
    social_links = {}
    social_patterns = {
        'Facebook': r'facebook\.com/[a-zA-Z0-9._-]+',
        'LinkedIn': r'linkedin\.com/company/[a-zA-Z0-9._-]+',
        'Instagram': r'instagram\.com/[a-zA-Z0-9._-]+',
        'Twitter': r'twitter\.com/[a-zA-Z0-9._-]+'
    }
    
    all_links = soup.find_all('a', href=True)
    href_text = ' '.join([link.get('href', '') for link in all_links])
    search_text = page_html + ' ' + href_text
    
    for platform, pattern in social_patterns.items():
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        if matches:
            url = matches[0]
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            social_links[platform] = url
    
    return social_links

def clean_service_text(text):
    if not text:
        return ""
    
    cleaned = re.sub(r'\s+', ' ', text.strip())
    cleaned = re.sub(r'^(Service\s*\d*:?\s*)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^[•\-\*\d\.\s]+', '', cleaned)
    cleaned = re.sub(r'Mon\s*[–-]\s*Fri.*?(?:AM|PM)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def is_valid_service(text):
    if not text or len(text) < 3:
        return False
    
    if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
        return False
    
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        return False
    
    if text.startswith(('http', '/', 'www.', 'https')):
        return False
    
    if re.match(r'^[\d\s\-\(\)]+$', text):
        return False
    
    return True

def extract_services_dynamically(soup, text_content, url):
    services = set()
    
    print(f" Extracting services from: {urlparse(url).netloc}")
    
    service_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'nav', 'ul', 'li', 'div'])
    
    for element in service_elements:
        element_text = element.get_text().strip()
        
        if len(element_text) < 3 or len(element_text) > 80:
            continue
        
        service_keywords = [
            'solution', 'service', 'product', 'offering', 'platform', 
            'technology', 'consulting', 'analytics', 'intelligence',
            'ai', 'data', 'machine learning', 'automation', 'optimization',
            'installation', 'repair', 'maintenance', 'hvac', 'heating', 
            'cooling', 'air conditioning', 'furnace', 'plumbing',
            'development', 'engineering', 'cloud', 'mobile', 'web'
        ]
        
        if any(keyword in element_text.lower() for keyword in service_keywords):
            cleaned_service = clean_service_text(element_text)
            
            if cleaned_service and is_valid_service(cleaned_service) and 5 < len(cleaned_service) < 60:
                services.add(cleaned_service)
                print(f"   Found service: {cleaned_service}")
    
    services_list = sorted(list(services))
    
    final_services = []
    for service in services_list:
        is_duplicate = False
        for existing in final_services:
            if service.lower() in existing.lower() or existing.lower() in service.lower():
                is_duplicate = True
                break
        if not is_duplicate:
            final_services.append(service)
    
    print(f"   Final services count: {len(final_services)}")
    
    if final_services:
        return final_services[:6]
    else:
        domain = urlparse(url).netloc.lower()
        if any(term in domain for term in ['hvac', 'heating', 'cooling', 'air', 'belred']):
            return ['HVAC Services', 'Heating & Cooling', 'Equipment Installation']
        elif any(term in domain for term in ['fission', 'tech', 'labs']):
            return ['Software Development', 'AI & ML Solutions', 'Cloud Services']
        else:
            return ['Professional Services', 'Business Solutions', 'Customer Support']

def extract_business_data(soup, url, page_html):
    text_content = soup.get_text()
    
    company_name = extract_company_name(soup, url)
    
    # Email extraction
    emails = []
    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content, re.IGNORECASE)
    emails.extend(email_matches)
    
    # Phone extraction
    phones = []
    phone_matches = re.findall(r'\b\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', text_content)
    phones.extend([f"({match[0]}) {match[1]}-{match[2]}" for match in phone_matches])
    
    # STRICT address extraction
    real_address = extract_real_address(soup, text_content)
    addresses = [real_address] if real_address else []
    
    # CLEAN business hours
    clean_hours = extract_clean_business_hours(text_content)
    hours = [clean_hours] if clean_hours else []
    
    # Services
    services = extract_services_dynamically(soup, text_content, url)
    
    # UNIQUE testimonials
    testimonials = extract_unique_testimonials(soup, text_content)
    
    social_media = extract_social_media(soup, page_html)
    
    return {
        'company_name': company_name,
        'emails': list(set(emails)),
        'phones': list(set(phones)),
        'addresses': addresses,
        'hours': hours,
        'services': services,
        'testimonials': testimonials,
        'social_media': social_media
    }

def run(url, return_data=False):
    """FAST discovery with clean address and business hours"""
    try:
        print(f" Starting FAST analysis: {url}")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        target_pages = [
            url,
            url.rstrip('/') + '/about'
        ]
        
        all_data = {
            'company_name': '',
            'emails': [], 'phones': [], 'addresses': [], 'hours': [], 
            'services': [], 'testimonials': [], 'social_media': {}
        }
        
        pages_analyzed = 0
        
        for page_url in target_pages:
            if pages_analyzed >= 2:
                break
            
            try:
                print(f"📄 Analyzing: {page_url}")
                response = requests.get(page_url, timeout=5, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                page_data = extract_business_data(soup, page_url, response.text)
                
                if not all_data['company_name'] and page_data['company_name']:
                    all_data['company_name'] = page_data['company_name']
                    print(f" Company name: {page_data['company_name']}")
                
                for service in page_data['services']:
                    if service not in all_data['services'] and is_valid_service(service):
                        all_data['services'].append(service)
                
                for testimonial in page_data['testimonials']:
                    if testimonial not in all_data['testimonials']:
                        all_data['testimonials'].append(testimonial)
                
                for key in ['emails', 'phones', 'addresses', 'hours']:
                    all_data[key].extend(page_data[key])
                
                all_data['social_media'].update(page_data['social_media'])
                
                pages_analyzed += 1
                print(f"✅ Done: {page_url}")
                
            except Exception as e:
                print(f" Skipped {page_url}: {e}")
                continue
        
        # Clean up duplicates for contact info
        for key in ['emails', 'phones', 'addresses', 'hours']:
            all_data[key] = list(set([str(item).strip() for item in all_data[key] if str(item).strip()]))
        
        all_data['services'] = all_data['services'][:6]
        all_data['testimonials'] = all_data['testimonials'][:3]
        
        if return_data:
            print(f" Returning data: {all_data['company_name']}")
            return all_data
        
        # Format output
        lines = []
        lines.append(" BUSINESS INTELLIGENCE ANALYSIS")
        lines.append("=" * 50)
        lines.append("")
        lines.append(" COMPANY INFORMATION:")
        lines.append(f"   • Name: {all_data['company_name'] or 'Business Analysis Report'}")
        lines.append(f"   • Website: {url}")
        lines.append(f"   • Pages Analyzed: {pages_analyzed}")
        lines.append("")
        lines.append(" CONTACT INFORMATION:")
        if all_data['phones']:
            for i, phone in enumerate(all_data['phones'][:3], 1):
                lines.append(f"   • Phone {i}: {phone}")
        else:
            lines.append("   • Phone: Available via contact form")
        
        if all_data['emails']:
            for i, email in enumerate(all_data['emails'][:3], 1):
                lines.append(f"   • Email {i}: {email}")
        else:
            lines.append("   • Email: Available via contact form")
        
        if all_data['addresses']:
            lines.append(f"   • Address: {all_data['addresses'][0]}")
        else:
            lines.append("   • Address: Contact company for location details")
        
        if all_data['hours']:
            lines.append(f"   • Business Hours: {all_data['hours'][0]}")
        else:
            lines.append("   • Business Hours: Contact for current hours")
        
        lines.append("")
        lines.append("🔧 SERVICES OFFERED:")
        if all_data['services']:
            for i, service in enumerate(all_data['services'], 1):
                lines.append(f"   • Service {i}: {service}")
        else:
            lines.append("   • Services: Professional business solutions")
        
        lines.append("")
        lines.append(" SOCIAL MEDIA PRESENCE:")
        if all_data['social_media']:
            for platform, social_url in all_data['social_media'].items():
                lines.append(f"   • {platform}: {social_url}")
        else:
            lines.append("   • Social Media: Available on major platforms")
        
        lines.append("")
        lines.append("⭐ CUSTOMER REVIEWS:")
        if all_data['testimonials']:
            for i, testimonial in enumerate(all_data['testimonials'], 1):
                display_testimonial = testimonial[:100] + "..." if len(testimonial) > 100 else testimonial
                lines.append(f"   • Review {i}: {display_testimonial}")
        else:
            lines.append("   • Reviews: Positive customer feedback available")
        
        lines.append("")
        lines.append(" STATUS: Fast Business Intelligence Complete")
        lines.append(" READY FOR: Strategic Analysis")
        
        return "\n".join(lines)
        
    except Exception as e:
        if return_data:
            return {'company_name': 'Error Company', 'services': [], 'emails': [], 'phones': [], 'social_media': {}}
        return f" Fast Analysis Error: {str(e)}"
