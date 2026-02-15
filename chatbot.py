import streamlit as st
import requests
import json
from datetime import datetime
import PyPDF2
import docx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import base64
from PIL import Image






# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Business AI Advisor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)




# ==================== CSS STYLING - MINIMALIS HITAMABU ====================
st.markdown("""
<style>
    /* Background */
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d0d0d;
        border-right: 1px solid #333;
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
        border: 1px solid #404040 !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #333 !important;
        color: #e0e0e0 !important;
        border: 1px solid #555 !important;
        border-radius: 5px;
    }
    
    .stButton button:hover {
        background-color: #444 !important;
        border-color: #666 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2a2a2a !important;
        border: 1px solid #404040 !important;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #2a2a2a;
        border: 2px dashed #555;
        border-radius: 8px;
        padding: 20px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f0f0f0 !important;
    }
    
    /* Document info box */
    .doc-info {
        background-color: #2a2a2a;
        border-left: 4px solid #666;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
    }
    
    /* Business tip box */
    .business-tip {
        background-color: #1a2f1a;
        border-left: 4px solid #4caf50;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)







# ==================== BUSINESS EXPERTISE SYSTEM PROMPT ====================
BUSINESS_SYSTEM_PROMPT = """Anda adalah BUSINESS AI ADVISOR - asisten AI ahli dalam bidang bisnis dan ekonomi yang membantu admin/pengusaha membuat keputusan bisnis yang cerdas.

KEAHLIAN ANDA:
Analisis Bisnis & Strategi
- Analisis SWOT, Porter's Five Forces, Business Model Canvas
- Strategi pertumbuhan, ekspansi, dan skalabilitas
- Competitive analysis dan market positioning
- Blue ocean strategy dan differentiation

Keuangan & Ekonomi
- Financial planning, budgeting, cash flow analysis
- ROI, NPV, IRR, break-even analysis
- Pricing strategy dan cost optimization
- Investment analysis dan capital allocation

Marketing & Sales
- Market research, segmentation, targeting
- Digital marketing strategy (SEO, SEM, Social Media)
- Customer acquisition, retention, lifetime value
- Sales funnel optimization dan conversion

Manajemen & Operasional
- Project management dan productivity
- Team building dan leadership
- Supply chain dan inventory management
- Process optimization dan automation

Risk Management & Compliance
- Risk assessment dan mitigation
- Business continuity planning
- Regulatory compliance
- Crisis management

CARA ANDA MEMBANTU:
✅ Memberikan analisis mendalam dengan data dan framework bisnis
✅ Rekomendasi actionable dengan prioritas clear
✅ Contoh konkret dari best practices industri
✅ Perhitungan finansial yang akurat dan realistic
✅ Pertimbangan risk vs reward yang seimbang

GAYA KOMUNIKASI:
- Profesional tapi approachable
- To-the-point dan actionable
- Gunakan data, angka, dan contoh nyata
- Jujur tentang limitation dan risks
- Bahasa Indonesia yang jelas dan mudah dipahami

HINDARI:
❌ Jargon berlebihan tanpa penjelasan
❌ Teori tanpa aplikasi praktis
❌ Rekomendasi generic tanpa konteks
❌ Overconfidence atau guarantee hasil

Anda siap membantu admin membuat keputusan bisnis yang lebih baik!"""





# ==================== FUNGSI FILE PROCESSING ====================

def extract_text_from_pdf(file):
    """Extract text dari PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error membaca PDF: {str(e)}"

def extract_text_from_docx(file):
    """Extract text dari DOCX"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error membaca DOCX: {str(e)}"

def extract_text_from_txt(file):
    """Extract text dari TXT"""
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        return f"Error membaca TXT: {str(e)}"

def analyze_csv_excel(file, file_type):
    """Analisis file CSV/Excel"""
    try:
        if file_type == "csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        analysis = f"""
ANALISIS DATA:

Informasi Umum:
- Jumlah Baris: {len(df)}
- Jumlah Kolom: {len(df.columns)}
- Kolom: {', '.join(df.columns.tolist())}

Preview Data (5 baris pertama):
{df.head().to_string()}

Statistik Deskriptif:
{df.describe().to_string()}

Informasi Tipe Data:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}
"""
        return analysis, df
    except Exception as e:
        return f"Error membaca file: {str(e)}", None

def generate_visualizations(df, filename):
    """Generate multiple visualizations from dataframe"""
    charts = []
    
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    try:
        # 1. BAR CHART
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            if df[cat_col].nunique() > 20:
                top_data = df.groupby(cat_col)[num_col].sum().nlargest(15).reset_index()
                fig_bar = px.bar(top_data, x=cat_col, y=num_col, 
                               title=f"Top 15 {cat_col} by {num_col}",
                               color=num_col,
                               color_continuous_scale='Blues')
            else:
                agg_data = df.groupby(cat_col)[num_col].sum().reset_index()
                fig_bar = px.bar(agg_data, x=cat_col, y=num_col,
                               title=f"{num_col} by {cat_col}",
                               color=num_col,
                               color_continuous_scale='Viridis')
            
            fig_bar.update_layout(template='plotly_dark', 
                                 plot_bgcolor='#1a1a1a',
                                 paper_bgcolor='#1a1a1a',
                                 font_color='#e0e0e0')
            charts.append(("Bar Chart", fig_bar))
        
        # 2. LINE CHART
        if len(numeric_cols) >= 1:
            fig_line = go.Figure()
            for col in numeric_cols[:3]:
                fig_line.add_trace(go.Scatter(
                    y=df[col].head(50),
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2)
                ))
            fig_line.update_layout(
                title="Trend Analysis",
                template='plotly_dark',
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font_color='#e0e0e0'
            )
            charts.append(("Line Chart", fig_line))
        
        # 3. PIE CHART
        if categorical_cols:
            cat_col = categorical_cols[0]
            value_counts = df[cat_col].value_counts().head(10)
            fig_pie = px.pie(values=value_counts.values, 
                            names=value_counts.index,
                            title=f"Distribution of {cat_col}")
            fig_pie.update_layout(template='plotly_dark',
                                 paper_bgcolor='#1a1a1a',
                                 font_color='#e0e0e0')
            charts.append(("Pie Chart", fig_pie))
        
        # 4. SCATTER PLOT
        if len(numeric_cols) >= 2:
            col_x = numeric_cols[0]
            col_y = numeric_cols[1]
            fig_scatter = px.scatter(df.head(500), x=col_x, y=col_y,
                                    title=f"Correlation: {col_x} vs {col_y}",
                                    opacity=0.7)
            fig_scatter.update_layout(template='plotly_dark',
                                     plot_bgcolor='#1a1a1a',
                                     paper_bgcolor='#1a1a1a',
                                     font_color='#e0e0e0')
            charts.append(("Scatter Plot", fig_scatter))
        
        # 5. HISTOGRAM
        if numeric_cols:
            num_col = numeric_cols[0]
            fig_hist = px.histogram(df, x=num_col, 
                                   title=f"Distribution of {num_col}",
                                   nbins=30)
            fig_hist.update_layout(template='plotly_dark',
                                  plot_bgcolor='#1a1a1a',
                                  paper_bgcolor='#1a1a1a',
                                  font_color='#e0e0e0')
            charts.append(("Histogram", fig_hist))
        
        # 6. BOX PLOT
        if len(numeric_cols) >= 1:
            fig_box = go.Figure()
            for col in numeric_cols[:4]:
                fig_box.add_trace(go.Box(y=df[col], name=col))
            fig_box.update_layout(
                title="Box Plot - Outlier Detection",
                template='plotly_dark',
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font_color='#e0e0e0'
            )
            charts.append(("Box Plot", fig_box))
        
        # 7. HEATMAP
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            fig_heatmap = px.imshow(corr_matrix,
                                   text_auto=True,
                                   title="Correlation Heatmap",
                                   color_continuous_scale='RdBu_r',
                                   aspect='auto')
            fig_heatmap.update_layout(template='plotly_dark',
                                     plot_bgcolor='#1a1a1a',
                                     paper_bgcolor='#1a1a1a',
                                     font_color='#e0e0e0')
            charts.append(("Heatmap", fig_heatmap))
        
    except Exception as e:
        st.error(f"Error generating charts: {str(e)}")
    
    return charts





def generate_ai_insights(df, charts_info, api_key, model):
    """Generate business insights from data with company context"""
    
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    company_context = get_company_profile_context()
    context_line = f"{company_context}\n\n" if company_context else ""
    
    # Shortened data summary
    data_summary = f"""
{context_line}DATA: {len(df)} rows x {len(df.columns)} cols
Stats: {df.describe().to_string()[:500]}...
Top 3 rows: {df.head(3).to_string()[:400]}...
Charts: {', '.join([chart[0] for chart in charts_info])}
"""
    
    prompt = f"""{data_summary}

