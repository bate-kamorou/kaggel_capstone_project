# ⚖️ The Decision Guide: Multi-Agent Consensus Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Google ADK](https://img.shields.io/badge/Google-ADK-red)
![Gemini](https://img.shields.io/badge/Model-Gemini%202.5%20Flash%20Lite-purple)

**The Decision Guide** is an intelligent orchestration system designed to cure "decision paralysis." Built using the **Google Agent Development Kit (ADK)** and powered by **Gemini 2.5**, it simulates a consultation board by pitting an eternal **Optimist** against a hardened **Skeptic**, while a **Moderator** synthesizes the debate into a clear, unbiased trade-off analysis.

---

## 🧠 The Problem
In the age of information overload, making a simple decision (e.g., *"Should I buy this car?"* or *"Should I move to this city?"*) is difficult.
1.  **Confirmation Bias:** We tend to search only for what validates our feelings.
2.  **Review Fatigue:** Sifting through hundreds of conflicting reviews takes hours.
3.  **Generic AI:** Standard chatbots often give "safe," neutral answers that lack depth.

## 💡 The Solution
This project utilizes a **Hierarchical Multi-Agent Architecture**. Instead of one AI trying to be everything, the workload is split among three specialized agents, each with a distinct personality and strict protocol.

### 1. The Optimist Agent ("The Enthusiast") 🟢
*   **Goal:** Find the "Wins."
*   **Tools:** Uses `google_search` to find rave reviews, unique features, and quality-of-life upgrades.
*   **Personality:** Focuses on happiness, utility, and best-case scenarios. Ignores costs.

### 2. The Skeptic Agent ("The Realist") 🔵
*   **Goal:** Find the "Pain Points."
*   **Tools:** Uses `google_search` to find 1-star reviews, hidden fees, maintenance nightmares, and recalls.
*   **Personality:** Stern, warning, and immune to the "cool factor."

### 3. The Moderator Agent (Root Orchestrator) 🟣
*   **Goal:** Synthesis and Guidance.
*   **Tools:** `AgentTool` (to call sub-agents), `load_memory` (to recall context).
*   **Logic:**
    *   Analyzes the user's intent.
    *   Dispatches tasks to the Optimist and Skeptic simultaneously.
    *   Synthesizes the conflicting data into a **"Trade-Off Matrix."**
    *   Handles follow-up questions using conversation history.

---

## 🛠️ Tech Stack

*   **Language:** Python
*   **Framework:** [Google Agent Development Kit (ADK)](https://github.com/google/google-adk)
*   **LLM:** Google Gemini 2.5 Flash Lite
*   **Search Engine:** Google Search Tool (ADK native)
*   **Orchestration:** ADK `Runner` & `InMemorySessionService`

---

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.9+
*   A Google Cloud Project with the Gemini API enabled.
*   A Google Search API Key (if required by your specific ADK configuration).

### 1. Clone the Repository
```bash
git clone https://github.com/bate-kamorou/kaggle_capstone_project.git
cd ./app
