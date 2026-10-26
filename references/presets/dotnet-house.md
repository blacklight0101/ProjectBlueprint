# Preset: .NET house

The house stack for intranet and line-of-business web applications: .NET 10, Blazor Server, Clean
Architecture with strictly inward dependencies, Dapper with hand-written SQL (no EF Core), SQL Server,
IIS with Windows (Negotiate) authentication, xUnit with FluentAssertions, test-first with a 60 / 30 / 10
pyramid, SOLID and KISS as review criteria.

Derived from a convention source repository (repository shape, `Program.cs` authentication branch, unit of
work, migrations runner, test fixtures) and from the rules a later project wrote on top of it to close its gaps (central package versions, code-behind, schema per area, fresh test
database, schema-version guard, test levels). Where the convention source and this preset differ, this
preset wins and the difference is noted.

`<Product>` below is the PascalCase form of `{{PROJECT}}` without spaces (for example `OrderDesk`); it names
the solution, the projects and the root namespaces.

Contents: 1. When to offer it | 2. Answers it fills | 3. Stack | 4. Solution layout | 5. Coding conventions | 6. Database conventions | 7. Testing | 8. ADRs this preset implies | 9. CLAUDE.md hard rules block | 10. Environments and delivery defaults | 11. Known gotchas | 12. Questions the preset leaves open

## 1. When to offer it

Offer it as `(Recommended)` when the project is a business web application for internal users on the
company network, runs on Windows servers, and needs a relational database. Signals: "intranet", "for the
team", "replaces an old WebForms or Access app", "IIS", "SQL Server", "Windows login". Do not offer it for
public internet sites with self sign-up, games, or mobile apps.

## 2. Answers it fills

| Bank id | Answer |
|---|---|
| 1.5 | Permission codes grouped into editable roles; code checks the permission, never the role name |
| 1.6 | Users from the company directory (Windows identity); access granted by an administrator in an application users table |
| 2.5 | Every external write carries an idempotency key persisted before the call |
| 3.6 | Store UTC (`datetime2(3)`, `Utc` suffix); display in the user's or site's time zone through a clock abstraction |
| 3.7 | Admin writes audited with before and after values |
| 4.1 | This preset |
| 4.2 | .NET 10, C# with `Nullable` and `ImplicitUsings` on |
| 4.3 | Blazor Server (interactive server render mode) |
| 4.4 | Dapper with hand-written, parameterised, schema-qualified SQL; no EF Core |
| 4.5 | SQL Server |
| 4.6 | IIS on the company's Windows servers, one site or sub-application per environment |
| 4.7 | Windows authentication (Negotiate) with application-managed permissions |
| 4.8 | Hosted background services inside the web app with a database lease; no Hangfire or Quartz |
| 4.9 | The package baseline in section 10.4; anything else needs an ADR |
| 5.3 | Light default with a dark toggle through a `data-theme` attribute |
| 5.4 | WCAG 2.1 AA |
| 5.5 | Own small component set on design tokens; no UI component library |
| 5.8 | Business error: message from resources plus an error code; technical error: error state with a correlation id and a retry; never a stack trace |
| 6.2 | Dev: `dotnet user-secrets`; servers: IIS environment variables or a server-side settings file outside the repository |
| 6.3 | Local verify script (restore, build with warnings as errors, tests per level, pyramid report, secrets scan); a pipeline file prepared but inactive |
| 7.1 | Test-first |
| 7.2 | 60 / 30 / 10 by test count, ten points tolerance, `[Trait("Level", ...)]` on every test |
| 7.4 | Fresh test database per run |
| 7.5 | Fakes for every external port, passing the same contract test as the real adapter |
| 7.6 | SOLID and KISS with concrete checks |

## 3. Stack

