import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DataRoutingModule } from './data-routing.module';
import { DataComponent } from './data.component';

@NgModule({
  imports: [
    CommonModule,
    DataRoutingModule
  ],
  declarations: [DataComponent]
})
export class DataModule { }
