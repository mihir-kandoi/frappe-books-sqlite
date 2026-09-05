<template>
  <div class="flex flex-col overflow-hidden text-base">
    <FrappeList
      v-if="dataSlice.length"
      :columns="listColumns"
      :selectable="isSelectionMode"
      :selection="selectedItems"
      :row-height="48"
      divider="full"
      class="custom-scroll custom-scroll-thumb1 min-h-0 flex-1 overflow-y-auto text-ink-gray-8 list-gap-4 list-row-px-3"
      @update:selection="updateSelection"
    >
      <FrappeListHeader class="sticky top-0 z-10 bg-surface-base">
        <FrappeListHeaderCell class="justify-end pe-2">#</FrappeListHeaderCell>
        <FrappeListHeaderCell
          v-for="column in columns"
          :key="column.label"
          :class="isNumeric(column.fieldtype) ? 'justify-end' : ''"
        >
          {{ column.label }}
        </FrappeListHeaderCell>
      </FrappeListHeader>

      <FrappeListRows :items="dataSlice" row-key="name">
        <template #default="{ item: row, index, value }">
          <FrappeListRow
            :value="value"
            @click="isSelectionMode ? undefined : $emit('openDoc', row.name)"
          >
            <FrappeListCell class="justify-end pe-2 text-ink-gray-5">
              {{ index + pageStart + 1 }}
            </FrappeListCell>
            <FrappeListCell
              v-for="column in columns"
              :key="column.label"
              :class="isNumeric(column.fieldtype) ? 'justify-end text-end' : ''"
            >
              <ListCell
                class="min-w-0 flex-1"
                :row="(row as RenderData)"
                :column="column"
                @status-found="handleStatusFound"
              />
            </FrappeListCell>
          </FrappeListRow>
        </template>
      </FrappeListRows>
    </FrappeList>

    <!-- Pagination Footer -->
    <div v-if="data?.length" class="mt-auto">
      <hr class="border-outline-gray-1" />
      <Paginator
        :item-count="data.length"
        class="px-4"
        @index-change="setPageIndices"
      />
    </div>

    <!-- Empty State -->
    <div
      v-if="!data?.length"
      class="flex flex-col items-center justify-center my-auto"
    >
      <img src="../../assets/img/list-empty-state.svg" alt="" class="w-24" />
      <p class="my-3 text-ink-gray-8">
        {{ t`No entries found` }}
      </p>
      <Button v-if="canCreate" type="primary" @click="$emit('makeNewDoc')">
        {{ t`Make Entry` }}
      </Button>
    </div>
  </div>
</template>
<script lang="ts">
import { ListViewSettings, RenderData } from 'fyo/model/types';
import {
  List as FrappeList,
  ListCell as FrappeListCell,
  ListHeader as FrappeListHeader,
  ListHeaderCell as FrappeListHeaderCell,
  ListRow as FrappeListRow,
  ListRows as FrappeListRows,
} from 'frappe-ui/list';
import { cloneDeep } from 'lodash';
import Button from 'src/components/Button.vue';
import Paginator from 'src/components/Paginator.vue';
import { fyo } from 'src/initFyo';
import { isNumeric } from 'src/utils';
import { QueryFilter } from 'utils/db/types';
import { PropType, defineComponent, toRaw } from 'vue';
import ListCell from './ListCell.vue';

