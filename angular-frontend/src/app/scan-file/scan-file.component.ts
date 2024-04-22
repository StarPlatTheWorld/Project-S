import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-scan-file',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './scan-file.component.html',
  styleUrl: './scan-file.component.css'
})
export class ScanFileComponent {
  uploadFile: File | null = null;
  uploadingFile = false;

  constructor(private http: HttpClient, private router: Router) { }

  onUploadFileSelected(event: any) {
    this.uploadFile = event.target.files[0];
    if (this.uploadFile && this.uploadFile.name !== 'requirements.txt'){
      alert('Please select a requirements.txt file.');
      this.uploadFile = null;
    }
  }

  onUploadFile(event: Event) {
    event.preventDefault();
    if (!this.uploadFile) {
      alert('Please select a requirements.txt file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', this.uploadFile);
    this.uploadingFile = true;

    this.http.post<any>('http://localhost:5000/api/upload', formData).subscribe(
      response => {
        alert(response.message);
        this.router.navigate(['/scan_results']);
      }
    );
  }
}