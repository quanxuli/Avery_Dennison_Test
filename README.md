## Install nescessary library ##
pip install pandas requests streamlit plotly

## Run the script ##
streamlit run app.py for Vietnamese version.
streamlit run app-en.py for English version.

## Question ##

1. Trend Analysis: Analyze the number of defects from January to June 2024. 
What patterns do you observe? Is this a positive or negative sign for the factory?
Answer:
Observation: During the initial months (January to March), the daily defect volume fluctuatesmoderately, mostly hovering around or below the overall mean (approximately 6-7 defects/day). However, moving into May and June, we observe a significant increase in volatility. 
The chart displays multiple extreme spikes, with daily defects frequently surging past 15 and even exceeding 20 cases per day towards the end of the observed period.
Conclusion: This escalating frequency of high-defect spikes indicates growing instability in the production process. 
Rather than improving, the system is generating larger batches of defective items simultaneously. This could be symptomatic of equipment wear and tear reaching a critical threshold, inconsistencies in raw material batches, or process deviations  during specific shifts that urgently require an operational audit.

2. Defect Location & Severity: Analyze where defects occur most frequently (Component Internal, Surface). Is there a relationship between defect location and severity level?
Answer:
Surface (High Frequency, Low Risk): Defects occur most frequently on the "Surface".However, they are overwhelmingly classified as Minor (159 cases—the highest concentration on the matrix). 
Surface anomalies are generally cosmetic and rarely impede the product's core functionality.
Component (High Risk): Conversely, defects located at the "Component" level pose the greatest threat to product quality. 
They predominantly translate into Critical severity (150 cases). This is logical, as the failure of an internal component directly disables the product.
Internal: Defects within the internal structure show a relatively balanced distribution across Critical (103), Minor (117), and Moderate (127) levels.
Actionable Insight: The factory is likely wasting manual QC labor on inspecting minor surface scratches. 
Management should consider implementing deep learning-based automated visual inspection systems (e.g., computer vision frameworks) to handle surface defects. This would completely free up the human QC team to focus their technical expertise on rigorously  testing Components, where the true critical failures are concentrated.

3. Pattern Recognition: Identify and present any other notable patterns you discover in the data.
Answer:
The Line-4 Bottleneck: Line-4 is significantly underperforming compared to the rest of the facility. It generated the highest total volume of defects (344 cases), which is over 50% higher than the most efficient line (Line-2, with 222 cases).
Category Vulnerability: Products classified under Category 1 (300 cases) and Category 4 (288 cases) are inherently more susceptible to manufacturing errors across all lines.
Conclusion: The data points to a systemic issue at Line-4. The Production Manager should immediately initiate preventative maintenance and calibrate the machinery on Line-4. Furthermore, operators on this line may require additional training, particularly when they are scheduled to run the highly vulnerable Category 1 or Category 4 products.

4. Data only delivers real value when it solves operational bottlenecks. If you were an end user using this solution every day — what are the current limitations of a "static dashboard", and what additional capabilities would you want?
Answer:
Limitations of a "Static" Dashboard:
Reactive Nature: It requires managers to actively check the dashboard. A critical defect spike could go unnoticed for hours if the team is busy on the factory floor.
Data Latency & Human Error: It relies on manual defect logging by workers, which introduces a time lag and high risk of misclassification.
Lacks Root-Cause Analysis: It shows what is failing (Line-4) and where (Component), but it doesn't explain why the bottleneck exists.

Desired Additional Capabilities:
Automated Image Classification (Deep Learning): To eliminate manual entry errors, I would integrate camera sensors directly  on the lines (especially Line-4) using optimized deep learning models (like YOLO architectures for image classification). This would automatically categorize surface and component defects and push data to the API in true real-time.
Proactive Alerting System: Implement automated triggers. If a specific product line exceeds an acceptable defect threshold (e.g., >10 Critical defects an hour), the system should instantly push an alert to shift supervisors via Email or Teams.
Predictive Maintenance: Integrate the dashboard with machine telemetry (temperature, vibration sensors) to forecast equipment wear and tear, allowing the factory to fix machinery before it starts producing defective items.