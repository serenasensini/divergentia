import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-home',
  imports: [
    FormsModule
  ],
  templateUrl: './home.html',
  standalone: true,
  styleUrl: './home.css'
})
export class Home {

  fileName: string = '';
  selectedOption: any;

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      const allowedExtensions = ['.docx', '.pdf'];
      const fileName = file.name.toLowerCase();
      const isValid = allowedExtensions.some(ext => fileName.endsWith(ext));
      if (!isValid) {
        console.error('Formato file non supportato. Seleziona un file .docx o .pdf');
        return;
      }
      console.log('File selezionato:', file.name);
      this.fileName = file.name;
      // Qui puoi aggiungere la logica per processare il file
    }
  }

  onDragOver($event: DragEvent) {
    $event.preventDefault();
    $event.stopPropagation();
    console.log('Dropped over');
    console.log($event);

  }

  onDrop($event: DragEvent) {
    $event.preventDefault();
    $event.stopPropagation();
    console.log('Dropped over');
    console.log($event);
  }

  onSubmit() {
    console.log('Form submitted with file:', this.fileName);
  }

  reset() {
    this.fileName = '';
    this.selectedOption = null;
    console.log('Form reset');
  }
}
