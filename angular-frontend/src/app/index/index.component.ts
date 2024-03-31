import { Component } from '@angular/core';
import { AppComponent } from '../app.component';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-index',
  standalone: true,
  imports: [AppComponent, RouterLink, RouterOutlet, RouterLinkActive],
  templateUrl: './index.component.html',
  styleUrl: './index.component.css'
})
export class IndexComponent {
  // results: any;
  // formData: FormData = new FormData();

  // constructor(private http: HttpClient) {}

  // onSelectedFile(event: any): void {
  //   const file: File = event.target.files[0];
  //   this.formData = new FormData();
  //   this.formData.append('file', file, file.name);
  // }

  // uploadFile(): void {
  //   this.http.post<any>('http://localhost:5000/api/upload', this.formData).subscribe(
  //     (response) => {
  //       this.results = response.results;
  //     },
  //     (error) => {
  //       console.error('Error uploading file:', error)
  //     }
  //   );
  // }
}
