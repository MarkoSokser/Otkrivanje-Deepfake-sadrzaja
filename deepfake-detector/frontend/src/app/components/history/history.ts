import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe, DatePipe } from '@angular/common';
import { HistoryService, HistoryEntry } from '../../services/history.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [RouterLink, DecimalPipe, DatePipe],
  templateUrl: './history.html',
})
export class HistoryComponent implements OnInit {
  private historyService = inject(HistoryService);
  private toastService = inject(ToastService);

  entries = signal<HistoryEntry[]>([]);
  expandedId = signal<string | null>(null);
  confirmClear = signal(false);

  ngOnInit() {
    this.entries.set(this.historyService.getAll());
  }

  toggleExpand(id: string) {
    this.expandedId.update(current => current === id ? null : id);
  }

  clearAll() {
    if (!this.confirmClear()) {
      this.confirmClear.set(true);
      setTimeout(() => this.confirmClear.set(false), 4000);
      return;
    }
    this.historyService.clearAll();
    this.entries.set([]);
    this.confirmClear.set(false);
    this.toastService.success('Povijest analiza obrisana.');
  }

  formatDate(timestamp: number): string {
    return new Date(timestamp).toLocaleString('hr-HR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  getVerdict(confidence: number): 'REAL' | 'SUSPICIOUS' | 'DEEPFAKE' {
    if (confidence <= 40) return 'REAL';
    if (confidence < 70) return 'SUSPICIOUS';
    return 'DEEPFAKE';
  }
}
