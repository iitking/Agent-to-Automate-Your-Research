import {
  ResearchTask,
  ResearchSource,
  ResearchFinding,
  ClaimItem,
  ResearchReport,
  ConfigStatus,
} from '../types';

const API_BASE = '/api';

export const api = {
  async listResearch(): Promise<ResearchTask[]> {
    const res = await fetch(`${API_BASE}/research`);
    if (!res.ok) throw new Error('Failed to fetch research tasks');
    return res.json();
  },

  async getResearch(id: string): Promise<ResearchTask> {
    const res = await fetch(`${API_BASE}/research/${id}`);
    if (!res.ok) throw new Error('Failed to fetch research details');
    return res.json();
  },

  async getResearchStatus(id: string) {
    const res = await fetch(`${API_BASE}/research/${id}/status`);
    if (!res.ok) throw new Error('Failed to fetch research status');
    return res.json();
  },

  async getResearchSources(id: string): Promise<ResearchSource[]> {
    const res = await fetch(`${API_BASE}/research/${id}/sources`);
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  async getResearchFindings(id: string): Promise<ResearchFinding[]> {
    const res = await fetch(`${API_BASE}/research/${id}/findings`);
    if (!res.ok) throw new Error('Failed to fetch findings');
    return res.json();
  },

  async getResearchClaims(id: string): Promise<ClaimItem[]> {
    const res = await fetch(`${API_BASE}/research/${id}/claims`);
    if (!res.ok) throw new Error('Failed to fetch verified claims');
    return res.json();
  },

  async getResearchReport(id: string): Promise<ResearchReport> {
    const res = await fetch(`${API_BASE}/research/${id}/report`);
    if (!res.ok) throw new Error('Failed to fetch report');
    return res.json();
  },

  async createResearch(payload: {
    topic: string;
    research_depth: string;
    max_sources: number;
    include_academic_papers: boolean;
    output_formats: string[];
  }): Promise<{ research_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Creation failed' }));
      throw new Error(err.detail || 'Failed to create research task');
    }
    return res.json();
  },

  async deleteResearch(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/research/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete research task');
  },

  async getConfig(): Promise<ConfigStatus> {
    const res = await fetch(`${API_BASE}/config`);
    if (!res.ok) throw new Error('Failed to fetch configuration');
    return res.json();
  },

  async updateConfig(payload: any): Promise<void> {
    const res = await fetch(`${API_BASE}/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update config');
  },

  getExportUrl(id: string, format: 'markdown' | 'pdf' | 'docx'): string {
    return `${API_BASE}/research/${id}/export?format=${format}`;
  },
};
