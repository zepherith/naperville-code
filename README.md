# Naperville Municipal Code

An unofficial copy of the Municipal Code of the City of Naperville, Illinois, kept as one Markdown file per chapter so that changes can be tracked with Git.

**The official text controls.** This copy is for reference only. The official code is published by Municode at [library.municode.com](https://library.municode.com/il/naperville/codes/code_of_ordinances).

- **Current through:** Supplement No. 100 (June 2026), which includes ordinances through Ord. No. 26-040, adopted April 21, 2026.
- **Layout:** one folder per title and one file per chapter. Chapter numbers are padded with zeros so files sort in order (`1-09.md` is Chapter 1-9, and `8-00.5.md` is Chapter 8-0.5). Lettered parts of a chapter (Article 6A, Chapter 9A and so on) are headings inside the chapter's file.
- **Traffic schedules:** the 31 schedules of Section 11-1-5 are kept one per file in `Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/`, because together they run about 260 pages.
- **Each file** starts with its citation, source, the supplement it reflects and the date the text was downloaded.
- **Word downloads:** Titles 1, 3, 4, 5, 6, 7, 8, 9, 10 come from Municode's online text, downloaded as Word, which is born-digital, so it has no OCR errors. Its files say so in `current_through`, keep Municode's tables and footnotes, and show its figures from the title's `images/` folder. To update them, run `tools/municode_word_import.py <file> <date downloaded>` on a fresh download.
- **How the text was made:** the other titles were extracted from Municode's PDF of the code. Wrapped lines were rejoined into paragraphs, tables and schedules were kept in fixed-width blocks, footnotes from the foot of a page were moved below the paragraph they interrupt (shown as quoted notes), and running page headers and footers were removed, along with the supplement sheets, Code Comparative Table and Index. No wording was changed.
- **Scanned pages:** many pages of Municode's PDF are scans of the 2010 printing with a machine-read (OCR) text layer, so some words in this copy may be misread. Where a passage matters, check it against the official code.
- **Updating:** download the full code from Municode as a PDF and run `tools/municode_import.py <file> <date downloaded>` (needs `pdftotext`). It rewrites only the chapters whose text changed and this page.

## Contents

### Title 1: Administrative

| Chapter | Name |
| --- | --- |
| [1-1](Title-01-Administrative/1-01.md) | Official Municipal Code |
| [1-2](Title-01-Administrative/1-02.md) | Saving Clause |
| [1-3](Title-01-Administrative/1-03.md) | Definitions and Rules of Construction |
| [1-4](Title-01-Administrative/1-04.md) | General Penalty |
| [1-5](Title-01-Administrative/1-05.md) | Mayor and City Council |
| [1-6](Title-01-Administrative/1-06.md) | Municipal Officers and Employees |
| [1-7](Title-01-Administrative/1-07.md) | Municipal Personnel Policies |
| [1-8](Title-01-Administrative/1-08.md) | Municipal Departments |
| [1-9](Title-01-Administrative/1-09.md) | Municipal Finances |
| [1-10](Title-01-Administrative/1-10.md) | Municipal Buildings |
| [1-11](Title-01-Administrative/1-11.md) | Comprehensive Plan |
| [1-12](Title-01-Administrative/1-12.md) | Disclosure of Beneficiaries |
| [1-13](Title-01-Administrative/1-13.md) | Conflict of Interest* |
| [1-14](Title-01-Administrative/1-14.md) | Pseba Benefit Administration |

### Title 2: Boards and Commissions

| Chapter | Name |
| --- | --- |
| [2-1](Title-02-Boards-and-Commissions/2-01.md) | General Provisions |
| [2-2](Title-02-Boards-and-Commissions/2-02.md) | Planning and Zoning Commission |
| 2-3 | Reserved (no file) |
| [2-4](Title-02-Boards-and-Commissions/2-04.md) | Building Review Board |
| [2-5](Title-02-Boards-and-Commissions/2-05.md) | Human Rights and Fair Housing Commission |
| [2-6](Title-02-Boards-and-Commissions/2-06.md) | Naper Settlement Museum Board |
| [2-7](Title-02-Boards-and-Commissions/2-07.md) | Board of Library Trustees |
| [2-8](Title-02-Boards-and-Commissions/2-08.md) | Financial Advisory Board |
| [2-9](Title-02-Boards-and-Commissions/2-09.md) | Transportation Advisory Board |
| [2-10](Title-02-Boards-and-Commissions/2-10.md) | Public Utilities Advisory Board |
| [2-11](Title-02-Boards-and-Commissions/2-11.md) | Sister Cities Commission |
| [2-12](Title-02-Boards-and-Commissions/2-12.md) | Riverwalk Commission |
| [2-13](Title-02-Boards-and-Commissions/2-13.md) | Board of Fire and Police Commissioners |
| [2-14](Title-02-Boards-and-Commissions/2-14.md) | Pension Plan Boards |
| [2-15](Title-02-Boards-and-Commissions/2-15.md) | Historic Preservation Commission |
| [2-16](Title-02-Boards-and-Commissions/2-16.md) | Advisory Commission on Disabilities |
| [2-17](Title-02-Boards-and-Commissions/2-17.md) | Foreign Fire Insurance Tax Board |
| [2-18](Title-02-Boards-and-Commissions/2-18.md) | Local Liquor Commission |
| [2-19](Title-02-Boards-and-Commissions/2-19.md) | Special Events and Community Arts Commission |

### Title 3: Business and License Regulations

| Chapter | Name |
| --- | --- |
| [3-1](Title-03-Business-and-License-Regulations/3-01.md) | Municipal Occupation Taxes |
| [3-2](Title-03-Business-and-License-Regulations/3-02.md) | General License Regulations |
| [3-3](Title-03-Business-and-License-Regulations/3-03.md) | Liquor and Tobacco Control* |
| [3-4](Title-03-Business-and-License-Regulations/3-04.md) | Amusements |
| [3-5](Title-03-Business-and-License-Regulations/3-05.md) | Contractors |
| 3-6 | Retail Dealers and Establishments (no file: repealed by Ord. 92-144, 8-4-1992) |
| [3-7](Title-03-Business-and-License-Regulations/3-07.md) | Solicitation in the Public Way* |
| [3-8](Title-03-Business-and-License-Regulations/3-08.md) | Taxicab Services* |
| [3-9](Title-03-Business-and-License-Regulations/3-09.md) | Amplifiers |
| [3-10](Title-03-Business-and-License-Regulations/3-10.md) | Hotel and Motel Use Tax |
| [3-11](Title-03-Business-and-License-Regulations/3-11.md) | Simplified Municipal Telecommu Nications Tax |
| [3-12](Title-03-Business-and-License-Regulations/3-12.md) | Municipal Motor Fuel Tax |
| 3-13 | Reserved (no file) |
| [3-14](Title-03-Business-and-License-Regulations/3-14.md) | Taxpayers' Bill of Rights |
| [3-15](Title-03-Business-and-License-Regulations/3-15.md) | Pedicab Regulations |
| [3-16](Title-03-Business-and-License-Regulations/3-16.md) | Commercial Quadricylces |
| 3-17 | Reserved (no file) |
| [3-18](Title-03-Business-and-License-Regulations/3-18.md) | Short-term Residential Rentals* |
| [3-19](Title-03-Business-and-License-Regulations/3-19.md) | Regulation of the Commercial Sale of Assault Rifles* |
| [3-20](Title-03-Business-and-License-Regulations/3-20.md) | Massage Establishments* |

### Title 4: Health and Sanitation

| Chapter | Name |
| --- | --- |
| [4-1](Title-04-Health-and-Sanitation/4-01.md) | General Health Regulations |
| [4-2](Title-04-Health-and-Sanitation/4-02.md) | Residential and Commercial Waste, Refuse, Recyclable Materials, and Landscape Waste |
| [4-3](Title-04-Health-and-Sanitation/4-03.md) | Trees, Plants, Weeds and Composting |
| [4-4](Title-04-Health-and-Sanitation/4-04.md) | Hazardous Materials |
| [4-5](Title-04-Health-and-Sanitation/4-05.md) | Inoperable Motor Vehicles |
| [4-6](Title-04-Health-and-Sanitation/4-06.md) | Heat and Heating Facilities |
| [4-7](Title-04-Health-and-Sanitation/4-07.md) | Body Art, Tattooing, and Body Piercing |
| [4-8](Title-04-Health-and-Sanitation/4-08.md) | Mosquito Control |
| [4-9](Title-04-Health-and-Sanitation/4-09.md) | Smoke Free |
| [4-10](Title-04-Health-and-Sanitation/4-10.md) | Direct Sales of Baked Goods From Home Kitchen Operation |

### Title 5: Building Regulations

| Chapter | Name |
| --- | --- |
| [5-1](Title-05-Building-Regulations/5-01.md) | Building Codes |
| [5-2](Title-05-Building-Regulations/5-02.md) | Construction and Fire Prevention Regulations |
| 5-3 | Dangerous Buildings (no file: repealed by Ord. 02-31, 2-19-2002, eff. 4-8-2002) |
| 5-4 | Reserved (no file) |
| 5-5 | Swimming Pools (no file: repealed by Ord. 02-31, 2-19-2002, eff. 4-8-2002) |
| [5-6](Title-05-Building-Regulations/5-06.md) | Flood Hazard Areas |
| [5-7](Title-05-Building-Regulations/5-07.md) | Storm Runoff Control |
| [5-8](Title-05-Building-Regulations/5-08.md) | Off Street Parking Facilities |
| [5-9](Title-05-Building-Regulations/5-09.md) | Soil Erosion and Sedimentation Control |
| [5-10](Title-05-Building-Regulations/5-10.md) | Landscaping, Screening and Tree Preservation |
| [5-11](Title-05-Building-Regulations/5-11.md) | Condominium Regulations |

### Title 6: Zoning Regulations

| Chapter | Name |
| --- | --- |
| [6-1](Title-06-Zoning-Regulations/6-01.md) | Zoning Title, Purpose, Definitions |
| [6-2](Title-06-Zoning-Regulations/6-02.md) | General Zoning Provisions |
| [6-3](Title-06-Zoning-Regulations/6-03.md) | Administration and Enforcement* |
| [6-4](Title-06-Zoning-Regulations/6-04.md) | Planned Unit Developments |
| [6-5](Title-06-Zoning-Regulations/6-05.md) | Zoning Districts; Map |
| [6-6](Title-06-Zoning-Regulations/6-06.md) | Residence Districts |
| [6-7](Title-06-Zoning-Regulations/6-07.md) | Business Districts |
| [6-8](Title-06-Zoning-Regulations/6-08.md) | Industrial Districts |
| [6-9](Title-06-Zoning-Regulations/6-09.md) | Off Street Parking |
| [6-10](Title-06-Zoning-Regulations/6-10.md) | Nonconforming Uses |
| [6-11](Title-06-Zoning-Regulations/6-11.md) | Historic Preservation* |
| [6-12](Title-06-Zoning-Regulations/6-12.md) | Adult Uses |
| [6-13](Title-06-Zoning-Regulations/6-13.md) | Regulations for Telecommunication Facilities* |
| [6-14](Title-06-Zoning-Regulations/6-14.md) | Performance Standards |
| [6-15](Title-06-Zoning-Regulations/6-15.md) | Small Wind and Solar Renewable Energy Systems |
| [6-16](Title-06-Zoning-Regulations/6-16.md) | Signs* |

### Title 7: Subdivision Regulations

| Chapter | Name |
| --- | --- |
| [7-1](Title-07-Subdivision-Regulations/7-01.md) | General Provisions |
| [7-2](Title-07-Subdivision-Regulations/7-02.md) | Subdivision Plat Procedures* |
| [7-3](Title-07-Subdivision-Regulations/7-03.md) | Required Improvements |
| [7-4](Title-07-Subdivision-Regulations/7-04.md) | Design Standards |
| [7-5](Title-07-Subdivision-Regulations/7-05.md) | Subdivision Names |

### Title 8: Public Utilities

| Chapter | Name |
| --- | --- |
| [8-0.5](Title-08-Public-Utilities/8-00.5.md) | Naperville Public Utilities Customer Bill of Rights |
| [8-1](Title-08-Public-Utilities/8-01.md) | Electricity |
| [8-2](Title-08-Public-Utilities/8-02.md) | Municipal Water and Sewer |
| [8-3](Title-08-Public-Utilities/8-03.md) | Utility Service |

### Title 9: Public Ways and Property

| Chapter | Name |
| --- | --- |
| [9-1](Title-09-Public-Ways-and-Property/9-01.md) | Streets and Sidewalks |
| [9-2](Title-09-Public-Ways-and-Property/9-02.md) | Street Numbering |
| [9-3](Title-09-Public-Ways-and-Property/9-03.md) | Urban Forest Protection* |
| [9-4](Title-09-Public-Ways-and-Property/9-04.md) | Block Parties |
| [9-5](Title-09-Public-Ways-and-Property/9-05.md) | City Parks |

### Title 10: Police Regulations

| Chapter | Name |
| --- | --- |
| [10-1](Title-10-Police-Regulations/10-01.md) | Civil Emergencies |
| [10-2](Title-10-Police-Regulations/10-02.md) | General Offenses |
| [10-3](Title-10-Police-Regulations/10-03.md) | Minors* |
| [10-4](Title-10-Police-Regulations/10-04.md) | Animal Control |
| 10-5 | Reserved (no file) |
| [10-6](Title-10-Police-Regulations/10-06.md) | Public Safety Emergency Response Alarm System |
| [10-7](Title-10-Police-Regulations/10-07.md) | Fireworks; Explosives |
| [10-8](Title-10-Police-Regulations/10-08.md) | Administrative Fees* |
| [10-9](Title-10-Police-Regulations/10-09.md) | Pawnbrokers and Secondhand Dealers 10-9-1 : Definitions 10-9-2: Prohibited Acts 10-9-3: Authorized Online Database Reporting 10-9-4: Waiting Period 10-9-5: Prohibited Transactions 10-9-6: Inspection of Records 10-9-7: Registration 10-9-8: Penalty Provisions |

### Title 11: Motor Vehicles and Traffic

| Chapter | Name |
| --- | --- |
| [11-1](Title-11-Motor-Vehicles-and-Traffic/11-01.md) | General Traffic Provisions |
| [11-1-5 Sch. I](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-01.md) | Stop Streets |
| [11-1-5 Sch. II](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-02.md) | Yield Right-Of-Way Streets |
| [11-1-5 Sch. III](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-03.md) | One-Way Streets |
| [11-1-5 Sch. IV](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-04.md) | Speed Limits |
| [11-1-5 Sch. V](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-05.md) | Non-Designated Local Highways |
| [11-1-5 Sch. VI](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-06.md) | No Parking Zones |
| [11-1-5 Sch. VII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-07.md) | Limited Parking |
| [11-1-5 Sch. VIII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-08.md) | Fee Parking Zones |
| [11-1-5 Sch. IX](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-09.md) | Parking By Permit |
| [11-1-5 Sch. X](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-10.md) | City Parking Lots |
| [11-1-5 Sch. XI](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-11.md) | Central Business District Restrictions |
| [11-1-5 Sch. XII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-12.md) | Tow Away Zones |
| [11-1-5 Sch. XIII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-13.md) | Loading Zones |
| [11-1-5 Sch. XIV](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-14.md) | Cabstands And Bus Stops |
| [11-1-5 Sch. XV](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-15.md) | Traffic-Control Signal Intersections |
| [11-1-5 Sch. XVI](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-16.md) | Lane Usage Limitations |
| [11-1-5 Sch. XVII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-17.md) | Turns Prohibited |
| [11-1-5 Sch. XVIII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-18.md) | Traffic Regulated By Agreement |
| [11-1-5 Sch. XIX](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-19.md) | Limited Load Streets |
| [11-1-5 Sch. XX](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-20.md) | Right-Of-Way Streets |
| [11-1-5 Sch. XXI](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-21.md) | Handicapped Parking |
| [11-1-5 Sch. XXII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-22.md) | Signs And Signals |
| [11-1-5 Sch. XXIII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-23.md) | Compact Car Parking |
| [11-1-5 Sch. XXIV](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-24.md) | U-Turns Prohibited |
| [11-1-5 Sch. XXV](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-25.md) | Cars Only Parking |
| [11-1-5 Sch. XXVI](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-26.md) | Traffic Prohibited |
| [11-1-5 Sch. XXVII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-27.md) | Reserved |
| [11-1-5 Sch. XXVIII](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-28.md) | Motorcycle Parking |
| [11-1-5 Sch. XXIX](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-29.md) | Traffic Calming Locations |
| [11-1-5 Sch. XXX](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-30.md) | Overnight Parking Exemptions |
| [11-1-5 Sch. XXXI](Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/Sch-31.md) | School Parking Restrictions |
| [11-2](Title-11-Motor-Vehicles-and-Traffic/11-02.md) | Parking |
| [11-3](Title-11-Motor-Vehicles-and-Traffic/11-03.md) | Truck Routes |
| [11-4](Title-11-Motor-Vehicles-and-Traffic/11-04.md) | Bicycles, Skateboards, Roller Skates, In-line Skates, E-bikes, E-scooters, and Other Mobility Devices* |
| [11-5](Title-11-Motor-Vehicles-and-Traffic/11-05.md) | Motor Vehicle Tows |
| [11-6](Title-11-Motor-Vehicles-and-Traffic/11-06.md) | Neighborhood Traffic Circle Intersections |

### Title 12: Human Rights and Fair Housing

| Chapter | Name |
| --- | --- |
| [12-1](Title-12-Human-Rights-and-Fair-Housing/12-01.md) | Declaration of Policy |
| [12-2](Title-12-Human-Rights-and-Fair-Housing/12-02.md) | Definitions |
| [12-3](Title-12-Human-Rights-and-Fair-Housing/12-03.md) | Unlawful Discrimination Prohibited |
| [12-4](Title-12-Human-Rights-and-Fair-Housing/12-04.md) | Fair Housing |
| [12-5](Title-12-Human-Rights-and-Fair-Housing/12-05.md) | Complaints |
| [12-6](Title-12-Human-Rights-and-Fair-Housing/12-06.md) | Hearing Procedure |
