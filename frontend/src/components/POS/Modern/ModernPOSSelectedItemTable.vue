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
              class="min-h-12 py-2 hover:bg-surface-gray-1"
            >
              <ModernPOSSelectedItemRow
                :row="(row as SalesInvoiceItem)"
                :expanded-batch-id="expandedBatchId"
                @set-expanded-batch-id="
                  (rowName) => $emit('setExpandedBatchId', rowName)
                "
                @selected-row="selectedItemRow"
                @run-sinv-formulas="runSinvFormulas"
                @apply-pricing-rule="$emit('applyPricingRule')"
                @toggle-modal="$emit('toggleModal')"
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
import ModernPOSSelectedItemRow from './ModernPOSSelectedItemRow.vue';
import { isNumeric } from 'src/utils';
import { t } from 'fyo';
import { inject, defineComponent, PropType } from 'vue';
import { SalesInvoiceItem } from 'models/baseModels/SalesInvoiceItem/SalesInvoiceItem';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { Field } from 'schemas/types';

export default defineComponent({
  name: 'ModernPOSSelectedItemTable',
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
    ModernPOSSelectedItemRow,
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
  emits: [
    'toggleModal',
    'selectedRow',
    'applyPricingRule',
    'setExpandedBatchId',
  ],
  computed: {
    ratio() {
      return [0.25, 1, 0.65, 0.8, 0.8, 0.3];
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
          label: t`Item`,
          placeholder: 'Item',
          required: true,
          schemaName: 'Item',
        },
        {
          fieldname: 'quantity',
          label: t`Qty`,
          placeholder: 'Quantity',
          fieldtype: 'Float',
          required: true,
          schemaName: '',
        },
        {
          fieldname: 'rate',
          label: t`Rate`,
          placeholder: 'Rate',
          fieldtype: 'Currency',
          required: true,
          schemaName: '',
        },
        {
          fieldname: 'amount',
          label: t`Amount`,
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
    selectedItemRow(row: SalesInvoiceItem, field: string) {
      this.$emit('selectedRow', row, field);
    },
    isNumeric,
  },
});
</script>
