import re
import streamlit as st
from study_buddy import explainer_agent, quiz_agent
import os
import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
import base64

# ============================================================================
# CUSTOM CSS & STYLING
# ============================================================================
st.markdown("""
<style>
    /* Main theme variables */
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --accent: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark: #1e293b;
        --light: #f8fafc;
        --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-light: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        --gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
        --gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    
    /* Global styles */
    body {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #fef3c7 100%);
        background-attachment: fixed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main header with animated gradient */
    .main-header {
        background: var(--gradient);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        animation: gradientShift 10s ease infinite;
        background-size: 400% 400%;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Card styles */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card {
        background: var(--gradient-light);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 5px solid var(--primary);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .agent-card {
        background: var(--gradient);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Button styles */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Primary button */
    .primary-btn {
        background: var(--gradient) !important;
        color: white !important;
    }
    
    /* Secondary button */
    .secondary-btn {
        background: var(--gradient-light) !important;
        color: var(--dark) !important;
        border: 2px solid var(--primary) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 12px;
        padding: 0 24px;
        font-weight: 600;
        background: var(--gradient-light);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient) !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        font-size: 14px !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: var(--gradient) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    /* Custom badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-primary {
        background: var(--gradient);
        color: white;
    }
    
    .badge-success {
        background: var(--gradient-success);
        color: white;
    }
    
    .badge-warning {
        background: var(--gradient-warning);
        color: white;
    }
    
    /* Floating elements */
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Pulse animation */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_quiz_as_points(quiz_text: str) -> str:
    """Convert raw quiz text into markdown nested bullet points for clearer display."""
    if not quiz_text:
        return ""
    out_lines = []
    for line in quiz_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r'^(?:\d+[\.)]|Question[:\s]|Q[:\s])', s, re.I):
            cleaned = re.sub(r'^(?:\d+[\.)]\s*|Question[:\s]*|Q[:\s]*)', '', s, flags=re.I)
            out_lines.append(f"### {cleaned}")
        elif re.match(r'^[A-D][\.|\)]', s, re.I):
            out_lines.append(f"• **{s[:2]}** {s[2:].strip()}")
        else:
            out_lines.append(f"- {s}")
    return "\n".join(out_lines)

def create_progress_chart(sessions_data):
    """Create a progress chart for the analytics dashboard."""
    dates = [s.get('date') for s in sessions_data if s.get('date')]
    if dates:
        date_counts = {}
        for date in dates:
            date_str = str(date)
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        df = pd.DataFrame({
            'Date': list(date_counts.keys()),
            'Sessions': list(date_counts.values())
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Sessions'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#764ba2'),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.update_layout(
            title='📈 Study Session Trend',
            xaxis_title='Date',
            yaxis_title='Number of Sessions',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter'),
            height=300
        )
        return fig

def create_difficulty_chart(sessions_data):
    """Create a difficulty distribution chart."""
    difficulties = [s.get('difficulty', 'Unknown') for s in sessions_data]
    if difficulties:
        diff_counts = {}
        for diff in difficulties:
            diff_counts[diff] = diff_counts.get(diff, 0) + 1
        
        colors = ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444']
        
        fig = go.Figure(data=[go.Pie(
            labels=list(diff_counts.keys()),
            values=list(diff_counts.values()),
            hole=.4,
            marker=dict(colors=colors[:len(diff_counts)])
        )])
        
        fig.update_layout(
            title='🎯 Difficulty Distribution',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter'),
            height=300,
            showlegend=True
        )
        return fig

def get_streak_days(sessions_data):
    """Calculate consecutive days with sessions."""
    if not sessions_data:
        return 0
    
    dates = sorted(set([s.get('date') for s in sessions_data if s.get('date')]))
    if not dates:
        return 0
    
    streak = 1
    current_date = dates[-1]
    
    for i in range(len(dates)-2, -1, -1):
        if (current_date - dates[i]).days == 1:
            streak += 1
            current_date = dates[i]
        else:
            break
    
    return streak

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'history' not in st.session_state:
    st.session_state.history = []
if 'quiz_attempts' not in st.session_state:
    st.session_state.quiz_attempts = []
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'user_level' not in st.session_state:
    st.session_state.user_level = 1
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'study_time' not in st.session_state:
    st.session_state.study_time = 0

# Initialize display variables
for key in ['last_quiz', 'last_explanation', 'last_session_data', 'current_text']:
    if key not in st.session_state:
        st.session_state[key] = ''

if 'show_results_notice' not in st.session_state:
    st.session_state.show_results_notice = False


def safe_switch_to_results():
    """Try switching to the Results page, otherwise set a notice for the user."""
    try:
        st.switch_page("Results")
    except Exception:
        st.session_state.show_results_notice = True
        try:
            st.experimental_rerun()
        except Exception:
            pass

# ============================================================================
# PAGE CONFIG & ASSETS
# ============================================================================

st.set_page_config(
    page_title="AI Study Buddy Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': '# AI Study Buddy Pro\nAn intelligent learning assistant powered by dual AI agents.'
    }
)

# Create assets directory if it doesn't exist
ASSETS_DIR = "assets"
ROBO_PATH = os.path.join(ASSETS_DIR, "robo.jpg")
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)

if not os.path.exists(ROBO_PATH):
    img = Image.new("RGB", (160, 160), color=(245, 245, 245))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([20, 20, 140, 120], radius=16, fill=(200, 200, 200), outline=(120, 120, 120))
    d.ellipse([42, 42, 68, 68], fill=(30, 30, 30))
    d.ellipse([92, 42, 118, 68], fill=(30, 30, 30))
    d.rectangle([60, 82, 100, 96], fill=(30, 30, 30))
    d.line((80, 20, 80, 6), fill=(120, 120, 120), width=4)
    d.ellipse([76, 0, 84, 8], fill=(220, 0, 0))
    img.save(ROBO_PATH, format="JPEG")

# ============================================================================
# HEADER
# ============================================================================

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown(f"""
    <div class="floating">
        <img src="data:image/jpeg;base64,{base64.b64encode(open(ROBO_PATH, 'rb').read()).decode()}" 
             width="120" style="border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 2.8rem; font-weight: 800;">🧠 AI Study Buddy Pro</h1>
        <p style="margin:0; opacity: 0.9; font-size: 1.2rem; margin-top: 0.5rem;">
            Dual-Agent Intelligent Learning System
        </p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <span class="badge badge-primary">🤖 Explainer Agent</span>
            <span class="badge badge-success">🎯 Quiz Master Agent</span>
            <span class="badge badge-warning">📊 Progress Tracker</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # XP and Level display
    xp_progress = (st.session_state.xp % 100) / 100
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.9); padding: 1rem; border-radius: 16px; 
                text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
        <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;">LEVEL</div>
        <div style="font-size: 2rem; font-weight: 800; color: #667eea;">{st.session_state.user_level}</div>
        <div style="height: 8px; background: #e2e8f0; border-radius: 4px; margin: 0.5rem 0; overflow: hidden;">
            <div style="height: 100%; width: {xp_progress*100}%; background: linear-gradient(90deg, #667eea, #764ba2);"></div>
        </div>
        <div style="font-size: 0.8rem; color: #64748b;">{st.session_state.xp % 100}/100 XP</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    # User Profile
    st.markdown("### 👤 Study Profile")
    
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("🔥 Streak", f"{get_streak_days(st.session_state.history)} days")
        with col_b:
            st.metric("⏱️ Study Time", f"{st.session_state.study_time} min")
    
    st.divider()
    
    # Study Settings
    st.markdown("### ⚙️ Study Settings")
    
    with st.expander("📊 **Configuration**", expanded=True):
        explanation_level = st.select_slider(
            "Explanation Depth",
            options=["Beginner", "Intermediate", "Advanced", "Expert"],
            value="Intermediate",
            help="Adjust how detailed the explanations should be"
        )
        
        quiz_difficulty = st.select_slider(
            "Quiz Challenge Level",
            options=["Easy", "Medium", "Hard", "Expert", "Master"],
            value="Medium",
            help="Set the difficulty of quiz questions"
        )
        
        num_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=20,
            value=7,
            help="How many questions to generate"
        )
        
        learning_mode = st.selectbox(
            "Learning Mode",
            ["Active Recall", "Concept Mapping", "Spaced Repetition", "Feynman Technique", "Mixed"],
            help="Choose your preferred learning strategy"
        )
    
    st.divider()
    
    # Session History
    st.markdown("### 📖 Recent Sessions")
    
    if st.session_state.history:
        recent_sessions = list(reversed(st.session_state.history[-5:]))
        for i, session in enumerate(recent_sessions):
            timestamp = session.get('timestamp', 'Recent')
            char_count = len(session['text'])
            
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="margin-bottom: 0.5rem; cursor: pointer;" 
                     onclick="this.style.transform='translateY(-2px)'">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <strong style="color: #1e293b;">Session {len(st.session_state.history)-i}</strong><br>
                            <small style="color: #64748b;">{timestamp} • {char_count} chars</small>
                        </div>
                        <span style="font-size: 0.8rem; background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); 
                                  padding: 0.2rem 0.5rem; border-radius: 10px;">
                            {session.get('level', 'N/A')}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(f"📝 Load", key=f"load_{i}", width='stretch'):
                        st.session_state.current_text = session['text']
                        st.success(f"📚 Loaded Session {len(st.session_state.history)-i}")
                with btn_col2:
                    if st.button(f"📊 Stats", key=f"stats_{i}", width='stretch'):
                        st.session_state.current_session = session
    else:
        st.info("🚀 No sessions yet. Start your learning journey!")
    
    st.divider()
    
    # Quick Stats
    if st.session_state.history:
        st.markdown("### 📈 Quick Stats")
        
        total_sessions = len(st.session_state.history)
        total_chars = sum(len(s['text']) for s in st.session_state.history)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("📚 Sessions", total_sessions)
        with col_s2:
            st.metric("📝 Characters", f"{total_chars:,}")

