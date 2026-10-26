# [UKÁZKA] Návrh: Uložené filtry v reportech · [SAMPLE] Proposal: Saved report filters

<!-- lang:cs -->

Linear: [TEAG-123](https://linear.app/keboola/issue/TEAG-123) · Stav: Ke kontrole · v1 · Autor: Jan Ukázka · Rozhoduje: Petr Šimeček · Aktualizováno: 2026-10-23 · Data k: 2026-10-20

Analytici si v reportu uloží sadu filtrů a znovu ji použijí jedním kliknutím. Týká se všech 120 aktivních analytiků na instanci. Potřebujeme rozhodnout D1 a D2 do 6. 11. 2026, aby fáze 1 stihla prosincové vydání.

<!-- lang:en -->

Linear: [TEAG-123](https://linear.app/keboola/issue/TEAG-123) · Status: In review · v1 · Owner: Jan Ukázka · Decides: Petr Šimeček · Updated: 2026-10-23 · Evidence as of: 2026-10-20

Analysts save a set of report filters and reapply it with one click. It affects all 120 active analysts on the instance. We need decisions D1 and D2 by 6 Nov 2026 so phase 1 makes the December release.

<!-- /lang -->

<!-- cs:changes -->
## Co se změnilo · What changed

<!-- lang:cs -->

Jen od verze 2; ve verzi 1 sekci smažte.

- **D1:** doporučení změněno z A na B, protože sdílené filtry chtěly 3 z 5 respondentů (komentář #12).

<!-- lang:en -->

Only from version 2; delete this section in version 1.

- **D1:** recommendation changed from A to B because 3 of 5 respondents asked for shared filters (comment #12).

<!-- /lang -->

<!-- cs:summary -->
## Shrnutí a potřebná rozhodnutí · Summary and decisions needed

<!-- lang:cs -->

- Tlačítko *Uložit filtry* v hlavičce reportu uloží aktuální filtry pod jménem.
- Uložené sady jsou vidět v rozbalovacím menu; výchozí sadu lze připnout.
- Fáze 1 jen osobní sady, fáze 2 sdílení se skupinou.
- Za přepínačem `saved_report_filters`, výchozí stav vypnuto.

| # | Rozhodnutí | Doporučení |
|---|---|---|
| D1 | Sdílet sady už ve fázi 1? | B: ne, až ve fázi 2 |
| D2 | Kde sady ukládat? | A: Postgres, nová tabulka |

<!-- lang:en -->

- A *Save filters* button in the report header saves the current filters under a name.
- Saved sets appear in a drop-down; one can be pinned as the default.
- Phase 1 is personal sets only, phase 2 adds sharing with a group.
- Behind the `saved_report_filters` switch, off by default.

| # | Decision | Recommendation |
|---|---|---|
| D1 | Share sets in phase 1? | B: no, in phase 2 |
| D2 | Where to store sets? | A: Postgres, new table |

<!-- /lang -->

<!-- cs:problem -->
## Problém · The problem

<!-- lang:cs -->

**Kdo:** analytici, kteří otevírají stejný report několikrát týdně. **Situace:** po každém otevření nastavují 4 až 6 filtrů znovu. **Cena dnes:** medián 47 s na otevření, 1 900 otevření týdně, tedy asi 25 hodin týdně (odvozeno) [1].

**Příklad:** „Každé pondělí naklikám region, měnu a tři produkty. Kdyby si to report pamatoval, ušetřím čtvrt hodiny.“ (ticket TEAG-000, 2026-10-02) [2]

<!-- lang:en -->

**Who:** analysts who open the same report several times a week. **Situation:** after each open they set 4 to 6 filters again. **Cost today:** median 47 s per open, 1,900 opens a week, about 25 hours a week (inferred) [1].

**Example:** "Every Monday I click region, currency and three products. If the report remembered it, I would save a quarter of an hour." (ticket TEAG-000, 2026-10-02) [2]

<!-- /lang -->

<!-- cs:goals -->
## Cíle a necíle · Goals and non-goals

<!-- lang:cs -->

Cíle:

- Analytik obnoví uloženou sadu filtrů jedním kliknutím.
- Výchozí sada se použije sama při otevření reportu.

Necíle:

- Filtry napříč různými reporty.
- Plánované odesílání reportu s filtry.

<!-- lang:en -->

Goals:

- An analyst restores a saved filter set with one click.
- A default set applies on its own when the report opens.

Non-goals:

- Filters shared across different reports.
- Scheduled delivery of a filtered report.

<!-- /lang -->

<!-- cs:principles -->
## Principy · Principles

<!-- lang:cs -->

1. Uložená sada nikdy nerozšíří přístup k datům; filtr jen zužuje [3].
2. Stejné chování na webu, v CLI i MCP.
3. Nová funkce za přepínačem, výchozí stav vypnuto.

<!-- lang:en -->

1. A saved set never widens data access; a filter only narrows [3].
2. The same behaviour on the web, in the CLI and over MCP.
3. New feature behind a switch, off by default.

<!-- /lang -->

<!-- cs:metrics -->
## Jak poznáme, že to funguje · How we know it worked

<!-- lang:cs -->

| Metrika | Dnes | Cíl | Do |
|---|---:|---:|---|
| Medián času od otevření po první graf | 47 s | ≤ 10 s | 2027-02-28 |
| Podíl otevření s uloženou sadou | 0 % | ≥ 40 % | 2027-02-28 |

Ochranné metriky: p95 načtení reportu nesmí stoupnout nad 2,0 s (dnes 1,6 s); žádný nárůst chyb 4xx/5xx na API reportů.

<!-- lang:en -->

| Metric | Baseline | Target | By |
|---|---:|---:|---|
| Median time from open to first chart | 47 s | ≤ 10 s | 2027-02-28 |
| Share of opens with a saved set | 0% | ≥ 40% | 2027-02-28 |

Guardrails: report load p95 must not rise above 2.0 s (today 1.6 s); no increase in 4xx/5xx errors on the report API.

<!-- /lang -->

<!-- cs:current-state -->
## Současný stav v Agnes · Current state in Agnes

<!-- lang:cs -->

**Pro uživatele:** filtry žijí jen v URL; po zavření karty jsou pryč (ověřeno).

**V kódu:** stav filtrů drží `web/src/example/ReportFilters.tsx`; API `app/api/example_reports.py` filtry neukládá.

Obrázek (ukázkový snímek, 2026-10-20): **Dnes musí analytik nastavit filtry ručně při každém otevření.** 1) Pět filtrů, žádné uložení. 2) Export zachová filtry jen v souboru, ne v reportu.

<!-- lang:en -->

**For users:** filters live only in the URL; they are gone once the tab closes (verified).

**In code:** `web/src/example/ReportFilters.tsx` holds the filter state; the API `app/api/example_reports.py` does not store filters.

Figure (sample screenshot, 2026-10-20): **Today an analyst sets the filters by hand on every open.** 1) Five filters, no save. 2) Export keeps the filters in the file only, not in the report.

