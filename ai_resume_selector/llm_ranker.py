import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMRanker:
    """Handles embedding generation and ranking using OpenAI."""

    def __init__(self, model: str = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_model = "text-embedding-3-small"

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a given text."""
        text = text.replace("\n", " ")
        response = self.client.embeddings.create(input=[text], model=self.embedding_model)
        return response.data[0].embedding

    def evaluate_match(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """
        Evaluates the match between a JD and a resume.
        Returns a score (0-100) and an explanation.
        """
        prompt = f"""
        You are an expert technical recruiter. Evaluate the following resume against the job description.
        
        Job Description:
        {job_description}
        
        Resume Content:
        {resume_text}
        
        Provide a match score (0-100) and a brief explanation (max 3 sentences) highlighting key strengths and missing gaps.
        
        Format your response as:
        Score: [Score]
        Explanation: [Explanation]
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional hiring assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content
        
        # Simple parsing logic
        score = 0
        explanation = ""
        
        try:
            for line in content.split('\n'):
                if line.lower().startswith('score:'):
                    score = int(line.split(':')[1].strip().replace('%', ''))
                elif line.lower().startswith('explanation:'):
                    explanation = line.split(':')[1].strip()
        except:
            explanation = content # Fallback if parsing fails

        return {"score": score, "explanation": explanation}

if __name__ == "__main__":
    # Example:
    # ranker = LLMRanker()
    # print(ranker.get_embedding("Software Engineer with experience in Python and Vector Databases."))
    pass
