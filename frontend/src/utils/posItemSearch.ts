import { POSItem } from 'src/components/POS/types';
import { fuzzyMatch } from 'src/utils';

type POSItemSearchRecord = Pick<POSItem, 'name' | 'itemCode' | 'barcode'>;

type POSItemSearchMatch = {
  distance: number;
  isMatch: boolean;
};

export function filterPOSItems<T extends POSItemSearchRecord>(
  items: T[],
  searchTerm: string | null | undefined
): T[] {
  const normalizedSearchTerm = searchTerm?.trim() ?? '';
  if (!normalizedSearchTerm) {
    return items;
  }

  return items
    .map((item) => ({ item, match: getBestMatch(item, normalizedSearchTerm) }))
    .filter(({ match }) => match.isMatch)
    .sort((a, b) => a.match.distance - b.match.distance)
    .map(({ item }) => item);
}

export function findExactPOSItem<T extends POSItemSearchRecord>(
  items: T[],
  searchTerm: string | null | undefined
): T | undefined {
  const normalizedSearchTerm = normalize(searchTerm);
  if (!normalizedSearchTerm) {
    return;
  }

  return items.find((item) =>
    getSearchValues(item).some(
      (value) => normalize(value) === normalizedSearchTerm
    )
  );
}

function getBestMatch(
  item: POSItemSearchRecord,
  searchTerm: string
): POSItemSearchMatch {
  return getSearchValues(item).reduce<POSItemSearchMatch>(
    (bestMatch, value) => {
      const match = fuzzyMatch(searchTerm, value);
      return match.isMatch && match.distance < bestMatch.distance
        ? match
        : bestMatch;
    },
    { isMatch: false, distance: Number.MAX_SAFE_INTEGER }
  );
}

function getSearchValues(item: POSItemSearchRecord): string[] {
  return [item.name, item.itemCode, item.barcode].filter(
    (value): value is string => typeof value === 'string' && !!value
  );
}

function normalize(value: string | null | undefined): string {
  return value?.trim().toLocaleLowerCase() ?? '';
}
