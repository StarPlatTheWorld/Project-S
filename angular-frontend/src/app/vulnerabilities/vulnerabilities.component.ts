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
    this.http.get<any[]>('http://localhost:5000/api/packages').subscribe(data => {
      this.packages = data;
    });
  }

  mappingThreats: { [key: number]: { label: string, color: string } } = {
    1: { label: 'Low', color: '#198313'},
    2: { label: 'Moderate', color: '#d68100'},
    3: { label: 'Severe', color: '#cc4f19'},
    4: { label: 'Critical', color: '#ad1a1a'}
  };

  ThreatLevel(threatLevel: number): string {
    return this.mappingThreats[threatLevel] ? this.mappingThreats[threatLevel].label : 'Unknown';
  }

  ThreatLevelColor(threatLevel: number): string {
    return this.mappingThreats[threatLevel] ? this.mappingThreats[threatLevel].color : 'black';
  }
}