| Area | Choice |
|---|---|
| Runtime | .NET 10 (`net10.0`), SDK pinned in `global.json` |
| UI | Blazor Server, `.razor` pages with `.razor.cs` code-behind partial classes |
| Architecture | Clean Architecture in four source projects plus tests: `Domain <- Application <- Infrastructure <- Web`, dependencies strictly inward |
| Data access | Dapper plus `Microsoft.Data.SqlClient`; SQL written by hand; one connection and one transaction per unit of work |
| Database | SQL Server, one database per environment (or per site when the interview says so), least-privilege logins per principal |
| Migrations | Numbered, idempotent T-SQL scripts run in order by a PowerShell runner through `sqlcmd` |
| Hosting | IIS (ASP.NET Core Module, in-process), framework-dependent folder publish |
| Authentication | Windows / Negotiate; IIS handles the handshake when hosted there; claims transformation adds the application's permissions |
| Tests | xUnit, FluentAssertions, `Microsoft.AspNetCore.Mvc.Testing` (`WebApplicationFactory<Program>`), Playwright for .NET for end-to-end |
| Principles | Test-first, pyramid 60 / 30 / 10, SOLID, KISS, one class per file |

## 4. Solution layout

```
<Product>.slnx
  src/<Product>.Domain/          Entities/ ValueObjects/ Enums/ ReadModels/ Repositories/ (ports) Exceptions/ Policies/
  src/<Product>.Application/     Services/Contracts/ (I<Module>Service) Services/Implementations/ Dtos/ Mapping/ (DtoMappings)
                                 Ports/ (outward ports: clock, directory, external systems) UnitOfWork/ (IUnitOfWork, IUnitOfWorkFactory)
                                 DependencyInjection.cs (Add<Product>Application)
  src/<Product>.Infrastructure/  Db/ (IDbConnectionFactory, SqlConnectionFactory) Persistence/UnitOfWork/ Repositories/
                                 Clock/ <Adapter>/ Fakes/ DependencyInjection.cs (Add<Product>Infrastructure)
                                 Properties/AssemblyInfo.cs (InternalsVisibleTo the test project)
  src/<Product>.Web/             Program.cs Components/{Layout,Pages,Shared}/ Authorization/ Api/ HostedServices/ Resources/ wwwroot/
  tests/<Product>.Tests/         Unit/ Integration/ Helpers/ (fixtures, test auth handler, DB collection) xunit.runner.json
  tests/<Product>.E2E/           Playwright journeys (E2E level)
  Database/Migrations/           NNNN_Name.sql
  Database/Tools/                bootstrap-db.ps1 (runner), predeploy.ps1 (verify recipe), app-offline.ps1
  docs/                          the documentation set
  .claude/launch.json            preview configuration for the verifier
  .claude/agents/                orchestrator, builders, verifier
  Directory.Build.props  Directory.Packages.props  global.json  .editorconfig
```

- **Dependency rule.** `Domain` references nothing. `Application` references `Domain` only and never uses
  `Dapper`, `SqlClient`, `HttpClient` or vendor SDK types. `Infrastructure` references `Application` and
  `Domain`. `Web` references all three and is the composition root. Tests may reference everything.
- **Namespaces are flat per project** (`<Product>.Domain`, `<Product>.Application`); folders are organisational.
  `Infrastructure` and `Web` may nest (`<Product>.Infrastructure.Repositories`).
- **Registration.** `Application/DependencyInjection.cs` exposes `Add<Product>Application(this IServiceCollection)`;
  `Infrastructure/DependencyInjection.cs` exposes `Add<Product>Infrastructure(this IServiceCollection, IConfiguration)`,
  reads the connection strings (throws a clear `InvalidOperationException` when one is missing), registers the
  connection factory and the unit-of-work factory as singletons and the module services as scoped. `Program.cs`
  calls both. (The convention source registers services in Infrastructure because it has the configuration;
  keep that.)
- **Unit of work.** `IUnitOfWork : IAsyncDisposable` exposes one property per repository and `CompleteAsync()`.
  `IUnitOfWorkFactory.CreateAsync(<Product>Principal principal, CancellationToken ct = default)` opens a
  connection as the chosen SQL principal and begins a transaction at once. Disposing without `CompleteAsync()`
  rolls back. Repositories are constructed by the unit of work with `(IDbConnection, IDbTransaction)` and
  never open connections themselves.
- **Principals.** An enum `<Product>Principal { Reader, Writer, Admin }` in `Domain` maps to one SQL login
  each; add principals (for example a log writer or a deploy login) only through an ADR.
- **Module service pattern.** A page injects exactly one `I<Module>Service` from `Application`, never a
  repository, a connection or the unit-of-work factory. A service method opens one unit of work, picks the
  principal (reads as `Reader`, admin writes as `Admin`), calls repositories, maps to DTOs, and calls
  `CompleteAsync()` on writes.
