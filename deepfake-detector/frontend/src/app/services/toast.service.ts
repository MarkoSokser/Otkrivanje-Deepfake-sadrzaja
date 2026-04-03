import { Injectable, signal } from '@angular/core';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private nextId = 0;
  toasts = signal<Toast[]>([]);

  success(message: string) {
    this.add('success', message);
  }

  error(message: string) {
    this.add('error', message);
  }

  info(message: string) {
    this.add('info', message);
  }

  remove(id: number) {
    this.toasts.update(list => list.filter(t => t.id !== id));
  }

  private add(type: ToastType, message: string) {
    const id = this.nextId++;
    this.toasts.update(list => [...list, { id, type, message }]);
    setTimeout(() => this.remove(id), 3500);
  }
}
