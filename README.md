# SocialPulse AI – Social Media Performance Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.15+-3F4F75.svg)](https://plotly.com/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.0+-brightgreen.svg)](https://www.reportlab.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent social media analytics dashboard and performance auditing platform built with Python, Streamlit, Pandas, Plotly, ReportLab, and Groq/OpenAI LLM APIs. Developed for the AI Engineering Internship technical assignment.

---

## 1. Project Overview

**SocialPulse AI** transforms raw, exported social media analytics datasets (Instagram Insights and LinkedIn Analytics) into actionable business intelligence. Rather than displaying hardcoded mock numbers, the application executes genuine end-to-end data processing: ingesting CSV files, validating schemas, cleansing records, calculating verified engagement and growth metrics, conducting period-over-period comparisons, identifying viral outlier content, generating data-grounded AI insights, and compiling executive-ready PDF audit reports.

The user interface reproduces the custom **Google Stitch SaaS design system**, featuring clean typography, structured metric cards, interactive multi-scale charts, and a responsive fixed-navigation layout.

---

## 2. Core Features

### 📁 CSV Upload & Quality Validation
- Drag-and-drop or file-browser ingestion for Instagram and LinkedIn analytics CSV exports (supports up to 25 MB and 50,000 rows).
- Automatic schema detection and flexible column mapping matching dozens of alternate field nomenclatures.
- Comprehensive data health inspection: reports total records, valid records, corrupted rows, negative metric values, and unparseable dates.
- Interactive data preview table displaying mapped standardized dimensions before ingestion.

### 📊 Dashboard Overview
- Real-time status strip detailing active channels, verified row counts, reporting date ranges, and period comparisons.
- Five core KPI cards: **Total Reach**, **Total Impressions**, **Total Engagements**, **Average Engagement Rate**, and **Net Follower Growth** with directional deltas.
- Interactive Plotly area/line charts supporting **Daily**, **Weekly**, and **Cumulative** trend aggregation.
- Format performance breakdown comparing Reels/Videos, Carousels, Static Images, and Stories.
- Quick preview of top 3 outlier posts and AI synthesis card.

### 🔬 Deep Analytics Workspace
- Comprehensive multi-metric trajectory analysis (Reach, Impressions, Engagements over time).
- Content format performance correlation matrix (post counts, reach, shares, and engagement rates).
- Engagement distribution donut chart (Likes, Comments, Shares, Saves).
- Audience follower growth tracking over reporting intervals.
- Period-over-period grouped bar charts benchmarking performance against previous intervals.

### 🏆 Top Posts Explorer
- Multi-dimensional sorting: **Highest Reach**, **Highest Engagement**, **Highest Engagement Rate**, **Most Likes**, and **Most Shares**.
- Real-time full-text search across captions and post topics.
- Post format filtering (Reels, Carousels, Static Images, Documents, Articles).
- Transparent normalized **Performance Score (0–100)** ranking individual posts relative to dataset peers.

### 🤖 AI Synthesized Insights
- Dual-mode architecture:
  - **AI-Powered Analysis**: Integrates with Groq (`llama-3.1-70b-versatile`) or OpenAI (`gpt-4o-mini`) via API key.
  - **Deterministic Rule-Based Fallback**: Seamless fallback ensures 100% functionality without API keys.
- Executive summary, primary performance takeaways, categorized strengths, and detected weaknesses.
- Prioritized tactical action plans with high, medium, and low impact designations.
- Strategy cards for Content Strategy, Engagement Optimization, Reach Growth, and Posting Consistency.

### 📄 Client-Ready PDF Report Export
- High-fidelity A4 document compilation powered by **ReportLab**.
- Branded cover page, executive summaries, KPI tables, period comparison tables, engagement breakdowns, top post performance ledger, AI findings, and methodology disclosures.
- Alternating row styling, custom typography, status badges, and dynamic page numbering.

---

## 3. Technology Stack

| Domain | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core application logic |
| **Frontend / App Framework** | Streamlit | Reactive dashboard UI and navigation |
| **Data Processing & Analytics** | Pandas, NumPy | Data cleaning, validation, and mathematical aggregation |
| **Interactive Visualizations** | Plotly Express, Plotly Graph Objects | Dynamic charts with custom tooltips |
| **AI Integration** | Groq API / OpenAI API | LLM synthesis of summarized performance metrics |
| **PDF Generation** | ReportLab | Programmatic compilation of multi-page PDF reports |
| **Testing** | Pytest | Automated unit and integration testing suite |
| **Configuration** | python-dotenv | Secure environment variable management |

---

## 4. Project Architecture & Folder Structure

