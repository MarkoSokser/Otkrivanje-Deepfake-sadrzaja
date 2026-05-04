import { Component, inject } from '@angular/core';
import { ToastService, Toast } from '../../services/toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  templateUrl: './toast.html',
})
export class ToastComponent {
  toastService = inject(ToastService);

  get toasts(): Toast[] {
    return this.toastService.toasts();
  }

  dismiss(id: number) {
    this.toastService.remove(id);
  }

  trackById(_: number, t: Toast) {
    return t.id;
  }
}
