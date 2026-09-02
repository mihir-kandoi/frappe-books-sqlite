interface ModMap {
  alt: boolean;
  ctrl: boolean;
  meta: boolean;
  shift: boolean;
  repeat: boolean;
}

type Mod = keyof ModMap;
type Context = unknown;
type ShortcutFunction = () => unknown;
type ShortcutConfig = {
  callback: ShortcutFunction;
  propagate: boolean;
};

type ShortcutMap = Map<Context, Map<string, ShortcutConfig>>;

const mods: Readonly<Mod[]> = ['alt', 'ctrl', 'meta', 'repeat', 'shift'];

function getIsMac(): boolean {
  return navigator.userAgent.includes('Mac');
}

/**
 * Used to add shortcuts based on **context**.
 *
 * **Context** is a identifier for where the shortcut belongs. For instance
 * a _Form_ component having shortcuts for _Submit Form_.
 *
 * In the above example an app can have multiple instances of the _Form_
 * component active at the same time, so the passed context should be a
 * unique identifier such as the component object.
 *
 * If only one instance of a component is meant to be active at a time
 * (for example a _Sidebar_ component) then do not use objects, use some
 * primitive datatype (`string`).
 */
export class Shortcuts {
  isMac: boolean;
  shortcuts: ShortcutMap;
  modMap: Partial<Record<Mod, boolean>>;
  #isListening: boolean;
  #keydownListener: (event: KeyboardEvent) => void;

  constructor(isMac = getIsMac()) {
    this.modMap = {};
    this.shortcuts = new Map();
    this.isMac = isMac;
    this.#isListening = false;
    this.#keydownListener = (event) => this.handleKeydown(event);
  }

  start(): void {
    if (this.#isListening) {
      return;
    }

    window.addEventListener('keydown', this.#keydownListener, true);
    this.#isListening = true;
  }

  stop(): void {
    if (!this.#isListening) {
      return;
    }

    window.removeEventListener('keydown', this.#keydownListener, true);
    this.#isListening = false;
  }

  handleKeydown(event: KeyboardEvent): boolean {
    if (this.#isEditableTarget(event)) {
      return false;
    }

    const key = this.getKey([event.code], {
      alt: event.altKey,
      ctrl: event.ctrlKey,
      meta: event.metaKey,
      repeat: event.repeat,
      shift: event.shiftKey,
    });

    if (!key) {
      return false;
    }

    if (!this.#hasActiveShortcut(key)) {
      if (!event.repeat) {
        return false;
      }

      const nonRepeatingKey = this.getKey([event.code], {
        alt: event.altKey,
        ctrl: event.ctrlKey,
        meta: event.metaKey,
        repeat: false,
        shift: event.shiftKey,
      });
      if (!nonRepeatingKey || !this.#hasActiveShortcut(nonRepeatingKey)) {
        return false;
      }

      event.preventDefault();
      return true;
    }

    event.preventDefault();
    this.#trigger(key);
    return true;
  }

  #trigger(key: string) {
    const configList = Array.from(this.shortcuts.keys())
      .map((cxt) => this.shortcuts.get(cxt)?.get(key))
      .filter(Boolean)
      .reverse() as ShortcutConfig[];

    for (const config of configList) {
      config.callback();
      if (!config.propagate) {
        break;
      }
    }
  }

  #hasActiveShortcut(key: string): boolean {
    return Array.from(this.shortcuts.values()).some((shortcuts) =>
      shortcuts.has(key)
    );
  }

  #isEditableTarget(event: KeyboardEvent): boolean {
    if (event.altKey || event.ctrlKey || event.metaKey) {
      return false;
    }

    const target = event.target as HTMLElement | null;
    const tagName = target?.tagName?.toLowerCase();
    return (
      tagName === 'input' ||
      tagName === 'select' ||
      tagName === 'textarea' ||
      target?.contentEditable === 'true'
    );
  }

  /**
   * Check if a context is present or if a shortcut
   * is present in a context.
   *
   * @param context context in which the shortcut is to be checked
   * @param shortcut shortcut that is to be checked
   * @returns boolean indicating presence
   */
  has(context: Context, shortcut?: string[]): boolean {
    if (!shortcut) {
      return this.shortcuts.has(context);
    }

    const contextualShortcuts = this.shortcuts.get(context);
    if (!contextualShortcuts) {
      return false;
    }

    const key = this.getKey(shortcut);
    if (!key) {
      return false;
    }

    return contextualShortcuts.has(key);
  }

  /**
   * Assign a function to a shortcut in a given context.
   *
   * @param context context object to which the shortcut belongs
   * @param shortcut keyboard event codes used as shortcut chord
   * @param callback function to be called when the shortcut is pressed
   * @param propagate whether to check and execute shortcuts in earlier contexts
   * @param removeIfSet whether to delete the set shortcut
   */
  set(
    context: Context,
    shortcut: string[],
    callback: ShortcutFunction,
    propagate = false,
    removeIfSet = true
  ): void {
    const key = this.getKey(shortcut);
    if (!key) {
      return;
    }

    let contextualShortcuts = this.shortcuts.get(context);

    /**
     * Maintain context order.
     */
    if (!contextualShortcuts) {
      contextualShortcuts = new Map();
    } else {
      this.shortcuts.delete(context);
    }

    if (contextualShortcuts.has(key) && !removeIfSet) {
      this.shortcuts.set(context, contextualShortcuts);
      throw new Error(`Shortcut ${key} already exists.`);
    }

    contextualShortcuts.set(key, { callback, propagate });
    this.shortcuts.set(context, contextualShortcuts);
  }

  /**
   * Either delete a single shortcut or all the shortcuts in
   * a given context.
   *
   * @param context context from which the shortcut is to be removed
   * @param shortcut shortcut that is to be deleted
   * @returns boolean indicating success
   */
  delete(context: Context, shortcut?: string[]): boolean {
    if (!shortcut) {
      return this.shortcuts.delete(context);
    }

    const contextualShortcuts = this.shortcuts.get(context);
    if (!contextualShortcuts) {
      return false;
    }

    const key = this.getKey(shortcut);
    if (!key) {
      return false;
    }

    return contextualShortcuts.delete(key);
  }

  /**
   * Converts shortcuts list and modMap to a string to be
   * used as a shortcut key.
   *
   * @param shortcut array of shortcut keys
   * @param modMap boolean map of mod keys to be used
   * @returns string to be used as the shortcut Map key
   */
  getKey(shortcut: string[], modMap?: Partial<ModMap>): string | null {
    const _modMap = modMap || this.modMap;
    this.modMap = {};

    const shortcutString = shortcut.sort().join('+');
    const modString = mods.filter((k) => _modMap[k]).join('+');
    if (shortcutString && modString) {
      return modString + '+' + shortcutString;
    }

    if (!modString) {
      return shortcutString;
    }

    if (!shortcutString) {
      return modString;
    }

    return null;
  }

  /**
   * Shortcut Modifiers
   */
  get alt() {
    this.modMap['alt'] = true;
    return this;
  }

  get ctrl() {
    this.modMap['ctrl'] = true;
    return this;
  }

  get meta() {
    this.modMap['meta'] = true;
    return this;
  }

  get shift() {
    this.modMap['shift'] = true;
    return this;
  }

  get pmodShift() {
    if (this.isMac) {
      this.modMap['meta'] = true;
    } else {
      this.modMap['ctrl'] = true;
    }
    this.modMap['shift'] = true;
    return this;
  }

  get repeat() {
    this.modMap['repeat'] = true;
    return this;
  }

  get pmod() {
    if (this.isMac) {
      return this.meta;
    }

    return this.ctrl;
  }
}
