import type { TemplateFile } from 'utils/types';

type FileSelection = {
  name: string;
  success: boolean;
  canceled: boolean;
  data: Uint8Array;
  filePath: string;
};

type FileSelectionOptions = {
  title?: string;
  accept?: string;
  defaultPath?: string;
  properties?: string[];
  filters?: { name?: string; extensions?: string[] }[];
};

type SaveFileSelection = {
  canceled: boolean;
  filePath: string;
};

export interface WebIPC {
  desktop: boolean;
  openLink(url: string): Window | null;
  openExternalUrl(url: string): Window | null;
  reloadWindow(): void;
  sendError(body: string): Promise<void>;
  showError(title: string, content: string): Promise<void>;
  sendAPIRequest(url: string, options?: RequestInit): Promise<unknown>;
  selectFile(options?: FileSelectionOptions): Promise<FileSelection>;
  getOpenFilePath(options?: FileSelectionOptions): Promise<FileSelection>;
  getSaveFilePath(options?: FileSelectionOptions): Promise<SaveFileSelection>;
  saveData(data: string | Uint8Array, filePath?: string): Promise<void>;
  makePDF(
    html: string,
    filePath?: string,
    width?: number,
    height?: number
  ): Promise<boolean>;
  printDocument(
    html: string,
    width?: number,
    height?: number
  ): Promise<boolean>;
  getTemplates(posTemplateWidth?: number): Promise<TemplateFile[]>;
  showItemInFolder(filePath: string): void;
  deleteFile(filePath: string): Promise<{
    error: null | {
      message: string;
      name: string;
      stack?: string;
      code?: string;
    };
  }>;
}

declare global {
  const ipc: WebIPC;

  interface Window {
    ipc?: WebIPC;
  }
}

export function installWebIpc() {
  if (window.ipc) return;

  window.ipc = {
    desktop: false,
    openLink: (url: string) =>
      window.open(url, '_blank', 'noopener,noreferrer'),
    openExternalUrl: (url: string) =>
      window.open(url, '_blank', 'noopener,noreferrer'),
    reloadWindow: () => window.location.reload(),
    sendError: () => Promise.resolve(),
    showError: (title: string, content: string) => {
      window.alert(`${title}\n\n${content}`);
      return Promise.resolve();
    },
    sendAPIRequest: (url: string, options?: RequestInit) =>
      fetch(url, options).then((response) => response.json()),
    selectFile: (options?: FileSelectionOptions) =>
      selectFile(options?.accept || extensionAccept(options?.filters)),
    getOpenFilePath: (options?: { filters?: { extensions?: string[] }[] }) =>
      selectFile(extensionAccept(options?.filters)),
    getSaveFilePath: (options?: FileSelectionOptions) =>
      Promise.resolve<SaveFileSelection>({
        canceled: false,
        filePath: options?.defaultPath || 'frappe-books-export',
      }),
    saveData: async (
      data: string | Uint8Array,
      filePath = 'frappe-books-export'
    ) => {
      download(data, filePath);
    },
    makePDF: async (
      html: string,
      filePath = 'frappe-books.pdf',
      _width?: number,
      _height?: number
    ) =>
      Boolean(filePath) && (await printHtml(html)),
    printDocument: (
      html: string,
      _width?: number,
      _height?: number
    ) => printHtml(html),
    getTemplates: (_posTemplateWidth?: number) =>
      Promise.resolve<TemplateFile[]>([]),
    showItemInFolder: () => undefined,
    deleteFile: () => Promise.resolve({ error: null }),
  };
}

function selectFile(accept = '*/*'): Promise<FileSelection> {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = accept;
    input.onchange = () => {
      const file = input.files?.[0];
      if (!file) {
        resolve({
          name: '',
          filePath: '',
          data: new Uint8Array(),
          success: false,
          canceled: true,
        });
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        if (!(reader.result instanceof ArrayBuffer)) {
          resolve({
            name: file.name,
            filePath: file.name,
            data: new Uint8Array(),
            success: false,
            canceled: false,
          });
          return;
        }

        resolve({
          name: file.name,
          filePath: file.name,
          data: new Uint8Array(reader.result),
          success: true,
          canceled: false,
        });
      };
      reader.readAsArrayBuffer(file);
    };
    input.click();
  });
}

function extensionAccept(filters?: { extensions?: string[] }[]) {
  const extensions =
    filters?.flatMap((filter) => filter.extensions || []) || [];
  return extensions.length
    ? extensions.map((extension) => `.${extension}`).join(',')
    : '*/*';
}

function download(data: string | Uint8Array, filePath: string) {
  let content: string | ArrayBuffer;
  if (typeof data === 'string') {
    content = data;
  } else {
    const bytes = new Uint8Array(data.byteLength);
    bytes.set(data);
    content = bytes.buffer;
  }
  const blob = new Blob([content], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filePath.split('/').pop() || 'frappe-books-export';
  anchor.click();
  URL.revokeObjectURL(url);
}

async function printHtml(html: string): Promise<boolean> {
  const popup = window.open('', '_blank');
  if (!popup) return false;

  popup.document.open();
  popup.document.write(`<!DOCTYPE html>${html}`);
  popup.document.close();
  await waitForPrintContent(popup);
  popup.focus();
  popup.addEventListener('afterprint', () => popup.close(), { once: true });
  popup.print();
  return true;
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
    new Promise<void>((resolve) => window.setTimeout(resolve, 3000)),
  ]);
  await new Promise<void>((resolve) =>
    popup.requestAnimationFrame(() =>
      popup.requestAnimationFrame(() => resolve())
    )
  );
}
