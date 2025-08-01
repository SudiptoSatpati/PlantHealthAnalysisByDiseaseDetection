import streamlit as st
import time
from PIL import Image
from utils.prediction import is_leaf, get_disease, get_nutrient_deficiency
from utils.preprocessing import preprocess_image
from utils.gemini import get_remedies

# Page configuration
st.set_page_config(
    page_title="Plant Health Analyzer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for farmer-friendly, plant-themed design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #a8e6cf 0%, #7fcdcd 50%, #81c784 100%);
        min-height: 100vh;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2e7d32, #4caf50, #66bb6a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #2e7d32;
        font-weight: 400;
        margin-bottom: 2rem;
        opacity: 0.9;
        line-height: 1.6;
    }
    
    .hero-description {
        font-size: 1.1rem;
        color: #4a5568;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.8;
    }
    
    /* Upload Section */
    .upload-container {
        max-width: 600px;
        margin: 3rem auto;
        padding: 2rem;
        background: rgba(255,255,255,0.9);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 2px dashed #4caf50;
        transition: all 0.3s ease;
    }
    
    .upload-container:hover {
        border-color: #2e7d32;
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
    }
    
    .upload-text {
        text-align: center;
        color: #2e7d32;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .upload-subtext {
        text-align: center;
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Animation for verification */
    .verification-animation {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        border-radius: 15px;
        margin: 2rem 0;
        animation: slideInUp 0.8s ease-out;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .verification-icon {
        font-size: 3rem;
        color: #2e7d32;
        margin-bottom: 1rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-20px);
        }
        60% {
            transform: translateY(-10px);
        }
    }
    
    /* Result Cards */
    .result-card {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 5px solid #4caf50;
        transition: all 0.3s ease;
        animation: fadeInScale 0.8s ease-out;
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .result-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2e7d32;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .result-content {
        font-size: 1.1rem;
        color: #4a5568;
        line-height: 1.6;
        background: #f1f8e9;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #c8e6c9;
    }
    
    .disease-card {
        border-left-color: #ff7043;
        background: linear-gradient(135deg, rgba(255,112,67,0.1) 0%, rgba(255,255,255,0.95) 100%);
    }
    
    .nutrient-card {
        border-left-color: #ffa726;
        background: linear-gradient(135deg, rgba(255,167,38,0.1) 0%, rgba(255,255,255,0.95) 100%);
    }
    
    .remedy-card {
        border-left-color: #66bb6a;
        background: linear-gradient(135deg, rgba(102,187,106,0.1) 0%, rgba(255,255,255,0.95) 100%);
        animation: remedyAppear 1.2s ease-out;
    }
    
    @keyframes remedyAppear {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Image display */
    .image-container {
        text-align: center;
        margin: 2rem 0;
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .leaf-image {
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        max-width: 100%;
        height: auto;
        border: 3px solid #4caf50;
    }
    
    /* Spinner styling */
    .analysis-spinner {
        text-align: center;
        padding: 2rem;
        color: #2e7d32;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .sidebar-section {
        background: rgba(255,255,255,0.9);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid #c8e6c9;
    }
    
    .sidebar-title {
        color: #2e7d32;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .hero-section {
            padding: 2rem 1rem;
        }
        
        .upload-container {
            margin: 2rem 1rem;
        }
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        color: #2e7d32;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Auto-scroll functionality */
    .scroll-target {
        scroll-margin-top: 20px;
    }
</style>

<script>
    // Auto-scroll function
    function scrollToElement(elementId, delay = 500) {
        setTimeout(() => {
            const element = document.getElementById(elementId);
            if (element) {
                element.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest'
                });
            }
        }, delay);
    }
    
    // Function to scroll to verification section
    function scrollToVerification() {
        scrollToElement('verification-section', 800);
    }
    
    // Function to scroll to results section
    function scrollToResults() {
        scrollToElement('results-section', 1000);
    }
    
    // Function to scroll to remedies section
    function scrollToRemedies() {
        scrollToElement('remedies-section', 1500);
    }
</script>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>🌱 Plant Health Lab</h2>
        <p>Your AI-powered farming assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">📋 How It Works</div>
        <p>1. <strong>Upload</strong> - Take a clear photo of your plant leaf</p>
        <p>2. <strong>Analyze</strong> - Our AI examines the leaf health</p>
        <p>3. <strong>Diagnose</strong> - Get disease and nutrient insights</p>
        <p>4. <strong>Treat</strong> - Follow personalized care recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">🔬 What We Detect</div>
        <p>• <strong>Plant Diseases</strong> - Common leaf infections and fungi</p>
        <p>• <strong>Nutrient Issues</strong> - Deficiencies affecting plant health</p>
        <p>• <strong>Growth Problems</strong> - Environmental stress indicators</p>
        <p>• <strong>Care Solutions</strong> - Targeted treatment recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">📸 Photo Tips</div>
        <p>• Use natural daylight for best results</p>
        <p>• Ensure the leaf fills most of the frame</p>
        <p>• Avoid shadows and reflections</p>
        <p>• Choose leaves showing clear symptoms</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">🌾 Supported Plants</div>
        <p>• Coffee</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">🌿 Plant Health Analyzer</h1>
    <p class="hero-subtitle">Advanced AI-powered leaf diagnosis for healthier crops</p>
    <p class="hero-description">
        Transform your farming with intelligent plant health monitoring. Upload a leaf photo and get instant 
        disease detection, nutrient analysis, and expert treatment recommendations powered by cutting-edge AI.
    </p>
</div>
""", unsafe_allow_html=True)

# Upload Section
st.markdown("""
<div class="upload-container">
    <div class="upload-text">📸 Upload Your Plant Leaf</div>
    <div class="upload-subtext">Supported formats: JPG, JPEG, PNG • Maximum size: 200MB</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a leaf image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear, well-lit image of your plant leaf for analysis",
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

# Processing and Results
if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(image, caption="🍃 Your Plant Leaf", use_column_width=True, output_format="auto")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Verification process
    with st.spinner("🔍 Verifying leaf image..."):
        time.sleep(1)  # Small delay for better UX
        img_cv = preprocess_image(image)
    
    # Check if it's a leaf
    if is_leaf(img_cv) == 0:
        st.markdown("""
        <div class="result-card" style="border-left-color: #f44336; background: linear-gradient(135deg, rgba(244,67,54,0.1) 0%, rgba(255,255,255,0.95) 100%);">
            <div class="result-title" style="color: #c62828;">
                ❌ Image Verification Failed
            </div>
            <div class="result-content" style="background: #ffebee; border-color: #ffcdd2;">
                This doesn't appear to be a plant leaf. Please upload a clear image of a leaf showing the surface details and any symptoms you're concerned about.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Verification successful - show animation
        st.markdown("""
        <div class="verification-animation scroll-target" id="verification-section">
            <div class="verification-icon">✅</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #2e7d32; margin-bottom: 0.5rem;">
                Leaf Verified Successfully!
            </div>
            <div style="color: #4a5568; font-size: 1rem;">
                Your plant leaf has been validated and is ready for comprehensive health analysis.
            </div>
        </div>
        <script>scrollToVerification();</script>
        """, unsafe_allow_html=True)
        
        # Analysis process
        with st.spinner("🧬 Analyzing plant health patterns..."):
            time.sleep(2)  # Simulate analysis time
            disease = get_disease(img_cv)
        
        with st.spinner("🌱 Evaluating nutrient levels..."):
            time.sleep(1.5)
            deficiency = get_nutrient_deficiency(img_cv)
        
        # Display results
        st.markdown('<div class="scroll-target" id="results-section"></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="result-card disease-card">
                <div class="result-title" style="color: #d84315;">
                    🦠 Disease Analysis
                </div>
                <div class="result-content" style="background: #fff3e0; border-color: #ffcc02;">
                    <strong>Diagnosis:</strong> {disease}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="result-card nutrient-card">
                <div class="result-title" style="color: #ef6c00;">
                    🌱 Nutrient Assessment
                </div>
                <div class="result-content" style="background: #fff8e1; border-color: #ffecb3;">
                    <strong>Status:</strong> {deficiency}
                </div>
            </div>
            <script>scrollToResults();</script>
            """, unsafe_allow_html=True)
        
        # AI Remedies Section
        st.markdown("---")
        st.markdown('<div class="scroll-target" id="remedies-section"></div>', unsafe_allow_html=True)
        st.markdown("### 💡 Expert Treatment Recommendations")
        
        with st.spinner("🤖 Generating personalized treatment plan..."):
            time.sleep(2)
            try:
                remedies = get_remedies(disease, deficiency)
                
                st.markdown(f"""
                <div class="result-card remedy-card">
                    <div class="result-title" style="color: #388e3c;">
                        🎯 Personalized Care Plan
                    </div>
                    <div class="result-content">
                        {remedies}
                    </div>
                </div>
                <script>scrollToRemedies();</script>
                """, unsafe_allow_html=True)
                
                # Success message
                st.markdown("""
                <div class="success-message">
                    🌟 Analysis Complete! Follow the recommendations above for optimal plant health.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown("""
                <div class="result-card" style="border-left-color: #f44336;">
                    <div class="result-title" style="color: #c62828;">
                        ⚠️ Remedy Service Unavailable
                    </div>
                    <div class="result-content" style="background: #ffebee; border-color: #ffcdd2;">
                        Unable to generate treatment recommendations at this time. Please try again later or consult with a local agricultural expert.
                    </div>
                </div>
                """, unsafe_allow_html=True)