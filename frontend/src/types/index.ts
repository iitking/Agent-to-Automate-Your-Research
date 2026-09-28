export interface ResearchTask {
  id: string;
  user_id: string;
  topic: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  research_depth: 'quick' | 'standard' | 'comprehensive';
  created_at: string;
  completed_at?: string;
  sources_count: number;
  findings_count: number;
  claims_count: number;
  error_message?: string;
  current_agent?: string;
  progress_percentage: number;
}

export interface ResearchSource {
  id: string;
  research_task_id: string;
  title: string;
  url: string;
  domain?: string;
  author?: string;
  published_at?: string;
  source_type: 'web' | 'academic' | 'pdf';
  provider: 'tavily' | 'brave' | 'arxiv' | 'semantic_scholar' | 'crossref' | 'live_web';
  relevance_score: number;
  credibility_score: number;
  extraction_status: 'pending' | 'success' | 'failed' | 'snippet_only';
  evaluation_notes?: string;
  snippet?: string;
  content_length: number;
  created_at?: string;
}

export interface ResearchFinding {
  id: string;
  research_task_id: string;
  question: string;
  finding: string;
  confidence: number;
  source_ids: string[];
}

export interface ClaimItem {
  id: string;
  research_task_id: string;
  claim_text: string;
  verification_status: 'supported' | 'partially_supported' | 'contradicted' | 'insufficient_evidence';
  supporting_passage?: string;
  page_number?: number;
  source_id?: string;
  source_title?: string;
  source_url?: string;
  confidence_score: number;
}

export interface ResearchReport {
  id: string;
  research_task_id: string;
  markdown_content: string;
  pdf_path?: string;
  docx_path?: string;
  word_count: number;
  references_count: number;
  created_at: string;
}

export interface ExecutionLog {
  agent: string;
  status: string;
  time: number;
  message: string;
  created_at?: string;
}

export interface ConfigStatus {
  llm_provider: string;
  llm_model: string;
  gemini_key_configured: boolean;
  openai_key_configured: boolean;
  tavily_key_configured: boolean;
  brave_key_configured: boolean;
  database_url: string;
  max_sources: number;
}