```
SocialPulse_AI/
│
├── app.py                         # Application entry point & router
│
├── pages/                         # Dashboard view modules & routes
│   ├── 1_Dashboard_Overview.py    # Multi-page route: Overview
│   ├── 2_CSV_Upload_and_Prep.py   # Multi-page route: Data Ingestion
│   ├── 3_Deep_Analytics.py        # Multi-page route: Deep Analytics
│   ├── 4_Top_Posts_Explorer.py    # Multi-page route: Top Posts
│   ├── 5_AI_Insights.py           # Multi-page route: AI Insights
│   ├── 6_Export_PDF_Reports.py    # Multi-page route: PDF Generator
│   ├── dashboard_overview.py      # Core view implementation: Overview
│   ├── csv_upload.py              # Core view implementation: CSV Upload
│   ├── deep_analytics.py          # Core view implementation: Deep Analytics
│   ├── top_posts_explorer.py      # Core view implementation: Top Posts
│   ├── ai_insights_page.py        # Core view implementation: AI Insights
│   └── export_pdf.py              # Core view implementation: Export PDF
│
├── components/                    # Reusable UI components
│   ├── sidebar.py                 # Stitch-styled sidebar & platform switcher
│   ├── header.py                  # Breadcrumbs, date display & action bar
│   ├── kpi_cards.py               # Metric cards with delta indicators
│   ├── charts.py                  # Interactive Plotly chart builders
│   ├── post_cards.py              # Viral outlier post preview cards
│   └── filters.py                 # Date, format, and sorting controls
│
├── services/                      # Decoupled business logic & processing
│   ├── csv_loader.py              # Multi-encoding CSV reader
│   ├── column_mapper.py           # Intelligent schema matcher & normalizer
│   ├── data_validator.py          # Data hygiene, health score & checks
│   ├── data_cleaner.py            # Type enforcement & NaN handling
│   ├── analytics_engine.py        # Mathematical KPI & trend formulas
│   ├── comparison_engine.py       # Period-over-period comparative logic
│   ├── ai_insights.py             # LLM orchestration & rule-based engine
│   └── pdf_generator.py           # ReportLab document construction
│
├── utils/                         # Helper utilities & state
│   ├── constants.py               # Design tokens, color palettes & schemas
│   ├── formatters.py              # Currency, compact number & date helpers
│   ├── helpers.py                 # Safe math, rolling averages & date filters
│   └── session_manager.py         # Persistent Streamlit session management
│
├── assets/                        # Static styling & branding assets
│   ├── custom.css                 # Stitch SaaS stylesheet
│   └── logo.png                   # SocialPulse AI branding emblem
│
├── data/                          # Bundled demonstration datasets
│   ├── sample_instagram_data.csv  # 64-row realistic Instagram export
│   └── sample_linkedin_data.csv   # 41-row realistic LinkedIn export
│
├── tests/                         # Automated test suite
│   ├── test_analytics.py          # Unit tests for KPI calculations
│   ├── test_validation.py         # Unit tests for schema validation
│   ├── test_comparison.py         # Unit tests for period comparisons
│   └── test_integration.py        # End-to-end pipeline verification
│
├── reports/                       # Generated PDF output directory
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusion rules
├── requirements.txt               # Pinned project dependencies
└── README.md                      # Project documentation
```

---

## 5. Metric Calculation Formulas & Methodology

To ensure consistency, mathematical rigour, and transparency, the following formulas are enforced across all modules:

### 1. Total Engagements
$$\text{Total Engagements} = \text{Likes} + \text{Comments} + \text{Shares} + \text{Saves}$$
*Note: If Saves or Shares are omitted in a user-provided CSV, the system sums available interactions without silently assuming missing values are zero, and clearly discloses the omitted dimension.*

### 2. Post-Level Engagement Rate (by Reach)
$$\text{Engagement Rate}_{\text{post}} = \left( \frac{\text{Engagements}_{\text{post}}}{\text{Reach}_{\text{post}}} \right) \times 100$$

### 3. Average Engagement Rate
$$\text{Average Engagement Rate} = \frac{1}{N} \sum_{i=1}^{N} \text{Engagement Rate}_i$$
*Calculated as the mean of individual post engagement rates across all valid posts in the reporting window.*

### 4. Aggregate Reach & Impressions
$$\text{Total Reach} = \sum \text{Reach}_{\text{post}}, \quad \text{Total Impressions} = \sum \text{Impressions}_{\text{post}}$$
*Disclosed as aggregate post-level exposures rather than unique de-duplicated account-level audience counts.*

### 5. Net Follower Growth
$$\text{Net Growth} = \text{Followers}_{\text{latest}} - \text{Followers}_{\text{earliest}}$$
*Calculated from chronological snapshots. If follower columns are unavailable, the metric is omitted with a clear disclosure.*

### 6. Period-over-Period Percentage Change
$$\Delta\% = \left( \frac{\text{Current Period Value} - \text{Previous Period Value}}{|\text{Previous Period Value}|} \right) \times 100$$
*Divisions by zero are safeguarded with fallbacks.*

### 7. Transparent Performance Score (0–100)
A relative score calculated via weighted normalized metrics:
- **Reach Contribution (30% weight)**: Normalized against min/max reach.
- **Engagement Rate (30% weight)**: Normalized against min/max rate.
- **Total Engagements (25% weight)**: Normalized against min/max total interactions.
- **Shares / Virality Multiplier (15% weight)**: Normalized against min/max shares.

---

## 6. Supported CSV Format & Column Mapping

