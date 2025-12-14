import re
import streamlit as st
from study_buddy import explainer_agent, quiz_agent
import time
from datetime import datetime

# Custom CSS for styling
st.markdown("""
<style>
    /* Main styling */
    body {
        background-color: #87CEEB;
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .history-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .history-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .agent-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    /* Make central container slightly opaque for readability */
    .block-container {
        background-color: rgba(255,255,255,0.93) !important;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Custom tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 8px 8px 0 0;
        padding: 0 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def format_quiz_as_points(quiz_text: str) -> str:
    """Convert raw quiz text into markdown nested bullet points for clearer display."""
    if not quiz_text:
        return ""
    out_lines = []
    for line in quiz_text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Question lines (numbered or labeled 'Question' or 'Q')
        if re.match(r'^(?:\d+[\.)]|Question[:\s]|Q[:\s])', s, re.I):
            cleaned = re.sub(r'^(?:\d+[\.)]\s*|Question[:\s]*|Q[:\s]*)', '', s, flags=re.I)
            out_lines.append(f"- {cleaned}")
        # Options like A., A)
        elif re.match(r'^[A-D][\.|\)]', s, re.I):
            out_lines.append(f"    - {s}")
        else:
            out_lines.append(f"- {s}")
    return "\n".join(out_lines)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'quiz_attempts' not in st.session_state:
    st.session_state.quiz_attempts = []
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
# Ensure last results and current text are initialized to avoid KeyError when rendering
if 'last_quiz' not in st.session_state:
    st.session_state.last_quiz = ''
if 'last_explanation' not in st.session_state:
    st.session_state.last_explanation = ''
if 'last_session_data' not in st.session_state:
    st.session_state.last_session_data = None
if 'current_text' not in st.session_state:
    st.session_state.current_text = ''
if 'show_results_notice' not in st.session_state:
    st.session_state.show_results_notice = False

# Page config
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header with gradient
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">🧠 AI Study Buddy</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Two-Agent Intelligent Learning Assistant</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Study Settings")
    
    # Study settings in expandable section
    with st.expander("📊 Configuration", expanded=True):
        explanation_level = st.select_slider(
            "Explanation Depth",
            options=["Simple", "Detailed", "Comprehensive"],
            value="Detailed",
            help="Adjust how detailed the explanations should be"
        )
        
        quiz_difficulty = st.select_slider(
            "Quiz Challenge Level",
            options=["Easy", "Medium", "Hard", "Expert"],
            value="Medium",
            help="Set the difficulty of quiz questions"
        )
        
        num_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=15,
            value=5,
            help="How many questions to generate"
        )
        
        learning_mode = st.selectbox(
            "Learning Mode",
            ["Active Recall", "Concept Mapping", "Spaced Repetition", "Mixed"],
            help="Choose your preferred learning strategy"
        )
    
    st.divider()
    
    # Session history with improved UI
    st.markdown("### 📖 Recent Sessions")
    if st.session_state.history:
        # Display last 5 sessions as cards
        recent_sessions = list(reversed(st.session_state.history[-5:]))
        for i, session in enumerate(recent_sessions):
            timestamp = session.get('timestamp', 'Recent')
            char_count = len(session['text'])
            
            with st.container():
                st.markdown(f"""
                <div class="history-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Session {len(st.session_state.history)-i}</strong><br>
                            <small>{timestamp} • {char_count} chars</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📝 Load", key=f"load_{i}"):
                        st.session_state.current_text = session['text']
                        st.rerun()
                with col2:
                    if st.button(f"📊 Stats", key=f"stats_{i}"):
                        st.session_state.current_session = session
                        st.rerun()
    else:
        st.info("No study sessions yet. Start by pasting some text!")
    
    st.divider()
    
    # Quick stats
    if st.session_state.history:
        st.markdown("### 📈 Quick Stats")
        total_sessions = len(st.session_state.history)
        total_chars = sum(len(s['text']) for s in st.session_state.history)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sessions", total_sessions)
        with col2:
            st.metric("Text Processed", f"{total_chars:,}")

# Main content tabs
tab1, tab2, tab3 = st.tabs(["🎯 Study Session", "📚 Results", "📊 Analytics"])

with tab1:
    # Two column layout
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        # Study material input
        st.markdown("### 📝 Study Material")
        
        input_container = st.container()
        with input_container:
            user_text = st.text_area(
                "Paste your notes, textbook content, or any study material:",
                height=300,
                placeholder="""Example: 
Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen. 
This process occurs in the chloroplasts and involves two main stages: light-dependent reactions and light-independent reactions (Calvin cycle).""",
                value=st.session_state.get('current_text', ''),
                help="Paste 1-3 paragraphs for best results"
            )
            
            # Character counter
            if user_text:
                st.caption(f"📏 {len(user_text)} characters")
        
        # Action buttons
        st.markdown("### ⚡ Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            generate_btn = st.button(
                "✨ Generate Explanation & Quiz", 
                type="primary",
                use_container_width=True,
                disabled=not user_text.strip()
            )
        
        with action_col2:
            explain_only = st.button(
                "🤖 Explain Only",
                use_container_width=True,
                disabled=not user_text.strip()
            )
        
        with action_col3:
            clear_btn = st.button(
                "🗑️ Clear",
                use_container_width=True,
                type="secondary"
            )
        
        if clear_btn and user_text:
            st.session_state.current_text = ''
            st.rerun()
    
    with col2:
        # Tips and features
        st.markdown("### 💡 Tips & Features")
        
        with st.expander("🎯 Best Practices", expanded=True):
            st.info("""
            1. **Focus on one topic** per session
            2. Include **key concepts** and **definitions**
            3. Use **clear, structured text** for best results
            4. Aim for **100-500 words** for optimal processing
            """)
        
        with st.expander("🚀 Quick Actions"):
            # Example texts for quick start
            st.markdown("**Try these examples:**")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                if st.button("🌱 Photosynthesis", use_container_width=True):
                    st.session_state.current_text = "Photosynthesis is the process by which plants convert sunlight into chemical energy. It involves chlorophyll capturing light energy to convert carbon dioxide and water into glucose and oxygen."
                    st.rerun()
            with col_ex2:
                if st.button("💡 Newton's Laws", use_container_width=True):
                    st.session_state.current_text = "Newton's First Law states that an object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force. This is also known as the law of inertia."
                    st.rerun()
        
        # Progress tracker
        if st.session_state.history:
            st.markdown("### 📊 Today's Progress")
            today_sessions = len([s for s in st.session_state.history if s.get('date') == datetime.now().date()])
            progress = min(today_sessions / 5, 1.0)  # Cap at 5 sessions
            st.progress(progress)
            st.caption(f"Completed {today_sessions} session(s) today")

# Processing logic
if generate_btn and user_text.strip():
    with st.spinner("🤖 Agents are analyzing your content..."):
        # Create progress bar
        progress_bar = st.progress(0)
        
        # Store in history with timestamp
        session_data = {
            'text': user_text,
            'explanation': None,
            'quiz': None,
            'timestamp': datetime.now().strftime("%H:%M"),
            'date': datetime.now().date(),
            'level': explanation_level,
            'difficulty': quiz_difficulty
        }
        st.session_state.history.append(session_data)
        
        # Agent 1: Explanation
        progress_bar.progress(30)
        with st.status("🦸‍♂️ **Agent 1 - Explainer**: Analyzing and simplifying content...", expanded=False):
            explanation_obj = explainer_agent(user_text, level=explanation_level)
            explanation = explanation_obj["explanation_text"]
            st.success("Explanation generated successfully!")
        
        # Agent 2: Quiz
        progress_bar.progress(70)
        with st.status("🦸‍♀️ **Agent 2 - Quiz Master**: Creating interactive questions...", expanded=False):
            quiz = quiz_agent(explanation, difficulty=quiz_difficulty, num_questions=num_questions)
            st.success(f"{num_questions} questions created!")
        
        progress_bar.progress(100)
        
        # Update session data
        st.session_state.history[-1]['explanation'] = explanation
        st.session_state.history[-1]['quiz'] = quiz
        
        # Store for display
        st.session_state.last_explanation = explanation
        st.session_state.last_quiz = quiz
        st.session_state.last_session_data = st.session_state.history[-1]
        
        time.sleep(0.5)
        progress_bar.empty()
        
        # Success message
        st.success("✅ Study materials generated successfully! Check the Results tab.")
        st.balloons()

elif explain_only and user_text.strip():
    with st.spinner("🤖 Generating explanation..."):
        explanation_obj = explainer_agent(user_text, level=explanation_level)
        st.session_state.last_explanation = explanation_obj["explanation_text"]
        st.success("Explanation ready! Switch to Results tab.")

# Results Tab
with tab2:
    if st.session_state.get('show_results_notice'):
        st.info("Session details loaded — open the Results tab or refresh to view them.")
        st.session_state.show_results_notice = False
    if 'last_explanation' in st.session_state:
        st.markdown("### 📋 Generated Content")
        
        # Export option at top
        export_col1, export_col2 = st.columns([3, 1])
        with export_col2:
            formatted_quiz = format_quiz_as_points(st.session_state.get('last_quiz', ''))
            export_content = f"""AI STUDY BUDDY - STUDY SESSION
{'='*40}

ORIGINAL TEXT:
{user_text[:500]}...

EXPLANATION LEVEL: {explanation_level}
QUIZ DIFFICULTY: {quiz_difficulty}
GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{'='*40}

SIMPLIFIED EXPLANATION:
{st.session_state.last_explanation}

{'='*40}

QUIZ QUESTIONS ({quiz_difficulty} Level):
{formatted_quiz}
            """
            
            st.download_button(
                label="📥 Export Session",
                data=export_content,
                file_name=f"study_session_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Results in tabs
        result_tab1, result_tab2 = st.tabs(["📖 Explanation", "❓ Interactive Quiz"])
        
        with result_tab1:
            st.markdown("#### 🎯 Simplified Explanation")
            st.markdown(st.session_state.last_explanation)
            
            st.divider()
            st.markdown("#### 💬 Explanation Feedback")
            
            feedback_cols = st.columns(4)
            with feedback_cols[0]:
                if st.button("👍 Clear & Helpful", use_container_width=True):
                    st.toast("Thanks! We'll maintain this level of detail.")
            with feedback_cols[1]:
                if st.button("👎 Too Complex", use_container_width=True):
                    st.info("Try adjusting the Explanation Level to 'Simple'")
            with feedback_cols[2]:
                if st.button("📝 More Details", use_container_width=True):
                    st.info("Try adjusting the Explanation Level to 'Comprehensive'")
            with feedback_cols[3]:
                if st.button("🔁 Regenerate", use_container_width=True):
                    with st.spinner("Creating new explanation..."):
                        new_exp = explainer_agent(user_text, level=explanation_level)
                        st.session_state.last_explanation = new_exp["explanation_text"]
                        st.rerun()
        
        with result_tab2:
            st.markdown(f"#### 🧠 Quiz ({quiz_difficulty} Level)")
            formatted = format_quiz_as_points(st.session_state.get('last_quiz', ''))
            if formatted:
                st.markdown(formatted)
            else:
                st.info("No quiz generated yet. Click 'Generate Explanation & Quiz' to create one.")
            
            st.divider()
            st.markdown("#### 🛠️ Quiz Tools")
            
            tool_cols = st.columns(3)
            with tool_cols[0]:
                if st.button("🔄 New Questions", use_container_width=True):
                    with st.spinner("Generating new questions..."):
                        new_quiz = quiz_agent(
                            st.session_state.last_explanation,
                            difficulty=quiz_difficulty,
                            num_questions=num_questions
                        )
                        st.session_state.last_quiz = new_quiz
                        st.rerun()
            
            with tool_cols[1]:
                difficulty_change = st.selectbox(
                    "Change Difficulty",
                    ["Easy", "Medium", "Hard", "Expert"],
                    index=["Easy", "Medium", "Hard", "Expert"].index(quiz_difficulty),
                    label_visibility="collapsed"
                )
                if difficulty_change != quiz_difficulty:
                    with st.spinner(f"Creating {difficulty_change.lower()} quiz..."):
                        new_quiz = quiz_agent(
                            st.session_state.last_explanation,
                            difficulty=difficulty_change,
                            num_questions=num_questions
                        )
                        st.session_state.last_quiz = new_quiz
                        st.session_state.history[-1]['difficulty'] = difficulty_change
                        st.rerun()
            
            with tool_cols[2]:
                if st.button("📊 Track Progress", use_container_width=True):
                    st.session_state.quiz_attempts.append({
                        'date': datetime.now(),
                        'difficulty': quiz_difficulty,
                        'questions': num_questions
                    })
                    st.success(f"Quiz attempt recorded! Total: {len(st.session_state.quiz_attempts)}")
    
    else:
        st.info("👈 Start by generating some study materials in the Study Session tab!")

# Analytics Tab
with tab3:
    st.markdown("### 📊 Learning Analytics")
    
    if st.session_state.history:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Sessions", len(st.session_state.history))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            total_chars = sum(len(s['text']) for s in st.session_state.history)
            st.metric("Text Processed", f"{total_chars:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            today = datetime.now().date()
            today_sessions = len([s for s in st.session_state.history if s.get('date') == today])
            st.metric("Today's Sessions", today_sessions)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_length = total_chars / len(st.session_state.history)
            st.metric("Avg. Length", f"{avg_length:.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Session details in expandable sections
        st.markdown("### 📝 Session Details")
        
        for i, session in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Session {len(st.session_state.history)-i} • {session.get('timestamp', 'N/A')} • {session.get('level', 'N/A')} Level", expanded=i==0):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Original Text Preview:**")
                    preview = session['text'][:300] + "..." if len(session['text']) > 300 else session['text']
                    st.text(preview)
                    
                    # Session metadata
                    st.caption(f"""
                    📊 Stats: {len(session['text'])} chars • 
                    🎯 Level: {session.get('level', 'N/A')} • 
                    ⚡ Difficulty: {session.get('difficulty', 'N/A')}
                    """)
                
                with col_b:
                    if session.get('explanation'):
                        st.markdown("**Key Insights:**")
                        # Extract first few key points
                        lines = [line.strip() for line in session['explanation'].split('\n') if line.strip()][:5]
                        for line in lines:
                            st.markdown(f"• {line}")
                    
                    # Action buttons for each session
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"🔍 View Details", key=f"view_{i}"):
                            st.session_state.current_text = session['text']
                            st.session_state.last_explanation = session.get('explanation')
                            st.session_state.last_quiz = session.get('quiz')
                            try:
                                st.switch_page("Results")
                            except Exception:
                                # Fallback: set a notice and keep data loaded for the Results tab
                                st.session_state.show_results_notice = True
                                # `st.experimental_rerun()` may not exist in all Streamlit versions; avoid AttributeError
                                try:
                                    st.experimental_rerun()
                                except Exception:
                                    # If rerun isn't available, simply continue; the notice will appear on the Results tab
                                    pass
                    
                    with btn_col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                            del st.session_state.history[len(st.session_state.history)-1-i]
                            st.rerun()
        
        # Clear history button
        st.divider()
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
            st.session_state.history = []
            st.session_state.quiz_attempts = []
            st.rerun()
    
    else:
        st.info("No analytics data yet. Generate your first study session to see insights here!")

# Footer
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
with footer_col1:
    st.caption("🧠 AI Study Buddy v2.1 • Powered by Two-Agent Learning System")
with footer_col2:
    st.caption("💡 Tip: Use the sidebar to manage sessions")
with footer_col3:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")