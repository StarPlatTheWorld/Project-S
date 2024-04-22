import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-scan-results',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './scan-results.component.html',
  styleUrl: './scan-results.component.css'
})
export class ScanResultsComponent implements OnInit {
  matchedPackages: any[] = [];
  packages: any[] = [];
  constructor(private http: HttpClient){ }

  ngOnInit(): void {
    this.getMatchedPackages();
  }

  getMatchedPackages() {
    this.http.get<any[]>('http://localhost:5000/api/scan_results').subscribe((data: any[]) => {
      if (data.length > 0){
        this.matchedPackages = data[0].matchedPackages;
      }
    })
  }

  mappingThreats: { [key: number]: string } = {
    1: 'Low',
    2: 'Moderate',
    3: 'Severe',
    4: 'Critical'
  };

  ThreatLevel(threatLevel: number): string {
    return this.mappingThreats[threatLevel] || 'Unknown';
  }
}