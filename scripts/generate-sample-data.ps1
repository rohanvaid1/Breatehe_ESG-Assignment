param(
    [int]$Rows = 120
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$sampleDir = Join-Path (Split-Path -Parent $root) "sample-data"
New-Item -ItemType Directory -Force -Path $sampleDir | Out-Null

function Get-RandomElement($list) { return $list | Get-Random }

# SAP Fuel & Procurement (German headers)
$sapHeaders = @(
    "Werk","Materialkurztext","Menge","ME","Kostenstelle","Lieferant","Buchungsdatum","Kraftstoffart","Währung"
)
$plants = @("DE01","DE02","PL07","CZ12","NL03")
$materials = @("Diesel fuel","Petrol blend","Boiler kerosene","Bulk LPG","Industrial lubricant")
$units = @("L","l","gal","KG","t","tonnes")
$costCenters = @("CC-100","CC-210","CC-330","CC-480")
$vendors = @("BASF AG","Shell DE","TotalEnergies","Orlen","BP Europe")
$fuelTypes = @("diesel","petrol","kerosene","natural gas","unknown")
$currencies = @("EUR","USD","GBP")

$sapPath = Join-Path $sampleDir "sap_fuel_procurement.csv"
Set-Content -Path $sapPath -Value ($sapHeaders -join ",") -Encoding UTF8
1..$Rows | ForEach-Object {
    $row = @{
        "Werk" = Get-RandomElement $plants
        "Materialkurztext" = Get-RandomElement $materials
        "Menge" = if ($_ % 37 -eq 0) { "" } elseif ($_ % 29 -eq 0) { "-15" } else { [math]::Round((Get-Random -Minimum 10 -Maximum 5000) / 3.7, 2) }
        "ME" = Get-RandomElement $units
        "Kostenstelle" = Get-RandomElement $costCenters
        "Lieferant" = Get-RandomElement $vendors
        "Buchungsdatum" = if ($_ % 10 -eq 0) { (Get-Date).AddDays(-$_).ToString("dd.MM.yyyy") } else { (Get-Date).AddDays(-$_).ToString("yyyy/MM/dd") }
        "Kraftstoffart" = Get-RandomElement $fuelTypes
        "Währung" = Get-RandomElement $currencies
    }
    ($sapHeaders | ForEach-Object { $row[$_] }) -join "," | Add-Content -Path $sapPath -Encoding UTF8
}

# Utility electricity
$utilityHeaders = @(
    "meter_id","billing_start","billing_end","kwh_usage","peak_usage","off_peak_usage","tariff_plan","utility_provider"
)
$meters = @("MTR-1001","MTR-2044","MTR-3099","MTR-4410")
$tariffs = @("T1-Standard","T2-Industrial","PeakSaver","GreenFlex")
$providers = @("E.ON","EnBW","RWE","Vattenfall")

$utilityPath = Join-Path $sampleDir "utility_electricity.csv"
Set-Content -Path $utilityPath -Value ($utilityHeaders -join ",") -Encoding UTF8
1..$Rows | ForEach-Object {
    $start = (Get-Date).AddDays(-($_ * 3))
    $end = $start.AddDays(29 + (Get-Random -Minimum -3 -Maximum 3))
    $usage = if ($_ % 33 -eq 0) { "" } elseif ($_ % 22 -eq 0) { (Get-Random -Minimum 4000 -Maximum 12000) } else { (Get-Random -Minimum 800 -Maximum 3200) }
    $row = @{
        "meter_id" = Get-RandomElement $meters
        "billing_start" = $start.ToString("yyyy-MM-dd")
        "billing_end" = if ($_ % 15 -eq 0) { $start.AddDays(10).ToString("yyyy-MM-dd") } else { $end.ToString("yyyy-MM-dd") }
        "kwh_usage" = $usage
        "peak_usage" = if ($usage) { [math]::Round($usage * 0.6, 1) } else { "" }
        "off_peak_usage" = if ($usage) { [math]::Round($usage * 0.4, 1) } else { "" }
        "tariff_plan" = Get-RandomElement $tariffs
        "utility_provider" = Get-RandomElement $providers
    }
    ($utilityHeaders | ForEach-Object { $row[$_] }) -join "," | Add-Content -Path $utilityPath -Encoding UTF8
}

# Corporate travel
$travelHeaders = @(
    "employee_id","travel_type","origin","destination","departure_date","return_date","airline","hotel_name","transport_mode","distance_km"
)
$employees = 1001..1055
$airports = @("FRA","LHR","JFK","SFO","SIN","DXB","DEL","BOM")
$airlines = @("Lufthansa","Emirates","United","British Airways","Singapore Airlines")
$hotels = @("Hilton","Marriott","NH Frankfurt","Hyatt Place","Radisson")
$transport = @("taxi","rail","flight")

$travelPath = Join-Path $sampleDir "corporate_travel.csv"
Set-Content -Path $travelPath -Value ($travelHeaders -join ",") -Encoding UTF8
1..$Rows | ForEach-Object {
    $travelType = Get-RandomElement @("flight","hotel","taxi","rail")
    $origin = Get-RandomElement $airports
    $destination = if ($_ % 40 -eq 0) { $origin } else { Get-RandomElement $airports }
    $depart = (Get-Date).AddDays(-($_ * 2))
    $return = $depart.AddDays((Get-Random -Minimum 1 -Maximum 8))
    $distance = if ($travelType -eq "flight" -and $_ % 9 -ne 0) { (Get-Random -Minimum 350 -Maximum 9800) } else { "" }
    $row = @{
        "employee_id" = Get-RandomElement $employees
        "travel_type" = $travelType
        "origin" = $origin
        "destination" = $destination
        "departure_date" = $depart.ToString("yyyy-MM-dd")
        "return_date" = $return.ToString("yyyy-MM-dd")
        "airline" = if ($travelType -eq "flight") { Get-RandomElement $airlines } else { "" }
        "hotel_name" = if ($travelType -eq "hotel") { Get-RandomElement $hotels } else { "" }
        "transport_mode" = if ($travelType -in @("taxi","rail")) { Get-RandomElement $transport } else { "" }
        "distance_km" = $distance
    }
    ($travelHeaders | ForEach-Object { $row[$_] }) -join "," | Add-Content -Path $travelPath -Encoding UTF8
}

Write-Host "Sample data written to $sampleDir"