<!-- /lang -->

<!-- cs:research -->
## Průzkum a konkurence · Research and competition

<!-- lang:cs -->

Konkurent A i B ukládají filtry na úrovni uživatele; jen B je umí sdílet se skupinou [4] [5].

| Schopnost | Konkurent A | Konkurent B | Agnes dnes | Po fázi 1 | Po fázi 2 |
|---|---|---|---|---|---|
| Uložit sadu filtrů | Ano | Ano | Ne | Ano | Ano |
| Sdílet se skupinou | Ne | Ano | Ne | Ne | Ano |
| Dostupné přes API / agenta | Částečně | Ne | Ne | Ano | Ano |

Poziční graf (sdílení a správa / rychlost pro analytika, 0–100, odhad autora): Konkurent A 25/70, Konkurent B 65/60, Agnes dnes 55/20, po fázi 1 60/70, po fázi 2 85/85. **Fáze 2 posune Agnes před oba konkurenty ve sdílení i rychlosti.**

<!-- lang:en -->

Competitors A and B both save filters per user; only B shares them with a group [4] [5].

| Capability | Competitor A | Competitor B | Agnes now | After phase 1 | After phase 2 |
|---|---|---|---|---|---|
| Save a filter set | Yes | Yes | No | Yes | Yes |
| Share with a group | No | Yes | No | No | Yes |
| Available via API / agent | Partly | No | No | Yes | Yes |

