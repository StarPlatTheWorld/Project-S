import { Component } from '@angular/core';
import { AppComponent } from '../app.component';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-index',
  standalone: true,
  imports: [AppComponent, RouterLink, RouterOutlet, RouterLinkActive],
  templateUrl: './index.component.html',
  styleUrl: './index.component.css'
})
export class IndexComponent {

}