- **Read models and DTOs.** Repositories return entities or read models (`Domain/ReadModels`), never tracked
  objects; services map to DTOs with extension methods in `Application/Mapping/DtoMappings.cs` (`ToDto()`).

## 5. Coding conventions

### 5.1 C#

- One class (record, enum, interface) per file; the file is named after the type.
- `sealed` by default; unseal only for a documented extension point.
- Every async method ends in `Async` and takes `CancellationToken ct = default` as its last parameter.
- UTC timestamps end in `Utc` (`CreatedUtc`, `ClosedAtUtc`); local business dates are `DateOnly` and end in `Date`.
- Private fields `_camelCase`; constructor injection of abstractions only.
- `Nullable` and `ImplicitUsings` enabled in every project through `Directory.Build.props`, with
  `TreatWarningsAsErrors` on for release builds and the verify recipe.
- Central package versions in `Directory.Packages.props`; the SDK in `global.json`; style in `.editorconfig`.
  (The convention source lacks these three; every new project has them from the first card.)
- No `DateTime.Now` or `DateTime.UtcNow` in business code: time comes from a clock port (`IClock`).
- No status strings or sentinel values in code or SQL; states are enums whose names match the database check constraint.
- No literals for things that differ per site, customer or environment; they are data or configuration.
- Class suffixes: `Service`, `Repository`, `Client`, `Adapter`, `Job`, `Endpoints`, `Dto`, `Command`, `Result`.
  Fakes are `Fake<Port>`.

### 5.2 SQL in repositories

- SQL lives in the repository as `const string` fields named by intent (`SelectActiveByOwnerSql`).
- Always schema-qualified, always parameterised, explicit column lists (never `SELECT *`), no string
  concatenation of identifiers or values.
- Positional record read models: the `SELECT` column order must match the record's constructor.
- Convert `DateOnly` at the repository edge (`DateOnly` <-> `DateTime`); do not register a global Dapper type handler.
- Optimistic concurrency through a `rowversion` column on every mutable table edited from a page.

### 5.3 Blazor pages

- `.razor` markup plus `.razor.cs` partial class; no `@code` block longer than five lines. (The convention
  source still uses `@code` blocks; new projects use code-behind.)
- Pages use only the documented components and design tokens; no hard-coded colours, sizes, fonts or user text.
- User text comes from resources (`.resx` per culture); resource keys `<Area>.<Screen>.<Element>`.
- Every page and endpoint carries an authorization policy naming one permission code (`<area>.<action>`,
  lower case). There is no anonymous page unless the spec names it.
- Routes lower-case kebab-case, no trailing slash, integer ids.
- Internal links and `NavigateTo` targets are base-relative (`admin/users`, not `/admin/users`), and
  `App.razor` sets `<base href>` from `Request.PathBase`, so the app works as an IIS sub-application.
- Identity inside components comes from the cascading `AuthenticationState`, never from
  `IHttpContextAccessor` (the `HttpContext` is null once the interactive circuit runs).
- A `disabled` attribute is not a guard: every handler re-checks its preconditions against live state and
  has a re-entrancy flag.
- A page whose rendering depends on per-circuit state uses `InteractiveServerRenderMode(prerender: false)`.
- Per-user state services are scoped (one per circuit), never singletons; timers live in components and
  marshal through `InvokeAsync`.

### 5.4 Error handling per layer

| Layer | Rule |
|---|---|
| Domain | Throws domain exceptions (`<Product>ValidationException`, `InvalidTransitionException`); never catches |
| Application | Translates domain and port failures into a `Result` (ok, business error with a resource key, technical error with a correlation id); logs technical errors once; never swallows |
| Infrastructure | Maps SQL errors (2627 and 2601 to a unique violation, 547 to a foreign-key violation) and adapter failures (timeout, rejected, unreachable) to typed failures; retries only where an adapter declares a policy |
| Pages | Business error: message component with the resource text and the error code. Technical error: error state with the correlation id and a retry. Unhandled: a global error boundary with the correlation id, never a stack trace |
| HTTP endpoints | RFC 7807 problem details; no stack traces; 400 for validation, 401, 403, 409 as the spec says |
| Error codes | `E-<AREA>-<nnn>` from a catalogue in `Application`, each with a resource key; a unit test checks every code has text in every enabled language |
| Background services | Catch per iteration, log, continue; release the lease on stop; failures visible on the health page |

