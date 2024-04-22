import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScanFileComponent } from './scan-file.component';

describe('ScanFileComponent', () => {
  let component: ScanFileComponent;
  let fixture: ComponentFixture<ScanFileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScanFileComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ScanFileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
