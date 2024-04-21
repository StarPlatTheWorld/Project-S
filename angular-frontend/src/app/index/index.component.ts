import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AppComponent } from '../app.component';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-index',
  standalone: true,
  imports: [AppComponent, RouterLink, RouterOutlet, RouterLinkActive, ReactiveFormsModule, CommonModule],
  templateUrl: './index.component.html',
  styleUrl: './index.component.css'
})
export class IndexComponent implements OnInit {
  addPackageForm: FormGroup = new FormGroup({});

  constructor(private fb: FormBuilder,
              public http: HttpClient
  ){}

  ngOnInit(): void {
    this.addPackageForm = this.fb.group({
      packageName: ['', Validators.required],
      currentVer: ['', Validators.required],
      threatLevel: ['', Validators.required],
      vulnerableVersions: ['', Validators.required],
      vulnerability: ['', Validators.required]
    });
  }

  onSubmit() {
      const packageData = this.addPackageForm.value;
      const headers = new HttpHeaders().set('Content-Type', 'application/json');
      this.http.post('http://localhost:5000/api/add_package', packageData, { headers }).subscribe({
        next: (res) => console.log(res),
        error: (err) => console.log(err),
        complete: () => console.log('Package has been added successfully:', packageData)
      }
      );
  }
}