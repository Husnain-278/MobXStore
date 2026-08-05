from django.db import transaction

from .chat_agent import ChatAgent
from admin_app.services.conversation_service import ConversationService

from admin_app.services.message_service import MessageService
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from .llm import llm
from .prompts import TITLE_PROMPT



class AIService:

    def __init__(self):
        self.agent = ChatAgent()
        
        
        
        
    def _generate_title(self, conversation):
            """
            Generate a title for a conversation.
            """
    
            first_message = MessageService.get_first_user_message(
                conversation
            )
    
            if not first_message:
                return "New Chat"
    
            response = llm.invoke(
                [
                    SystemMessage(content=TITLE_PROMPT),
                    HumanMessage(content=first_message.content),
                ]
            )
    
            return response.content.strip()[:255]
    
    
        

    @transaction.atomic
    def generate_reply(self, conversation, user_input):
        """
        Generate an AI response for the given conversation.
        """

        # Save user message
        MessageService.create_user_message(
            conversation=conversation,
            content=user_input,
        )

        # Load conversation history
        messages = MessageService.get_recent(conversation)

        # Generate AI response
        response = self.agent.invoke(messages)


        # Save assistant message
        MessageService.create_assistant_message(
            conversation=conversation,
            content=response.ai_message.content,
        )
        if not conversation.title:

            title = self._generate_title(conversation)

            ConversationService.update_title(
                conversation,
                title,
            )

        return response.ai_message
    
    
    