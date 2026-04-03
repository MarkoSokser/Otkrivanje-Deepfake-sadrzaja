import { Component, ElementRef, EventEmitter, HostListener, Input, Output, ViewChild, signal } from '@angular/core';

const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'video/mp4',
  'video/quicktime',
  'video/x-msvideo',
];

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [],
  templateUrl: './file-upload.html',
  styleUrl: './file-upload.css',
})
export class FileUploadComponent {
  @Input() accept = '.jpg,.jpeg,.png,.mp4,.mov,.avi';
  @Input() maxSizeMB = 50;

  @Output() fileSelected = new EventEmitter<File>();
  @Output() validationError = new EventEmitter<string>();

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  isDragOver = signal(false);
  errorMessage = signal<string | null>(null);

  @HostListener('dragover', ['$event'])
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(true);
  }

  @HostListener('dragleave', ['$event'])
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(false);
  }

  @HostListener('drop', ['$event'])
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      this.processFile(file);
    }
  }

  openFilePicker(): void {
    this.fileInput.nativeElement.click();
  }

  onFileInputChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.processFile(file);
    }
    input.value = '';
  }

  private processFile(file: File): void {
    this.errorMessage.set(null);

    if (!ALLOWED_MIME_TYPES.includes(file.type)) {
      const msg = 'Nepodržani format datoteke. Dozvoljeni formati: JPG, PNG, MP4, MOV, AVI.';
      this.errorMessage.set(msg);
      this.validationError.emit(msg);
      return;
    }

    const maxBytes = this.maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      const msg = `Datoteka je prevelika. Maksimalna veličina je ${this.maxSizeMB} MB.`;
      this.errorMessage.set(msg);
      this.validationError.emit(msg);
      return;
    }

    this.fileSelected.emit(file);
  }
}
