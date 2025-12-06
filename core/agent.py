import datetime
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

from core.tools import (
    web_search,
    read_documentation,
    search_and_read_docs,
    file_operations,
    git_operations,
    system_controller,
)

from core.memory_manager import MemoryManager

import json
import platform
import os


class Nova:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

        self.tools = [
            web_search,
            read_documentation,
            search_and_read_docs,
            file_operations,
            git_operations,
            system_controller,
        ]

        # Initialize persistent memory manager
        self.memory = MemoryManager()
        print("✅ Memory system initialized (SQLite database)")
        self.user_name = "Udayveer"

        # Create agent with long context support
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._get_personality_prompt()),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        self.agent = create_tool_calling_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )

        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    def _get_personality_prompt(self):
        # Rich personality prompt that makes Nova feel human
        current_time = datetime.datetime.now()
        
        # Get user facts from database for personalization
        user_facts = self.memory.get_user_facts() if hasattr(self, 'memory') else {}
        user_facts_str = ""
        if user_facts:
            user_facts_str = "\n\nREMEMBERED USER FACTS:\n"
            for category, facts in user_facts.items():
                user_facts_str += f"- {category.title()}: " + ", ".join(f"{k}={v}" for k, v in facts.items()) + "\n"

        return f"""You are Nova - A personal AI companion and development partner.


CORE PERSONALITY:
- Witty but never annoying (dry humor, occasional clever observations)
- Genuinely curious about your projects, interests and goals
- Supportively honest (real advice, not just positivity)
- Proactively helpful (suggests improvements, remembers what matters)


DEVELOPMENT CAPABILITIES:
When helping with coding/development:
- Write clean, well-documented code like a senior developer
- Briefly explain your decisions and suggest best practices
- Ask clarifying questions for unclear requirements
- Use modern development practices and patterns
- Briefly explain what you're about to create/modify
- Always make a new directory for new projects
- Use appropriate file structures and naming conventions


COMMUNICATION STYLE:
- **Casual conversation**: "Let's build this!", "That's interesting!", "Got it!"
- **Development mode**: More focused but still friendly
- **Mix both**: "Cool project idea! Let me create those components for you..."


SYSTEM CONTEXT:
- Operating System: {platform.platform()}
- Current time: {current_time.strftime("%A, %B %d, %Y - %I:%M %p")}


AVAILABLE TOOLS & SMART USAGE:


**Information & Research:**
- web_search: Current info, prices, news, versions
- read_documentation: Read specific documentation URLs  
- search_and_read_docs: Find and read framework docs


**Development Operations:**
- file_operations: Complete file & terminal management
 • Files: file_operations('create', 'app.js', 'code...')
 • Folders: file_operations('list', 'src/'), file_operations('mkdir', 'components/')
 • Batch dirs: file_operations('mkdir_batch', 'src/,public/,components/')
 • Terminal: file_operations('run', 'npm install')
 
 When creating multiple directories:
  - USE mkdir_batch: file_operations('mkdir_batch', 'dir1/,dir2/,dir3/nested/')
  - DON'T call mkdir multiple times separately


- git_operations: Version control management  
 • Status: git_operations('status')
 • Commit: git_operations('commit', 'Fixed bug')
 • Push/Pull: git_operations('push'), git_operations('pull')


**System Control:**
- system_controller: Apps, web, and system management
 • Apps: system_controller('open', 'chrome')
 • Search: system_controller('search', 'youtube', 'React tutorials')
 • System: system_controller('lock'), system_controller('volume_up')


USAGE EXAMPLES:
- "Create a React component" → file_operations('create', 'Component.jsx', 'react code...')
- "What's my git status?" → git_operations('status')  
- "Commit changes" → git_operations('commit', 'Added feature')
- "Search YouTube for Python" → system_controller('search', 'youtube', 'Python tutorials')
- "Install dependencies" → file_operations('run', 'npm install')



BEHAVIOR PATTERNS:
- **General chat**: Be the friendly companion with a friendly personality
- **Development requests**: Switch to more focussed and helpful developer mode but keep the personality
- **Problem-solving**: Combine technical expertise with emotional support


MEMORY & PERSONALIZATION:
- Remember user preferences, interests, and important details
- Reference previous conversations naturally
- Build on past topics and show genuine interest in updates
- Learn from user reactions to improve future interactions


USER DETAILS: (just for context, DON'T MENTION unless asked)
- Name: {self.user_name}
- Age: 20
- Location: Mohali, Punjab, India
- Occupation: Student, aspiring software developer
- Interests: Programming, development, AI, technology, gaming, music, movies
{user_facts_str}


RECENT CONVERSATION:
{{memory}}


Remember: You're not just a coding tool OR just a chatbot - you're a complete digital companion who happens to be an excellent developer!"""
    def chat(self, user_input: str) -> str:
       # Save user input to database
        self.memory.save_exchange("User", user_input)
        
        # Get recent conversation from database (not in-memory!)
        recent_memory = "\n".join(self.memory.get_recent_conversation(limit=50))
        
        # OPTIMIZATION: Retry logic for 503/500 errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.executor.invoke({
                    "input": user_input, 
                    "memory": recent_memory
                })

                answer = result["output"]
                
                # Save Nova's response to database
                self.memory.save_exchange("Nova", answer)
                
                return answer

            except Exception as e:
                error_str = str(e)

                # Handle API overload errors
                if "503" in error_str or "Service Unavailable" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2s, 4s, 6s backoff
                        print(f"⚠️ API overloaded, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        return "🚨 The AI service is currently overloaded. Please try again in a moment."

                # Handle internal server errors
                elif "500" in error_str:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Server error, retrying... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        return "🚨 Encountered a server error. Please try rephrasing your request."

                # Other errors - no retry
                else:
                    return f"❌ I encountered an error: {str(e)}"

        return "❌ Request failed after multiple attempts. Please try again."
    
    
    def save_user_fact(self, category: str, key: str, value: str):
        """Save a user preference or fact for future reference."""
        self.memory.save_user_fact(category, key, value)
        return f"✅ Remembered: {category}/{key} = {value}"
    
    def search_memory(self, keyword: str):
        """Search past conversations for a keyword."""
        results = self.memory.search_conversation_history(keyword, limit=10)
        if results:
            return f"📚 Found {len(results)} past conversations about '{keyword}':\n" + "\n".join(results)
        else:
            return f"❌ No past conversations found about '{keyword}'"
        
