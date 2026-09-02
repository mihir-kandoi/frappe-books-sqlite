import type { SelectFileOptions } from 'utils/types';

export type SelectedFile = {
  name: string;
  data: Uint8Array;
};

export function downloadFile(
  data: string | Uint8Array,
  fileName: string,
  type = 'application/octet-stream'
) {
  let content: string | ArrayBuffer;
  if (typeof data === 'string') {
    content = data;
  } else {
    const bytes = new Uint8Array(data.byteLength);
    bytes.set(data);
    content = bytes.buffer;
  }
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = fileName;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url));
}

export function selectFile(
  options?: Partial<SelectFileOptions>
): Promise<SelectedFile | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = getAcceptedExtensions(options?.filters);
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) {
        resolve(null);
        return;
      }

      resolve({
        name: file.name,
        data: new Uint8Array(await file.arrayBuffer()),
      });
    };
    input.click();
  });
}

export async function printHtml(html: string): Promise<boolean> {
  const popup = window.open('', '_blank');
  if (!popup) {
    return false;
  }

  popup.document.open();
  popup.document.write(`<!DOCTYPE html>${html}`);
  popup.document.close();
  await waitForPrintContent(popup);
  popup.focus();
  popup.addEventListener('afterprint', () => popup.close(), { once: true });
  popup.print();
  return true;
}

function getAcceptedExtensions(
  filters?: { extensions: string[] }[]
): string {
  const extensions = filters?.flatMap((filter) => filter.extensions) ?? [];
  return extensions.length
    ? extensions.map((extension) => `.${extension}`).join(',')
    : '*/*';
}

async function waitForPrintContent(popup: Window) {
  const images = Array.from(popup.document.images).filter(
    (image) => !image.complete
  );
  const imageReady = Promise.all(
    images.map(
      (image) =>
        new Promise<void>((resolve) => {
          image.addEventListener('load', () => resolve(), { once: true });
          image.addEventListener('error', () => resolve(), { once: true });
        })
    )
  );
  const fontsReady = popup.document.fonts?.ready ?? Promise.resolve();

  await Promise.race([
    Promise.all([imageReady, fontsReady]),
    new Promise<void>((resolve) => window.setTimeout(resolve, 3_000)),
  ]);
  await new Promise<void>((resolve) =>
    popup.requestAnimationFrame(() =>
      popup.requestAnimationFrame(() => resolve())
    )
  );
}