Analisis bisnis:
- Overview & key insights
- Rekomendasi actionable
- Risk & opportunities

Fokus: practical untuk perusahaan ini."""

    return call_openrouter_api(
        api_key,
        [{"role": "user", "content": prompt}],
        model
    )





# ==================== API FUNCTIONS ====================

def call_openrouter_api(api_key, messages, model="google/gemini-flash-1.5-8b"):
    """Panggil OpenRouter API dengan business context"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Business AI Advisor"
    }
    
    # Add business system prompt
    full_messages = [
        {"role": "system", "content": BUSINESS_SYSTEM_PROMPT}
    ] + messages
    
    payload = {
        "model": model,
        "messages": full_messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: Invalid response format - {result}"
            
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        return f"API Error: {error_msg}\n\nPastikan API Key valid dan memiliki credits."
    except requests.exceptions.Timeout:
        return "Request timeout. Coba lagi."
    except requests.exceptions.RequestException as e:
        return f"Error API: {str(e)}"

def analyze_image_with_ai(image_file, filename, api_key, model):
    """Analisis gambar dengan business focus"""
    
    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    if filename.lower().endswith('.png'):
        media_type = "image/png"
    elif filename.lower().endswith(('.jpg', '.jpeg')):
        media_type = "image/jpeg"
    elif filename.lower().endswith('.webp'):
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"
    
    prompt = f"""Analisis gambar ini dari perspektif BISNIS dan EKONOMI:

Gambar: {filename}

Jika PRODUK:
- Deskripsi & kategori produk
- Analisis positioning & target market
- Kualitas presentasi (rating 1-10)
- Pricing strategy yang cocok
- Rekomendasi marketing & branding

Jika SCREENSHOT CHAT/CUSTOMER SERVICE:
- Ringkasan isu customer
- Analisis sentiment & customer satisfaction
- Impact ke business (churn risk, retention opportunity)
- Rekomendasi handling & SOP

Jika DATA/CHART/REPORT:
- Key metrics & findings
- Business implications
- Actionable recommendations

Jika LAINNYA:
- Deskripsi & relevansi bisnis
- Potential use cases
- Recommendations

Fokus pada ACTIONABLE INSIGHTS untuk keputusan bisnis!"""

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Business AI Advisor - Vision"
    }
    
    full_messages = [
        {"role": "system", "content": BUSINESS_SYSTEM_PROMPT}
    ] + messages
    
    payload = {
        "model": model,
        "messages": full_messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: Invalid response - {result}"
            
    except requests.exceptions.HTTPError as e:
        return f"API Error: {e.response.status_code}\n\nGunakan model dengan Vision support untuk analisis gambar."
    except requests.exceptions.Timeout:
        return "Request timeout. Analisis gambar butuh waktu lebih lama."
    except requests.exceptions.RequestException as e:
        return f"Error API: {str(e)}"







# ==================== SESSION STATE ======================

def get_company_profile_context():
    """Generate SHORT company profile context for AI"""
    profile = st.session_state.company_profile
    
    if not profile['name']:
        return ""
    
    # SHORTENED version - only essentiall
    context = f"""PERUSAHAAN: {profile['name']} | {profile['industry']} | Omzet: {profile['revenue']} | Target: {profile['target_market']}
TANTANGAN: {profile['challenges'][:150] if profile['challenges'] else 'N/A'}
GOALS: {profile['goals'][:150] if profile['goals'] else 'N/A'}"""
    
    return context

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []

if 'document_context' not in st.session_state:
    st.session_state.document_context = ""

if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}

