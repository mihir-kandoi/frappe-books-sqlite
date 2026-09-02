import { copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptDirectory, '../..');
const builtEntry = path.resolve(
  appRoot,
  'frappe_books/public/books/index.html'
);
const websiteEntry = path.resolve(appRoot, 'frappe_books/www/books.html');

await copyFile(builtEntry, websiteEntry);
