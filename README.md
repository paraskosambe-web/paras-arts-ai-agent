# 🤖 Paras Arts AI Data Agent

### AI-Powered Data Analysis & Business Intelligence Agent for Paras Arts

The **Paras Arts AI Data Agent** is an AI-powered data analysis system developed as an intelligent extension of the **Paras Arts** full-stack digital art and custom sketch ordering platform.

The agent connects an AI reasoning layer with approved Paras Arts business data stored in **MongoDB Atlas**, allowing users to ask natural-language questions, analyze website data, generate business insights, and perform a limited set of controlled data updates.

The project combines **Generative AI, Python, FastAPI, MongoDB, data analysis, and controlled tool execution** to create a practical AI agent for a real-world business application.

> 🎨 Related Project: [Paras Arts Website](https://github.com/paraskosambe-web/paras-arts.git)

---

## 📌 Project Overview

Traditional database systems require users to understand database structures and write queries to retrieve information.

This project provides a natural-language interface where a user can ask questions such as:

```text
How many orders are currently pending?
```

```text
What are the most common sketch types?
```

```text
Give me a summary of the current business data.
```

```text
Which artworks are currently featured?
```

```text
Analyze the current order and payment status.
```

The AI agent interprets the user's request, selects the appropriate tool, retrieves the required data, performs the analysis, and returns a human-readable response.

---

# 🎯 Problem Statement

The Paras Arts website contains different types of business data, including:

* Orders
* Payments
* Artworks
* Services
* FAQs
* Testimonials
* Customer messages
* Newsletter subscriptions

Manually checking this information through the database can be time-consuming.

The goal of this project is to provide a controlled AI interface that can:

1. Understand natural-language requests
2. Identify the required data
3. Retrieve relevant information
4. Analyze the data
5. Generate meaningful responses
6. Perform only approved database updates

---

# ✨ Key Features

## 🔎 Natural-Language Data Search

Users can ask questions about Paras Arts data without directly interacting with MongoDB.

Examples:

```text
Show me the pending orders.
```

```text
How many completed orders are there?
```

```text
Find orders for portrait sketches.
```

---

## 📊 Data Analysis

The agent can analyze approved business datasets and generate useful summaries.

Supported analysis areas include:

* Order statistics
* Payment status
* Sketch type distribution
* Budget analysis
* Artwork information
* Service information
* FAQ information
* Business summaries

---

## 🧠 AI-Powered Reasoning

The system uses a Gemini-based generative AI model to interpret user requests and determine which available tools are relevant.

Instead of directly giving the language model unrestricted database access, the agent uses predefined tools for specific operations.

Conceptually:

```text
User Question
      ↓
AI Reasoning
      ↓
Tool Selection
      ↓
Approved Data Operation
      ↓
Data Analysis
      ↓
AI-Generated Response
```

---

# 🛠️ Available Agent Capabilities

The agent currently provides controlled tools for areas such as:

### Orders

* Search orders
* Analyze order status
* Analyze payment status
* Analyze sketch types
* Analyze budgets
* Generate order-related summaries

### Artworks

* Search artwork information
* Analyze artwork data
* Check featured artwork

### Services

* Search available services
* Analyze service information
* Update approved service information

### FAQs

* Search FAQs
* Analyze FAQ information
* Update approved FAQ answers

### Controlled Updates

The agent supports a limited number of write operations, including:

* Update order status
* Update payment status
* Update artwork featured status
* Update service price
* Update FAQ answer

Write operations require explicit confirmation before the change is executed.

Example:

```text
Agent: This action will update the order status.

Type YES to confirm or NO to cancel.
```

---

# 🔐 Controlled Database Access

Security and controlled access are an important part of the project.

The AI agent is **not designed to have unrestricted MongoDB access**.

Instead, database operations are exposed through predefined tools.

```text
                  AI Agent
                     │
                     ▼
              Tool Selection
                     │
          ┌──────────┴──────────┐
          │                     │
       Read Tool             Write Tool
          │                     │
          ▼                     ▼
    Approved Data       Confirmation Required
          │                     │
          └──────────┬──────────┘
                     ▼
               MongoDB Atlas
```

This approach provides a controlled interface between the AI model and the application's database.

The agent also intentionally avoids exposing unnecessary sensitive website information through its normal analysis workflow.

---

# 🧩 System Architecture

```text
                         ┌──────────────────┐
                         │      User        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   FastAPI API    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    AI Agent      │
                         │                  │
                         │ Gemini Model     │
                         │ Tool Selection   │
                         │ Reasoning        │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌──────────────┐           ┌──────────────┐
             │ Read Tools   │           │ Write Tools  │
             └──────┬───────┘           └──────┬───────┘
                    │                          │
                    │                   Confirmation
                    │                          │
                    └─────────────┬────────────┘
                                  ▼
                         ┌──────────────────┐
                         │  MongoDB Atlas   │
                         │                  │
                         │ Orders           │
                         │ Artworks         │
                         │ Services         │
                         │ FAQs             │
                         │ Testimonials     │
                         │ Messages         │
                         │ Newsletter       │
                         └──────────────────┘
```

---

# 🧰 Technology Stack

## Programming

* Python

## AI

* Google Gemini
* `google-genai`
* Generative AI / LLM-based reasoning
* Tool calling

## Backend

* FastAPI
* Pydantic
* Uvicorn

## Database

* MongoDB Atlas
* PyMongo

## Data & Environment

* Python environment / virtual environment
* `python-dotenv`

## Development

* Visual Studio Code
* Git
* GitHub

---

# 📂 Project Structure

The project is organized around the AI agent, API layer, database tools, and supporting utilities.

```text
paras-arts-ai-agent/
│
├── agent.py
│       └── AI agent logic
│
├── api.py
│       └── FastAPI application
│
├── paras_tools.py
│       └── Controlled database tools
│
├── inspect_paras_db.py
│       └── Database inspection utility
│
├── inspect_scheme.py
│       └── Database/schema inspection utility
│
├── test_gemini.py
│       └── Gemini integration testing
│
├── requirements.txt
│       └── Python dependencies
│
├── .env.example
│       └── Environment variable template
│
├── .gitignore
│
└── README.md
```

---

# 🔄 How the Agent Works

A typical request follows this process:

### 1. User asks a question

```text
How many orders are currently pending?
```

### 2. API receives the request

FastAPI receives the user's input.

### 3. AI interprets the request

The Gemini model determines what information is required.

### 4. Agent selects a tool

The agent selects the appropriate predefined order-analysis tool.

### 5. Tool retrieves data

The tool accesses the required MongoDB collection.

### 6. Data is analyzed

The returned information is processed and summarized.

### 7. AI generates the response

The agent converts the result into a natural-language response.

```text
There is currently 1 pending order.
```

---

# 💬 Example Queries

The agent can handle questions such as:

### Orders

```text
How many orders are there?
```

```text
How many orders are completed?
```

```text
Show me the current order status distribution.
```

### Payments

```text
How many payments are pending?
```

```text
Give me a payment status summary.
```

### Sketch Types

```text
What types of sketches are being ordered?
```

```text
Which sketch type appears most frequently?
```

### Budgets

```text
Analyze the budgets associated with current orders.
```

### Artworks

```text
How many artworks are in the portfolio?
```

```text
Which artworks are featured?
```

### Services

```text
What services are currently available?
```

### FAQs

```text
Show me the frequently asked questions.
```

### Business Summary

```text
Give me a summary of the current Paras Arts business data.
```

---

# 📝 Controlled Write Operations

Unlike simple read-only AI assistants, this project also demonstrates how an AI agent can perform **controlled actions**.

Examples include:

```text
Update an order status
        ↓
Agent requests confirmation
        ↓
User enters YES
        ↓
Tool executes approved update
        ↓
MongoDB is updated
```

The confirmation step helps prevent unintended modifications.

---

# 🗄️ Database Integration

The agent connects to the Paras Arts MongoDB database.

Relevant application collections include:

```text
artworks
orders
services
faqs
testimonials
messages
newsletters
```

The agent's tools are designed to expose only the operations required for its intended use cases.

Administrative authentication data is kept outside the agent's normal analysis workflow.

---

# 🔐 Environment Variables

Create a `.env` file locally.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_connection_string
```

Never commit the real `.env` file or API keys to GitHub.

A `.env.example` file can be provided for reference:

```env
GEMINI_API_KEY=
MONGODB_URI=
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
```

## 2. Enter the project directory

```bash
cd paras-arts-ai-agent
```

## 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_connection_string
```

## 6. Run the FastAPI application

```bash
uvicorn api:app --reload
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

---

# 🧪 Testing

The project includes testing utilities for checking Gemini integration and database-related functionality.

Example:

```bash
python test_gemini.py
```

Additional testing can be performed through the FastAPI endpoints and the connected frontend interface.

---

# 🖥️ Frontend Integration

The FastAPI backend can be connected to a frontend interface that sends natural-language requests to the AI agent.

Conceptually:

```text
Paras Arts Frontend
        │
        │ User Question
        ▼
FastAPI Backend
        │
        ▼
Paras Arts AI Agent
        │
        ▼
Gemini + Tools
        │
        ▼
MongoDB Atlas
        │
        ▼
Formatted AI Response
        │
        ▼
Frontend UI
```

The goal is to provide users with an interactive interface instead of requiring them to directly interact with databases or backend APIs.

---

# 📸 Screenshots

Add screenshots of the actual agent interface here.

### AI Agent Interface

![Paras Arts AI Agent](./screenshots/agent-ui.png)

### Example Analysis

![AI Agent Response](./screenshots/analysis.png)

### Tool / Data Interaction

![Agent Data Analysis](./screenshots/data-analysis.png)

> Replace these paths with the screenshots available in the repository.

---

# 🎯 Project Goals

The project was developed to explore how generative AI agents can be connected to real application data while maintaining controlled access to business operations.

The main goals are:

* Build a practical AI agent
* Connect an LLM with real application data
* Use natural language for data analysis
* Integrate MongoDB with an AI workflow
* Implement tool-based agent architecture
* Separate AI reasoning from database operations
* Add confirmation-based write operations
* Provide a foundation for AI-assisted business intelligence

---

# 🧠 What I Learned

Through this project, I worked with:

* Generative AI APIs
* AI agent architecture
* Tool/function calling
* Prompt and instruction design
* MongoDB data access
* Python backend development
* FastAPI
* Pydantic
* Environment configuration
* API integration
* Controlled database operations
* Natural-language data analysis
* AI application testing
* Connecting AI systems to real-world application data

---

# 🔮 Future Improvements

Planned improvements include:

* Improved response formatting
* More advanced data visualizations
* Better conversational context
* More robust error handling
* Improved agent response speed
* Additional analytical tools
* More advanced business analytics
* Better frontend experience
* Improved testing
* Additional AI-powered insights

---

# 🎨 Related Project

This AI agent was developed as an extension of the **Paras Arts** full-stack platform.

### Paras Arts Website

A full-stack digital art portfolio and custom sketch ordering system.

**Technology:** React • Node.js • Express • MongoDB • Cloudinary

👉 [View Paras Arts Website](YOUR_PARAS_ARTS_REPOSITORY_URL)

---

# 👨‍💻 Developer

**Paras Kosambe**

B.Sc. Computer Science Student
Aspiring Data Scientist | AI/ML | Python | SQL | Web Development

This project is part of my ongoing journey of building practical AI, Data Science, and full-stack applications.

---

# 📄 License

This project is currently intended for personal portfolio, educational, and demonstration purposes.

The Paras Arts brand, artwork, logo, and original creative assets belong to the respective creator.

---

## ⭐ Project Status

**Status:** 🚧 Active Development / Testing

The AI agent is currently being tested and improved, particularly around response formatting, performance, reliability, and user experience.

---

### Built with Python, FastAPI, MongoDB & Generative AI

**Paras Arts AI Data Agent — Turning application data into actionable insights.**