### 5.5 Authentication and authorization

- `Program.cs` branches three ways (from the convention source): environment `Testing` registers nothing (the
  test host adds its scheme); hosted under IIS (`ASPNETCORE_IIS_HTTPAUTH` set) uses
  `AddAuthentication(IISDefaults.AuthenticationScheme)` without `AddNegotiate`; otherwise
  `AddAuthentication(NegotiateDefaults.AuthenticationScheme).AddNegotiate()`.
- An `IClaimsTransformation` looks the Windows identity up in the application users table and adds one
  claim per granted permission code.
- Policies are registered per permission code; pages use `[Authorize(Policy = ...)]`, endpoints
  `.RequireAuthorization(...)`. Authorization is by permission code, never by role name.
- A development-only impersonation middleware may inject a configured identity, active only when
  `IsDevelopment()` and a `Dev:ImpersonateUser` setting are both present, and logged as a warning.
- Verify Negotiate-protected pages under IIS Express or IIS, not Kestrel on `localhost`: on a machine outside
  a domain, Windows loopback protection answers Kestrel's handshake with HTTP 400.

## 6. Database conventions

| Topic | Rule |
|---|---|
| Schemas | One schema per area (and one per feature module when the project has modules); no objects in `dbo`. Never create a schema named `sys`: SQL Server reserves it (error 2760). The schema-version and settings tables live in a schema named `app` |
| Tables | PascalCase plural (`Orders`, `OrderLines`) |
| Keys | `Id int identity(1,1)` clustered primary key; business keys as unique constraints; GUIDs only for identifiers that leave the system (`PublicId`, `CorrelationId`, `IdempotencyKey`); `bigint` for very high-volume log tables. (The convention source uses GUID keys; this preset uses integer keys, confirm in the data-model walk-through) |
| Constraint names | `PK_<Table>`, `FK_<Child>_<Parent>`, `UQ_`, `CK_`, `IX_`; every foreign-key column indexed |
| Foreign keys | Every relationship is a real foreign key, `ON DELETE NO ACTION`; deletes are soft or forbidden |
| Text | `nvarchar(n)` only; a fixed-length code is `nvarchar(n)` plus a `CK_` on its length or pattern |
| Time | `datetime2(3)` UTC with the `Utc` suffix; `date` for local business dates |
| Numbers | `decimal(18,3)` for money and weights unless the domain says otherwise |
| Enumerations | `nvarchar(30)` holding the C# enum name, with a `CK_` listing the allowed values; no integer codes, no sentinels |
| Booleans | `bit NOT NULL` named `Is...` or `Has...` |
| Audit columns | Mutable tables: `CreatedUtc`, `CreatedBy`, `ModifiedUtc`, `ModifiedBy`; append-only tables: `CreatedUtc`, `CreatedBy`; catalogues also `IsDeleted` |
| JSON | Only for copies of payloads (`nvarchar(max)` with an `ISJSON` check), never for data a query filters on |
| Collation | One collation for every database of the product; temp tables declare `COLLATE DATABASE_DEFAULT` |
| Logins | One SQL login per principal (`<Product>Reader`, `<Product>Writer`, `<Product>Admin`, plus `<Product>Deploy` for migrations); schema-level grants; each object's grants in the migration that creates it |
| Business rules | Rules the database can enforce (uniqueness, "at most one open" through a filtered unique index, allowed values) are constraints, listed in `docs/data-model.md` as a verifier checklist |

**Migrations**

- Files `Database/Migrations/NNNN_Name.sql`, four digits, applied in order. (The convention source uses
  `Database/Scripts/NN_Name.sql`; four digits leave room for reserved ranges.)
- Number ranges reserved per phase or module in `docs/data-model.md` so parallel builders never collide;
  each task card names its migration numbers.
- Every script starts with `SET NOCOUNT ON; SET QUOTED_IDENTIFIER ON; SET ANSI_NULLS ON;` and `USE $(DbName);`
  and is idempotent (`IF OBJECT_ID(...) IS NULL`, `IF NOT EXISTS`, `MERGE` for seeds). A header comment says
  what it adds and which grants it changes.