The system automatically recognizes standard headers across both major social platforms:

| Standard Field | Supported CSV Header Aliases |
|---|---|
| **Date** | `Date`, `Published Date`, `Post Date`, `Publish Date`, `Publish_Date`, `date`, `timestamp` |
| **Post Content** | `Post`, `Caption`, `Content`, `Description`, `Text`, `Title`, `Post Caption` |
| **Post ID** | `Post_ID`, `Post ID`, `post_id`, `ID`, `id`, `Permalink`, `permalink` |
| **Reach** | `Reach`, `reach`, `Accounts Reached`, `accounts_reached`, `Total Reach` |
| **Impressions** | `Impressions`, `impressions`, `Views`, `views`, `Total Impressions` |
| **Likes / Reactions** | `Likes`, `likes`, `Reactions`, `reactions`, `Hearts`, `Like Count` |
| **Comments** | `Comments`, `comments`, `Comment Count`, `Replies`, `replies` |
| **Shares / Reposts** | `Shares`, `shares`, `Reposts`, `reposts`, `Retweets`, `Share Count` |
| **Saves / Bookmarks** | `Saves`, `saves`, `Bookmarks`, `bookmarks`, `Save Count` |
| **Followers** | `Followers`, `followers`, `Followers Count`, `Total Followers` |
| **Post Type / Format** | `Post Type`, `Post_Type`, `Media Type`, `Content Type`, `Format`, `type` |

---

## 7. Installation & Quick Start

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your machine.
- Git installed.

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/SocialPulse_AI.git
cd SocialPulse_AI
```

### Step 2: Create and Activate Virtual Environment
**Windows (PowerShell / Command Prompt):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional for AI)
Copy the example environment configuration file:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Open `.env` and supply your API key:
```env
# AI Provider: "groq" or "openai"
AI_PROVIDER=groq

# Groq API Key (Obtain from https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: OpenAI API Key (Obtain from https://platform.openai.com)
OPENAI_API_KEY=sk-your_openai_api_key_here

# Model identifier
AI_MODEL=llama-3.1-70b-versatile
```
*Note: If no API key is provided, SocialPulse AI automatically runs in **Deterministic Rule-Based Mode**, providing complete functionality without external API dependencies.*

### Step 5: Launch the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 8. Verification & Automated Testing

SocialPulse AI includes a full Pytest suite verifying metric calculations, period comparisons, schema validations, and data cleaning.

Execute the test suite with:
```bash
python -m pytest tests/ -v
```

Execute the full end-to-end integration test:
```bash
python tests/test_integration.py
```

### Test Coverage Results:
- `tests/test_analytics.py`: 18 tests (Total reach, impressions, engagements, follower delta, engagement rate, empty inputs, format grouping, viral scoring).
- `tests/test_validation.py`: 11 tests (Schema completeness, corrupted rows, negative metric guards, date parsing, health ratings).
- `tests/test_comparison.py`: 8 tests (Period midpoint splitting, percentage changes, directional indicators, empty dataframe handling).
- **Result: 37 of 37 tests passing (100% pass rate).**

---

## 9. Assumptions and Known Limitations

1. **Post-Level vs Account-Level Metrics**: Reach and impressions are calculated as post-level aggregates over the reporting timeframe. They do not represent deduplicated unique human viewers across multiple posts.
2. **Follower Growth Snapshots**: Follower growth reflects the delta between the earliest and latest recorded follower values in the dataset. If cumulative snapshots are repeated across posts on the same date, they are not summed.
3. **Period Midpoint Splitting**: When arbitrary date ranges are uploaded without explicit comparison parameters, the comparison engine divides the available date span at its temporal midpoint (first 50% vs second 50%).
4. **Data Privacy**: CSV processing and metric normalization occur entirely in memory within the local runtime session. When AI features are utilized, only aggregated KPI summaries are transmitted to LLM endpoints—raw post bodies and proprietary identifier fields are never transmitted.

---

## 10. Future Enhancements

- Multi-account comparative benchmarking (Instagram vs LinkedIn side-by-side).
- Direct Meta Graph API & LinkedIn Marketing Developer API OAuth integrations.
- Time-of-day and day-of-week heatmaps for optimal posting schedule recommendation.
- Automated sentiment analysis on post comment streams using local transformer models.
- Scheduled background PDF email delivery.

---

## 11. Evaluation Deliverables Checklist

- [x] **Working Application**: Clean local execution via `streamlit run app.py`.
- [x] **Real Data Processing**: Actual computations across 64-row Instagram and 41-row LinkedIn datasets.
- [x] **Custom UI/UX**: Faithful implementation of Google Stitch design specifications (colors, cards, typography, navigation).
- [x] **AI Synthesis**: Data-grounded executive summaries with Groq/OpenAI integration and rule-based fallback.
- [x] **PDF Report Generation**: Complete multi-page ReportLab export with tables, covers, and metrics.
- [x] **Robust Test Suite**: 37 unit and integration tests passing.
- [x] **Documentation**: Comprehensive architecture, formulas, and user guide.
