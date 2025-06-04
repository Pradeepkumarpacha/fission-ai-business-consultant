from flask import Flask, render_template, request
import agents.discovery as discovery
import agents.creative as creative
import agents.campaign as campaign
app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def run_agents():
    log = []
    url = ""
    
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url.startswith("http"):
            url = "https://" + url
        
        # Step 1: Discovery Agent - Get both formatted output and raw data
        log.append(" Discovery Agent: Starting comprehensive business intelligence analysis...")
        discovery_output = discovery.run(url)  # Formatted output for display
        discovery_data = discovery.run(url, return_data=True)  # Raw data for Creative Agent
        log.append(discovery_output)
        
        # Step 2: Business Consultant Agent - Use discovery data
        log.append(" Business Consultant: Analyzing company data for strategic transformation...")
        consulting_result = creative.run(discovery_data)  # Pass structured data
        log.append(consulting_result)
        
        # Step 3: Campaign Agent
        log.append(" Campaign Agent: Creating implementation marketing strategy...")
        campaign_result = campaign.run(discovery_data)
        log.append(campaign_result)
        
        log.append("✅ All Strategic Agents Completed Successfully!")
        
    return render_template("index.html", log=log, url=url)
if __name__ == "__main__":
    app.run(debug=True)