# ============================================================================
# MAIN CONTENT TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Study Session", "📚 Results", "📊 Analytics", "🏆 Achievements"])

# ============================================================================
# TAB 1: STUDY SESSION
# ============================================================================

with tab1:
    st.markdown("### 📝 Study Material Input")
    
    col_input, col_tips = st.columns([3, 2], gap="large")
    
    with col_input:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            user_text = st.text_area(
                "Paste your notes, textbook content, or any study material here:",
                height=320,
                placeholder="""Example: 
Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen. 
This process occurs in the chloroplasts and involves two main stages: light-dependent reactions and light-independent reactions (Calvin cycle).""",
                value=st.session_state.get('current_text', ''),
                help="For best results, paste 1-3 paragraphs (100-500 words) on a single topic.",
                label_visibility="collapsed"
            )
            
            if user_text:
                char_count = len(user_text)
                word_count = len(user_text.split())
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.metric("📏 Characters", char_count)
                with col_c2:
                    st.metric("📝 Words", word_count)
                with col_c3:
                    readability = "Good" if 100 <= word_count <= 500 else "Needs adjustment"
                    st.metric("📊 Readability", readability)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Action Buttons
        st.markdown("### ⚡ Actions")
        
        col_actions = st.columns(5)
        with col_actions[0]:
            generate_btn = st.button(
                "✨ Generate All", 
                type="primary",
                width='stretch',
                disabled=not user_text.strip() or len(user_text.strip()) < 50
            )
        with col_actions[1]:
            explain_only = st.button(
                "🤖 Explain Only",
                width='stretch',
                disabled=not user_text.strip() or len(user_text.strip()) < 50
            )
        with col_actions[2]:
            quiz_only = st.button(
                "🎯 Quiz Only",
                width='stretch',
                disabled=not user_text.strip() or len(user_text.strip()) < 50
            )
        with col_actions[3]:
            if st.button("💾 Save Draft", width='stretch'):
                if user_text:
                    st.session_state.current_text = user_text
                    st.success("Draft saved!")
        with col_actions[4]:
            clear_btn = st.button("🗑️ Clear", width='stretch', type="secondary")
            
            if clear_btn and user_text:
                st.session_state.current_text = ''
                st.rerun()
    
    with col_tips:
        st.markdown("### 💡 Smart Tips")
        
        with st.expander("🎯 **Best Practices**", expanded=True):
            tips = [
                ("📚 Focused Topics", "One topic per session for best results"),
                ("🎯 Key Concepts", "Include definitions and main ideas"),
                ("📊 Structured Content", "Use clear paragraphs and headings"),
                ("⏱️ Optimal Length", "Aim for 200-500 words"),
                ("🔍 Quality over Quantity", "Clear content beats lengthy text")
            ]
            
            for icon, tip in tips:
                st.markdown(f"""
                <div style="background: var(--gradient-light); padding: 0.8rem; border-radius: 12px; 
                            margin-bottom: 0.5rem; border-left: 4px solid var(--primary);">
                    <div style="font-weight: 600; color: #1e293b;">{icon} {tip.split(':')[0]}</div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">
                        {tip.split(':')[1] if ':' in tip else tip}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with st.expander("🚀 **Quick Start**"):
            examples = [
                ("🌱 Biology", "Photosynthesis process in plants"),
                ("⚛️ Physics", "Newton's Laws of Motion"),
                ("💻 Computer Science", "Machine Learning basics"),
                ("📊 Economics", "Supply and demand principles"),
                ("📚 Literature", "Literary analysis techniques")
            ]
            
            for emoji, topic in examples:
                if st.button(f"{emoji} {topic}", width='stretch', key=f"ex_{topic}"):
                    example_texts = {
                        "Biology": "Photosynthesis is the process by which plants convert sunlight into chemical energy...",
                        "Physics": "Newton's First Law states that an object at rest stays at rest...",
                        "Computer Science": "Machine Learning is a subset of AI that enables computers to learn patterns...",
                        "Economics": "Supply and demand is an economic model of price determination...",
                        "Literature": "Literary analysis involves examining the elements of a literary text..."
                    }
                    st.session_state.current_text = example_texts.get(topic.split()[0], "")
                    st.rerun()

# ============================================================================
# TAB 2: RESULTS
# ============================================================================

with tab2:
    if st.session_state.get('show_results_notice'):
        st.success("✅ Session details loaded successfully!")
        st.session_state.show_results_notice = False
    
    if st.session_state.last_explanation:
        st.markdown("### 📋 Generated Content")
        
        # Export and Tools Bar
        with st.container():
            col_tools1, col_tools2, col_tools3, col_tools4 = st.columns(4)
            
            with col_tools1:
                formatted_quiz = format_quiz_as_points(st.session_state.get('last_quiz', ''))
                export_content = f"""AI STUDY BUDDY PRO - STUDY SESSION
{'='*60}

METADATA:
• Explanation Level: {explanation_level}
• Quiz Difficulty: {quiz_difficulty}
• Learning Mode: {learning_mode}
• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}

