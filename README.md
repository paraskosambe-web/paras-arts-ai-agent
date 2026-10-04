<!-- ═══════════════════════ HEADER ═══════════════════════ -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:00d4ff&height=280&section=header&text=Paras%20Arts%20AI%20Data%20Agent&fontSize=48&fontColor=ffffff&fontAlignY=36&animation=twinkling&desc=Ask%20your%20business%20data%20anything.%20In%20plain%20language.&descSize=18&descAlignY=58" width="100%" alt="Paras Arts AI Data Agent"/>

<!-- Animated terminal: the agent "thinking" -->
<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=500&size=17&duration=2600&pause=1400&color=39FF14&background=0D111700&center=true&vCenter=false&multiline=true&repeat=true&width=720&height=130&lines=%24+ask-agent+%22How+many+orders+are+pending%3F%22;%F0%9F%A7%A0+Understanding+your+question...;%F0%9F%9B%A0%EF%B8%8F+Selecting+the+right+approved+tool...;%F0%9F%97%84%EF%B8%8F+Reading+data+from+MongoDB+Atlas...;%E2%9C%85+There+is+currently+1+pending+order." alt="Agent terminal animation"/>

<br/>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
<img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Gemini"/>
<img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"/>

<img src="https://img.shields.io/badge/Status-Active%20Development%20%2F%20Testing-f97316?style=for-the-badge&labelColor=0f172a" alt="Status"/>
<img src="https://img.shields.io/github/last-commit/paraskosambe-web/paras-arts-ai-agent?style=for-the-badge&label=Last%20Commit&color=00d4ff&labelColor=0f172a" alt="Last commit"/>

<br/><br/>

<!-- ═══════════════════════ NAVIGATION ═══════════════════════ -->
<a href="#overview"><img src="https://img.shields.io/badge/Overview-00d4ff?style=for-the-badge&labelColor=0f172a" alt="Overview"/></a>
<a href="#features"><img src="https://img.shields.io/badge/Capabilities-a855f7?style=for-the-badge&labelColor=0f172a" alt="Capabilities"/></a>
<a href="#how"><img src="https://img.shields.io/badge/How%20It%20Works-39FF14?style=for-the-badge&labelColor=0f172a" alt="How it works"/></a>
<a href="#safety"><img src="https://img.shields.io/badge/Safety-ef4444?style=for-the-badge&labelColor=0f172a" alt="Safety"/></a>
<a href="#install"><img src="https://img.shields.io/badge/Install-f97316?style=for-the-badge&labelColor=0f172a" alt="Install"/></a>

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ OVERVIEW ═══════════════════════ -->
<a id="overview"></a>

## 🧠 Overview

