<template>
  <div>
    <!-- Search Bar Button -->
    <Button
      class="px-3 py-2 rounded-r-none dark:bg-gray-900"
      :padding="false"
      :title="t`Search`"
      :aria-label="t`Search`"
      @click="open"
    >
      <feather-icon
        name="search"
        class="w-4 h-4 text-gray-700 dark:text-gray-300"
      />
    </Button>
  </div>

  <!-- Search Modal -->
  <Modal
    :open-modal="openModal"
    size="3xl"
    @closemodal="close"
  >
    <div class="w-full">
      <!-- Search Input -->
      <div class="p-1">
        <FrappeTextInput
          ref="input"
          v-model="inputValue"
          type="search"
          autocomplete="off"
          spellcheck="false"
          :placeholder="t`Type to search...`"
          class="w-full"
          variant="subtle"
          size="xl"
          @keydown.up="up"
          @keydown.down="down"
          @keydown.enter="() => select()"
          @keydown.esc="close"
        />
      </div>
      <hr v-if="suggestions.length" class="dark:border-gray-800" />

      <!-- Search List -->
      <div
        :style="`max-height: ${49 * 6 - 1}px`"
        class="overflow-auto custom-scroll custom-scroll-thumb2"
      >
        <div
          v-for="(si, i) in suggestions"
          :key="`${i}-${si.label}`"
          :data-index="`search-suggestion-${i}`"
          class="hover:bg-gray-50 dark:hover:bg-gray-875 cursor-pointer"
          :class="
            idx === i
              ? 'border-gray-700 dark:border-gray-200 bg-gray-50 dark:bg-gray-875 border-s-4'
              : ''
          "
          @click="select(i)"
        >
          <!-- Search List Item -->
          <div
            class="flex w-full justify-between px-3 items-center"
            style="height: var(--h-row-mid)"
          >
            <div class="flex items-center">
              <p
                :class="
                  idx === i
                    ? 'text-gray-900 dark:text-gray-100'
                    : 'text-gray-700 dark:text-gray-400'
                "
                :style="idx === i ? 'margin-left: -4px' : ''"
              >
                {{ si.label }}
              </p>
              <p
                v-if="si.group === 'Docs'"
                class="text-gray-600 dark:text-gray-400 text-sm ms-3"
              >
                {{ si.more.filter(Boolean).join(', ') }}
              </p>
            </div>
            <p
              class="text-sm text-end justify-self-end"
              :class="`text-${groupColorMap[si.group]}-500`"
            >
              {{
                si.group === 'Docs' ? si.schemaLabel : groupLabelMap[si.group]
              }}
            </p>
          </div>

          <hr
            v-if="i !== suggestions.length - 1"
            class="dark:border-gray-800"
          />
        </div>
      </div>

      <!-- Footer -->
      <hr class="dark:border-gray-800" />
      <div class="m-1 flex justify-between flex-col gap-2 text-sm select-none">
        <!-- Group Filters -->
        <div class="flex justify-between">
          <div class="flex gap-1">
            <FrappeButton
              v-for="g in searchGroups"
              :key="g"
              size="xs"
              variant="outline"
              :class="getGroupFilterButtonClass(g)"
              @click="
                setSearchFilter(g, !searcher!.filters.groupFilters[g])
              "
            >
              {{ groupLabelMap[g] }}
            </FrappeButton>
          </div>
          <FrappeButton size="xs" variant="ghost" @click="showMore = !showMore">
            {{ showMore ? t`Less Filters` : t`More Filters` }}
          </FrappeButton>
        </div>

        <!-- Additional Filters -->
        <div v-if="showMore" class="-mt-1">
          <!-- Group Skip Filters -->
          <div class="flex gap-1 text-gray-800 dark:text-gray-200">
            <FrappeButton
              v-for="s in ['skipTables', 'skipTransactions'] as const"
              :key="s"
              size="xs"
              :variant="searcher?.filters[s] ? 'subtle' : 'outline'"
              @click="setSearchFilter(s, !searcher?.filters[s])"
            >
              {{
                s === 'skipTables' ? t`Skip Child Tables` : t`Skip Transactions`
              }}
            </FrappeButton>
          </div>

          <!-- Schema Name Filters -->
          <div
            class="flex mt-1 gap-1 text-blue-500 dark:text-blue-100 flex-wrap"
          >
            <FrappeButton
              v-for="sf in schemaFilters"
              :key="sf.value"
              class="whitespace-nowrap"
              size="xs"
              theme="blue"
              :variant="
                searcher?.filters.schemaFilters[sf.value] ? 'subtle' : 'outline'
              "
              @click="
                setSearchFilter(
                  sf.value,
                  !searcher?.filters.schemaFilters[sf.value]
                )
              "
            >
              {{ sf.label }}
            </FrappeButton>
          </div>
        </div>

        <!-- Keybindings Help -->
        <div class="flex text-sm text-gray-500 justify-between items-center">
          <div class="flex items-center gap-4">
            <p class="flex h-7 items-center">↑↓ {{ t`Navigate` }}</p>
            <p class="flex h-7 items-center">↩ {{ t`Select` }}</p>
            <p class="flex h-7 items-center">
              <span class="tracking-tighter">esc</span>&nbsp;{{ t`Close` }}
            </p>
            <FrappeButton
              class="h-7"
              size="xs"
              variant="ghost"
              icon-left="lucide-circle-help"
              @click="openDocs"
            >
              {{ t`Help` }}
            </FrappeButton>
          </div>

          <p v-if="searcher?.numSearches" class="ms-auto">
            {{ t`${suggestions.length} out of ${searcher.numSearches}` }}
          </p>

          <div
            v-if="(searcher?.numSearches ?? 0) > 50"
            class="
              border border-gray-100
              dark:border-gray-875
              rounded
              flex
              justify-self-end
              ms-2
            "
          >
            <template
              v-for="c in allowedLimits.filter(
                (c) => c < (searcher?.numSearches ?? 0) || c === -1
              )"
              :key="c + '-count'"
            >
              <FrappeButton
                class="w-9"
                size="xs"
                :variant="limit === c ? 'subtle' : 'ghost'"
                @click="limit = Number(c)"
              >
                {{ c === -1 ? t`All` : c }}
              </FrappeButton>
            </template>
          </div>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script lang="ts">
