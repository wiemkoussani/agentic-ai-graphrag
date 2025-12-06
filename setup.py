"""Setup helper script for the Agentic AI system."""
import os
import sys


def check_env_file():
    """Check if .env file exists and create template if not."""
    if not os.path.exists('.env'):
        print("📝 Creating .env file template...")
        env_template = """NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
GROQ_API_KEY=your_groq_api_key_here
"""
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Created .env file. Please update it with your credentials.")
        return False
    else:
        print("✅ .env file exists")
        return True


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'langchain',
        'langchain_groq',
        'langgraph',
        'neo4j',
        'fastapi',
        'sentence_transformers'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True


def main():
    """Main setup function."""
    print("🚀 Agentic AI System Setup")
    print("=" * 50)
    
    env_ok = check_env_file()
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    if env_ok and deps_ok:
        print("✅ Setup complete! You can now:")
        print("   1. Update .env with your credentials")
        print("   2. Run: python scripts/setup_graph.py")
        print("   3. Run: uvicorn main:app --reload")
        print("   4. Open frontend/index.html in your browser")
    else:
        if not env_ok:
            print("⚠️  Please update .env file with your credentials")
        if not deps_ok:
            print("⚠️  Please install missing dependencies")


if __name__ == "__main__":
    main()



