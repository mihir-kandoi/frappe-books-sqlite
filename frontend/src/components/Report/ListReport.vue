<template>
  <div class="overflow-hidden flex flex-col h-full">
    <FrappeList
      v-if="dataSlice.length"
      :columns="listColumns"
      :row-height="hconst"
      divider="full"
      class="custom-scroll custom-scroll-thumb1 min-h-0 flex-1 overflow-auto px-4 list-gap-0 [--list-row-padding-x:0px]"
    >
      <FrappeListHeader class="sticky top-0 z-10 bg-surface-base">
        <FrappeListHeaderCell
          v-for="(column, index) in report.columns"
          :key="`${index}-column`"
          class="px-3 text-base"
          :class="getAlignmentClass(column)"
        >
          {{ column.label }}
        </FrappeListHeaderCell>
      </FrappeListHeader>

      <FrappeListRows :items="dataSlice" :row-key="getRowKey">
        <template #default="{ item: row, index, value }">
          <FrappeListRow
            v-if="!row.folded"
            :value="value"
            :on-click="row.isGroup ? () => onRowClick(row, index) : undefined"
            :class="row.isGroup ? 'font-medium' : ''"
          >
            <FrappeListCell
              v-for="(cell, cellIndex) in row.cells"
              :key="`${cellIndex}-${index}-cell`"
              class="min-w-0 px-3 text-base"
              :class="[getCellColorClass(cell), getAlignmentClass(cell)]"
              :style="getCellStyle(cell)"
            >
              <span class="w-full truncate">{{ cell.value }}</span>
            </FrappeListCell>
          </FrappeListRow>
        </template>
      </FrappeListRows>
    </FrappeList>
    <p v-else class="w-full text-center mt-20 text-ink-gray-8 text-base">
      {{ report.loading ? t`Loading Report...` : t`No Values to be Displayed` }}
    </p>

    <!-- Pagination Footer -->
    <div v-if="report.usePagination" class="mt-auto flex-shrink-0">
      <Paginator
        :item-count="report?.reportData?.length ?? 0"
        class="px-4"
        @index-change="setPageIndices"
      />
    </div>
    <div v-else class="h-4" />
  </div>
</template>
<script>
import { Report } from 'reports/Report';
import {
  List as FrappeList,
  ListCell as FrappeListCell,
  ListHeader as FrappeListHeader,
  ListHeaderCell as FrappeListHeaderCell,
  ListRow as FrappeListRow,
  ListRows as FrappeListRows,
} from 'frappe-ui/list';
import { isNumeric } from 'src/utils';
import { languageDirectionKey } from 'src/utils/injectionKeys';
import { defineComponent } from 'vue';
import Paginator from '../Paginator.vue';
import { inject } from 'vue';

export default defineComponent({
  components: {
    FrappeList,
    FrappeListCell,
    FrappeListHeader,
    FrappeListHeaderCell,
    FrappeListRow,
    FrappeListRows,
    Paginator,
  },
  props: {
    report: Report,
  },
  setup() {
    return {
      languageDirection: inject(languageDirectionKey),
    };
  },
  data() {
    return {
      wconst: 8,
      hconst: 48,
      pageStart: 0,
      pageEnd: 0,
    };
  },
  computed: {
    dataSlice() {
      if (this.report?.usePagination) {
        return this.report.reportData.slice(this.pageStart, this.pageEnd);
      }

      return this.report.reportData;
    },
    listColumns() {
      return this.report.columns.map(
        (column) => `${(column.width ?? 1) * this.wconst}rem`
      );
    },
  },
  methods: {
    getRowKey(row, index) {
      return `${index}-${row.cells?.[0]?.value ?? ''}`;
    },
    setPageIndices({ start, end }) {
      this.pageStart = start;
      this.pageEnd = end;
    },
    onRowClick(clickedRow, r) {
      if (!clickedRow.isGroup) {
        return;
      }

      r += 1;
      clickedRow.foldedBelow = !clickedRow.foldedBelow;
      const folded = clickedRow.foldedBelow;
      let row = this.dataSlice[r];

      while (row && row.level > clickedRow.level) {
        row.folded = folded;
        r += 1;
        row = this.dataSlice[r];
      }
    },
    getCellStyle(cell) {
      const styles = {};

      if (cell.bold) {
        styles['font-weight'] = 'bold';
      }

      if (cell.italics) {
        styles['font-style'] = 'oblique 15deg';
      }

      if (cell.indent) {
        if (this.languageDirection === 'rtl') {
          styles['padding-right'] = `${cell.indent * 2}rem`;
        } else {
          styles['padding-left'] = `${cell.indent * 2}rem`;
        }
      }

      return styles;
    },
    getAlignmentClass(cell) {
      if (this.languageDirection === 'rtl') {
        return 'justify-end text-end';
      }

      const alignment = cell.align ?? (isNumeric(cell.fieldtype) ? 'right' : 'left');
      if (alignment === 'right') {
        return 'justify-end text-end';
      }
      if (alignment === 'center') {
        return 'justify-center text-center';
      }
      return 'justify-start text-start';
    },
    getCellColorClass(cell) {
      if (cell.color === 'red') {
        return 'text-red-600';
      } else if (cell.color === 'green') {
        return 'text-green-600';
      }

      if (!cell.rawValue) {
        return 'text-ink-gray-6';
      }

      if (typeof cell.rawValue !== 'number') {
        return 'text-ink-gray-9';
      }

      if (cell.rawValue === 0) {
        return 'text-ink-gray-6';
      }

      const prec = this.fyo?.singles?.displayPrecision ?? 2;
      if (Number(cell.rawValue.toFixed(prec)) === 0) {
        return 'text-ink-gray-6';
      }

      return 'text-ink-gray-9';
    },
  },
});
</script>