Position chart (sharing and governance / speed for the analyst, 0–100, author's estimate): Competitor A 25/70, Competitor B 65/60, Agnes now 55/20, after phase 1 60/70, after phase 2 85/85. **Phase 2 moves Agnes ahead of both competitors in sharing and speed.**

<!-- /lang -->

<!-- cs:proposal -->
## Návrh · Proposal

<!-- lang:cs -->

Cesta uživatele:

1. Analytik nastaví filtry a klikne *Uložit filtry*.
2. Zadá jméno (max. 60 znaků) a volitelně zaškrtne *Výchozí*.
3. Při dalším otevření se výchozí sada použije sama; jiné vybere z menu.

Chování a limity:

- Max. 20 sad na uživatele a report; 21. uložení ukáže chybu s odkazem na správu sad.
- Filtr na sloupec, který zmizel, se přeskočí a uživatel to uvidí v liště.

Obrázek (**Koncept**, vygenerováno pro ilustraci, ne návrh UI): menu uložených sad s připnutou výchozí sadou. 1) Výchozí sada je první a označená špendlíkem.

<!-- lang:en -->

User journey:

1. The analyst sets filters and clicks *Save filters*.
2. Enters a name (max 60 characters) and optionally ticks *Default*.
3. On the next open the default set applies on its own; others are picked from the menu.

Behaviour and limits:

- Max 20 sets per user and report; the 21st save shows an error linking to set management.
- A filter on a column that no longer exists is skipped, and the user sees that in a bar.

Figure (**Concept**, generated for illustration, not a UI spec): the saved-sets menu with a pinned default set. 1) The default set is first and marked with a pin.

<!-- /lang -->

<!-- cs:alternatives -->
## Alternativy a proč tahle · Alternatives and why this one

<!-- lang:cs -->

| Varianta | Čas analytika | Náklad | Riziko |
|---|---|---|---|
| Nic nedělat | 47 s | 0 | Analytici odcházejí k nástroji A |
| Záložky v prohlížeči (URL) | 15 s | 2 dny | Nefunguje v CLI ani MCP |
| **Uložené sady (návrh)** | ≤ 10 s | 3 týdny | Nová tabulka a migrace |

**Proč návrh:** jen on splní princip 2 (stejné chování na všech plochách). Záložky jsou levnější, ale agent je nepoužije.

<!-- lang:en -->

| Option | Analyst time | Effort | Risk |
|---|---|---|---|
| Do nothing | 47 s | 0 | Analysts move to tool A |
| Browser bookmarks (URL) | 15 s | 2 days | Does not work in CLI or MCP |
| **Saved sets (proposal)** | ≤ 10 s | 3 weeks | New table and migration |

**Why the proposal:** only it meets principle 2 (same behaviour on every surface). Bookmarks are cheaper, but an agent cannot use them.

<!-- /lang -->

<!-- cs:decisions -->
## Rozhodnutí · Decisions

<!-- lang:cs -->

### D1: Sdílet uložené sady se skupinou už ve fázi 1?

**O co jde.** Dnes si každý analytik nastavuje filtry sám. Rozhodujeme, jestli si sady filtrů mohou kolegové předávat hned, nebo až později; určuje to termín fáze 1.

**Jak to vypadá.** Jana uloží sadu „Pondělí“. *A:* Petr ji hned vidí v menu svého reportu. *B:* Petr ji uvidí až po fázi 2; do té doby si ji nastaví sám.

| | A: ano, hned | B: až ve fázi 2 |
|---|---|---|
| Pro | Tým sdílí stejný pohled od prvního dne. | Fáze 1 vyjde v prosinci. |
| Proti | +2 týdny; nutná kontrola oprávnění skupin. | Sdílení čeká 2 měsíce. |
| Změnit později | Sdílení nejde vzít zpět, až ho lidé používají. | Přidat sdílení je snadné. |
| Kdo to tak dělá | Konkurent B [5]. | Konkurent A [4]. |

**Doporučení: B.** 80 % otevření dělá autor reportu sám (odvozeno); sdílení přinese méně, než kolik stojí zpoždění.

### D2: Kde uložené sady ukládat?

