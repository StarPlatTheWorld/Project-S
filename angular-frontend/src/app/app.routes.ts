import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { IndexComponent } from './index/index.component';
import { ScanResultsComponent } from './scan-results/scan-results.component';
import { VulnerabilitiesComponent } from './vulnerabilities/vulnerabilities.component';
import { ScanFileComponent } from './scan-file/scan-file.component';


export const routes: Routes = [
    {
        path: "", component: IndexComponent
    },
    {
        path: "scan", component: ScanFileComponent
    },
    {
        path: "packages", component: VulnerabilitiesComponent
    },
    {
        path: "scan_results", component: ScanResultsComponent
    },
    {
        path: "**", redirectTo: ""
    }
];
