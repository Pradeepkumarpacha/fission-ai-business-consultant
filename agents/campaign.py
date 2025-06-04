import subprocess
import json
import os
import re
from datetime import datetime

class FormattedCampaignAgent:
    def __init__(self):
        print(" Initializing Formatted Campaign Agent...")
    
    def analyze_target_market(self, discovery_data=None):
        """Analyze target market based on discovery data"""
        if isinstance(discovery_data, dict):
            company_name = discovery_data.get('company_name', 'Target Company')
            services = discovery_data.get('services', [])
            
            # Determine industry focus for campaign targeting
            services_text = ' '.join(services).lower()
            if any(term in services_text for term in ['hvac', 'heating', 'cooling', 'plumbing', 'electrical']):
                industry = 'hvac'
                target_audience = 'Homeowners, Property Managers, Facility Directors'
                keywords = 'HVAC services, heating repair, cooling installation, plumbing services'
            elif any(term in services_text for term in ['tech', 'software', 'ai', 'cloud']):
                industry = 'tech'
                target_audience = 'IT Directors, CTOs, Tech Managers'
                keywords = 'AI solutions, cloud services, software development'
            else:
                industry = 'general'
                target_audience = 'Business Owners, Decision Makers, Managers'
                keywords = 'professional services, business solutions, consulting'
        else:
            company_name = 'Target Company'
            industry = 'general'
            target_audience = 'Business Owners, Decision Makers'
            keywords = 'professional services, business solutions'
        
        return {
            'company_name': company_name,
            'industry': industry,
            'target_audience': target_audience,
            'keywords': keywords
        }
    
    def generate_platform_strategy(self, market_analysis):
        """Generate detailed platform-specific marketing strategies"""
        company_name = market_analysis['company_name']
        industry = market_analysis['industry']
        keywords = market_analysis['keywords']
        target_audience = market_analysis['target_audience']
        
        # Budget allocation based on industry
        if industry == 'hvac':
            google_budget = 600
            facebook_budget = 250
            linkedin_budget = 150
        elif industry == 'tech':
            google_budget = 400
            linkedin_budget = 400
            facebook_budget = 200
        else:
            google_budget = 500
            linkedin_budget = 350
            facebook_budget = 150
        
        total_budget = google_budget + facebook_budget + linkedin_budget
        
        strategies = {
            'google_ads': {
                'budget': google_budget,
                'percentage': f"{(google_budget/total_budget)*100:.0f}%",
                'keywords': keywords,
                'target': target_audience,
                'cpc_range': '$2-5' if industry == 'hvac' else '$3-7',
                'estimated_clicks': f"{google_budget//4}-{google_budget//2}",
                'roi_target': '350%' if industry == 'hvac' else '300%'
            },
            'linkedin_ads': {
                'budget': linkedin_budget,
                'percentage': f"{(linkedin_budget/total_budget)*100:.0f}%",
                'target': 'Business decision makers, industry professionals',
                'industries': 'Construction, Real Estate, Property Management' if industry == 'hvac' else 'Technology, Software, Consulting',
                'cpc_range': '$5-10',
                'estimated_clicks': f"{linkedin_budget//7}-{linkedin_budget//5}",
                'roi_target': '400%'
            },
            'facebook_ads': {
                'budget': facebook_budget,
                'percentage': f"{(facebook_budget/total_budget)*100:.0f}%",
                'target': 'Local homeowners, business owners' if industry == 'hvac' else 'Tech enthusiasts, startup founders',
                'age_group': '30-55 years' if industry == 'hvac' else '25-45 years',
                'cpc_range': '$1-4',
                'estimated_clicks': f"{facebook_budget//3}-{facebook_budget//1}",
                'roi_target': '250%'
            }
        }
        
        return strategies, total_budget
    
    def calculate_success_metrics(self, total_budget, industry):
        """Calculate expected success metrics"""
        if industry == 'hvac':
            target_leads = '20-30'
            cost_per_lead = '$35-50'
            conversion_rate = '4-6%'
            expected_revenue = '$8000-12000'
        elif industry == 'tech':
            target_leads = '15-25'
            cost_per_lead = '$40-65'
            conversion_rate = '3-5%'
            expected_revenue = '$5000-8000'
        else:
            target_leads = '18-28'
            cost_per_lead = '$35-55'
            conversion_rate = '3-5%'
            expected_revenue = '$6000-10000'
        
        return {
            'target_leads': target_leads,
            'cost_per_lead': cost_per_lead,
            'conversion_rate': conversion_rate,
            'expected_revenue': expected_revenue,
            'brand_awareness': '75,000+ impressions',
            'website_traffic': '800+ new visitors',
            'social_engagement': '300+ interactions'
        }
    
    def format_campaign_output(self, market_analysis, strategies, total_budget, success_metrics):
        """Format campaign output with proper spacing like Discovery Agent"""
        company_name = market_analysis['company_name']
        industry = market_analysis['industry']
        
        lines = []
        
        # Header section
        lines.append(" MARKETING CAMPAIGN STRATEGY")
        lines.append("=" * 50)
        lines.append("")
        
        # Campaign Overview Section
        lines.append(" CAMPAIGN OVERVIEW:")
        lines.append(f"   • Target Company: {company_name}")
        lines.append(f"   • Industry Focus: {industry.upper()} Marketing Strategy")
        lines.append(f"   • Total Budget: ${total_budget}")
        lines.append(f"   • Campaign Duration: 3 months")
        lines.append(f"   • Strategy Date: {datetime.now().strftime('%B %d, %Y')}")
        lines.append("")
        
        # Target Audience Section
        lines.append(" TARGET AUDIENCE ANALYSIS:")
        lines.append(f"   • Primary Audience: {market_analysis['target_audience']}")
        lines.append(f"   • Geographic Focus: Local and regional markets")
        lines.append(f"   • Demographics: Business decision makers, property owners")
        lines.append(f"   • Psychographics: Quality-focused, value-driven customers")
        lines.append("")
        
        # Platform Allocation Section
        lines.append(" PLATFORM ALLOCATION STRATEGY:")
        lines.append("=" * 40)
        lines.append("")
        
        # Google Ads Details
        google_strategy = strategies['google_ads']
        lines.append(f" GOOGLE ADS - ${google_strategy['budget']} ({google_strategy['percentage']})")
        lines.append(f"   • Target Keywords: {google_strategy['keywords']}")
        lines.append(f"   • Target Audience: {google_strategy['target']}")
        lines.append(f"   • Expected CPC: {google_strategy['cpc_range']}")
        lines.append(f"   • Estimated Clicks: {google_strategy['estimated_clicks']}")
        lines.append(f"   • ROI Target: {google_strategy['roi_target']}")
        lines.append("")
        
        # LinkedIn Ads Details
        linkedin_strategy = strategies['linkedin_ads']
        lines.append(f" LINKEDIN ADS - ${linkedin_strategy['budget']} ({linkedin_strategy['percentage']})")
        lines.append(f"   • Target Professionals: {linkedin_strategy['target']}")
        lines.append(f"   • Target Industries: {linkedin_strategy['industries']}")
        lines.append(f"   • Expected CPC: {linkedin_strategy['cpc_range']}")
        lines.append(f"   • Estimated Clicks: {linkedin_strategy['estimated_clicks']}")
        lines.append(f"   • ROI Target: {linkedin_strategy['roi_target']}")
        lines.append("")
        
        # Facebook Ads Details
        facebook_strategy = strategies['facebook_ads']
        lines.append(f" FACEBOOK ADS - ${facebook_strategy['budget']} ({facebook_strategy['percentage']})")
        lines.append(f"   • Target Audience: {facebook_strategy['target']}")
        lines.append(f"   • Age Demographics: {facebook_strategy['age_group']}")
        lines.append(f"   • Expected CPC: {facebook_strategy['cpc_range']}")
        lines.append(f"   • Estimated Clicks: {facebook_strategy['estimated_clicks']}")
        lines.append(f"   • ROI Target: {facebook_strategy['roi_target']}")
        lines.append("")
        
        # Success Metrics Section
        lines.append(" SUCCESS METRICS & KPIs:")
        lines.append("=" * 30)
        lines.append("")
        lines.append(" LEAD GENERATION TARGETS:")
        lines.append(f"   • Target Leads: {success_metrics['target_leads']} qualified leads")
        lines.append(f"   • Cost Per Lead: {success_metrics['cost_per_lead']}")
        lines.append(f"   • Conversion Rate: {success_metrics['conversion_rate']}")
        lines.append(f"   • Expected Revenue: {success_metrics['expected_revenue']}")
        lines.append("")
        
        lines.append(" BRAND AWARENESS METRICS:")
        lines.append(f"   • Brand Impressions: {success_metrics['brand_awareness']}")
        lines.append(f"   • Website Traffic: {success_metrics['website_traffic']}")
        lines.append(f"   • Social Engagement: {success_metrics['social_engagement']}")
        lines.append(f"   • Brand Recognition: 40% increase in local market")
        lines.append("")
        
        # Campaign Objectives Section
        lines.append(" CAMPAIGN OBJECTIVES:")
        lines.append("   • Primary Goal: Lead generation and customer acquisition")
        lines.append("   • Secondary Goal: Brand awareness and market positioning")
        lines.append("   • Tertiary Goal: Website traffic and engagement growth")
        lines.append("   • Long-term Goal: Market share expansion and retention")
        lines.append("")
        
        # Implementation Timeline
        lines.append(" IMPLEMENTATION TIMELINE:")
        lines.append("   • Week 1-2: Campaign setup and creative development")
        lines.append("   • Week 3-4: Campaign launch and initial optimization")
        lines.append("   • Month 2: Performance monitoring and adjustment")
        lines.append("   • Month 3: Scaling successful campaigns and ROI analysis")
        lines.append("")
        
        # Status Section
        lines.append(" CAMPAIGN STATUS: Strategy Development Complete")
        lines.append(" READY FOR: Campaign Launch, Creative Development, Implementation")
        
        return "\n".join(lines)

def run(discovery_data=""):
    """Main campaign function with proper formatting"""
    campaign_agent = FormattedCampaignAgent()
    
    try:
        print(" Starting formatted marketing campaign strategy...")
        
        # Analyze target market from discovery data
        market_analysis = campaign_agent.analyze_target_market(discovery_data)
        print(f" Target market: {market_analysis['industry']} industry")
        
        # Generate platform strategies
        strategies, total_budget = campaign_agent.generate_platform_strategy(market_analysis)
        print(f" Total budget allocated: ${total_budget}")
        
        # Calculate success metrics
        success_metrics = campaign_agent.calculate_success_metrics(total_budget, market_analysis['industry'])
        
        # Format output matching Discovery Agent style
        final_output = campaign_agent.format_campaign_output(market_analysis, strategies, total_budget, success_metrics)
        
        print(" Formatted marketing campaign strategy complete!")
        return final_output
        
    except Exception as e:
        print(f" Campaign error: {e}")
        return f" Marketing Campaign Error: {str(e)}"
