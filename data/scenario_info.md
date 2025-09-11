# OsloMod scenarios overview

## Baseline

 * Agricultural measures from 2021 are assumed to be in place for all years during the simulation period (2017 to 2019). Measures are those registered in RMP in 2021.

 * For "large" wastewater plants, use reported discharges for 2017 to 2019 i.e. measured data where available, and otherwise estimated/interpolated values based on the number of people and fritidsboliger connected to each plant.

 * Assume 2% overflow for all wastewater sites larger than 1000 p.e. For example, if a site has a measured inflow of 1000 tonnes of TOTP and a measured outflow of 400 tonnes, assume nutrient losses at the outflow co-ordinates of 400 + 0.02*1000 = 420 tonnes.

## Scenario A ("Vedtatte tiltak – effekt 2033")

 * Agricultural measures are added to the five "miljøkravsoner", corresponding to "forskrifter om miljøkrav". Outside of the miljøkravsoner, baseline conditions are maintained.

 * All WWTPs larger than 10 000 p.e. are upgraded to `Kjemisk-biologisk m/N-fjerning`, with minimum treatment efficiencies of 80% for TOTN, 95% for BOF5, 95% for KOF and 95% for SS. Any sites that already have better treatment efficiencies than this are not changed (e.g. if a site already has 85% efficiency for TOTN in the baseline, it will keep this efficiency in the scenario).

 * Assume 2% overflow from all sites larger than 1000 p.e. (the same as for the baseline).

## Scenario B ("Ambisiøst scenarie – effekt ca 2040")

 * Agricultural measures are maximised everywhere - both inside and outside of miljøkravsoner.

 * For WWTPs, all measures from Scenario A are included (i.e. the treatment type is changed to `Kjemisk-biologisk m/N-fjerning` and treatment efficiencies are at least 80% for TOTN, 95% for BOF5, 95% for KOF and 95% for SS for all sites >10 000 p.e.).

 * In addition, sites >10 000 p.e. with outflows **directly** to Oslofjorden are upgraded to have at least 85% efficiency for TOTN. The list of sites with direct discharges is the same as those originally defined as "internal sources" in the Martini model. See [here](https://github.com/NIVANorge/oslomod_phase3_teotil/blob/main/data/wwtp_direct_to_oslofjord.csv) for details.

 * WWTPs with capacity between 5000 to 10 000 p.e. are upgraded to have at least 70% efficiency for TOTN. The site type ("renseprinsipp") is not changed.

 * Overflow is reduced to 1% of the inflow for sites >1000 p.e.