- **A: Postgres, nová tabulka (doporučeno).** Jedno místo pro web, CLI i MCP.
- B: Nastavení uživatele (JSON). Bez migrace, ale bez sdílení.
- C: Jen v prohlížeči. Nejlevnější, nefunguje pro agenty.

**Proč A:** fáze 2 potřebuje sdílení; B by se musela znovu migrovat. Odpověď: formulář v dokumentu (volba + komentář).

<!-- lang:en -->

### D1: Share saved sets with a group already in phase 1?

**What it is about.** Today each analyst sets filters alone. We decide whether colleagues can share filter sets at once or later; this sets the phase 1 date.

**What it looks like.** Jana saves the set "Monday". *A:* Petr sees it in his report menu at once. *B:* Petr sees it only after phase 2; until then he sets it himself.

| | A: yes, now | B: in phase 2 |
|---|---|---|
| Pros | The team shares one view from day one. | Phase 1 ships in December. |
| Cons | +2 weeks; needs a group permission check. | Sharing waits 2 months. |
| Change later | Sharing cannot be taken back once people use it. | Adding sharing is easy. |
| Who does this | Competitor B [5]. | Competitor A [4]. |

**Recommendation: B.** 80% of opens are by the report's own author (inferred); sharing adds less than the delay costs.

### D2: Where do saved sets live?

- **A: Postgres, new table (recommended).** One place for web, CLI and MCP.
- B: User settings (JSON). No migration, but no sharing.
- C: Browser only. Cheapest, does not work for agents.

**Why A:** phase 2 needs sharing; B would have to be migrated again. Answer: the form in the document (choice + comment).

<!-- /lang -->

<!-- cs:architecture -->
## Dopad na architekturu · Architecture impact

<!-- lang:cs -->

Diagram C4 (kontejnery podle `docs/c4/MODEL.md`): **Mění se web a API, přibývá jedna tabulka; agent sandbox zůstává.** Web app (React, mění se: menu uložených sad) → API (FastAPI, mění se: `/api/report-filters`) → Tabulka sad (Postgres, nové: `report_filter_sets`). CLI + MCP (beze změny kontejneru, nový příkaz a nástroj) → API. Agent sandbox (externí, beze změny) → MCP.

| Plocha | Mění se? | Proč |
|---|---|---|
| Testy | Ano | Nový endpoint a limit 20 sad. |
| Dokumentace | Ano | Uživatelská stránka reportů. |
| Frontend | Ano | Tlačítko a menu v hlavičce reportu. |
| API | Ano | CRUD pro sady. |
| CLI | Ano | Princip 2: stejné chování. |
| MCP | Ano | Princip 2: stejné chování. |
| Externí služby (agent sandbox) | Ne | Agent volá MCP; sandbox se nemění. |

<!-- lang:en -->

C4 diagram (containers per `docs/c4/MODEL.md`): **The web app and API change and one table is added; the agent sandbox stays as is.** Web app (React, changes: saved-sets menu) → API (FastAPI, changes: `/api/report-filters`) → Sets table (Postgres, new: `report_filter_sets`). CLI + MCP (container unchanged, new command and tool) → API. Agent sandbox (external, unchanged) → MCP.

| Surface | Changes? | Why |
|---|---|---|
| Tests | Yes | New endpoint and the 20-set limit. |
| Docs | Yes | The reports user page. |
| Frontend | Yes | Button and menu in the report header. |
| API | Yes | CRUD for sets. |
| CLI | Yes | Principle 2: same behaviour. |
| MCP | Yes | Principle 2: same behaviour. |
| External services (agent sandbox) | No | The agent calls MCP; the sandbox does not change. |

<!-- /lang -->

<!-- cs:delivery -->
## Plán dodání · Delivery plan

<!-- lang:cs -->

| Fáze | Kdy | Hotovo když |
|---|---|---|
| 1: osobní sady | 2026-11 → 2026-12 | 10 analytiků na dev používá sady 2 týdny. |
| 2: sdílení | 2027-01 → 2027-02 | Sada sdílená se skupinou respektuje její oprávnění. |
| Zapnout pro všechny | 2027-03 | Metriky splní cíl a přepínač je odstraněn. |

**Přepínač:** `saved_report_filters`, výchozí vypnuto. **Závislosti:** žádné. **Riziko:** sloupec zmizí ze zdroje → filtr se přeskočí a uživatel to vidí.

