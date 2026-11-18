"""
SocialPulse AI - Constants and Configuration
Central configuration for colors, column mappings, and application settings.
"""

# ─── Brand Colors ───────────────────────────────────────────────────────────
PRIMARY = "#4648D4"
PRIMARY_LIGHT = "#6063EE"
PRIMARY_BG = "#F0F0FF"
BACKGROUND = "#F9F9FF"
CARD_BG = "#FFFFFF"
SECONDARY = "#00687A"
SUCCESS = "#00885D"
SUCCESS_LIGHT = "#E6F4ED"
DANGER = "#DC3545"
DANGER_LIGHT = "#FDE8EA"
WARNING = "#F59E0B"
TEXT_PRIMARY = "#141B2B"
TEXT_MUTED = "#767586"
BORDER_COLOR = "#E8E8F0"

# Chart color palette
CHART_COLORS = [PRIMARY, SECONDARY, SUCCESS, "#F59E0B", "#E11D48", "#8B5CF6", "#06B6D4"]
CHART_REACH_COLOR = PRIMARY
CHART_IMPRESSIONS_COLOR = SECONDARY
CHART_ENGAGEMENT_COLOR = SUCCESS

# ─── Platform Options ───────────────────────────────────────────────────────
PLATFORMS = ["Instagram", "LinkedIn"]

# ─── Page Configuration ─────────────────────────────────────────────────────
PAGES = {
    "Dashboard Overview": {"icon": "📊", "file": "1_Dashboard_Overview"},
    "CSV Upload & Prep": {"icon": "📁", "file": "2_CSV_Upload_and_Prep"},
    "Deep Analytics": {"icon": "🔬", "file": "3_Deep_Analytics"},
    "Top Posts Explorer": {"icon": "🏆", "file": "4_Top_Posts_Explorer"},
    "AI Insights": {"icon": "🤖", "file": "5_AI_Insights"},
    "Export & PDF Reports": {"icon": "📄", "file": "6_Export_PDF_Reports"},
}

# ─── KPI Configuration ──────────────────────────────────────────────────────
KPI_CONFIG = {
    "total_reach": {"label": "Total Reach", "icon": "👁️", "format": "number"},
    "total_impressions": {"label": "Total Impressions", "icon": "📈", "format": "number"},
    "total_engagements": {"label": "Total Engagements", "icon": "💬", "format": "number"},
    "avg_engagement_rate": {"label": "Avg Eng. Rate", "icon": "⚡", "format": "percentage"},
    "net_follower_growth": {"label": "Net Growth", "icon": "👥", "format": "number"},
}

# ─── Standard Column Names ───────────────────────────────────────────────────
# These are the internal standard names used throughout the application
STD_DATE = "date"
STD_POST = "post"
STD_POST_ID = "post_id"
STD_REACH = "reach"
STD_IMPRESSIONS = "impressions"
STD_LIKES = "likes"
STD_COMMENTS = "comments"
STD_SHARES = "shares"
STD_SAVES = "saves"
STD_FOLLOWERS = "followers"
STD_POST_TYPE = "post_type"
STD_ENGAGEMENT_RATE = "engagement_rate"
STD_PROFILE_VISITS = "profile_visits"

