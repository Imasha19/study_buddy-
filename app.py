import streamlit as st
from study_buddy import explainer_agent, quiz_agent

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Buddy - Two-Agent Learning Assistant")

# Sidebar for options
with st.sidebar:
    st.header("⚙️ Settings")
    
    explanation_level = st.select_slider(
        "Explanation Level",
        options=["Simple", "Detailed", "Comprehensive"],
        value="Detailed"
    )
    
    quiz_difficulty = st.select_slider(
        "Quiz Difficulty",
        options=["Easy", "Medium", "Hard"],
        value="Medium"
    )
    
    num_questions = st.slider(
        "Number of Quiz Questions",
        min_value=1,
        max_value=10,
        value=5
    )
    
    st.divider()
    st.header("📖 History")
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"Session {len(st.session_state.history)-i}", key=f"hist_{i}"):
                st.session_state.current_text = item['text']
                st.rerun()
    else:
        st.caption("No history yet")

# Main content area with tabs
tab1, tab2 = st.tabs(["📝 Study Session", "📊 History Analysis"])

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Input Your Study Material")
        user_text = st.text_area(
            "Paste your notes or textbook paragraph here:",
            height=250,
            placeholder="Example: Photosynthesis is the process by which plants convert sunlight into chemical energy...",
            value=st.session_state.get('current_text', '')
        )
        
        # Clear button for current text
        if st.session_state.get('current_text'):
            if st.button("Clear Current Text"):
                st.session_state.current_text = ''
                st.rerun()
        
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            if st.button("✨ Generate Explanation & Quiz", type="primary", use_container_width=True):
                if not user_text.strip():
                    st.warning("Please paste some text first.")
                else:
                    # Store in history
                    st.session_state.history.append({
                        'text': user_text,
                        'explanation': None,
                        'quiz': None
                    })
                    
                    with st.spinner("🤖 Agent 1: Analyzing and simplifying content..."):
                        explanation_obj = explainer_agent(user_text, level=explanation_level)
                        explanation = explanation_obj["explanation_text"]
                    
                    with st.spinner("🤖 Agent 2: Creating quiz questions..."):
                        quiz = quiz_agent(explanation, difficulty=quiz_difficulty, num_questions=num_questions)
                    
                    # Update history with results
                    st.session_state.history[-1]['explanation'] = explanation
                    st.session_state.history[-1]['quiz'] = quiz
                    
                    st.session_state.last_explanation = explanation
                    st.session_state.last_quiz = quiz
                    st.rerun()
        
        with col1_2:
            if st.button("🔄 Generate New Quiz Only", use_container_width=True):
                if 'last_explanation' in st.session_state:
                    with st.spinner("🤖 Agent 2: Creating new quiz..."):
                        new_quiz = quiz_agent(
                            st.session_state.last_explanation, 
                            difficulty=quiz_difficulty, 
                            num_questions=num_questions
                        )
                    st.session_state.last_quiz = new_quiz
                    st.rerun()
                else:
                    st.warning("Please generate an explanation first.")
    
    with col2:
        st.subheader("📋 Quick Tips")
        st.info("""
        **Best practices:**
        1. Paste 1-3 paragraphs at a time
        2. Include key concepts and definitions
        3. Focus on one topic per session
        4. Use clear, structured text for best results
        """)
        
        st.divider()
        
        st.subheader("📤 Export Results")
        if 'last_explanation' in st.session_state:
            # Create downloadable content
            export_content = f"""AI STUDY BUDDY RESULTS
================================

EXPLANATION:
{st.session_state.last_explanation}

QUIZ:
{st.session_state.last_quiz}
            """
            
            st.download_button(
                label="📥 Download Results",
                data=export_content,
                file_name="study_buddy_results.txt",
                mime="text/plain",
                use_container_width=True
            )

# Display results in an expandable section
if 'last_explanation' in st.session_state:
    st.divider()
    
    # Create tabs for Explanation and Quiz
    exp_tab, quiz_tab = st.tabs(["📖 Explanation", "❓ Quiz"])
    
    with exp_tab:
        st.subheader("Simplified Explanation")
        st.markdown(st.session_state.last_explanation)
        
        # Add feedback for explanation
        col_fb1, col_fb2, col_fb3 = st.columns(3)
        with col_fb1:
            if st.button("👍 Helpful", use_container_width=True):
                st.success("Thanks for your feedback!")
        with col_fb2:
            if st.button("👎 Too Complex", use_container_width=True):
                st.info("Try setting Explanation Level to 'Simple'")
        with col_fb3:
            if st.button("🔁 Regenerate", use_container_width=True):
                with st.spinner("Generating new explanation..."):
                    new_exp = explainer_agent(user_text, level=explanation_level)
                    st.session_state.last_explanation = new_exp["explanation_text"]
                    st.rerun()
    
    with quiz_tab:
        st.subheader("Quiz Questions")
        st.markdown(st.session_state.last_quiz)
        
        # Add quiz interaction
        st.divider()
        st.subheader("Quiz Tools")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("🎲 Shuffle Questions", use_container_width=True):
                with st.spinner("Creating new quiz variation..."):
                    new_quiz = quiz_agent(
                        st.session_state.last_explanation, 
                        difficulty=quiz_difficulty, 
                        num_questions=num_questions
                    )
                    st.session_state.last_quiz = new_quiz
                    st.rerun()
        
        with col_q2:
            if st.button("📝 Show Answer Key", use_container_width=True):
                st.info("Answer key feature coming soon!")

with tab2:
    st.header("Study History Analysis")
    
    if st.session_state.history:
        for i, session in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Session {len(st.session_state.history)-i} - {len(session['text'])} chars"):
                col_h1, col_h2 = st.columns(2)
                
                with col_h1:
                    st.markdown("**Original Text:**")
                    st.caption(session['text'][:200] + "..." if len(session['text']) > 200 else session['text'])
                
                with col_h2:
                    if session['explanation']:
                        st.markdown("**Key Topics Covered:**")
                        # Simple extraction of first few lines from explanation
                        lines = session['explanation'].split('\n')[:3]
                        for line in lines:
                            if line.strip():
                                st.write(f"• {line.strip()}")
        
        # Statistics
        st.divider()
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Total Sessions", len(st.session_state.history))
        with col_stat2:
            avg_length = sum(len(s['text']) for s in st.session_state.history) / len(st.session_state.history)
            st.metric("Avg. Input Length", f"{avg_length:.0f} chars")
        with col_stat3:
            if st.button("Clear History", type="secondary"):
                st.session_state.history = []
                st.rerun()
    else:
        st.info("No study sessions recorded yet. Generate your first explanation and quiz!")

# Footer
st.divider()
st.caption("AI Study Buddy v2.0 • Powered by Two-Agent Learning System")
