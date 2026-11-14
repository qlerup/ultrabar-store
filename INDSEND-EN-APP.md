# Fra egen app til UltraBar Store — trin for trin

Din kode bor i **dit eget offentlige GitHub-repository**. Du forker kun
`qlerup/ultrabar-store` for at foreslå en registrering eller opdatering. En fork
giver ikke andre ret til at udgive opdateringer under din eksisterende Store-identitet.
Du styrer dit eget repository; Store-ejeren godkender hver Store-udgivelse.

## 1. Vælg typen

| Type i filen | Hvad brugeren får | Pakke |
| --- | --- | --- |
| `corebar-app` | Selvstændig Android-app, installeret og kørt på Core | Færdig, signeret `app.apk` |
| `corebar-widget` | Widget i venstre bibliotek, trækkes ind på baren, indstilles til højre og aktiveres med Deploy | `widget.json` |
| `studio-plugin` | En samling indstillinger/presets til eksisterende widgettyper | `plugin.json` |

Vivo Screen Sync er en **corebar-app**, fordi den kører en baggrundstjeneste på Core.
Clock & Date, Drive Usage og System Monitor er **corebar-widget**-pakker.
En widgetpakke kan indeholde flere muligheder; hver placeret blok har egne indstillinger.
`studio-plugin` giver ikke mulighed for at køre vilkårlig Python, JavaScript eller programmer på PC'en.

Alle typer bruger `submissions/<unik-pakkemappe>/`. Der er ikke tre forskellige
mappetræer: feltet **type** i `repository.json` og `manifest.json` bestemmer typen,
og Actions afviser uoverensstemmelser. Én PR må kun ændre én pakkemappe.

## 2. Opret dit eget repository

1. Log ind på GitHub med den personlige konto, der skal eje pakken.
2. Vælg **New repository**, giv det et navn og vælg **Public**.
3. Tilføj din egen kildekode, `README.md`, `LICENSE` og `icon.png`.
4. Ikonet skal være en statisk PNG på 256×256 eller 512×512, højst 256 KiB.
   Lever det firkantet; Studio afrunder selv hjørnerne.
5. README skal forklare funktion, opsætning, tilladelser, databrug, krav,
   udførte tests og kendte begrænsninger. LICENSE skal give mulighed for den
   distribution, du ønsker gennem Store. Medtag ikke nøgler, tokens eller private enhedsoplysninger.

For **widgets** ligger `widget.json` i roden. Se `examples/clock/widget.json`.
Understøttede typer er clock, cpu, memory, gpu og disk. `kindOptions` kan give
CPU/RAM/GPU-valg pr. blok og kræver Studio 0.24+. Disk får valg af drev.
JSON-formatet kan ikke tilføje en helt ny renderer eller vilkårlig kode.

For **presets** ligger `plugin.json` i roden:

```json
{
  "pluginApi": 1,
  "widgets": [{"name": "My RAM preset", "kind": "memory", "accent": "#A5DFCB"}]
}
```

For **Android-apps** skal roden indeholde `AndroidManifest.xml`, hele kilden
og byggeinstruktioner. Byg en release-APK med `debuggable=false`, mindst Android
API 26 og APK-v2-signatur. Brug din egen private signeringsnøgle og behold den
til opdateringer. Brug et unikt Android package ID, ikke et reserveret system-
eller UltraBar ID. Eventuel specialopsætning skal være understøttet af Studio
eller appen selv; en manifestfil kan ikke tilføje installationsscripts.

## 3. Test og udgiv på dit eget repository

1. Test på den hardware og firmware, du vil erklære understøttet.
2. Vælg versionsnummer, fx `1.0.0`, og commit alle kildefiler.
3. Find det fulde commit-SHA på 40 tegn. Gem det til registreringen.
4. Gå til **Releases → Draft a new release**, lav tag `v1.0.0` på dette commit
   og udgiv en almindelig release, ikke en draft eller prerelease.
5. Widgets/presets ligger allerede som kildefil i det fastlåste commit.
   Android-apps skal have **app.apk** og **source.zip** som release-assets.
   Lav source.zip med `git archive --format=zip --output=source.zip HEAD`.
   Arkivet skal indeholde præcis alle tracked filer i roden, uden en ekstra topmappe,
   højst 256 filer/16 MiB udpakket og uden submoduler eller symlinks.
6. Flyt ikke tagget og udskift ikke filerne efter indsendelse. Rettelser får en ny release.

Store bygger **ikke** APK'en ved brugerens Install. Den henter den færdige,
kontrollerede APK. Du kan bruge GitHub Actions i dit eget repository til at bygge
den, men din signeringsnøgle må kun ligge som privat secret, aldrig i Git.

## 4. Fork Store og lav én pakkemappe

1. Åbn https://github.com/qlerup/ultrabar-store og tryk **Fork**.
2. Opret en branch i din fork, fx `submit/my-app`.
3. Opret `submissions/my-app/`.
4. Kopiér de præcise filer fra din release. Undgå ændringer i linjeskift:

