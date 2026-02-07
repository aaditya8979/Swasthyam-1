# Swasthyam - Complete Implementation Guide

## 🎯 Project Overview

Swasthyam is a comprehensive, community-driven health companion designed for expecting mothers, parents, and health-conscious individuals. It combines context-aware AI assistance with community support and detailed health tracking.

### Key Features
- **Context-Aware RAG Chatbot**: Personalized health advice using OpenAI API with user profile context
- **Community Forum**: Real-time discussions with likes, comments, and moderation
- **Child Health Tracker**: Vaccine schedules, growth monitoring, medication tracking
- **Health Calculators**: BMI, nutrition, and other health metrics
- **Multi-language Support**: Full Hindi/English localization
- **Dark Mode**: Creative theme switching with smooth transitions
- **Mobile Responsive**: Optimized for all device sizes

---

## 📁 Project Structure


---

## 🚀 Installation Instructions

### 1. Prerequisites
```bash
# Python 3.8+
python --version

# pip package manager
pip --version
```
2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```
3. Install Dependencies

# Create requirements.txt
```bash
cat > requirements.txt << EOF
Django==4.2.7
Pillow==10.1.0
openai==1.3.0
python-dotenv==1.0.0
EOF

# Install
pip install -r requirements.txt
```

4. Environment Variables
```bash
# Create .env file in project root
cat > .env << EOF
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
OPENAI_API_KEY=your-openai-api-key-here
EOF
```

5. Run Development Server - 
```bash
python manage.py runserver
```

Visit: http://localhost:8000