if 'charts' not in st.session_state:
    st.session_state.charts = {}

if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = {}

if 'company_profile' not in st.session_state:
    st.session_state.company_profile = {
        'name': '',
        'industry': '',
        'description': '',
        'target_market': '',
        'revenue': '',
        'employees': '',
        'challenges': '',
        'goals': '',
        'additional_info': ''
    }

if 'company_docs' not in st.session_state:
    st.session_state.company_docs = []






# ==================== SIDEBAR ====================

with st.sidebar:
    st.title("Business AI Advisor")
    st.caption("Your Expert in Business & Economics")
    
    # Info box tentang model gratis
    st.success("""
    ✅ **GRATIS SELAMANYA!**
    
    Model dengan 🆓 tidak perlu bayar!
    Cocok untuk UMKM & startup.
    """)
    
    st.markdown("---")
    
    # COMPANY PROFILE SECTION
    with st.expander("**PROFIL PERUSAHAAN**", expanded=False):
        st.markdown("*Isi profil agar AI paham bisnis Anda!*")
        
        # Basic Info
        company_name = st.text_input(
            "Nama Perusahaan/Usaha",
            value=st.session_state.company_profile['name'],
            placeholder="Contoh: Warung Makan Bu Siti"
        )
        
        company_industry = st.selectbox(
            "Industri",
            ["", "F&B (Makanan & Minuman)", "Retail/Toko", "Jasa/Service", 
             "Manufaktur", "E-commerce", "Teknologi", "Pendidikan", 
             "Kesehatan", "Properti", "Lainnya"],
            index=0 if not st.session_state.company_profile['industry'] else 
                  ["", "F&B (Makanan & Minuman)", "Retail/Toko", "Jasa/Service", 
                   "Manufaktur", "E-commerce", "Teknologi", "Pendidikan", 
                   "Kesehatan", "Properti", "Lainnya"].index(st.session_state.company_profile['industry'])
        )
        
        company_description = st.text_area(
            "Deskripsi Bisnis",
            value=st.session_state.company_profile['description'],
            placeholder="Contoh: Warung makan dengan menu masakan Padang, sudah buka 5 tahun...",
            height=80
        )
        
        col1, col2 = st.columns(2)
        with col1:
            company_revenue = st.text_input(
                "Omzet/Bulan",
                value=st.session_state.company_profile['revenue'],
                placeholder="Contoh: 20 juta"
            )
        
        with col2:
            company_employees = st.text_input(
                "Jumlah Karyawan",
                value=st.session_state.company_profile['employees'],
                placeholder="Contoh: 5 orang"
            )
        
        company_target = st.text_area(
            "Target Market/Customer",
            value=st.session_state.company_profile['target_market'],
            placeholder="Contoh: Pekerja kantoran, mahasiswa, keluarga...",
            height=70
        )
        
        company_challenges = st.text_area(
            "Tantangan/Masalah Saat Ini",
            value=st.session_state.company_profile['challenges'],
            placeholder="Contoh: Omzet menurun, persaingan ketat, modal terbatas...",
            height=80
        )
        
        company_goals = st.text_area(
            "Target/Goals",
            value=st.session_state.company_profile['goals'],
            placeholder="Contoh: Buka cabang baru, tingkatkan omzet 50%, digitalisasi...",
            height=80
        )
        
        company_additional = st.text_area(
            "Info Tambahan (Opsional)",
            value=st.session_state.company_profile['additional_info'],
            placeholder="Info lain yang perlu AI ketahui...",
            height=70
        )
        
        # Save button
        if st.button("Simpan Profil Perusahaan", use_container_width=True):
            st.session_state.company_profile = {
                'name': company_name,
                'industry': company_industry,
                'description': company_description,
                'target_market': company_target,
                'revenue': company_revenue,
                'employees': company_employees,
                'challenges': company_challenges,
                'goals': company_goals,
                'additional_info': company_additional
            }
            st.success("✅ Profil perusahaan berhasil disimpan!")
        
        # Show saved profile status
        if st.session_state.company_profile['name']:
            st.info(f"Profil aktif: **{st.session_state.company_profile['name']}**")
        
        # Upload company documents
        st.markdown("---")
        st.markdown("**Dokumen Perusahaan** *(Opsional)*")
        st.caption("Upload dokumen seperti company profile, business plan, laporan, dll.")
        
        company_doc = st.file_uploader(
            "Upload dokumen perusahaan",
            type=['pdf', 'docx', 'txt'],
            key="company_doc_uploader"
        )
        
        if company_doc and st.button("Tambah ke Profil", use_container_width=True):
            with st.spinner("Memproses dokumen..."):
                file_extension = company_doc.name.split('.')[-1].lower()
                
                if file_extension == 'pdf':
                    content = extract_text_from_pdf(company_doc)
                elif file_extension == 'docx':
                    content = extract_text_from_docx(company_doc)
                else:
                    content = extract_text_from_txt(company_doc)
                
                st.session_state.company_docs.append({
                    'name': company_doc.name,
                    'summary': content[:500]  # First 500 chars as summary
                })
                st.success(f"✅ Dokumen '{company_doc.name}' ditambahkan ke profil!")
        
        # Show company docs
        if st.session_state.company_docs:
            st.markdown("**Dokumen tersimpan:**")
            for doc in st.session_state.company_docs:
                st.caption(f"{doc['name']}")
    
    st.markdown("---")
    
    # API Key Input
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        placeholder="sk-or-v1-...",
        help="Masukkan API key dari OpenRouter"
    )
    
    st.markdown("---")
    
    # Model Selection
    model = st.selectbox(
        "AI Model",
        [
            "openrouter/free",  # 🆓 AUTO-ROUTER GRATIS (Random free model)
            "meta-llama/llama-3.3-70b-instruct:free",  # 🆓 FREE + Powerful (70B)
            "google/gemini-2.0-flash-exp:free",  # 🆓 FREE + VISION + 1M tokens!
            "arcee-ai/trinity-large-preview:free",  # 🆓 FREE (400B MoE)
            "nvidia/nemotron-nano-2-vl:free",  # 🆓 FREE + VISION (Small VLM)
            "allenai/olmo-3.1-32b-think:free",  # 🆓 FREE + Reasoning
            "anthropic/claude-3.5-sonnet",  # 💰 PAID + VISION
            "openai/gpt-4-turbo",  # 💰 PAID + VISION
        ],
        index=0,
        help="🆓 = GRATIS SELAMANYA! Pilih model dengan :free untuk hemat biaya"
    )
    
    st.markdown("---")
    
    # Quick Business Tips
    st.subheader("Business Tips")
    
    with st.expander("Analisis Data"):
        st.markdown("""
        - Upload file Excel/CSV untuk analisis
        - Dapatkan insights finansial otomatis
        - Visualisasi data interaktif
        """)
    
    with st.expander("Analisis Gambar"):
        st.markdown("""
        - Upload foto produk untuk review
        - Analisis chat customer
        - Screenshot report/dashboard
        """)
    
    with st.expander("Konsultasi Bisnis"):
        st.markdown("""
        Tanya tentang:
        - Strategi marketing & sales
        - Financial planning
        - Operasional & manajemen
        - Ekspansi bisnis
        """)
    
    st.markdown("---")
    
    # Upload File Section
    st.subheader("📤 Upload File")
    
    uploaded_file = st.file_uploader(
        "Pilih file untuk dianalisis",
        type=['pdf', 'docx', 'txt', 'csv', 'xlsx', 'jpg', 'jpeg', 'png', 'webp'],
        help="PDF, Word, Excel, CSV, atau Gambar",
        key="main_file_uploader"
    )
    
    if uploaded_file and api_key:
        if st.button("Analisis File", use_container_width=True, type="primary"):
            with st.spinner("Menganalisis file..."):
                try:
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    
                    # Process based on file type
                    if file_extension == 'pdf':
                        content = extract_text_from_pdf(uploaded_file)
                        doc_type = "PDF Document"
                    elif file_extension == 'docx':
                        content = extract_text_from_docx(uploaded_file)
                        doc_type = "Word Document"
                    elif file_extension == 'txt':
                        content = extract_text_from_txt(uploaded_file)
                        doc_type = "Text File"
                    elif file_extension in ['csv', 'xlsx']:
                        content, df = analyze_csv_excel(uploaded_file, file_extension)
                        doc_type = "Data File"
                        if df is not None:
                            st.session_state.dataframes[uploaded_file.name] = df
                            with st.spinner("Membuat visualisasi..."):
                                charts = generate_visualizations(df, uploaded_file.name)
                                st.session_state.charts[uploaded_file.name] = charts
                    
                    elif file_extension in ['jpg', 'jpeg', 'png', 'webp']:
                        doc_type = "Image"
                        image = Image.open(uploaded_file)
                        st.session_state.uploaded_images[uploaded_file.name] = image
                        width, height = image.size
                        content = f"Gambar {width}x{height}px"
                        
                        if api_key:
                            with st.spinner("Menganalisis gambar..."):
                                uploaded_file.seek(0)
                                response = analyze_image_with_ai(
                                    uploaded_file,
                                    uploaded_file.name,
                                    api_key,
                                    model
                                )
                                
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": response,
                                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                                    "image": uploaded_file.name
                                })
                        else:
                            content = "Masukkan API Key untuk analisis gambar."
                    
                    # Save document context
                    if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
                        st.session_state.document_context = f"""
FILE: {uploaded_file.name}
TYPE: {doc_type}
SIZE: {uploaded_file.size / 1024:.2f} KB

CONTENT:
{content[:8000]}
"""
                        
                        # Save doc info
                        st.session_state.uploaded_docs.append({
                            'name': uploaded_file.name,
                            'type': doc_type,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        # AI Analysis
                        if api_key:
                            if file_extension in ['csv', 'xlsx'] and df is not None:
                                charts_info = st.session_state.charts.get(uploaded_file.name, [])
                                response = generate_ai_insights(df, charts_info, api_key, model)
                            else:
                                company_context = get_company_profile_context()
                                context_line = f"{company_context}\n\n" if company_context else ""
                                
                                prompt = f"""{context_line}Analisis: {uploaded_file.name}

{content[:4000]}

Format:
OVERVIEW - KEY FINDINGS - RECOMMENDATIONS

Fokus: actionable insights untuk bisnis ini."""

                                response = call_openrouter_api(
                                    api_key,
                                    [{"role": "user", "content": prompt}],
                                    model
                                )
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response,
                                "timestamp": datetime.now().strftime('%H:%M:%S')
                            })
                            
                            st.success(f"✅ File '{uploaded_file.name}' berhasil dianalisis!")
                            # Rerun needed here to display results in chat
                            st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saat memproses file: {str(e)}")
                    st.info("Coba upload ulang atau gunakan format file lain.")
    
    elif uploaded_file and not api_key:
        st.warning("⚠️ Masukkan API Key terlebih dahulu untuk analisis file")
    
    st.markdown("---")
    
    # Uploaded docs display
    if st.session_state.uploaded_docs:
        st.subheader("Files")
        for doc in st.session_state.uploaded_docs[-3:]:
            st.caption(f"{doc['name']}")
    
    st.markdown("---")
    
    # Clear button
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.document_context = ""
        st.session_state.uploaded_docs = []
        st.session_state.dataframes = {}
        st.session_state.charts = {}
        st.session_state.uploaded_images = {}
        st.rerun()