Akceptační příklady:

- **Výchozí sada se použije sama.** Dáno: sada „Pondělí“ je výchozí. Když: analytik otevře report. Pak: report ukáže data s filtry sady „Pondělí“ do 2 s.
- **Limit 20 sad.** Dáno: uživatel má u reportu 20 sad. Když: uloží 21. Pak: vidí chybu s odkazem na správu sad a nic se neuloží.

<!-- lang:en -->

| Phase | When | Done when |
|---|---|---|
| 1: personal sets | 2026-11 → 2026-12 | 10 analysts on dev use sets for 2 weeks. |
| 2: sharing | 2027-01 → 2027-02 | A set shared with a group respects its permissions. |
| On for everyone | 2027-03 | Metrics meet target and the switch is removed. |

**Switch:** `saved_report_filters`, off by default. **Dependencies:** none. **Risk:** a column disappears from the source → the filter is skipped and the user sees it.

Acceptance examples:

- **The default set applies on its own.** Given: set "Monday" is the default. When: the analyst opens the report. Then: the report shows data with the "Monday" filters within 2 s.
- **The 20-set limit.** Given: the user has 20 sets on the report. When: they save a 21st. Then: they see an error linking to set management and nothing is saved.

<!-- /lang -->

<!-- cs:second-opinion -->
## Druhý názor · Second opinion

<!-- lang:cs -->

GPT Astra posoudila verzi 1 dne 2026-10-22.

| # | Nález | Řešení |
|---|---|---|
| 1 | Chybí chování při smazaném sloupci. | **Změněno:** doplněno do Návrhu. |
| 2 | Ukládat do localStorage. | **Odmítnuto:** porušuje princip 2. |

<!-- lang:en -->

GPT Astra reviewed version 1 on 2026-10-22.

| # | Finding | Resolution |
|---|---|---|
| 1 | Behaviour for a deleted column is missing. | **Changed:** added to Proposal. |
| 2 | Store in localStorage. | **Rebutted:** breaks principle 2. |

<!-- /lang -->

<!-- cs:glossary -->
## Slovník · Glossary

<!-- lang:cs -->

- **Uložená sada filtrů:** pojmenovaná kombinace filtrů jednoho reportu, kterou lze znovu použít.
- **Výchozí sada:** sada, která se použije sama při otevření reportu.

<!-- lang:en -->

- **Saved filter set:** a named combination of one report's filters that can be reapplied.
- **Default set:** the set applied on its own when the report opens.

<!-- /lang -->

<!-- cs:sources -->
## Zdroje · Sources

<!-- lang:cs -->

1. Ukázková telemetrie otevření reportů, 2026-10-01 až 2026-10-14. <https://example.com/telemetry>
2. Ukázkový ticket TEAG-000, 2026-10-02. <https://example.com/teag-000>
3. `docs/table-access-policies.md`, commit `0000000`.
4. Konkurent A, dokumentace „Saved views“, čteno 2026-10-20. <https://example.com/competitor-a>
5. Konkurent B, dokumentace „Shared filters“, čteno 2026-10-20. <https://example.com/competitor-b>

<!-- lang:en -->

1. Sample report-open telemetry, 2026-10-01 to 2026-10-14. <https://example.com/telemetry>
2. Sample ticket TEAG-000, 2026-10-02. <https://example.com/teag-000>
3. `docs/table-access-policies.md`, commit `0000000`.
4. Competitor A, "Saved views" docs, read 2026-10-20. <https://example.com/competitor-a>
5. Competitor B, "Shared filters" docs, read 2026-10-20. <https://example.com/competitor-b>

<!-- /lang -->

<!-- cs:appendix -->
## Příloha: technické detaily · Appendix: technical detail

<!-- lang:cs -->

Datový model:

<!-- lang:en -->

Data model:

<!-- /lang -->

```sql
report_filter_sets(
  id uuid primary key,
  report_id text not null,
  owner_user_id uuid not null,
  name varchar(60) not null,
  filters jsonb not null,
  is_default boolean not null default false
)
```

```text
GET    /api/reports/{id}/filter-sets
POST   /api/reports/{id}/filter-sets   {name, filters, is_default}
DELETE /api/reports/{id}/filter-sets/{set_id}
```
