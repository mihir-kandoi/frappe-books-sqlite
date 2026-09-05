import type { RouteLocationNormalizedLoaded } from 'vue-router';

type SidebarRoute = Pick<
  RouteLocationNormalizedLoaded,
  'path' | 'params' | 'meta'
>;

export function getSidebarPath(route: SidebarRoute): string {
  const pattern = route.meta.sidebarPath;
  if (typeof pattern !== 'string') {
    return route.path;
  }

  return pattern.replace(/:(\w+)/g, (_, key: string) =>
    encodeURIComponent(String(route.params[key] ?? ''))
  );
}

export function matchesSidebarPath(
  currentPath: string,
  itemPath: string
): boolean {
  const current = decodeURI(currentPath);
  const item = decodeURI(itemPath);
  if (current === item) {
    return true;
  }

  // List titles distinguish filtered lists, but their forms share one schema.
  if (current.startsWith('/list/') && item.startsWith('/list/')) {
    return current.split('/')[2] === item.split('/')[2];
  }

  return item !== '/' && current.startsWith(item + '/');
}