import { fyo } from 'src/initFyo';
import { getBgTextColorClass } from 'src/utils/colors';
import { searcherKey, shortcutsKey } from 'src/utils/injectionKeys';
import { docsPathMap } from 'src/utils/misc';
import {
  SearchGroup,
  SearchItems,
  SearchItem,
  getGroupLabelMap,
  searchGroups,
} from 'src/utils/search';
import { defineComponent, inject, nextTick } from 'vue';
import {
  Button as FrappeButton,
  TextInput as FrappeTextInput,
} from 'frappe-ui';
import Button from './Button.vue';
import Modal from './Modal.vue';

const COMPONENT_NAME = 'SearchBar';

type SchemaFilters = { value: string; label: string; index: number }[];

export default defineComponent({
  components: { FrappeButton, FrappeTextInput, Modal, Button },
  setup() {
    return {
      searcher: inject(searcherKey),
      shortcuts: inject(shortcutsKey),
    };
  },
  data() {
    return {
      idx: 0,
      searchGroups,
      openModal: false,
      inputValue: '',
      showMore: false,
      limit: 50,
      allowedLimits: [50, 100, 500, -1],
      filterRevision: 0,
    };
  },
  computed: {
    groupLabelMap(): Record<SearchGroup, string> {
      return getGroupLabelMap();
    },
    schemaFilters(): SchemaFilters {
      const searchables = this.searcher?.searchables ?? {};

      const schemaNames = Object.keys(searchables);
      const filters = schemaNames
        .map((value) => {
          const schema = fyo.schemaMap[value];
          if (!schema) {
            return;
          }

          let index = 1;
          if (schema.isSubmittable) {
            index = 0;
          } else if (schema.isChild) {
            index = 2;
          }

          return { value, label: schema.label, index };
        })
        .filter(Boolean) as SchemaFilters;

      return filters.sort((a, b) => a.index - b.index);
    },
    groupColorMap(): Record<SearchGroup, string> {
      return {
        Docs: 'blue',
        Create: 'green',
        List: 'teal',
        Report: 'yellow',
        Page: 'orange',
        Recent: 'purple',
      };
    },
    groupColorClassMap(): Record<SearchGroup, string> {
      return searchGroups.reduce((map, g) => {
        map[g] = getBgTextColorClass(this.groupColorMap[g]);
        return map;
      }, {} as Record<SearchGroup, string>);
    },
    suggestions(): SearchItems {
      // The web app keeps Search in a shallow ref; track filter mutations here.
      this.filterRevision;
      if (!this.searcher) {
        return [];
      }

      const suggestions = this.searcher.search(this.inputValue);
      if (this.limit === -1) {
        return suggestions;
      }

      return suggestions.slice(0, this.limit);
    },
  },
  async mounted() {
    if (fyo.store.isDevelopment) {
      // @ts-ignore
      window.search = this;
    }

    this.openModal = false;
    this.setShortcuts();
  },
  activated() {
    this.setShortcuts();
    this.openModal = false;
  },
  deactivated() {
    this.shortcuts?.delete(COMPONENT_NAME);
  },
  unmounted() {
    this.shortcuts?.delete(COMPONENT_NAME);
  },
  methods: {
    openDocs() {
      ipc.openLink('https://docs.frappe.io/' + docsPathMap.Search);
    },
    getShortcuts() {
      const shortcuts: { shortcut: string; callback: () => void }[] = [];

      for (const i in searchGroups) {
        shortcuts.push({
          shortcut: `Digit${Number(i) + 1}`,
          callback: () => {
            const group = searchGroups[i];
            if (!this.searcher) {
              return;
            }

            const value = this.searcher.filters.groupFilters[group];
            if (typeof value !== 'boolean') {
              return;
            }

            this.setSearchFilter(group, !value);
          },
        });
      }

      return shortcuts;
    },
    setShortcuts() {
      if (!this.shortcuts) {
        return;
      }

      this.shortcuts.pmod.set(COMPONENT_NAME, ['KeyK'], () => {
        if (!this.openModal) {
          this.open();
        }
      });

      if (!this.openModal) {
        return;
      }

      for (const { shortcut, callback } of this.getShortcuts()) {
        this.shortcuts.pmod.set(COMPONENT_NAME, [shortcut], callback);
      }
    },
    clearFilterShortcuts() {
      for (const { shortcut } of this.getShortcuts()) {
        this.shortcuts?.pmod.delete(COMPONENT_NAME, [shortcut]);
      }
    },
    open(): void {
      this.openModal = true;
      this.setShortcuts();
      this.searcher?.updateKeywords();

      nextTick(() => {
        (
          this.$refs.input as {
            focus?: () => void;
          }
        )?.focus?.();
      });
    },
    close(): void {
      this.clearFilterShortcuts();
      this.openModal = false;
      this.reset();
    },
    reset(): void {
      this.inputValue = '';
    },
    setSearchFilter(filterName: string, value: boolean): void {
      if (!this.searcher) {
        return;
      }

      this.searcher.set(filterName, value);
      this.filterRevision += 1;
      this.idx = 0;
    },
    up(): void {
      this.idx = Math.max(this.idx - 1, 0);
      this.scrollToHighlighted();
    },
    down(): void {
      this.idx = Math.max(
        Math.min(this.idx + 1, this.suggestions.length - 1),
        0
      );
      this.scrollToHighlighted();
    },
    select(idx?: number): void {
      this.idx = idx ?? this.idx;
      const selectedItem = this.suggestions[this.idx];

      if (selectedItem?.action) {
        this.searcher?.addToRecent(selectedItem);
        selectedItem.action();
      }

      this.close();
    },
    scrollToHighlighted(): void {
      const query = `[data-index="search-suggestion-${this.idx}"]`;
      const element = document.querySelectorAll(query)?.[0];
      element?.scrollIntoView({ block: 'nearest' });
    },
    getGroupFilterButtonClass(g: SearchGroup): string {
      if (!this.searcher) {
        return '';
      }

      const isOn = this.searcher.filters.groupFilters[g];
      const color = this.groupColorMap[g];
      if (isOn) {
        return `${getBgTextColorClass(
          color
        )} border-${color}-100 dark:border-${color}-800`;
      }

      return `text-${color}-600 dark:text-${color}-400 border-${color}-100 dark:border-${color}-800`;
    },
  },
});
</script>
