import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-vulnerabilities',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './vulnerabilities.component.html',
  styleUrl: './vulnerabilities.component.css'
})
export class VulnerabilitiesComponent {
  packages: any[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.getPackages();
  }

  getPackages() {
    this.http.get<any[]>('http://localhost:5000/vulnerabilities').subscribe(data => {
      this.packages = data;
    });
  }
}