```text
submissions/my-app/
  repository.json
  manifest.json
  icon.png
  README.md
  LICENSE
  widget.json       # kun corebar-widget
  plugin.json       # kun studio-plugin
  app.apk          # kun corebar-app
  source.zip       # kun corebar-app
```

Kun filerne til din valgte type skal med. For APK-kode kontrollerer botten
source.zip mod dit fastlåste Git-commit. APK og source.zip skal også være identiske
med assets på din egen release.

## 5. Udfyld repository.json

Kopiér dette og erstat værdierne:

```json
{
  "repository": "DIT_GITHUB_NAVN/DIT_REPOSITORY",
  "commit": "FULDT_COMMIT_SHA_PAA_40_TEGN",
  "release": "v1.0.0",
  "type": "corebar-app"
}
```

`repository` indeholder både dit GitHub-navn og repository-navnet. Brug ikke en
fuld URL her. Den personlige konto, der åbner PR'en, skal være repository-ejeren.
Organisationer, delegerede udgivere og ejerskifte kræver særskilt maintainer-håndtering.

## 6. Udfyld manifest.json

Start med et eksempel eller en godkendt pakke af samme type. Udfyld:

- `schemaVersion`: 1; stabilt og unikt `id`, navn, beskrivelse og version.
- `type`: præcis samme værdi som i repository.json.
- `source`: `https://github.com/NAVN/REPO/blob/SHA/widget.json`, `plugin.json`
  eller `AndroidManifest.xml`, afhængigt af typen.
- `license`: kort licensbeskrivelse.
- `compatibility`: mindste Studio-version, `hostApi: 1` og faktisk understøttede
  modeller, firmwareversioner og ABI'er. Native widgets kræver de dokumenterede
  CB01/ARM32/LineOS-versioner; erklær ikke uprøvet hardware som testet.
- `permissions`: tom liste for JSON-pakker; præcis APK'ens Android-tilladelser for apps.
- Kun APK: `android` med `packageId`, heltals-`versionCode`, `minSdk` og
  `signerSha256` fra `apksigner verify --print-certs app.apk`.

Første indsendelse kan undlade `artifact` og `icon`-downloadmetadata.
Store-maintaineren offentliggør de gennemgåede bytes som versionsfastlåste assets
i det officielle Store-repository og tilføjer URL, byteantal og SHA-256 samt den
identiske katalogpost. Botten bliver først helt grøn, når dette er på plads.
Det er en distributionskopi; dit eget repository er fortsat kildens hjemsted.

## 7. Åbn PR og udfyld checklisten

1. Commit mappen i din fork.
2. Vælg **Contribute → Open pull request** mod `qlerup/ultrabar-store:main`.
3. Udfyld den automatiske skabelon: type, pakke-ID, eget repository, release,
   commit, ændringer, testresultater og begrænsninger.
4. Sæt kun kryds ved det, du faktisk har udført. Checkbokse erstatter ikke kontrol.
5. Vent på **Store submission checks**. Fork-bidrag køres kun som data;
   botten udfører ikke din indsendte kode eller dine workflowændringer.

## 8. Ret fejl og kør igen

Botten opdaterer sin kommentar med kontroller og fejl. Ret filerne og push til
**samme PR-branch**; så kører Actions automatisk igen. Hvis fejlen kræver ændret
kilde/byg, udgiv først en ny version i dit eget repository og opdatér SHA/tag/filer.
En maintainer kan også vælge **Actions → Store submission checks → Run workflow**
og skrive PR-nummeret. To ændrede pakker betyder: del dem i to PR'er.

**Ready for approval** og grøn status betyder, at automatiske fil-, identitets-
og pakkekontroller er bestået. Det beviser ikke sikkerhed, ophavsret eller korrekt
funktion på hardware. Store-ejeren gennemgår og tester pakken før merge.

## 9. Godkendelse og brugernes installation

Når Store-ejeren merger PR'en, er pakken i kataloget på main. Brugeren åbner Store
og trykker **Refresh store**; eventuel GitHub-cache kan give en kort forsinkelse.
Der kræves ingen ny Studio-udgivelse, hvis den installerede Studio allerede
understøtter pakkens type, funktioner og krævede minimumsversion.

- Core-app: forbind Core, vælg Install, og åbn appen i Core's appliste.
- Core-widget: Install → biblioteket til venstre → træk en blok ind → vælg dens
  indstillinger til højre → Deploy.
- Preset: Install til biblioteket → tilføj blokken og Deploy som en widget.

## 10. Send en opdatering senere

Behold repository, pakke-ID og type. Ret koden i dit eget repository, hæv version,
test, lav nyt commit og ny stable release. APK'er skal også hæve versionCode og
bruge samme Android package ID og signeringsnøgle. Opdatér **samme pakkemappe**
i en ny Store-PR med nye filer, SHA og release. Ejerskab og alle checks gentages.
Efter ejerens merge kan brugere hente opdateringen fra Store.

En ny release i dit eget repository alene ændrer ikke Store. En uvedkommende fork
kan heller ikke overtage din godkendte registrering. Installerede Android-apps
opdateres med bevaret app-data; ændringer i appens eget dataformat er udviklerens
ansvar. Widget-opdateringer overskriver ikke allerede placerede blokkes indstillinger.