# ─── Column Mapping Dictionary ──────────────────────────────────────────────
# Maps standard column names to possible CSV column names (case-insensitive matching)
COLUMN_MAPPING = {
    STD_DATE: [
        "Date", "Published Date", "Post Date", "Publish Date", "Publish_Date",
        "date", "publish_date", "published_date", "post_date", "PUBLISH_DATE",
        "DATE", "Created", "created_at", "timestamp", "Timestamp"
    ],
    STD_POST: [
        "Post", "Caption", "Content", "Description", "Text", "Title",
        "post", "caption", "content", "description", "text", "title",
        "POST", "CAPTION", "CONTENT", "Post Caption", "Post Content"
    ],
    STD_POST_ID: [
        "Post_ID", "Post ID", "post_id", "ID", "id", "Post_Id",
        "POST_ID", "PostID", "postId", "Permalink", "permalink"
    ],
    STD_REACH: [
        "Reach", "reach", "REACH", "Accounts Reached", "accounts_reached",
        "Accounts reached", "Total Reach", "total_reach", "Post Reach"
    ],
    STD_IMPRESSIONS: [
        "Impressions", "impressions", "IMPRESSIONS", "Views", "views",
        "Total Impressions", "total_impressions", "Post Impressions",
        "Imp", "Page Views"
    ],
    STD_LIKES: [
        "Likes", "likes", "LIKES", "Reactions", "reactions", "REACTIONS",
        "Like Count", "like_count", "Hearts"
    ],
    STD_COMMENTS: [
        "Comments", "comments", "COMMENTS", "Comment Count",
        "comment_count", "Replies", "replies"
    ],
    STD_SHARES: [
        "Shares", "shares", "SHARES", "Reposts", "reposts", "REPOSTS",
        "Share Count", "share_count", "Retweets"
    ],
    STD_SAVES: [
        "Saves", "saves", "SAVES", "Bookmarks", "bookmarks", "BOOKMARKS",
        "Save Count", "save_count"
    ],
    STD_FOLLOWERS: [
        "Followers", "followers", "FOLLOWERS", "Followers Count",
        "followers_count", "Follower Count", "follower_count",
        "Total Followers"
    ],
    STD_POST_TYPE: [
        "Post Type", "Post_Type", "post_type", "POST_TYPE", "Media Type",
        "media_type", "Content Type", "content_type", "Format", "format",
        "Type", "type", "Content_Type", "Media_Type"
    ],
    STD_ENGAGEMENT_RATE: [
        "Engagement Rate", "Engagement_Rate", "engagement_rate",
        "ENGAGEMENT_RATE", "Eng Rate", "eng_rate", "ER"
    ],
    STD_PROFILE_VISITS: [
        "Profile Visits", "Profile_Visits", "profile_visits",
        "PROFILE_VISITS", "Profile Views", "Clicks", "clicks"
    ],
}

# Required columns for minimum viable analysis
REQUIRED_COLUMNS = [STD_DATE]
RECOMMENDED_COLUMNS = [STD_REACH, STD_IMPRESSIONS, STD_LIKES, STD_COMMENTS]

# ─── Post Type Normalization ─────────────────────────────────────────────────
POST_TYPE_MAPPING = {
    # Instagram
    "reels": "Reels",
    "reel": "Reels",
    "video": "Reels",
    "REELS": "Reels",
    "carousel": "Carousel",
    "carousels": "Carousel",
    "CAROUSEL": "Carousel",
    "album": "Carousel",
    "static": "Static Image",
    "image": "Static Image",
    "photo": "Static Image",
    "STATIC": "Static Image",
    "IMAGE": "Static Image",
    "stories": "Stories",
    "story": "Stories",
    "STORIES": "Stories",
    # LinkedIn
    "article": "Article",
    "Article": "Article",
    "document": "Document",
    "Document": "Document",
    "text": "Text Post",
    "Text": "Text Post",
}

# Post type icons
POST_TYPE_ICONS = {
    "Reels": "🎬",
    "Carousel": "🖼️",
    "Static Image": "📷",
    "Stories": "📱",
    "Article": "📝",
    "Document": "📄",
    "Text Post": "💬",
    "Video": "🎥",
    "Other": "📌",
}

# ─── PDF Settings ────────────────────────────────────────────────────────────
PDF_MARGIN_LEFT = 50
PDF_MARGIN_RIGHT = 50
PDF_MARGIN_TOP = 60
PDF_MARGIN_BOTTOM = 50
PDF_PAGE_WIDTH = 595  # A4
PDF_PAGE_HEIGHT = 842  # A4

# ─── File Upload Settings ────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 25
MAX_ROWS = 50000
SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "iso-8859-1", "cp1252"]

# ─── AI Settings ─────────────────────────────────────────────────────────────
AI_MAX_CONTEXT_ROWS = 200  # Max rows to summarize for AI
AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 2000
