# Data Source Research Notes

## SAP Fuel & Procurement
- **Format researched:** SAP ECC/BW exports (MB51/SE16 style) and flat-file extracts with German headers.
- **Why chosen:** CSV exports are common in enterprise workflows and match the reality of sustainability teams receiving ad‑hoc extracts.
- **Sample data shape:** Plant code (Werk), material description, quantity (Menge), unit (ME), cost center, vendor, posting date, fuel type, currency.
- **Realistic assumptions:** Units vary across plants (liters, gallons, kg, tonnes). Dates vary by locale. German headers appear in localized installations.
- **Production limitations:** Real SAP extracts often include many more columns (document IDs, movement types) and large volumes that require incremental processing.

## Utility Electricity
- **Format researched:** Utility portal CSV exports with meter-level billing data.
- **Why chosen:** CSV aligns with how facility teams download bills and includes billing periods and tariffs.
- **Sample data shape:** Meter ID, billing start/end, kWh usage, peak/off-peak usage, tariff plan, provider.
- **Realistic assumptions:** Billing periods do not align to months; duplicates and overlaps occur; sudden spikes can indicate meter issues.
- **Production limitations:** Some utilities only provide PDFs; OCR or API integrations would be required.

## Corporate Travel
- **Format researched:** Concur/Navan expense reports with travel legs and hotel stays.
- **Why chosen:** CSV export is a standard feature for corporate travel platforms and includes travel type and routing.
- **Sample data shape:** Employee ID, travel type, origin/destination airports, dates, airline, hotel, transport mode, distance.
- **Realistic assumptions:** Flights may lack distances; airport lookup is needed; trips can include multiple modes.
- **Production limitations:** True itineraries can have multi-leg flights and routing complexity that requires segment-level modeling.
