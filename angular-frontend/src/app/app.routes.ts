import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { IndexComponent } from './index/index.component';
import { ScanResultsComponent } from './scan-results/scan-results.component';
import { VulnerabilitiesComponent } from './vulnerabilities/vulnerabilities.component';


export const routes: Routes = [
    {
        path: "", component: IndexComponent
    },
    {
        path: "results", component: ScanResultsComponent
    },
    {
        path: "vulnerabilities", component: VulnerabilitiesComponent
    }
];