export default defineComponent({
  name: 'List',
  components: {
    FrappeList,
    FrappeListCell,
    FrappeListHeader,
    FrappeListHeaderCell,
    FrappeListRow,
    FrappeListRows,
    ListCell,
    Button,
    Paginator,
  },
  props: {
    listConfig: {
      type: Object as PropType<ListViewSettings | undefined>,
      default: () => ({ columns: [] }),
    },
    filters: {
      type: Object as PropType<QueryFilter>,
      default: () => ({}),
    },
    schemaName: { type: String, required: true },
    canCreate: Boolean,
    isSelectionMode: Boolean,
  },
  emits: ['openDoc', 'makeNewDoc', 'updatedData', 'selected-items-changed'],
  data() {
    return {
      data: [] as RenderData[],
      pageStart: 0,
      pageEnd: 0,
      statusMap: {} as Record<string, string>,
      selectedItems: [] as string[],
    };
  },
  computed: {
    dataSlice() {
      return this.data.slice(this.pageStart, this.pageEnd);
    },
    count() {
      return this.pageEnd - this.pageStart + 1;
    },
    listColumns(): string[] {
      return ['2rem', ...this.columns.map(() => 'minmax(0, 1fr)')];
    },
    columns() {
      let columns = this.listConfig?.columns ?? [];

      if (columns.length === 0) {
        columns = fyo.schemaMap[this.schemaName]?.quickEditFields ?? [];
        columns = [...new Set(['name', ...columns])];
      }

      return columns
        .map((fieldname) => {
          if (typeof fieldname === 'object') {
            return fieldname;
          }

          return fyo.getField(this.schemaName, fieldname);
        })
        .filter(Boolean);
    },
  },
  watch: {
    async schemaName(oldValue, newValue) {
      if (oldValue === newValue) {
        return;
      }

      await this.updateData();
    },
  },
  async mounted() {
    await this.updateData();
    this.setUpdateListeners();
  },
  methods: {
    handleStatusFound({ rowId, status }: { rowId: string; status: string }) {
      this.statusMap[rowId] = status;
    },
    isNumeric,
    setPageIndices({ start, end }: { start: number; end: number }) {
      this.pageStart = start;
      this.pageEnd = end;
    },
    setUpdateListeners() {
      if (!this.schemaName) {
        return;
      }

      const listener = async () => {
        await this.updateData();
      };

      if (fyo.schemaMap[this.schemaName]?.isSubmittable) {
        fyo.doc.observer.on(`submit:${this.schemaName}`, listener);
        fyo.doc.observer.on(`revert:${this.schemaName}`, listener);
      }

      fyo.doc.observer.on(`sync:${this.schemaName}`, listener);
      fyo.db.observer.on(`delete:${this.schemaName}`, listener);
      fyo.doc.observer.on(`rename:${this.schemaName}`, listener);
    },
    async updateData(filters?: Record<string, unknown>) {
      const baseFilters = cloneDeep(toRaw(this.filters));
      filters = cloneDeep({ ...baseFilters, ...filters });

      let statusFilter: [string, string] | undefined;

      if ('status' in filters) {
        statusFilter = filters['status'] as [string, string];
      }

      const isStatusFilter =
        Array.isArray(statusFilter) && statusFilter[0] === 'like';
      if (isStatusFilter) {
        delete filters['status'];
      }

      const orderBy = ['created'];
      if (fyo.db.fieldMap[this.schemaName]['date']) {
        orderBy.unshift('date');
      }

      const tableData = await fyo.db.getAll(this.schemaName, {
        fields: ['*'],
        filters: filters as QueryFilter,
        orderBy,
      });

      let filteredData = tableData;

      if (isStatusFilter && statusFilter?.[1]) {
        const lowercaseStatus = String(statusFilter[1]).toLowerCase();

        const matchedNames = Object.entries(this.statusMap)
          .filter((entry) => entry[1].toLowerCase() === lowercaseStatus)
          .map((entry) => entry[0]);

        filteredData = tableData.filter((row) =>
          matchedNames.includes(String(row.name))
        );
      }

      this.data = filteredData.map((d) => ({
        ...d,
        schema: fyo.schemaMap[this.schemaName],
      })) as RenderData[];
      this.$emit('updatedData', filters);
    },
    updateSelection(selectedItems: string[]) {
      this.selectedItems = selectedItems;
      this.$emit('selected-items-changed', this.selectedItems);
    },
  },
});
</script>
