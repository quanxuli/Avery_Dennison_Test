# Data Analyst — Case Study

> **Time:** 3 business days  
> **Submission:** GitHub repository (public)

## Getting Started

Clone the repository to get the master data and access the API endpoint:

```bash
git clone https://github.com/phongtdt/RFID_Data-Analyst_Case-Study-Test.git
```
or using GitHub CLI:
```bash
gh repo clone phongtdt/RFID_Data-Analyst_Case-Study-Test
```

## Context

You have just joined the **Data** team at a manufacturing plant. The factory operates 4 production lines (Line 1-4), producing 100 products across 4 categories.

Currently, the Production team manages defect data from 2 sources:
- **Master Data** (product information)
- **Defect Records** (defects logged from the production floor)

## Business Problem

The factory records product defect data from 4 production lines. However, the data is scattered across multiple sources and has not been utilized effectively.

**Production Team Leaders & Managers** currently need:
- A consolidated view of production quality trends over time
- Visibility into which products and lines have high defect rates
- Understanding of how repair costs are distributed
- Early detection of defect anomalies instead of waiting for manual weekly reports
- The ability to export or share data with relevant departments when needed

Currently, defect data consolidation and reporting is done manually, taking 2-3 days. By the time the data reaches decision-makers, it is already outdated.

## Data Sources

### 1. Master Data — `master_data.csv` (attached file)

Product reference data.

| Field | Type | Description |
|---|---|---|
| `product_id` | integer | Unique identifier for each product |
| `product_name` | string | Name of the product |
| `category` | string | Product category (e.g., Category 1, Category 2) |
| `production_line` | string | Production line the product belongs to (e.g., Line-1, Line-2) |
| `monthly_output` | integer | Total monthly production output |

### 2. Defect Records — API Endpoint

Defect data logged from the production floor.

**Endpoint:**
```
GET https://raw.githubusercontent.com/phongtdt/RFID_Data-Analyst_Case-Study-Test/main/mock-api/defect_records.json
```

**Response format:** JSON array

| Field | Type | Description |
|---|---|---|
| `defect_id` | integer | Unique identifier for each defect |
| `product_id` | integer | Identifier for the product associated with the defect |
| `defect_type` | string | Category of the defect (e.g., Cosmetic, Functional, Structural) |
| `defect_date` | string | Date when the defect was detected |
| `defect_location` | string | Location within the product where the defect was found (e.g., Surface, Component) |
| `severity` | string | Severity level of the defect (e.g., Minor, Moderate, Critical) |
| `inspection_method` | string | Method used to detect the defect (e.g., Visual Inspection, Automated Testing) |
| `repair_cost` | float | Cost incurred to repair the defect (in local currency) |

> ⚠️ Defect records **must** be fetched via HTTP request. **Do not** download the JSON file and read it locally.

## Task

As a **Data Analyst**, design and build a **web app dashboard** that addresses the problems above and communicates insights from the data.

You are free to choose your tech stack. React / Node.js is preferred, but any technology is accepted — as long as the solution runs, solves the business problem, and clearly communicates insights.

After building your solution, answer the following analytical questions:

1. **Trend Analysis:** Analyze the number of defects from January to June 2024. What patterns do you observe? Is this a positive or negative sign for the factory?

2. **Defect Location & Severity:** Analyze where defects occur most frequently (Component, Internal, Surface). Is there a relationship between defect location and severity level?

3. **Pattern Recognition:** Identify and present any other notable patterns you discover in the data.

Data only delivers real value when it solves operational bottlenecks. If you were an end user using this solution every day — what are the current limitations of a "static dashboard", and what additional capabilities would you want?

## Deliverables

Source code on GitHub, including:

- **`README.md`** containing:
  - Setup and run instructions
  - Detailed answers to the 3 analytical questions above
  - A brief explanation of the dashboard's key components and features

**Note:** You may use AI-assisted tools if needed (human in the loop approach).  
**Submission deadline:** 3 days
