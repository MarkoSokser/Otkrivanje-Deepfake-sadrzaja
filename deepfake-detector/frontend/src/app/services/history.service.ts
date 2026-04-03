import { Injectable } from '@angular/core';

export interface HistoryEntry {
  id: string;
  timestamp: number;
  verdict: 'REAL' | 'DEEPFAKE';
  confidence: number;
  media_type: 'image' | 'video';
  model_used: string;
  explanation: string;
  fileName: string;
}

const STORAGE_KEY = 'deepfake_history';
const MAX_ENTRIES = 20;

@Injectable({ providedIn: 'root' })
export class HistoryService {
  getAll(): HistoryEntry[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  save(entry: Omit<HistoryEntry, 'id' | 'timestamp'>) {
    const all = this.getAll();
    const newEntry: HistoryEntry = {
      ...entry,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    };
    const updated = [newEntry, ...all].slice(0, MAX_ENTRIES);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  }

  clearAll() {
    localStorage.removeItem(STORAGE_KEY);
  }
}
