# Oversikt over OsloMod-scenarier

## Basisscenariet

 * Jordbrukstiltak fra 2021 antas å være på plass for alle år i simuleringsperioden (2017 til 2019). Tiltakene er de som er registrert i RMP i 2021.

 * For "store" avløpsanlegg er utslippene basert på data i Miljødirektoratets database for 2017 til 2019. Målte verdier brukes der de er tilgjengelige, ellers estimeres/interpoleres de basert på antall personer og fritidsboliger tilknyttet hvert anlegg.

 * Overløp på 2 % antas for alle avløpsanlegg større enn 1000 personekvivalenter (pe). Hvis for eksempel et anlegg har et målt tilsig på 1000 tonn TOTP og et målt utløp på 400 tonn, antar basisscenariet TOTP-tap ved utløpskoordinatene `400 + 0,02*1000 = 420` tonn.

## Scenario A ("Vedtatte tiltak – effekt 2033")

 * Jordbrukstiltak legges til de fem miljøkravsonene, tilsvarende "forskrifter om miljøkrav". Utenom miljøkravsonene opprettholdes grunnlinjeforholdene.

 * Alle avløpsanlegg større enn 10 000 pe oppgraderes til «Kjemisk-biologisk m/N-fjerning», med minimum renseeffektivitet på 80 % for TOTN, 95 % for BOF5, 95 % for KOF, og 95 % for SS. Alle anlegg som allerede har bedre renseeffektivitet enn dette endres ikke (f.eks. hvis et anlegg allerede har 85 % effektivitet for TOTN i basisscenariet, vil det beholde denne effektiviteten i dette scenariet).

 * Anta 2 % overløp fra alle anlegg større enn 1000 pe (det samme som for basisscenariet).

## Scenario B ("Ambisiøst scenario – effekt ca 2040")

 * Jordbrukstiltak maksimeres overalt - både innenfor og utenfor miljøkravsoner.

 * For avløpsrensing er alle tiltak fra Scenario A inkludert (dvs. rensetypen endres til «Kjemisk-biologisk m/N-fjerning» og renseeffektiviteten er minst 80 % for TOTN, 95 % for BOF5, 95 % for KOF, og 95 % for SS for alle anlegg >10 000 pe).

 * I tillegg oppgraderes anlegg >10 000 pe med utløp **direkte** til Oslofjorden til å ha minst 85 % effektivitet for TOTN. Listen over anlegg med direkte utslipp er den samme som de som er definert som «interne kilder» i den opprinnelige Martini-modellen. Se [her](https://github.com/NIVANorge/oslomod_phase3_teotil/blob/main/data/wwtp_direct_to_oslofjord.csv) for detaljer.

 * Avløpsanlegg med kapasitet mellom 5000 og 10 000 pe oppgraderes til å ha minst 70 % effektivitet for TOTN. Renseprinsippet endres imidlertid ikke.

* Overløp reduseres til 1 % av tilløpet for anlegg >1000 pe.