import { Component, Input, OnChanges } from '@angular/core';

@Component({
  selector: 'app-confidence-meter',
  standalone: true,
  imports: [],
  templateUrl: './confidence-meter.html',
  styleUrl: './confidence-meter.css',
})
export class ConfidenceMeterComponent implements OnChanges {
  @Input() value = 0; // 0–100
  @Input() label = 'Pouzdanost';

  displayValue = 0;
  barColor = 'bg-green-500';

  ngOnChanges(): void {
    this.displayValue = Math.min(100, Math.max(0, Math.round(this.value)));
    if (this.value <= 40) {
      this.barColor = 'bg-green-500';
    } else if (this.value <= 70) {
      this.barColor = 'bg-yellow-500';
    } else {
      this.barColor = 'bg-red-500';
    }
  }
}