- The first script creates `app.SchemaVersion` (number, name, applied time, checksum); every script ends by
  inserting its row. At start-up the app compares the applied set with the set the build expects and refuses
  to run on a mismatch (optionally allowing the previous build within a one-release rollback window, decided
  by ADR).
- The runner `Database/Tools/bootstrap-db.ps1` takes `-ServerInstance`, `-DatabaseName`, `-SeedDemo`, and
  optional `-SqlUser`/`-SqlPassword` (Windows authentication otherwise); calls `sqlcmd -b -f 65001` (UTF-8)
  with `-v DbName=... SeedDemo=...`; clears `SQLCMDUSER` and `SQLCMDPASSWORD` first; stops on the first failure.
- Demo data only behind `$(SeedDemo)`; reference data every environment needs is seeded by migrations.
- Login passwords are never in scripts: they are `sqlcmd` variables supplied by the runner from a secure prompt.
- Never write a down-migration; a rollback is the previous build on the newer schema within the agreed window.
- A migration and `docs/data-model.md` change in the same branch.

**Test database.** Integration and E2E fixtures create `<Product>Test_<stamp>`, run every migration, seed the
minimal reference set, and drop it on dispose; a sweep removes stale ones. (The convention source uses one
shared local database with per-test cleanup; a fresh database per run is what keeps parallel builders
from colliding.) Test runs need rights to create and drop databases on the local SQL Server.

## 7. Testing

- **Levels.** Unit: no I/O at all (Domain, Application with fakes). Integration: exactly one real boundary
  (the test SQL Server, `WebApplicationFactory` HTTP, a local process or listener). E2E: a user journey in a
  real browser against the running app, Playwright for .NET, in `<Product>.E2E`.
- Every test class carries `[Trait("Level", TestLevels.Unit | Integration | E2E)]`.
- **Pyramid** 60 / 30 / 10 by test count per release, ten points tolerance; reported per card and per
  release by a pyramid report in the verify recipe. Default: the share only warns and `-EnforcePyramid`
  makes it block (bank 7.2); a missing `Level` trait or zero tests counted always fails `predeploy.ps1`.
- **Test-first.** The failing test comes first; branch history shows tests before or with the code; the
  verifier spot-checks that removing an implementation breaks a test.
- **Fixtures.** Integration tests needing the database are in `[Collection("DB")]` (a collection definition
  with `DisableParallelization = true`); `xunit.runner.json` disables assembly parallelisation where needed.
  HTTP tests use `WebApplicationFactory<Program>` with the environment forced to `Testing` and a
  `TestAuthHandler` scheme that reads the user from a request header, so the real claims transformation and
  policies run. `Program.cs` ends with `public partial class Program;`.
- **Fakes** for every external port live in `Infrastructure/Fakes` (selectable by configuration so the E2E
  host and the dev machine can use them) and pass the same contract test as the real adapter.
- **Naming.** Test files mirror the subject (`OrderServiceTests.cs`); methods
  `Given_<state>_When_<action>_Then_<outcome>` or `<Action>_<condition>_<result>`, one style per file; E2E
  journeys `Journey_<Area>_<Name>`.
- **Done means** `dotnet build` with no warnings and `dotnet test` green after every structural change, with
  the per-level counts reported.

## 8. ADRs this preset implies

Create these at scaffold time, numbered from the next free id after `ADR-001` (record architecture
decisions), in this order. Status `Accepted` when the user took the preset; the two marked "confirm" stay
`Proposed` until the data-model walk-through or the environments round confirms them.

