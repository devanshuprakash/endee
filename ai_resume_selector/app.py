import os
import gradio as gr
from resume_processor import ResumeProcessor
from vector_db_manager import VectorDBManager
from llm_ranker import LLMRanker
from dotenv import load_dotenv

load_dotenv()

# Initialize components
processor = ResumeProcessor()
db_manager = VectorDBManager(index_name="resume_selector_index", dimension=1536)
ranker = LLMRanker()

def process_resumes(files):
    if not files:
        return "No files uploaded."
    
    resumes_to_index = []
    for file in files:
        file_path = file.name
        file_name = os.path.basename(file_path)
        
        try:
            text = processor.extract_text(file_path)
            # Use the first 2000 characters for embedding to avoid token limits and keep it efficient
            embedding_text = text[:2000] 
            vector = ranker.get_embedding(embedding_text)
            
            resumes_to_index.append({
                "id": str(hash(file_name)), # Simplified ID
                "vector": vector,
                "meta": {
                    "name": file_name,
                    "text": text[:5000] # Store first 5000 chars in meta for retrieval
                }
            })
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            continue

    if resumes_to_index:
        db_manager.upsert_resumes(resumes_to_index)
        return f"Successfully processed and indexed {len(resumes_to_index)} resumes."
    return "Failed to process resumes."

def screen_candidates(jd_file, job_description, top_k=5):
    # If a JD file is uploaded, extract text from it
    if jd_file is not None:
        try:
            job_description = processor.extract_text(jd_file.name)
        except Exception as e:
            return f"Error reading JD file: {e}"

    if not job_description or not job_description.strip():
        return "Please provide a Job Description (either paste text or upload a file)."
    
    try:
        # 1. Embed JD
        query_vector = ranker.get_embedding(job_description[:2000])
        
        # 2. Retrieve relevant resumes from Endee
        results = db_manager.search(query_vector, top_k=top_k)
        
        if not results:
            return "No matching resumes found in the database. Please ingest resumes first."
        
        # 3. Use LLM to score and rank retrieved candidates
        ranked_results = []
        for res in results:
            resume_text = res.get('meta', {}).get('text', '')
            candidate_name = res.get('meta', {}).get('name', 'Unknown')
            
            evaluation = ranker.evaluate_match(job_description, resume_text)
            ranked_results.append({
                "name": candidate_name,
                "score": evaluation['score'],
                "explanation": evaluation['explanation']
            })
        
        # Sort by score descending
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Format output
        output_text = "### 📋 Job Description Used:\n"
        output_text += f"> {job_description[:200]}{'...' if len(job_description) > 200 else ''}\n\n"
        output_text += "---\n\n### 🏆 Candidate Ranking:\n\n"
        for i, res in enumerate(ranked_results):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            output_text += f"{medal} **{res['name']}** — Match Score: **{res['score']}%**\n"
            output_text += f"   > {res['explanation']}\n\n"
            
        return output_text

    except Exception as e:
        return f"An error occurred during screening: {e}"

# Build UI
with gr.Blocks() as demo:
    gr.Markdown("# 🚀 AI Resume Selector (RAG with Endee)")
    gr.Markdown("Upload candidate resumes and provide a Job Description to rank them using AI.")
    
    with gr.Tab("1. Ingest Resumes"):
        file_input = gr.File(label="Upload Resumes (PDF, DOCX, TXT)", file_count="multiple")
        upload_button = gr.Button("Process & Index", variant="primary")
        upload_status = gr.Textbox(label="Status")
        upload_button.click(process_resumes, inputs=file_input, outputs=upload_status)
    
    with gr.Tab("2. Screen Candidates"):
        gr.Markdown("Provide a Job Description by **uploading a file** or **pasting text** below.")
        jd_file_input = gr.File(label="Upload JD (PDF, DOCX, TXT) — Optional", file_count="single")
        jd_input = gr.Textbox(label="Or Paste Job Description", placeholder="Paste the JD here...", lines=10)
        top_k_slider = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Top K Candidates")
        screen_button = gr.Button("Analyze & Rank", variant="primary")
        ranking_output = gr.Markdown(label="Results")
        screen_button.click(screen_candidates, inputs=[jd_file_input, jd_input, top_k_slider], outputs=ranking_output)

if __name__ == "__main__":
    # Ensure index exists at startup
    try:
        db_manager.initialize_index()
    except:
        print("Warning: Could not initialize index. Make sure Endee server is running at localhost:8080")
    port = int(os.getenv("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, theme=gr.themes.Soft())

