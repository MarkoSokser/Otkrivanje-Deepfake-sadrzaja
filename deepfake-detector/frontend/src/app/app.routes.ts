import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home';
import { AnalyzeComponent } from './components/analyze/analyze';
import { ResultsComponent } from './components/results/results';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'analyze', component: AnalyzeComponent },
  { path: 'results', component: ResultsComponent },
  { path: '**', redirectTo: '' },
];