| Order | Title | Decision in one line |
|---|---|---|
| 1 | Build on the .NET house baseline | .NET 10 Blazor Server, Clean Architecture in four projects plus tests, repository shape and rules of the house convention source |
| 2 | Access data with Dapper and hand-written SQL | Dapper plus `Microsoft.Data.SqlClient`, unit of work per service call, repositories as ports in `Domain`; no EF Core |
| 3 | Use Windows authentication with application-managed permissions | Negotiate on IIS, users table plus claims transformation, one permission code per page and endpoint, roles are data |
| 4 | Keep secrets out of source control | User secrets in development, environment variables or server-side protected configuration elsewhere, a secrets scan in the verify recipe, rotation on exposure |
| 5 | Adopt test-first with a 60/30/10 pyramid and SOLID/KISS review criteria | Levels by trait, pyramid by count per release, verifier checks history order and design rules |
| 6 | Set the database conventions (confirm) | Integer keys, schema per area, `nvarchar` only, UTC `datetime2`, named enums with check constraints, real foreign keys, fresh test database per run |
| 7 | Version the schema with numbered idempotent migrations and a start-up guard (confirm) | Four-digit scripts in reserved ranges, `app.SchemaVersion`, set-based check at start-up, no down-migrations |
| 8 | Own a small component set on design tokens instead of a UI library | Only when the design round confirms it: tokens file, prefixed components, a gallery page, no third-party UI library |
| 9 | Run background work as hosted services with a database lease | Only when the project has background work: `BackgroundService` plus a lease row, no Hangfire or Quartz |

## 9. CLAUDE.md hard rules block

Paste between the `<!-- STACK-RULES:BEGIN -->` and `<!-- STACK-RULES:END -->` markers under the `## Stack rules`
heading of the project's `CLAUDE.md`, replacing the FILL comment there (replace `<Product>`; keep the ADR
references in step with the real numbers). The block uses level-3 headings so it nests under `## Stack rules`:

```markdown
### Hard rules (.NET house preset)

- **Clean Architecture, strictly inward**: `Domain <- Application <- Infrastructure <- Web`. `Domain` has
  zero project references. `Application` has no `using Dapper`, `SqlClient`, `HttpClient` or SDK types.
- **Dapper only. No EF Core anywhere.** SQL is hand-written, parameterised, schema-qualified, with explicit
  column lists, embedded as `const string` fields named by intent.
- **Repository ports live in `Domain/Repositories`**, implementations in `Infrastructure/Repositories`;
  repositories take `(connection, transaction)` and never open connections.
- **Module service pattern**: a page injects exactly one `IXxxService` from `Application`; never a
  repository, a connection or the unit-of-work factory.
- **Unit of work**: `IUnitOfWorkFactory.CreateAsync(principal, ct)`; the service picks the SQL principal and
  calls `CompleteAsync()` on writes; dispose without complete rolls back.
- **Code-behind**: `.razor` + `.razor.cs` partial classes; no `@code` block longer than five lines.
- **Migrations**: `Database/Migrations/NNNN_Name.sql` (four digits, in the range of its card), idempotent,
  `SET QUOTED_IDENTIFIER ON`, `USE $(DbName)`, run in order by `Database/Tools/bootstrap-db.ps1`; each writes
  its `app.SchemaVersion` row; demo seeds behind `$(SeedDemo)`; never a schema named `sys`; no `dbo` objects.
  A migration and `docs/data-model.md` change together.
- **One class per file; `sealed` by default; `CancellationToken ct = default` last on every async method;
  timestamps suffixed `Utc`; `_camelCase` private fields; `Nullable` and `ImplicitUsings` on.**
- **Time only through the clock port**; store UTC; no `DateTime.Now` and no `GETDATE()` for business values.
- **No status strings and no sentinel values** in code or SQL; states are enums backed by `CK_` constraints.
- **Every page and endpoint has an authorization policy** naming one permission code; never check a role name.
- **Never log, store or echo credentials or connection strings.** Committed `appsettings*.json` hold no secret.
- **Tests**: xUnit + FluentAssertions; every test has `[Trait("Level", ...)]`; test-first; pyramid 60/30/10
  by count; external systems through fakes that pass the contract test.
  **Run `dotnet build` and `dotnet test` after every structural change** before reporting done.
- **SOLID and KISS**: one reason to change per class; extend through ports, never by editing a switch; no
  interface with a single implementation unless a port rule requires it; no framework beyond the card; no
  new package without an ADR.

### Prohibitions

- Do not add EF Core, MediatR, AutoMapper, FluentValidation, a UI component library, Hangfire or Quartz
  without an ADR; the package baseline is `docs/environments-and-delivery.md` and anything outside it needs an ADR.
- Do not hard-code colours, sizes, fonts or user text in pages; use the tokens, components and resources.
- Do not create per-environment or per-site build configurations, `#if` blocks or branches.
- Do not put runtime secrets in committed settings files; use user secrets locally and server-side
  configuration on servers.
