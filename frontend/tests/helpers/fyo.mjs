import { after } from 'node:test';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const directory = await mkdtemp(path.join(tmpdir(), 'books-custom-form-'));
after(() => rm(directory, { recursive: true, force: true }));
const output = path.join(directory, 'models.cjs');
const frontend = fileURLToPath(new URL('../..', import.meta.url));
await build({
  absWorkingDir: frontend,
  stdin: {
    contents:
      "export { Fyo } from './fyo'; export { getSchemas } from './schemas';",
    resolveDir: frontend,
  },
  bundle: true,
  platform: 'node',
  format: 'cjs',
  outfile: output,
});
export const { Fyo, getSchemas } = createRequire(import.meta.url)(output);
