<template>
  <div v-if="tableFields?.length">
    <div v-if="showLabel" class="text-gray-600 dark:text-gray-400 text-sm mb-1">
      {{ df.label }}
    </div>

    <FrappeList
      :columns="listColumns"
      :row-height="48"
      divider="full"
      class="list-gap-2 [--list-row-padding-x:0px]"
      :class="border ? 'overflow-hidden rounded-md border border-outline-gray-1' : ''"
    >
      <FrappeListHeader v-if="showHeader">
        <FrappeListHeaderCell class="justify-center">#</FrappeListHeaderCell>
        <FrappeListHeaderCell
          v-for="df in tableFields"
          :key="df.fieldname"
          class="min-w-0"
          :class="[
            cellPaddingClass,
            df.sub_label ? 'flex-col justify-center' : 'items-center',
            isNumeric(df)
              ? df.sub_label
                ? 'items-end text-end'
                : 'justify-end text-end'
              : df.sub_label
              ? 'items-center text-center'
              : '',
          ]"
        >
          <span>{{ df.label }}</span>
          <p v-if="df.sub_label" class="text-xs">
            {{ df.sub_label }}
          </p>
        </FrappeListHeaderCell>
        <FrappeListHeaderCell v-if="canEditRow">
          <span class="sr-only">{{ t`Actions` }}</span>
        </FrappeListHeaderCell>
      </FrappeListHeader>

      <!-- Data Rows -->
      <div
        v-if="value"
        :class="{
          'overflow-x-hidden overflow-y-auto custom-scroll custom-scroll-thumb1':
            rowsOverflow,
          'overscroll-contain': rowsOverflow,
        }"
        :style="{ 'max-height': maxHeight }"
      >
        <TableRow
          v-for="row of value"
          ref="table-row"
          :key="row.name"
          v-bind="{ row, tableFields, size }"
          :read-only="isReadOnly"
          :can-edit-row="canEditRow"
          @remove="removeRow(row)"
          @change="(field, value) => $emit('row-change', field, value, df)"
        />
      </div>

      <!-- Add Row and Row Count -->
      <FrappeListRow
        v-if="!isReadOnly"
        class="
          border-t border-outline-gray-1 text-ink-gray-5
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-3
        "
        @click="addRow"
      >
        <FrappeListCell class="justify-center">
          <Icon name="plus" class="w-4 h-4 text-gray-500" />
        </FrappeListCell>
        <FrappeListCell
          class="justify-between px-2"
          style="grid-column: 2 / -1"
        >
          <p>
            {{ t`Add Row` }}
          </p>
          <p
            v-if="
              value &&
              maxRowsBeforeOverflow &&
              value.length > maxRowsBeforeOverflow
            "
            class="text-end px-2"
          >
            {{ t`${value.length} rows` }}
          </p>
        </FrappeListCell>
      </FrappeListRow>
    </FrappeList>
  </div>
</template>

<script>
import Icon from 'src/components/Icon.vue';
import {
  List as FrappeList,
  ListCell as FrappeListCell,
  ListHeader as FrappeListHeader,
  ListHeaderCell as FrappeListHeaderCell,
  ListRow as FrappeListRow,
} from 'frappe-ui/list';
import { fyo } from 'src/initFyo';
import { nextTick } from 'vue';
import Base from './Base.vue';
import TableRow from './TableRow.vue';

export default {
  name: 'Table',
  components: {
    FrappeList,
    FrappeListCell,
    FrappeListHeader,
    FrappeListHeaderCell,
    FrappeListRow,
    Icon,
    TableRow,
  },
  extends: Base,
  props: {
    value: { type: Array, default: () => [] },
    showHeader: {
      type: Boolean,
      default: true,
    },
    maxRowsBeforeOverflow: {
      type: Number,
      default: 0,
    },
    border: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['editrow', 'row-change'],
  computed: {
    canEditRow() {
      return this.df.edit;
    },
    rowsOverflow() {
      return (
        this.maxRowsBeforeOverflow > 0 &&
        this.value.length > this.maxRowsBeforeOverflow
      );
    },
    maxHeight() {
      if (!this.rowsOverflow) {
        return '';
      }

      return `calc(var(--h-row-mid) * ${this.maxRowsBeforeOverflow})`;
    },
    ratio() {
      const ratio = [0.3].concat(this.tableFields.map(() => 1));

      if (this.canEditRow) {
        return ratio.concat(0.3);
      }

      return ratio;
    },
    listColumns() {
      return this.ratio.map((ratio) => `minmax(0, ${ratio}fr)`);
    },
    cellPaddingClass() {
      return this.size === 'small' ? 'px-2' : 'px-3';
    },
    tableFields() {
      const fields = fyo.schemaMap[this.df.target].tableFields ?? [];
      return fields.map((fieldname) => fyo.getField(this.df.target, fieldname));
    },
  },
  mounted() {
    if (fyo.store.isDevelopment) {
      window.tab = this;
    }
  },

  methods: {
    focus() {},
    async addRow() {
      await this.doc.append(this.df.fieldname);
      await nextTick();
      this.scrollToRow(this.value.length - 1);
      this.triggerChange(this.value);
      this.$nextTick(() => {
        const rows = this.$refs['table-row'];
        if (rows && rows.length > 0) {
          const lastRow = rows[rows.length - 1];
          if (lastRow.focusFirstInput) {
            lastRow.focusFirstInput();
          }
        }
      });
    },
    removeRow(row) {
      this.doc.remove(this.df.fieldname, row.idx).then((s) => {
        if (!s) {
          return;
        }
        this.triggerChange(this.value);
      });
    },

    scrollToRow(index) {
      const row = this.$refs['table-row'][index];
      row && row.$el.scrollIntoView({ block: 'nearest' });
    },
  },
};
</script>
