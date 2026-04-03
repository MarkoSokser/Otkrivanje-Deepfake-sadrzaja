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
  barGradient = 'from-green-500 to-green-400';

  ngOnChanges(): void {
    this.displayValue = Math.min(100, Math.max(0, Math.round(this.value)));
    if (this.value <= 40) {
      this.barGradient = 'from-green-600 to-green-400';
    } else if (this.value <= 70) {
      this.barGradient = 'from-yellow-500 to-orange-400';
    } else {
      this.barGradient = 'from-orange-500 to-red-500';
    }
  }
}