The **Paras Arts AI Data Agent** is an AI-powered data analysis and business-intelligence agent. It is an intelligent extension of the **[Paras Arts](https://github.com/paraskosambe-web/paras-arts)** full-stack art portfolio and custom sketch ordering platform.

It connects an **AI reasoning layer (Google Gemini)** to approved business data in **MongoDB Atlas**. Instead of writing database queries, the artist simply asks a question in plain language, and the agent finds the data, analyzes it and answers.

> 💡 **In one line:** *You ask → the AI picks an approved tool → the tool reads the data → you get a clear answer.*

### 💬 See it in action

> 🧑 **You:** How many orders are currently pending?
>
> 🤖 **Agent:** There is currently 1 pending order.

> 🧑 **You:** What are the most common sketch types?
>
> 🤖 **Agent:** *Analyzes the order data and returns the distribution of sketch types.*

> 🧑 **You:** Give me a summary of the current business data.
>
> 🤖 **Agent:** *Combines order, payment, artwork and service data into a readable business summary.*

<details>
<summary><b>🎯 Why build this? (the problem it solves)</b></summary>
<br/>

The Paras Arts website holds many kinds of data: **orders, payments, artworks, services, FAQs, testimonials, customer messages and newsletter subscriptions**. Checking all of this by hand in the database is slow, and it needs technical knowledge.

This project gives the artist a **controlled AI interface** that can:

1. Understand natural-language requests
2. Identify the data needed
3. Retrieve the relevant information
4. Analyze it
5. Generate a meaningful response
6. Perform **only approved** database updates

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ FEATURES ═══════════════════════ -->
<a id="features"></a>

## ✨ Agent Capabilities

<table>
<tr>
<td width="50%" valign="top">

### 🔎 Natural-Language Search
Ask about Paras Arts data without touching MongoDB.
- *"Show me the pending orders."*
- *"How many completed orders are there?"*
- *"Find orders for portrait sketches."*

</td>
<td width="50%" valign="top">

### 📊 Data Analysis
Turns raw records into useful summaries.
- Order statistics and payment status
- Sketch-type distribution and budgets
- Artwork, service and FAQ information
- Overall business summaries

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🧠 AI-Powered Reasoning
A Gemini model understands the request and decides **which approved tool** to use. It never gets unrestricted database access.

</td>
<td width="50%" valign="top">

### ✅ Confirmed Updates
A small set of write actions are available, and each one needs an explicit **YES** before it runs.

</td>
</tr>
</table>

### 🛠️ Tools the agent can use

<div align="center">

| 📦 **Orders** | 🎨 **Artworks** | 💰 **Services** | ❓ **FAQs** |
|:---|:---|:---|:---|
| Search orders | Search artwork info | Search services | Search FAQs |
| Analyze order status | Analyze artwork data | Analyze service info | Analyze FAQ info |
| Analyze payment status | Check featured artwork | 🔒 Update service price | 🔒 Update FAQ answer |
| Analyze sketch types | 🔒 Update featured status | | |
| Analyze budgets | | | |
| Order summaries | | | |

</div>

> 🔒 = a **write action** that always asks for confirmation first. Order status and payment status updates are also confirmation-protected.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ HOW IT WORKS ═══════════════════════ -->
<a id="how"></a>

## 🔄 How the Agent Works

```mermaid
sequenceDiagram
    autonumber
    actor U as 🧑 User
    participant API as ⚡ FastAPI
    participant AI as 🧠 Gemini Agent
    participant T as 🛠️ Approved Tool
    participant DB as 🗄️ MongoDB Atlas

    U->>API: "How many orders are pending?"
    API->>AI: Pass the question
    AI->>AI: Understand request and pick a tool
    AI->>T: Call order-analysis tool
    T->>DB: Read approved data
    DB-->>T: Order records
    T-->>AI: Analyzed result
    AI-->>API: Natural-language answer
    API-->>U: "There is currently 1 pending order."
```

### 🧩 System architecture

```mermaid
flowchart TB
    U["👤 User / Frontend"] --> F["⚡ FastAPI Layer"]
    F --> A["🧠 AI Agent<br/>Gemini · Reasoning · Tool Selection"]
    A --> R["📖 Read Tools"]
    A --> W["✏️ Write Tools"]
    W --> C{"✅ User<br/>confirms?"}
    C -- "YES" --> DB
    C -- "NO" --> X["🚫 Cancelled"]
    R --> DB[("🗄️ MongoDB Atlas<br/>Orders · Artworks · Services<br/>FAQs · Testimonials · Messages · Newsletter")]
    style U fill:#0ea5e9,stroke:none,color:#fff
    style F fill:#009688,stroke:none,color:#fff
    style A fill:#8E75B2,stroke:none,color:#fff
    style R fill:#6366f1,stroke:none,color:#fff
    style W fill:#f97316,stroke:none,color:#fff
    style C fill:#eab308,stroke:none,color:#000
    style X fill:#ef4444,stroke:none,color:#fff
    style DB fill:#47A248,stroke:none,color:#fff
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ SAFETY ═══════════════════════ -->
<a id="safety"></a>

## 🔐 Controlled Database Access

Safety is a core part of this project. The AI is **not** given unrestricted MongoDB access. Every database operation goes through a **predefined tool**.

<div align="center">

| 🛡️ Safety Layer | What it does |
|:---|:---|
| 🧰 **Predefined tools only** | The AI can only do what a tool allows |
| 📖 **Read / write separation** | Reading data and changing data are different tools |
| ✅ **Confirmation for writes** | Nothing is changed until the user types YES |
| 🙈 **Sensitive data kept out** | Admin authentication data stays outside the normal analysis workflow |

</div>

### ✍️ What a confirmed update looks like

> 🧑 **You:** Update the status of this order to Accepted.
>
> 🤖 **Agent:** ⚠️ This action will update the order status. **Type YES to confirm or NO to cancel.**
>
> 🧑 **You:** YES
>
> 🤖 **Agent:** ✅ Done. The order status has been updated.

```mermaid
flowchart LR
    A["Update request"] --> B["⚠️ Agent asks<br/>for confirmation"] --> C["User types YES"] --> D["🛠️ Tool runs<br/>approved update"] --> E["🗄️ MongoDB<br/>updated"]
    style A fill:#0ea5e9,stroke:none,color:#fff
    style B fill:#eab308,stroke:none,color:#000
    style C fill:#22c55e,stroke:none,color:#fff
    style D fill:#a855f7,stroke:none,color:#fff
    style E fill:#47A248,stroke:none,color:#fff
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ TECH STACK ═══════════════════════ -->
## 🧰 Technology Stack

<div align="center">

<table align="center"><tr>
<td align="center" width="100"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python"/><br/><sub><b>Python</b></sub></td>
<td align="center" width="100"><img src="https://cdn.simpleicons.org/googlegemini/8E75B2" width="48" height="48" alt="Gemini"/><br/><sub><b>Gemini</b></sub></td>
<td align="center" width="100"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="48" height="48" alt="FastAPI"/><br/><sub><b>FastAPI</b></sub></td>
<td align="center" width="100"><img src="https://cdn.simpleicons.org/pydantic/E92063" width="48" height="48" alt="Pydantic"/><br/><sub><b>Pydantic</b></sub></td>
<td align="center" width="100"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg" width="48" height="48" alt="MongoDB"/><br/><sub><b>MongoDB</b></sub></td>
<td align="center" width="100"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" width="48" height="48" alt="Git"/><br/><sub><b>Git</b></sub></td>
<td align="center" width="100"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg" width="48" height="48" alt="VS Code"/><br/><sub><b>VS Code</b></sub></td>
</tr></table>

</div>

| Layer | Technologies |
|:---|:---|
| 🐍 **Programming** | Python |
| 🤖 **AI** | Google Gemini, `google-genai`, LLM-based reasoning, tool calling |
| ⚙️ **Backend** | FastAPI, Pydantic, Uvicorn |
| 🗄️ **Database** | MongoDB Atlas, PyMongo |
| 🌱 **Environment** | Python virtual environment, `python-dotenv` |
| 🧰 **Development** | Visual Studio Code, Git, GitHub |

<details>
<summary><b>📂 Project structure (click to expand)</b></summary>
<br/>

```text
paras-arts-ai-agent/
├── agent.py               → AI agent logic
├── api.py                 → FastAPI application
├── paras_tools.py         → Controlled database tools
├── inspect_paras_db.py    → Database inspection utility
├── inspect_scheme.py      → Database / schema inspection utility
├── test_gemini.py         → Gemini integration testing
├── requirements.txt       → Python dependencies
├── .env.example           → Environment variable template
├── .gitignore
└── README.md
```

</details>

<details>
<summary><b>🗄️ Database collections the agent works with (click to expand)</b></summary>
<br/>

```text
artworks   orders   services   faqs   testimonials   messages   newsletters
```

The tools expose only the operations needed for the agent's intended use cases.

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ EXAMPLES ═══════════════════════ -->
## 💬 Example Queries

<details open>
<summary><b>Try asking the agent…</b></summary>
<br/>

<div align="center">

| 📦 **Orders** | 💳 **Payments** | ✏️ **Sketch Types & Budgets** |
|:---|:---|:---|
| How many orders are there? | How many payments are pending? | What types of sketches are being ordered? |
| How many orders are completed? | Give me a payment status summary. | Which sketch type appears most frequently? |
| Show me the order status distribution. | | Analyze the budgets of current orders. |

| 🎨 **Artworks** | 💰 **Services & FAQs** | 📊 **Business Summary** |
|:---|:---|:---|
| How many artworks are in the portfolio? | What services are currently available? | Give me a summary of the current Paras Arts business data. |
| Which artworks are featured? | Show me the frequently asked questions. | |

</div>

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ INSTALL ═══════════════════════ -->
<a id="install"></a>

## 🚀 Installation

**1️⃣ Clone and enter the project**

```bash
git clone https://github.com/paraskosambe-web/paras-arts-ai-agent.git
cd paras-arts-ai-agent
```

**2️⃣ Create a virtual environment**

<table>
<tr>
<td width="50%" valign="top">

🪟 **Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

</td>
<td width="50%" valign="top">

🐧 **Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

</td>
</tr>
</table>

**3️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

**4️⃣ Add your environment variables**

Create a local `.env` file (a `.env.example` template is included):

```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_connection_string
```

> 🔐 **Never commit your real `.env` file or API keys to GitHub.**

**5️⃣ Run the API**

```bash
uvicorn api:app --reload
```

The API will be available locally at **http://127.0.0.1:8000**

<details>
<summary><b>🧪 Testing (click to expand)</b></summary>
<br/>

Check the Gemini integration with:

```bash
python test_gemini.py
```

You can also test through the FastAPI endpoints and the connected frontend interface.

</details>

<details>
<summary><b>🖥️ Frontend integration (click to expand)</b></summary>
<br/>

The FastAPI backend can connect to a frontend that sends natural-language requests to the agent, so users get a friendly interface instead of working with databases or raw APIs.

```mermaid
flowchart LR
    A["🎨 Paras Arts<br/>Frontend"] -- "question" --> B["⚡ FastAPI"] --> C["🧠 AI Agent<br/>Gemini + Tools"] --> D[("🗄️ MongoDB Atlas")]
    D --> E["💬 Formatted<br/>response"] --> A
    style A fill:#0ea5e9,stroke:none,color:#fff
    style B fill:#009688,stroke:none,color:#fff
    style C fill:#8E75B2,stroke:none,color:#fff
    style D fill:#47A248,stroke:none,color:#fff
    style E fill:#ec4899,stroke:none,color:#fff
```

</details>

<!-- ═══════════════════════ SCREENSHOTS ═══════════════════════ -->
<!--
  SCREENSHOTS: add your images to a /screenshots folder in this repo, then delete the
  opening and closing comment lines around this block to show it.

## 📸 Screenshots

<table>
<tr>
<td align="center"><b>Agent Interface</b><br/><img src="./screenshots/agent-ui.png" alt="Agent interface"/></td>
<td align="center"><b>Example Analysis</b><br/><img src="./screenshots/analysis.png" alt="Analysis"/></td>
</tr>
<tr>
<td align="center" colspan="2"><b>Tool / Data Interaction</b><br/><img src="./screenshots/data-analysis.png" alt="Data analysis"/></td>
</tr>
</table>
-->

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ GOALS ═══════════════════════ -->
## 🎯 Project Goals

This project explores how **generative AI agents can work with real application data** while keeping access to business operations under control.

- 🤖 Build a practical, working AI agent
- 🔗 Connect an LLM with real application data
- 💬 Use natural language for data analysis
- 🗄️ Integrate MongoDB into an AI workflow
- 🛠️ Implement a tool-based agent architecture
- 🧱 Separate AI reasoning from database operations
- ✅ Add confirmation-based write operations
- 📈 Lay a foundation for AI-assisted business intelligence

## 🧠 What I Learned

<div align="center">

![GenAI](https://img.shields.io/badge/Generative%20AI%20APIs-8E75B2?style=for-the-badge&labelColor=0f172a)
![Agents](https://img.shields.io/badge/AI%20Agent%20Architecture-a855f7?style=for-the-badge&labelColor=0f172a)
![Tools](https://img.shields.io/badge/Tool%20%2F%20Function%20Calling-6366f1?style=for-the-badge&labelColor=0f172a)
![Prompts](https://img.shields.io/badge/Prompt%20%26%20Instruction%20Design-ec4899?style=for-the-badge&labelColor=0f172a)
![MongoDB](https://img.shields.io/badge/MongoDB%20Data%20Access-47A248?style=for-the-badge&labelColor=0f172a)
![FastAPI](https://img.shields.io/badge/FastAPI%20%26%20Pydantic-009688?style=for-the-badge&labelColor=0f172a)
![Control](https://img.shields.io/badge/Controlled%20DB%20Operations-f97316?style=for-the-badge&labelColor=0f172a)
![Testing](https://img.shields.io/badge/AI%20App%20Testing-ef4444?style=for-the-badge&labelColor=0f172a)

</div>

## 🔮 Future Improvements

<details>
<summary><b>See what's planned (click to expand)</b></summary>
<br/>

- ✨ Improved response formatting
- 📊 More advanced data visualizations
- 💬 Better conversational context
- 🛡️ More robust error handling
- ⚡ Faster agent responses
- 🧰 Additional analytical tools and business analytics
- 🖥️ A better frontend experience
- 🧪 Improved testing
- 💡 Additional AI-powered insights

</details>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00d4ff,50:a855f7,100:00d4ff&height=3" width="100%" alt="divider"/>

<!-- ═══════════════════════ RELATED + DEVELOPER ═══════════════════════ -->
## 🎨 Related Project

This agent was built as an extension of the **Paras Arts** platform, a full-stack digital art portfolio and custom sketch ordering system.

![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white)
![Express](https://img.shields.io/badge/Express-000000?style=flat-square&logo=express&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=flat-square&logo=cloudinary&logoColor=white)

<a href="https://github.com/paraskosambe-web/paras-arts"><img src="https://img.shields.io/badge/View%20Paras%20Arts%20Website-%E2%86%92-00d4ff?style=for-the-badge&logo=github&logoColor=black" alt="Paras Arts website"/></a>

## 👨‍💻 Developer

<div align="center">

### Paras Kosambe
**B.Sc. Computer Science Student** • Aspiring Data Scientist • AI/ML • Python • SQL • Web Development

*This project is part of my ongoing journey of building practical AI, Data Science and full-stack applications.*

<br/>

<a href="https://github.com/paraskosambe-web"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
<a href="https://www.linkedin.com/in/paras-kosambe"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
<a href="https://www.instagram.com/paras.arts.3313"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram"/></a>
<a href="mailto:paraskosambe@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>

</div>

<br/>

<details>
<summary><b>📄 License</b></summary>
<br/>

This project is intended for personal portfolio, educational and demonstration purposes. The Paras Arts brand, artwork, logo and original creative assets belong to their creator.

</details>

<br/>

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&size=17&duration=3500&pause=1200&color=00D4FF&center=true&vCenter=true&width=700&lines=Built+with+Python%2C+FastAPI%2C+MongoDB+%26+Generative+AI;Turning+application+data+into+actionable+insights.+%F0%9F%9A%80" alt="Footer typing"/>

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:00d4ff&height=120&section=footer" width="100%" alt="footer wave"/>
