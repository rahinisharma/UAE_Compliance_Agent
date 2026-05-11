import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate 

load_dotenv()

class UAEComplianceEngine:
    def __init__(self):
        cohere_api_key = os.getenv("COHERE_API_KEY")
        
        if not cohere_api_key:
            raise ValueError("❌ COHERE_API_KEY not found in .env!")

        # Embeddings for searching
        self.embeddings = CohereEmbeddings(
            cohere_api_key=cohere_api_key, 
            model="embed-english-v3.0"
        )
        
        # LLM for answering
        self.llm = ChatCohere(
            cohere_api_key=cohere_api_key,
            model="command-r7b-12-2024" 
        )
        
        # Load the existing database
        self.vector_db = Chroma(
            persist_directory="./cohere_db", 
            embedding_function=self.embeddings
        )

    def get_legal_answer(self, question):
        # Find relevant laws
        docs = self.vector_db.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        template = """You are a senior UAE Compliance Officer. Answer using the law segments below. 
        Always mention which Law you are citing.
        
        CONTEXT: {context}
        QUESTION: {question}
        ANSWER:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        response = chain.invoke({"context": context, "question": question})
        return response.content