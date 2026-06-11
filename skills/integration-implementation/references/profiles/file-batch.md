# File / batch profile

Per-boundary guidance for the
[`integration-implementation`](../../SKILL.md) skill when the
target boundary is a file import or export — SFTP pickup, S3 /
blob storage object, scheduled batch file, etc. Read on demand;
do not load wholesale.

> **Scope:** This profile covers the file-transfer layer
> (fetch, parse, validate, hand off to the consumer, write
> results). The business logic that consumes the parsed rows is
> **backend code** and is covered by
> [`backend-implementation`](../../../backend-implementation/SKILL.md).

## Detection cues

The target boundary matches this profile if any of the following
are present:

- SFTP / FTP / FTPS client (`ssh2-sftp-client`,
  `paramiko`, `jsch`)
- S3 / Azure Blob / GCS client (`@aws-sdk/client-s3`,
  `boto3`, `azure-storage-blob`, `@google-cloud/storage`)
- Local file pickup with cron / scheduled task
- File format parsers: CSV (`papaparse`, `csv-parse`,
  `pandas.read_csv`), JSON, XML, fixed-width, Excel
  (`xlsx`, `openpyxl`, `exceljs`)
- File naming convention with date / batch id
  (`users_2025-01-15.csv`, `outbound_2025-01-15_001.parquet`)

## Conventions to preserve

- **Transfer mechanism:** match the repo (SFTP, S3, blob
  storage, local). Do not introduce a new mechanism.
- **File format:** match the repo (CSV, JSON, XML, Parquet,
  Avro, fixed-width). Reuse the existing parser.
- **Encoding / delimiter:** match the repo (UTF-8 with BOM,
  Latin-1, comma vs semicolon for CSV).
- **Schema:** match the repo's schema definition (header row,
  schema file, Avro / Protobuf schema, Parquet schema).
- **Idempotency:** match the repo's existing approach (file
  name + processed marker, processed-files table, S3 object
  lock, archival to `processed/` prefix).
- **Error handling:** match the repo (per-row error vs
  whole-file abort, dead-letter file).
- **Logging:** match the repo. **Do not log full file
  contents**; log file name, batch id, row counts, error
  summaries.

## Required design checks

| Check | Default expectation |
| --- | --- |
| Parsing | schema-validated, malformed rows surfaced |
| Malformed file | partial failure handling — bad rows in error file, good rows processed |
| Idempotency | processed marker (table, S3 prefix, file move); second run on same file is a no-op |
| Audit trail | who / when / what / outcome recorded |
| Logging without secrets | payload redaction list documented |
| Observability | batch id, file name, row counts logged |
| Backpressure / scale | stream parser for large files; do not load entire file in memory when avoidable |

## Required tests

At minimum, cover:

- success — valid file, all rows processed
- malformed row — partial failure, bad row in error file,
  good rows processed
- malformed file (header / encoding wrong) — whole-file abort,
  no rows processed, error logged
- duplicate file (idempotency) — second run is a no-op
- empty file — explicit handling (success with zero rows, or
  abort, depending on repo policy)
- large file — stream-parse, memory bounded (manual check or
  perf test, only when relevant)

For each, use a recorded fixture file or a generated test file.
**Do not use a real production file location.**

## Forbidden actions

- **Do not use a real production file location** (real S3
  bucket, real SFTP server) for tests. Use local fixtures,
  MinIO, LocalStack, or a test bucket / SFTP server with
  synthetic data.
- **Do not commit real data files** to the repo, even as
  fixtures, when they may contain PII. Generate synthetic
  data instead.
- **Do not change the file format** (CSV → JSON, JSON →
  Parquet) without explicit approval and a
  [`dependency-change-review`](../../../dependency-change-review/SKILL.md)
  gate if a new parser is introduced.
- **Do not introduce a new file-transfer mechanism** (SFTP →
  S3, local → S3) without explicit approval.
- **Do not log full file contents** when they may contain
  PII; log counts, ids, and error summaries instead.
- **Do not bypass the orchestrator** when the task also
  touches pure backend or frontend code.

## Small example

A CSV importer that processes a daily user file, with explicit
partial-failure handling, idempotency, and redacted logging:

```typescript
// user-csv-importer.ts
export class UserCsvImporter {
  constructor(
    private readonly storage: BlobStorage,         // matches repo
    private readonly processed: ProcessedMarker,   // matches repo
    private readonly logger: Logger,
  ) {}

  async import(fileName: string, stream: ReadableStream): Promise<ImportResult> {
    if (await this.processed.isDone(fileName)) {
      this.logger.info('import.skipped', { fileName });
      return { processed: 0, errors: 0, skipped: true };
    }
    const errors: RowError[] = [];
    let processed = 0;
    await streamRows(stream, async (row, lineNo) => {
      try {
        validateRow(row);
        await processUserRow(row);                 // backend
        processed++;
      } catch (e) {
        errors.push({ lineNo, error: String(e), redacted: redactRow(row) });
      }
    });
    if (errors.length) {
      await this.storage.putObject(`errors/${fileName}.errors.json`, errors);
    }
    await this.processed.markDone(fileName);
    this.logger.info('import.done', { fileName, processed, errors: errors.length });
    return { processed, errors: errors.length, skipped: false };
  }
}
```

```typescript
// user-csv-importer.test.ts
import { Readable } from 'node:stream';

it('skips a file that is already processed', async () => {
  processed.isDone.mockResolvedValueOnce(true);
  const res = await importer.import('users_2025-01-15.csv', Readable.from([]));
  expect(res.skipped).toBe(true);
  expect(res.processed).toBe(0);
});

it('records malformed rows to the error file and continues', async () => {
  storage.putObject.mockResolvedValueOnce(undefined);
  const stream = Readable.from([
    'id,name\n1,Ada\n,bad\n3,Lin\n',
  ]);
  const res = await importer.import('users_2025-01-16.csv', stream);
  expect(res.processed).toBe(2);
  expect(res.errors).toBe(1);
  expect(storage.putObject).toHaveBeenCalledWith(
    expect.stringContaining('users_2025-01-16.csv.errors.json'),
    expect.anything(),
  );
});

it('does not log full row contents', async () => {
  const stream = Readable.from(['id,name\n1,Ada\n']);
  await importer.import('users_2025-01-17.csv', stream);
  expect(logger.lastInfo()).not.toMatchObject({ row: expect.anything() });
});
```

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profiles: [`rest-api.md`](rest-api.md),
  [`async-messaging.md`](async-messaging.md),
  [`webhook.md`](webhook.md),
  [`contract-testing.md`](contract-testing.md)
- Backend (row processing): [`../../../backend-implementation/SKILL.md`](../../../backend-implementation/SKILL.md)
- Dependency review: [`../../../dependency-change-review/SKILL.md`](../../../dependency-change-review/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md),
  [`../../../security-review/SKILL.md`](../../../security-review/SKILL.md)
