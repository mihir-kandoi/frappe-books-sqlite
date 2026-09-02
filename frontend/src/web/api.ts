type FrappeResponse<T> = {
  message: T;
  exception?: string;
  _server_messages?: string;
};

export async function call<T>(method: string, args: unknown = {}): Promise<T> {
  const csrfToken = window.frappe?.csrf_token || window.csrf_token;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  if (csrfToken) {
    headers['X-Frappe-CSRF-Token'] = csrfToken;
  }

  const response = await fetch(`/api/method/${method}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers,
    body: JSON.stringify(args),
  });
  const payload = (await response.json()) as FrappeResponse<T>;
  if (!response.ok || payload.exception) {
    throw new Error(getErrorMessage(payload));
  }
  return payload.message;
}

function getErrorMessage(payload: FrappeResponse<unknown>): string {
  if (payload._server_messages) {
    try {
      const messages = JSON.parse(payload._server_messages) as unknown;
      if (Array.isArray(messages)) {
        return messages.map(getServerMessage).join('\n');
      }
    } catch {
      return payload._server_messages;
    }
  }
  return payload.exception || 'The Frappe Books request failed.';
}

function getServerMessage(value: unknown): string {
  if (typeof value !== 'string') {
    return String(value);
  }

  try {
    const parsed = JSON.parse(value) as unknown;
    if (parsed && typeof parsed === 'object') {
      const message = (parsed as Record<string, unknown>).message;
      if (typeof message === 'string') {
        return message;
      }
    }
  } catch {
    return value;
  }

  return value;
}

declare global {
  interface Window {
    csrf_token?: string;
    frappe: {
      csrf_token?: string;
      boot?: {
        lang?: string;
        user?: { name?: string };
        [key: string]: unknown;
      };
    };
    books_boot: {
      country_code: string;
      setup_complete: boolean;
      app_version: string;
      developer_mode: boolean;
    };
  }
}
