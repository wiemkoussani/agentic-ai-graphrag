# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment
Create a `.env` file in the project root:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
GROQ_API_KEY=your_groq_key_here
```

### Step 3: Start Neo4j
Make sure Neo4j is running. You can:
- Use Neo4j Desktop
- Use Neo4j Aura (cloud)
- Use Docker: `docker run -p 7474:7474 -p 7687:7687 neo4j:latest`

### Step 4: Initialize the Graph
```bash
python scripts/setup_graph.py
```

This will:
- Create the graph schema
- Load sample data (companies, people, technologies)
- Generate embeddings for all nodes

### Step 5: Start the Streamlit App
```bash
streamlit run app.py
```

You should see:
```
✅ Connected to Neo4j at bolt://localhost:7687
✅ Agentic AI system initialized
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

The app will open automatically in your browser!

## 🧪 Test the System

### Try These Queries:
1. **Graph Query**: "Who acted in Inception?"
2. **Director Query**: "What films did Christopher Nolan direct?"
3. **Calculation**: "Calculate 25 * 17 + 100"
4. **Complex**: "What genres does Breaking Bad belong to and who acted in it?"

### Run Test Scenarios:
```bash
python tests/test_scenarios.py
```

## 📊 Verify Graph Setup

Check the graph info:
```bash
curl http://localhost:8000/graph-info
```

Or visit: `http://localhost:8000/graph-info` in your browser

## 🔧 Troubleshooting

### Neo4j Connection Issues
- Verify Neo4j is running: `neo4j status`
- Check connection string in `.env`
- Verify credentials

### Groq API Issues
- Check your API key is valid
- Ensure you have credits/quota
- Get your key from https://console.groq.com/
- Try a different model in `agent/agent.py` (line 22)

### Import Errors
- Make sure you're in the project root directory
- Verify all packages installed: `pip list | grep langchain`
- Try: `pip install -r requirements.txt --upgrade`

### Streamlit Issues
- Make sure Streamlit is installed: `pip install streamlit`
- Check if port 8501 is available
- Try: `streamlit run app.py --server.port 8502`

## 📝 Next Steps

1. **Customize the Graph**: Edit `scripts/setup_graph.py` to add your own data
2. **Add More Tools**: Extend `agent/tools.py` with new capabilities
3. **Improve Prompts**: Modify system messages in `agent/agent.py`
4. **Enhance UI**: Customize `app.py` and add custom CSS in the Streamlit app

## 🎥 Demo Video Checklist

When creating your demo video, show:
- [ ] System architecture overview
- [ ] Neo4j graph visualization
- [ ] Agent workflow in action
- [ ] Tool selection and execution
- [ ] GraphRAG retrieval process
- [ ] End-to-end query processing
- [ ] Web UI interaction
- [ ] Test scenarios execution

## 📚 Learn More

- [Architecture Documentation](./docs/architecture.md)
- [API Documentation](./README.md#-api-endpoints)
- [Test Scenarios](./tests/test_scenarios.py)

