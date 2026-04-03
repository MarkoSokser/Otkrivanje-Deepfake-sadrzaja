import { Component, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class HomeComponent {
  openFaqIndex = signal<number | null>(null);

  toggleFaq(index: number) {
    this.openFaqIndex.update(current => current === index ? null : index);
  }

  faqs = [
    {
      question: 'Što je deepfake?',
      answer: 'Deepfake je digitalno manipulirani sadržaj (video, slika ili zvuk) koji se izrađuje pomoću AI tehnologije, posebno generativnih suparničkih mreža (GAN). Sadržaj izgleda realistično, ali je lažan – najčešće se radi o zamjeni ili rekonstrukciji lica.',
    },
    {
      question: 'Koliko je točna analiza?',
      answer: 'Točnost ovisi o korištenom modelu i kvaliteti ulaznog sadržaja. Naš sustav koristi moderne CNN modele (npr. Xception) koji postižu visoku točnost na standardnim datasetima poput FaceForensics++. Preporučujemo tretirati rezultat kao indikator, a ne apsolutnu istinu.',
    },
    {
      question: 'Koje formate datoteka podržavate?',
      answer: 'Podržani formati slika su .jpg, .jpeg i .png. Za videozapise podržavamo .mp4 i .mov. Maksimalna veličina datoteke je 50 MB. Veće datoteke ili drugi formati trenutno nisu podržani.',
    },
    {
      question: 'Kako se čuvaju moje datoteke?',
      answer: 'Vaše datoteke šalju se isključivo na lokalni backend server radi analize i ne pohranjuju se trajno. Nakon obrade rezultat se prikazuje u aplikaciji, a datoteka se briše s poslužitelja. Povijest analiza čuva se samo lokalno u vašem pregledniku.',
    },
    {
      question: 'Što znači razina pouzdanosti?',
      answer: 'Razina pouzdanosti (0–100%) pokazuje koliko je model siguran u svoju procjenu. Vrijednosti ispod 40% upućuju na autentičan sadržaj, između 40–70% zahtijevaju dodatnu provjeru, a iznad 70% snažno upućuju na deepfake manipulaciju.',
    },
  ];
}
