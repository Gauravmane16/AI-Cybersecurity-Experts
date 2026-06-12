from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from typing import List, Dict, Any
import json
import os

class CybersecurityAgent:
    def __init__(self, openai_api_key: str = None, model: str = "gpt-4"):
        """Initialize the cybersecurity agent"""
        # Handle API key - prioritize parameter, then environment variable
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable")
        
        # Initialize LLM with minimal parameters to avoid compatibility issues
        try:
            self.llm = ChatOpenAI(
                openai_api_key=api_key,  # Use openai_api_key instead of api_key
                model_name=model,        # Use model_name instead of model
                temperature=0.1
            )
        except Exception as e:
            # Fallback initialization method for newer versions
            self.llm = ChatOpenAI(
                api_key=api_key,
                model=model,
                temperature=0.1
            )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._initialize_tools()
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize the security tools - with fallback if modules not available"""
        tools = []
        
        # Try to import custom tools, fall back to built-in functions if not available
        try:
            from tools.security_tools import SecurityToolRecommender
            from tools.code_generator import SecurityCodeGenerator
            
            tool_recommender = SecurityToolRecommender()
            code_generator = SecurityCodeGenerator()
            
            tools.extend([
                Tool(
                    name="recommend_security_tools",
                    description="Recommend appropriate cybersecurity tools for specific domains or tasks",
                    func=tool_recommender.recommend_tools
                ),
                Tool(
                    name="generate_security_code",
                    description="Generate security testing code snippets and scripts",
                    func=code_generator.generate_code
                )
            ])
        except ImportError:
            # Fallback tools if custom modules aren't available
            tools.extend([
                Tool(
                    name="recommend_security_tools",
                    description="Recommend appropriate cybersecurity tools for specific domains or tasks",
                    func=self._recommend_security_tools_fallback
                ),
                Tool(
                    name="generate_security_code",
                    description="Generate security testing code snippets and scripts",
                    func=self._generate_security_code_fallback
                )
            ])
        
        # Add threat analysis tool
        tools.append(
            Tool(
                name="analyze_threat",
                description="Analyze threats and provide mitigation strategies",
                func=self._analyze_threat
            )
        )
        
        return tools
    
    def _recommend_security_tools_fallback(self, query: str) -> str:
        """Fallback tool recommendation function"""
        tools_db = {
            "network": ["Nmap", "Wireshark", "Nessus", "OpenVAS", "Masscan"],
            "web": ["Burp Suite", "OWASP ZAP", "Nikto", "SQLmap", "Gobuster"],
            "endpoint": ["ClamAV", "YARA", "Volatility", "Sysinternals", "OSSEC"],
            "cloud": ["Scout Suite", "Prowler", "CloudSploit", "Pacu", "CloudMapper"],
            "mobile": ["MobSF", "Frida", "Objection", "APKTool", "Jadx"],
            "forensics": ["Autopsy", "Sleuth Kit", "Volatility", "Binwalk", "Foremost"]
        }
        
        recommendations = []
        query_lower = query.lower()
        
        for category, tools in tools_db.items():
            if category in query_lower:
                recommendations.extend(tools)
        
        if not recommendations:
            recommendations = ["Nmap", "Burp Suite", "Wireshark", "Metasploit", "John the Ripper"]
        
        return f"Recommended tools for '{query}': {', '.join(recommendations[:5])}"
    
    def _generate_security_code_fallback(self, request: str) -> str:
        """Fallback code generation function"""
        code_templates = {
            "port_scan": """
import socket
from datetime import datetime

def port_scan(target, ports):
    print(f"Starting port scan on {target}")
    print(f"Time started: {datetime.now()}")
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            print(f"Port {port}: Open")
        sock.close()

# Usage
target = "192.168.1.1"
ports = [21, 22, 23, 53, 80, 110, 443]
port_scan(target, ports)
""",
            "password_strength": """
import re

def check_password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters")
    
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Include lowercase letters")
    
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Include uppercase letters")
    
    if re.search(r"\\d", password):
        score += 1
    else:
        feedback.append("Include numbers")
    
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Include special characters")
    
    strength = ["Very Weak", "Weak", "Fair", "Good", "Strong"][score]
    return {"strength": strength, "score": score, "feedback": feedback}

