import type { Directive } from 'vue';

type OutsideClickCallback = (event: Event) => void;

const instanceMap = new Map<HTMLElement, OutsideClickCallback>();

export const outsideClickDirective: Directive<
  HTMLElement,
  OutsideClickCallback
> = {
  beforeMount(element, binding) {
    const clickHandler = (event: Event) => {
      onDocumentClick(event, element, binding.value);
    };

    removeHandlerIfPresent(element);
    instanceMap.set(element, clickHandler);
    document.addEventListener('click', clickHandler);
  },
  unmounted(element) {
    removeHandlerIfPresent(element);
  },
};

function onDocumentClick(
  event: Event,
  element: HTMLElement,
  callback: OutsideClickCallback
) {
  const target = event.target as Node;
  if (element !== target && !element.contains(target)) {
    callback(event);
  }
}

function removeHandlerIfPresent(element: HTMLElement) {
  const clickHandler = instanceMap.get(element);
  if (!clickHandler) {
    return;
  }

  instanceMap.delete(element);
  document.removeEventListener('click', clickHandler);
}
