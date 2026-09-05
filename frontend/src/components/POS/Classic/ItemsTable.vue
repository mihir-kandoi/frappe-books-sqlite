<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <FrappeList
      :columns="listColumns"
      :row-height="48"
      divider="full"
      class="mt-4 flex min-h-0 flex-1 flex-col overflow-hidden rounded-4 border border-outline-gray-1 list-gap-2 [--list-row-padding-x:0px]"
    >
      <FrappeListHeader>
        <FrappeListHeaderCell
          v-for="df in tableFields"
          :key="df.fieldname"
          class="px-3"
          :class="isNumeric(df as Field) ? 'justify-end' : ''"
        >
          {{ df.label }}
        </FrappeListHeaderCell>
      </FrappeListHeader>

      <div
        class="custom-scroll custom-scroll-thumb2 min-h-0 flex-1 overflow-y-auto"
      >
        <FrappeListRows v-if="items" :items="items as POSItem[]" row-key="name">
          <template #default="{ item: row, value }">
            <FrappeListRow
              :value="value"
              class="text-ink-gray-8"
              :aria-label="`Add ${row.name}`"
              @click="handleChange(row)"
            >
              <FrappeListCell
                v-for="df in tableFields"
                :key="df.fieldname"
                class="min-w-0 px-3"
                :class="isNumeric(df as Field) ? 'justify-end text-end' : ''"
              >
                <span
                  class="truncate"
                  :title="fyo.format(row[df.fieldname as keyof POSItem], df)"
                >
                  {{ fyo.format(row[df.fieldname as keyof POSItem], df) }}
                </span>
              </FrappeListCell>
            </FrappeListRow>
          </template>
        </FrappeListRows>
      </div>
    </FrappeList>
  </div>
</template>

<script lang="ts">
import {
  List as FrappeList,
  ListCell as FrappeListCell,
  ListHeader as FrappeListHeader,
  ListHeaderCell as FrappeListHeaderCell,
  ListRow as FrappeListRow,
  ListRows as FrappeListRows,
} from 'frappe-ui/list';
import { isNumeric } from 'src/utils';
import { defineComponent } from 'vue';
import { Field } from 'schemas/types';
import { POSItem } from '../types';

export default defineComponent({
  name: 'ItemsTable',
  components: {
    FrappeList,
    FrappeListCell,
    FrappeListHeader,
    FrappeListHeaderCell,
    FrappeListRow,
    FrappeListRows,
  },
  emits: ['addItem', 'updateValues'],
  props: {
    items: Array,
    itemQtyMap: Object,
    itemVisibility: {
      type: String,
      default: 'Inventory Items',
    },
  },
  computed: {
    ratio() {
      return [1.6, 0.9, 0.8, 0.7];
    },
    listColumns(): string[] {
      return this.ratio.map((ratio) => `minmax(0, ${ratio}fr)`);
    },
    tableFields() {
      const fields = [
        {
          fieldname: 'name',
          fieldtype: 'Data',
          label: 'Item',
          placeholder: 'Item',
          readOnly: true,
        },
        {
          fieldname: 'rate',
          label: 'Rate',
          placeholder: 'Rate',
          fieldtype: 'Currency',
          readOnly: true,
        },
        {
          fieldname: 'unit',
          label: 'Unit',
          placeholder: 'Unit',
          fieldtype: 'Data',
          target: 'UOM',
          readOnly: true,
        },
      ] as Field[];

      fields.splice(2, 0, {
        fieldname: 'availableQty',
        label: 'Qty',
        placeholder: 'Available Qty',
        fieldtype: 'Float',
        readOnly: true,
      });

      return fields;
    },
  },
  methods: {
    handleChange(value: POSItem) {
      this.$emit('addItem', value);
      this.$emit('updateValues');
    },
    isNumeric,
  },
});
</script>