ORIGINAL TEXT:
{user_text[:1000]}{'...' if len(user_text) > 1000 else ''}

{'='*60}

SIMPLIFIED EXPLANATION:
{st.session_state.last_explanation}

{'='*60}

QUIZ QUESTIONS ({quiz_difficulty} Level):
{formatted_quiz}
                """
                
                st.download_button(
                    label="📥 Export Session",
                    data=export_content,
                    file_name=f"study_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    width='stretch'
                )
            
            with col_tools2:
                if st.button("🔄 New Session", width='stretch'):
                    st.session_state.current_text = ''
                    st.session_state.last_explanation = None
                    st.session_state.last_quiz = None
                    st.success("Ready for new session!")
            
            with col_tools3:
                if st.button("📊 Add to Analytics", width='stretch'):
                    st.session_state.study_time += 15
                    st.session_state.xp += 10
                    if st.session_state.xp >= 100:
                        st.session_state.user_level += 1
                        st.session_state.xp = 0
                        st.balloons()
                        st.success(f"🎉 Level up! You're now level {st.session_state.user_level}")
            
            with col_tools4:
                if st.button("💬 Get Feedback", width='stretch'):
                    st.info("Coming soon: AI-powered personalized feedback!")
        
        # Results Tabs
        result_tabs = st.tabs(["📖 Explanation", "❓ Interactive Quiz", "🎯 Key Points"])
        
        with result_tabs[0]:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### 🎯 Simplified Explanation")
                st.markdown(st.session_state.last_explanation)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Feedback
                st.markdown("#### 💬 Explanation Feedback")
                feedback_options = ["👍 Perfect!", "👎 Too Complex", "📝 Need More Detail", "🎯 Off Topic"]
                selected_feedback = st.radio("How was this explanation?", feedback_options, horizontal=True)
                
                if st.button("Submit Feedback", type="secondary"):
                    st.toast("Thank you for your feedback! 🎯")
        
        with result_tabs[1]:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(f"#### 🧠 Quiz ({quiz_difficulty} Level)")
                
                if st.session_state.last_quiz:
                    formatted = format_quiz_as_points(st.session_state.last_quiz)
                    st.markdown(formatted)
                    
                    # Interactive Quiz Options
                    st.divider()
                    quiz_mode = st.radio(
                        "Quiz Mode:",
                        ["📋 Standard View", "🎮 Practice Mode", "⏱️ Timed Challenge"],
                        horizontal=True
                    )
                    
                    if quiz_mode == "🎮 Practice Mode":
                        st.info("Practice mode coming soon! Stay tuned.")
                    elif quiz_mode == "⏱️ Timed Challenge":
                        st.info("Timed challenge feature in development.")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with result_tabs[2]:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### 🎯 Key Learning Points")
                
                # Extract key points from explanation
                lines = [line.strip() for line in st.session_state.last_explanation.split('\n') if line.strip()]
                key_points = lines[:min(10, len(lines))]
                
                for i, point in enumerate(key_points, 1):
                    st.markdown(f"""
                    <div style="background: var(--gradient-light); padding: 1rem; border-radius: 12px; 
                                margin-bottom: 0.5rem; border-left: 4px solid var(--primary);">
                        <div style="display: flex; align-items: center;">
                            <div style="background: var(--primary); color: white; width: 24px; height: 24px; 
                                      border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                      margin-right: 0.75rem; font-weight: 600;">
                                {i}
                            </div>
                            <div>{point}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        col_empty1, col_empty2, col_empty3 = st.columns([1, 2, 1])
        with col_empty2:
            st.markdown("""
            <div style="text-align: center; padding: 4rem; background: rgba(255,255,255,0.9); 
                        border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📚</div>
                <h3 style="color: #64748b;">No Content Yet</h3>
                <p style="color: #94a3b8; margin-bottom: 2rem;">
                    Generate your first study session to see amazing results here!
                </p>
                <button onclick="parent.document.querySelector('[data-testid=\"stTabButton\"][data-baseweb=\"tab\"][aria-selected=\"false\"]').click()" 
                        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               color: white; padding: 0.8rem 2rem; border: none; border-radius: 12px; 
                               font-size: 1rem; cursor: pointer; font-weight: 600;">
                    Start Your First Session
                </button>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# TAB 3: ANALYTICS
# ============================================================================

with tab3:
    st.markdown("### 📊 Learning Analytics Dashboard")
    
    if st.session_state.history:
        # Summary Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📚 Total Sessions", len(st.session_state.history), 
                         delta=f"+{len([s for s in st.session_state.history if s.get('date') == datetime.now().date()])} today")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_m2:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_chars = sum(len(s['text']) for s in st.session_state.history)
                st.metric("📝 Text Processed", f"{total_chars:,}", 
                         delta=f"~{total_chars//max(1, len(st.session_state.history)):,} avg")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_m3:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                today = datetime.now().date()
                today_sessions = len([s for s in st.session_state.history if s.get('date') == today])
                st.metric("🔥 Today's Sessions", today_sessions, 
                         delta="Goal: 3" if today_sessions < 3 else "Goal Achieved! 🎉")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_m4:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                streak = get_streak_days(st.session_state.history)
                st.metric("⚡ Study Streak", f"{streak} days", 
                         delta="Keep it up!" if streak > 0 else "Start your streak!")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig1 = create_progress_chart(st.session_state.history)
            st.plotly_chart(fig1, width='stretch')
        
        with col_chart2:
            fig2 = create_difficulty_chart(st.session_state.history)
            st.plotly_chart(fig2, width='stretch')
        
        # Session Details
        st.markdown("### 📝 Session History")
        
        for i, session in enumerate(reversed(st.session_state.history)):
            with st.expander(
                f"Session {len(st.session_state.history)-i} • "
                f"{session.get('timestamp', 'N/A')} • "
                f"{session.get('level', 'N/A')} • "
                f"⭐ Difficulty: {session.get('difficulty', 'N/A')}",
                expanded=i < 2  # Expand first two by default
            ):
                col_sess1, col_sess2 = st.columns(2)
                
                with col_sess1:
                    st.markdown("**Original Text Preview:**")
                    preview = session['text'][:400] + "..." if len(session['text']) > 400 else session['text']
                    with st.container():
                        st.markdown(f'<div style="background: #f8fafc; padding: 1rem; border-radius: 12px; font-size: 0.9rem;">{preview}</div>', 
                                  unsafe_allow_html=True)
                
                with col_sess2:
                    if session.get('explanation'):
                        st.markdown("**Key Insights:**")
                        lines = [line.strip() for line in session['explanation'].split('\n') if line.strip()][:4]
                        for line in lines:
                            st.markdown(f"• {line}")
                    
                    # Session Actions
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button(f"📖 Review", key=f"review_{i}", width='stretch'):
                            st.session_state.current_text = session['text']
                            st.session_state.last_explanation = session.get('explanation')
                            st.session_state.last_quiz = session.get('quiz')
                            safe_switch_to_results()
                    
                    with col_act2:
                        if st.button(f"📥 Export", key=f"export_{i}", width='stretch'):
                            st.success("Session exported to downloads!")
                    
                    with col_act3:
                        if st.button(f"🗑️", key=f"delete_{i}", width='stretch', type="secondary"):
                            del st.session_state.history[len(st.session_state.history)-1-i]
                            st.rerun()
        
        # Clear History
        st.divider()
        if st.button("🗑️ Clear All History", type="secondary", width='stretch', icon="⚠️"):
            st.session_state.history = []
            st.session_state.quiz_attempts = []
            st.success("History cleared successfully!")
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem; background: rgba(255,255,255,0.9); 
                    border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #64748b;">No Analytics Data Yet</h3>
            <p style="color: #94a3b8;">
                Start creating study sessions to unlock detailed analytics and insights!
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: ACHIEVEMENTS
# ============================================================================

with tab4:
    st.markdown("### 🏆 Achievements & Progress")
    
    col_ach1, col_ach2 = st.columns([2, 1])
    
    with col_ach1:
        achievements = [
            {"icon": "🚀", "name": "First Session", "desc": "Complete your first study session", "xp": 50},
            {"icon": "🔥", "name": "3-Day Streak", "desc": "Study for 3 consecutive days", "xp": 100},
            {"icon": "📚", "name": "Bookworm", "desc": "Process 10,000+ characters", "xp": 75},
            {"icon": "🎯", "name": "Quiz Master", "desc": "Complete 5 quizzes", "xp": 125},
            {"icon": "⚡", "name": "Speed Learner", "desc": "Complete 3 sessions in one day", "xp": 150},
            {"icon": "🌟", "name": "Expert Level", "desc": "Use Expert difficulty 5 times", "xp": 200},
        ]
        
        for ach in achievements:
            unlocked = random.choice([True, False])  # Replace with actual logic
            with st.container():
                st.markdown(f"""
                <div style="background: {'var(--gradient-success)' if unlocked else 'var(--gradient-light)'}; 
                            padding: 1rem; border-radius: 16px; margin-bottom: 1rem; 
                            border-left: 4px solid {'var(--accent)' if unlocked else '#cbd5e1'};">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="font-size: 1.5rem;">{ach['icon']}</div>
                            <div>
                                <div style="font-weight: 600; color: {'white' if unlocked else '#1e293b'};">
                                    {ach['name']}
                                </div>
                                <div style="font-size: 0.9rem; color: {'rgba(255,255,255,0.8)' if unlocked else '#64748b'};">
                                    {ach['desc']}
                                </div>
                            </div>
                        </div>
                        <div style="background: {'rgba(255,255,255,0.2)' if unlocked else 'white'}; 
                                    padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600; 
                                    color: {'white' if unlocked else 'var(--primary)'};">
                            {ach['xp']} XP
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_ach2:
        st.markdown("#### 📈 Progress Overview")
        
        progress_data = {
            "Category": ["Sessions", "Quizzes", "Study Time", "Characters"],
            "Progress": [
                min(len(st.session_state.history) / 10, 1.0),
                min(len(st.session_state.quiz_attempts) / 5, 1.0),
                min(st.session_state.study_time / 60, 1.0),
                min(sum(len(s['text']) for s in st.session_state.history) / 10000, 1.0)
            ]
        }
        
        df_progress = pd.DataFrame(progress_data)
        
        fig = px.bar(df_progress, x='Category', y='Progress', 
                     color='Progress', color_continuous_scale='Blues')
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, width='stretch')
        
        st.markdown("#### 🎯 Next Milestones")
        milestones = [
            f"📚 Reach {max(0, 10 - len(st.session_state.history))} more sessions for Bookworm",
            f"🔥 Maintain streak for {max(0, 3 - get_streak_days(st.session_state.history))} more days",
            f"🎯 Complete {max(0, 5 - len(st.session_state.quiz_attempts))} more quizzes"
        ]
        
        for milestone in milestones:
            st.markdown(f"- {milestone}")