```

## 10. Environments and delivery defaults

### 10.1 Environments

| Environment | Where | Database | External systems | `ASPNETCORE_ENVIRONMENT` |
|---|---|---|---|---|
| Dev | developer machine, local SQL Server | `<Product>Dev`; tests create and drop `<Product>Test_<stamp>` | fakes, recorded contracts | `Development` |
| Test | IIS site or sub-application on the test server | `<Product>Test` | test instances where they exist | `Test` |
| Prod | IIS site on the production server | `<Product>` | production | `Production` |

- One IIS site (or sub-application) and one application pool per environment. The pool runs as a gMSA
  (group managed service account) where the directory team can create one, otherwise a dedicated service
  account; never a personal account.
- Prerequisites on each server: the .NET 10 ASP.NET Core Hosting Bundle, IIS Windows Authentication feature;
  IIS Anonymous Authentication off for the site unless the spec names anonymous pages.
- `appsettings.Development.json` is committed without secrets and marked `CopyToPublishDirectory="Never"`.
  `appsettings.<Environment>.json` on servers holds non-secret settings only.
- The `Testing` authentication scheme and the dev impersonation exist only in `Development` and `Testing`.

### 10.2 Secrets

| Secret | Dev | Test and Prod |
|---|---|---|
| Connection strings per principal | `dotnet user-secrets` on the Web project | IIS site environment variables (`ConnectionStrings__<Product>Writer`) set by the runbook, or a protected settings file outside the site folder |
| SQL login passwords | runner prompt, stored in user secrets | runner secure prompt; different per environment; rotated when a builder or a log saw one |
| External credentials and API keys | user secrets | environment variables or a DPAPI-protected file with an ACL for the pool identity |

The verify recipe greps committed files for secret patterns. (The convention source still commits
development passwords in `appsettings.json`; new projects do not.)

### 10.3 Source control and CI

- Git working repository with `main` and a branch per task card; linear history (fast-forward or squash).
- The system of record (company server or GitHub) is an interview answer (bank 0.9); a remote is a human gate
  before the first code card.
- CI: `Database/Tools/predeploy.ps1` is the verify recipe (restore, build with warnings as errors, tests per
  level, pyramid report, secrets scan, publish). A pipeline file running the same script is committed but
  inactive until the team has a build server.

### 10.4 Package baseline (`Directory.Packages.props`)

| Area | Packages |
|---|---|
| Data | `Dapper`, `Microsoft.Data.SqlClient` |
| Web | `Microsoft.AspNetCore.Authentication.Negotiate` |
| Tests | `xunit`, `xunit.runner.visualstudio`, `Microsoft.NET.Test.Sdk`, `FluentAssertions`, `Microsoft.AspNetCore.Mvc.Testing`, `Microsoft.Playwright` |
| Optional, by interview answer | `ClosedXML` (Excel export), `Microsoft.AspNetCore.OpenApi` (inbound API) |
| Forbidden without an ADR | EF Core, MediatR, AutoMapper, FluentValidation, any UI component library, Hangfire, Quartz, Serilog or NLog (logging goes through `Microsoft.Extensions.Logging`) |

FluentAssertions: the convention source pins 7.x; version 8 and later need a paid licence for commercial use.
Record the choice as a `Q-nn` with the default "pin 7.x" unless the user already has a licence.

### 10.5 Versioning, deployment, rollback

- Version `MAJOR.MINOR.PATCH` (or `Release.Phase.Build` when the roadmap has numbered releases), stamped into
  the assemblies, the health page and log entries; a release is an annotated git tag plus a line in
  `docs/releases.md` (cards included, migrations, rollback notes).
- Deployment (manual until CI deploys): run the verify recipe and publish; put `app_offline.htm` in the site
  folder (IIS locks the DLLs otherwise); copy the published folder; run `bootstrap-db.ps1` against the
  environment's database with the deploy login; remove `app_offline.htm`; check the health page; run a smoke
  journey. Deployment windows and approvers come from the interview (bank 6.4, 6.7).
- Rollback: the previous published folder, on the newer schema within the agreed window; never a down-migration.
- A runbook `docs/deploy-test.md` (and later `docs/deploy-prod.md`) is written by the card that first deploys.

### 10.6 Observability

- Logging through `Microsoft.Extensions.Logging` with a correlation id on every request and every external
  call; never a secret in a log entry.
- `/health` (authenticated, detailed: build version, database reachable per login, schema version status,
  background service leases) and `/api/health` (anonymous liveness only).
- Alerts to developers only unless the interview decides otherwise (bank 6.5); backup and restore follow the
  server team's standard until the interview decides otherwise (bank 6.6).

## 11. Known gotchas

| Trap | Rule |
|---|---|
| `sys` is a reserved schema in SQL Server (error 2760) | Name the internal schema `app` |
| `sqlcmd` runs with `QUOTED_IDENTIFIER OFF`; DML on a table with a filtered index then fails (error 1934) | Every migration and ad-hoc script starts with `SET QUOTED_IDENTIFIER ON` |
| `sqlcmd` reads files as the ANSI code page by default and mangles non-ASCII seed text | The runner passes `-f 65001` |
| `SQLCMDUSER` / `SQLCMDPASSWORD` environment variables override the runner's authentication | The runner clears both before running |
| `HttpContext` is null inside the interactive circuit | Read identity from the cascading authentication state |
| Queued clicks bypass a `disabled` button in Blazor Server | Re-check preconditions inside the handler |
| Prerender shows the wrong branch for per-circuit state | `prerender: false` on such pages |
| A singleton for per-user UI state leaks between circuits | Scoped services; timers in components with `InvokeAsync` |
| Absolute links break under an IIS sub-application | `<base href>` from `PathBase`; base-relative links |
| Kestrel on `localhost` fails Negotiate with HTTP 400 outside a domain | Verify under IIS Express or IIS |
| Server culture does not format Excel cells, template engines or native date inputs | Set explicit formats per surface; one shared date display helper |
| A global Dapper type handler must be registered before the first query | Convert `DateOnly` at the repository edge instead |
| Publishing over a running IIS site fails on locked DLLs | `app_offline.htm` first |
| SQL Server restores are forward-only (a newer-version backup does not restore on an older server) | Keep test and production on the same SQL Server version and collation |
| The running app (preview) locks `bin/Debug` DLLs; MSB3021/MSB3026 copy errors print as "N Error(s)" although the code is fine | Build and test with `-c Release` while the preview runs, or stop it; judge by the exit code |
| The secrets scan in `predeploy.ps1` uses `git ls-files` and breaks when the code moves to TFS or a plain folder | Walk the files under the repository root with a skip list (`bin`, `obj`, `TestResults`, `node_modules`, `.vs`, worktrees) |
| A document that lists the secret patterns (the security review) trips the secrets scan | Write the patterns self-safe (`Passwor[d]=`), no allow-list entry |
| A demo seed inserts workflow rows into a period the app already created in another state (a request inside a week that is still a draft), and approving it throws | The seed inserts such rows only when the period is in the state the workflow requires; recreate the local database from the migrations after changing a seed |

## 12. Questions the preset leaves open

Ask these in the next numbered batch (defaults shown):

| Question | Default |
|---|---|
| Integer keys (this preset) or GUID keys (the convention source)? | Integer keys, GUID `PublicId` only where an id leaves the system |
| SQL logins with passwords, or Windows logins for the pool identity? | SQL logins per principal (works for dev and servers alike) |
| Server names for test and production; is there a test server at all before a pilot? | Test and production on the team's existing IIS and SQL servers |
| Can the directory team create a gMSA for the application pool? | Yes; otherwise a dedicated service account |
| Does the app need to search the directory (user picker), and through Microsoft Graph or LDAP? | No; administrators type the Windows account name |
| How are people and teams added in release 1 (bank 1.10)? | An admin screen if they change monthly; otherwise `add-person.ps1` / `add-team.ps1` that write `Users`, the person row and the scoped role in one transaction |
| Collation and languages stored (bank 1.7)? | `Latin1_General_100_CI_AS_SC` for every database |
| One database per environment, or per site as well (bank 3.5)? | One per environment |
| FluentAssertions version (licence)? | Pin 7.x |
| Is there a build server for the prepared pipeline? | Not yet; the local verify recipe is the gate |
| Background work needed (ADR order 9)? | None in release 1 |
