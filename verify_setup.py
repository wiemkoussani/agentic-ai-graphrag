"""Script to verify the setup is correct."""
import os
import sys


def check_files():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'main.py',
        'requirements.txt',
        'README.md',
        'agent/agent.py',
        'agent/tools.py',
        'agent/graphrag.py',
        'neo4j/client.py',
        'neo4j/schema.py',
        'scripts/setup_graph.py',
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("❌ Missing files:")
        for file in missing:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True


def check_env():
    """Check if .env file exists."""
    if os.path.exists('.env'):
        print("✅ .env file exists")
        # Check if it has been configured
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_password_here' in content or 'your_groq_api_key_here' in content:
                print("⚠️  .env file needs to be configured with your credentials")
                return False
            else:
                print("✅ .env file appears to be configured")
                return True
    else:
        print("❌ .env file not found. Run: python setup.py")
        return False


def check_dependencies():
    """Check if key packages can be imported."""
    packages = {
        'langchain': 'langchain',
        'langchain_groq': 'langchain_groq',
        'langgraph': 'langgraph',
        'neo4j': 'neo4j',
        'fastapi': 'fastapi',
        'sentence_transformers': 'sentence_transformers',
    }
    
    missing = []
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages installed")
        return True


def main():
    """Main verification function."""
    print("🔍 Verifying Setup...")
    print("=" * 50)
    
    files_ok = check_files()
    env_ok = check_env()
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    
    if files_ok and env_ok and deps_ok:
        print("✅ Setup verification complete!")
        print("\nNext steps:")
        print("1. Make sure Neo4j is running")
        print("2. Run: python scripts/setup_graph.py")
        print("3. Run: streamlit run app.py")
        print("4. The app will open automatically in your browser")
    else:
        print("⚠️  Some issues found. Please fix them before proceeding.")
        if not files_ok:
            print("   - Fix missing files")
        if not env_ok:
            print("   - Configure .env file")
        if not deps_ok:
            print("   - Install missing packages")


if __name__ == "__main__":
    main()