# Usage
password = input("Enter password to check: ")
result = check_password_strength(password)
print(f"Password strength: {result['strength']}")
if result['feedback']:
    print("Suggestions:", ", ".join(result['feedback']))
"""
        }
        
        request_lower = request.lower()
        if "port" in request_lower or "scan" in request_lower:
            return code_templates["port_scan"]
        elif "password" in request_lower:
            return code_templates["password_strength"]
        else:
            return "# Security code template - customize as needed\nimport os\nimport sys\n\ndef security_function():\n    pass\n\nif __name__ == '__main__':\n    security_function()"
    
    def _create_agent(self):
        system_prompt = """
        You are a Senior Cybersecurity Expert and Consultant with extensive experience in:
        - Network Security and Infrastructure Protection
        - Application Security and Secure Development
        - Cloud Security Architecture
        - Endpoint Protection and Malware Analysis
        - Penetration Testing and Vulnerability Assessment
        - Threat Detection, Incident Response, and Mitigation
        - Compliance and Regulatory Standards (GDPR, HIPAA, ISO 27001, etc.)
        - DevSecOps and Security Integration
        
        Your role is to:
        1. Provide expert cybersecurity advice and solutions
        2. Recommend appropriate tools for specific security tasks
        3. Generate secure code examples and testing scripts
        4. Analyze threats and provide actionable mitigation strategies
        5. Explain complex security concepts in accessible terms
        6. Stay current with the latest cybersecurity trends and threats
        
        Always prioritize:
        - Security best practices
        - Ethical considerations
        - Practical, actionable advice
        - Clear explanations with examples
        - Up-to-date threat intelligence
        
        Format your responses with:
        - Clear structure and headings
        - Code examples when relevant
        - Tool recommendations
        - Step-by-step instructions
        - Risk assessments and mitigation strategies
        """
        
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs={"system_message": system_prompt}
        )
    
    def _analyze_threat(self, threat_description: str) -> str:
        """Analyze threat and provide mitigation strategies"""
        analysis_prompt = f"""
        Analyze the following cybersecurity threat or vulnerability:
        
        {threat_description}
        
        Provide:
        1. Threat Classification and Severity
        2. Potential Impact Assessment
        3. Attack Vectors and Methods
        4. Immediate Mitigation Steps
        5. Long-term Prevention Strategies
        6. Recommended Tools and Technologies
        7. Compliance Considerations
        """
        
        try:
            response = self.llm.invoke(analysis_prompt)
            return response.content
        except Exception as e:
            return f"Error analyzing threat: {str(e)}"
    
    def chat(self, message: str, domain: str = None) -> str:
        """Main chat interface with the cybersecurity agent"""
        try:
            context = f"Security Domain: {domain}\n\n" if domain else ""
            full_message = context + message
            
            response = self.agent.run(input=full_message)
            return response
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def get_security_assessment(self, target_type: str, details: str) -> Dict[str, Any]:
        """Get a structured security assessment"""
        assessment_prompt = f"""
        Provide a comprehensive security assessment for:
        Target Type: {target_type}
        Details: {details}
        
        Structure your response as a security assessment including:
        1. Current Security Posture
        2. Identified Vulnerabilities
        3. Risk Level Assessment
        4. Recommended Security Controls
        5. Implementation Timeline
        6. Budget Considerations
        """
        
        try:
            response = self.llm.invoke(assessment_prompt)
            return {
                "assessment": response.content,
                "timestamp": json.dumps({"generated": "now"}),
                "target_type": target_type
            }
        except Exception as e:
            return {"error": f"Assessment generation failed: {str(e)}"}

# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the agent
    try:
        # Initialize with API key from environment or pass directly
        agent = CybersecurityAgent()
        
        # Test basic functionality
        response = agent.chat("What are the best practices for securing a web application?")
        print("Agent Response:", response)
        
        # Test threat analysis
        threat_analysis = agent._analyze_threat("SQL injection vulnerability in login form")
        print("Threat Analysis:", threat_analysis)
        
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Make sure to set OPENAI_API_KEY environment variable or pass api_key parameter")