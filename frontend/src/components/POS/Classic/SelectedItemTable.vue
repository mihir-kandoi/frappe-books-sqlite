<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <FrappeList
      :columns="listColumns"
      divider="full"
      class="mt-2 flex min-h-0 flex-1 flex-col overflow-hidden rounded-4 border border-outline-gray-1 list-gap-2 [--list-row-padding-x:0px]"
    >
      <FrappeListHeader>
        <FrappeListHeaderCell
          v-for="df in tableFields"
          :key="df.fieldname"
          class="px-2"
          :class="isNumeric(df as Field) ? 'justify-end' : ''"
        >
          {{ df.label }}
        </FrappeListHeaderCell>
      </FrappeListHeader>

      <div class="custom-scroll custom-scroll-thumb1 min-h-0 flex-1 overflow-auto">
        <FrappeListRows :items="sinvDoc.items ?? []" :row-key="getRowKey">
          <template #default="{ item: row, value }">
            <FrappeListRow
              :value="value"
              class="group min-h-12 py-2 hover:bg-surface-gray-1"
            >
              <SelectedItemRow
                :row="(row as SalesInvoiceItem)"
                :expanded-batch-id="expandedBatchId"
                @set-expanded-batch-id="
                  (rowName) => $emit('setExpandedBatchId', rowName)
                "
                @run-sinv-formulas="runSinvFormulas"
                @apply-pricing-rule="$emit('applyPricingRule')"
                @selected-row="selectedItemRow"
              />
            </FrappeListRow>
          </template>
        </FrappeListRows>
      </div>
    </FrappeList>
  </div>
</template>

<script lang="ts">
import FormContainer from 'src/components/FormContainer.vue';
import FormControl from 'src/components/Controls/FormControl.vue';
import Link from 'src/components/Controls/Link.vue';
import {
  List as FrappeList,
  ListHeader as FrappeListHeader,
  ListHeaderCell as FrappeListHeaderCell,
  ListRow as FrappeListRow,
  ListRows as FrappeListRows,
} from 'frappe-ui/list';
import RowEditForm from 'src/pages/CommonForm/RowEditForm.vue';
import SelectedItemRow from './SelectedItemRow.vue';
import { isNumeric } from 'src/utils';
import { inject } from 'vue';
import { defineComponent, PropType } from 'vue';
import { SalesInvoiceItem } from 'models/baseModels/SalesInvoiceItem/SalesInvoiceItem';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { Field } from 'schemas/types';

export default defineComponent({
  name: 'SelectedItemTable',
  components: {
    FormContainer,
    FormControl,
    Link,
    FrappeList,
    FrappeListHeader,
    FrappeListHeaderCell,
    FrappeListRow,
    FrappeListRows,
    RowEditForm,
    SelectedItemRow,
  },
  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
    };
  },
  props: {
    expandedBatchId: {
      type: String as PropType<string | null | undefined>,
      default: undefined,
    },
  },
  emits: ['applyPricingRule', 'selectedRow', 'setExpandedBatchId'],
  computed: {
    ratio() {
      return [0.1, 0.9, 0.8, 0.8, 0.8, 0.8, 0.2];
    },
    listColumns(): string[] {
      return this.ratio.map((ratio) => `minmax(0, ${ratio}fr)`);
    },
    tableFields() {
      return [
        {
          fieldname: 'toggler',
          fieldtype: 'Link',
          label: ' ',
        },
        {
          fieldname: 'item',
          fieldtype: 'Link',
          label: 'Item',
          placeholder: 'Item',
          required: true,
          schemaName: 'Item',
        },
        {
          fieldname: 'quantity',
          label: 'Quantity',
          placeholder: 'Quantity',
          fieldtype: 'Float',
          required: true,
          schemaName: '',
        },
        {
          fieldname: 'unit',
          label: 'Unit Type',
          placeholder: 'Unit',
          fieldtype: 'Link',
          required: true,
          schemaName: 'UOM',
        },
        {
          fieldname: 'rate',
          label: 'Rate',
          placeholder: 'Rate',
          fieldtype: 'Currency',
          required: true,
          schemaName: '',
        },
        {
          fieldname: 'amount',
          label: 'Amount',
          placeholder: 'Amount',
          fieldtype: 'Currency',
          required: true,
          schemaName: '',
        },
        {
          fieldname: 'removeItem',
          fieldtype: 'Link',
          label: ' ',
        },
      ];
    },
  },
  methods: {
    getRowKey(row: SalesInvoiceItem): string {
      return String(row.name ?? row.idx ?? row.item ?? '');
    },
    async runSinvFormulas() {
      await this.sinvDoc.runFormulas();
    },
    selectedItemRow(row: SalesInvoiceItem) {
      this.$emit('selectedRow', row);
    },
    isNumeric,
  },
});
</script>
