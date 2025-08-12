from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.config import get_llm_config


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured response following a specific schema."""
        pass
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Generate a chat completion response."""
        pass


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service implementation."""
    
    def __init__(self, api_key: str, model: str):
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=model,
            temperature=0.1
        )
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt
        
        # Use HumanMessage for ChatOpenAI
        from langchain.schema import HumanMessage
        response = await self.llm.agenerate([[HumanMessage(content=full_prompt)]])
        return response.generations[0][0].text
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        structured_prompt = f"""
        Please provide a response in the following JSON format:
        {json.dumps(schema, indent=2)}
        
        Question: {prompt}
        
        Response (JSON only):
        """
        
        response = await self.llm.agenerate([[structured_prompt]])
        response_text = response.generations[0][0].text.strip()
        
        try:
            # Extract JSON from response
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse structured response: {response_text}")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            else:
                langchain_messages.append(HumanMessage(content=msg["content"]))
        
        response = await self.llm.agenerate([langchain_messages])
        return response.generations[0][0].text


class LLMService:
    """Model-agnostic LLM service factory."""
    
    def __init__(self):
        self._service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the appropriate LLM service based on configuration."""
        config = get_llm_config()
        provider = config["provider"]
        
        if provider == "openai":
            self._service = OpenAILLMService(config["api_key"], config["model"])
        else:
            raise ValueError(f"Only OpenAI is supported for now. Configured provider: {provider}")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response from the configured LLM."""
        return await self._service.generate_response(prompt, context)
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured response following a specific schema."""
        return await self._service.generate_structured_response(prompt, schema)
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Generate a chat completion response."""
        return await self._service.chat_completion(messages)
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current LLM provider."""
        config = get_llm_config()
        return {
            "provider": config["provider"],
            "model": config["model"]
        } 