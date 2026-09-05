import { Doc } from 'fyo/model/doc';
import { FieldTypeEnum } from 'schemas/types';

type PrintTemplateData = Record<string, unknown>;

export async function getPrintTemplateDocValues(
  doc: Doc,
  fieldnames?: string[],
  ancestors: ReadonlySet<Doc> = new Set()
) {
  const values: PrintTemplateData = {};
  if (!(doc instanceof Doc) || ancestors.has(doc)) {
    return values;
  }
  // Linked records can point back to a parent, but siblings must expand independently.
  const path = new Set(ancestors).add(doc);

  let fields = doc.schema.fields;
  if (fieldnames) {
    fields = fields.filter((f) => fieldnames.includes(f.fieldname));
  }

  // Set Formatted Doc Data
  for (const field of fields) {
    const { fieldname, fieldtype, meta } = field;
    if (fieldtype === FieldTypeEnum.Attachment || meta) {
      continue;
    }

    const value = doc.get(fieldname);

    if (!value) {
      values[fieldname] = '';
      continue;
    }

    if (!Array.isArray(value)) {
      values[fieldname] = doc.fyo.format(value, field, doc);
      continue;
    }

    const table: PrintTemplateData[] = [];
    for (const row of value) {
      const rowProps = await getPrintTemplateDocValues(row, undefined, path);
      table.push(rowProps);
    }

    values[fieldname] = table;
  }

  values.submitted = doc.submitted;
  values.entryType = doc.schema.name;
  values.entryLabel = doc.schema.label;

  // Set Formatted Doc Link Data
  await doc.loadLinks();
  const links: PrintTemplateData = {};
  for (const [linkName, linkDoc] of Object.entries(doc.links ?? {})) {
    if (fieldnames && !fieldnames.includes(linkName)) {
      continue;
    }
    if (path.has(linkDoc)) {
      continue;
    }

    links[linkName] = await getPrintTemplateDocValues(linkDoc, undefined, path);
  }

  if (Object.keys(links).length) {
    values.links = links;
  }
  return values;
}