# ============================================================================
# PROCESSING LOGIC
# ============================================================================

if generate_btn and user_text.strip() and len(user_text.strip()) >= 50:
    with st.spinner("🤖 Agents are analyzing your content..."):
        # Show progress animation
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        # Create session data
        session_data = {
            'text': user_text,
            'explanation': None,
            'quiz': None,
            'timestamp': datetime.now().strftime("%H:%M"),
            'date': datetime.now().date(),
            'level': explanation_level,
            'difficulty': quiz_difficulty,
            'mode': learning_mode
        }
        st.session_state.history.append(session_data)
        
        # Update progress
        progress_bar.progress(30)
        status_container.markdown("""
        <div class="agent-card">
            <h4 style="margin:0; color: white;">🦸‍♂️ Agent 1 - Explainer</h4>
            <p style="margin:0; opacity: 0.9;">Analyzing and simplifying content...</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate explanation
        explanation_obj = explainer_agent(user_text, level=explanation_level)
        explanation = explanation_obj["explanation_text"]
        
        progress_bar.progress(70)
        status_container.markdown("""
        <div class="agent-card" style="background: var(--gradient-success);">
            <h4 style="margin:0; color: white;">🦸‍♀️ Agent 2 - Quiz Master</h4>
            <p style="margin:0; opacity: 0.9;">Creating interactive questions...</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate quiz
        quiz = quiz_agent(explanation, difficulty=quiz_difficulty, num_questions=num_questions)
        
        progress_bar.progress(100)
        
        # Update session data
        st.session_state.history[-1]['explanation'] = explanation
        st.session_state.history[-1]['quiz'] = quiz
        
        # Store for display
        st.session_state.last_explanation = explanation
        st.session_state.last_quiz = quiz
        st.session_state.last_session_data = st.session_state.history[-1]
        
        # Update XP and study time
        st.session_state.xp += 15
        st.session_state.study_time += 10
        
        time.sleep(0.5)
        progress_bar.empty()
        status_container.empty()
        
        # Success message
        st.success("""
        🎉 **Study materials generated successfully!**
        
        **What's ready:**
        • 📖 Detailed explanation with key concepts
        • ❓ Interactive quiz with multiple choice questions
        • 📊 Session saved to your history
        • 🏆 +15 XP added to your profile
        
        Switch to the **Results** tab to explore!
        """)
        
        # Auto-switch to results tab
        safe_switch_to_results()

elif explain_only and user_text.strip() and len(user_text.strip()) >= 50:
    with st.spinner("🤖 Generating explanation..."):
        explanation_obj = explainer_agent(user_text, level=explanation_level)
        st.session_state.last_explanation = explanation_obj["explanation_text"]
        st.session_state.xp += 5
        st.success("✅ Explanation ready! Switch to Results tab to view.")
        safe_switch_to_results()

elif quiz_only and user_text.strip() and len(user_text.strip()) >= 50:
    with st.spinner("🤖 Creating quiz..."):
        if not st.session_state.last_explanation:
            explanation_obj = explainer_agent(user_text, level=explanation_level)
            explanation = explanation_obj["explanation_text"]
            st.session_state.last_explanation = explanation
        
        quiz = quiz_agent(st.session_state.last_explanation, difficulty=quiz_difficulty, num_questions=num_questions)
        st.session_state.last_quiz = quiz
        st.session_state.xp += 8
        st.success("✅ Quiz ready! Switch to Results tab to view.")
        safe_switch_to_results()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<hr style="border: none; height: 2px; background: linear-gradient(90deg, transparent, var(--primary), transparent); margin: 2rem 0;">

<div style="text-align: center; padding: 2rem; color: #64748b; font-size: 0.9rem;">
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; flex-wrap: wrap;">
        <span>🧠 AI Study Buddy Pro v3.5</span>
        <span>•</span>
        <span>⚡ Powered by Dual-Agent AI System</span>
        <span>•</span>
        <span>🔒 Your data is private & secure</span>
    </div>
    <div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 0.5rem;">
        <span>📅 {date}</span>
        <span>•</span>
        <span>⏱️ {study_time} min studied</span>
        <span>•</span>
        <span>🔥 {streak}-day streak</span>
        <span>•</span>
        <span>🎯 Level {level}</span>
    </div>
</div>
""".format(
    date=datetime.now().strftime('%Y-%m-%d'),
    study_time=st.session_state.study_time,
    streak=get_streak_days(st.session_state.history),
    level=st.session_state.user_level
), unsafe_allow_html=True)

# Floating Action Button
st.markdown("""
<div style="position: fixed; bottom: 20px; right: 20px; z-index: 999;">
    <style>
    .fab-btn {
        background: var(--gradient);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .fab-btn:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6);
    }
    </style>
    <button class="fab-btn" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">↑</button>
</div>
""", unsafe_allow_html=True)