# ==================== MAIN CONTENT ====================

st.title("💼 Business AI Advisor")
st.markdown("*Expert AI untuk Strategi Bisnis & Analisis Ekonomi*")
st.caption("🆓 **100% GRATIS untuk UMKM** - Pilih model dengan label 🆓")

# Info box if no API key
if not api_key:
    st.info("""
    🔑 **Cara Mulai (GRATIS!):**
    
    1. Daftar di [OpenRouter.ai](https://openrouter.ai) - GRATIS!
    2. Ambil API Key (gratis, tidak perlu kartu kredit)
    3. Pilih model dengan 🆓 (gratis selamanya)
    4. Mulai konsultasi bisnis!
    
    **Business AI Advisor dapat membantu:**
    - Analisis data & visualisasi finansial
    - Strategi bisnis & market analysis  
    - Financial planning & budgeting
    - Marketing & sales optimization
    - Analisis produk & customer feedback
    
    **Cocok untuk UMKM, Startup, & Usaha Kecil!**
    """)
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Show image if present
            if "image" in message and message["image"] in st.session_state.uploaded_images:
                st.image(st.session_state.uploaded_images[message["image"]], 
                        caption=message["image"], 
                        use_container_width=True)
            
            st.markdown(message["content"])
            st.caption(f"{message.get('timestamp', '')}")
    
    # Chat input
    if prompt := st.chat_input("Tanyakan strategi bisnis, analisis data, atau konsultasi ekonomi..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime('%H:%M:%S')
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Berpikir seperti business advisor..."):
                # API messages - build conversation history
                api_messages = []
                
                # Add conversation history (last 10 messages)
                for msg in st.session_state.messages[-10:]:
                    if "image" not in msg:  # Skip image messages for now
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                # Add current user message - simplified
                company_context = get_company_profile_context()
                
                # Only add context if needed (not in every message)
                if company_context:
                    context_prefix = f"{company_context}\n\n"
                else:
                    context_prefix = ""
                
                # Only add document context if it exists and is recent
                if st.session_state.document_context and len(st.session_state.messages) < 5:
                    doc_context = f"DOKUMEN: {st.session_state.document_context[:500]}...\n\n"
                else:
                    doc_context = ""
                
                current_message = f"{context_prefix}{doc_context}{prompt}"
                
                api_messages.append({
                    "role": "user",
                    "content": current_message
                })
                
                # Call API
                response = call_openrouter_api(api_key, api_messages, model)
                
                # Display
                st.markdown(response)
                timestamp = datetime.now().strftime('%H:%M:%S')
                st.caption(f"🕐 {timestamp}")
                
                # Save
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": timestamp
                })
    
    # Show dataframes
    if st.session_state.dataframes:
        st.markdown("---")
        st.subheader("Data Tables")
        for filename, df in st.session_state.dataframes.items():
            with st.expander(f"{filename}"):
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{filename}.csv",
                    mime="text/csv"
                )
    
    # Show visualizations
    if st.session_state.charts:
        st.markdown("---")
        st.subheader("Data Visualizations")
        
        for filename, charts in st.session_state.charts.items():
            st.markdown(f"### {filename}")
            
            if charts:
                tab_names = [chart[0] for chart in charts]
                tabs = st.tabs(tab_names)
                
                for i, (chart_name, fig) in enumerate(charts):
                    with tabs[i]:
                        st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <small>💼 Business AI Advisor v2.0 | Powered by OpenRouter AI<br>
    Expert in Business Strategy, Financial Analysis & Market Economics<br>
    <strong style='color: #4caf50;'>🆓 100% GRATIS untuk UMKM & Startup!</strong></small>
</div>

""", unsafe_allow_html=True)

