<template>
  <Modal
    :open-modal="openModal"
    size="2xl"
    class="flex h-[calc(100vh-6rem)] max-h-[40rem] w-full flex-col p-5"
    @closemodal="closeModal"
  >
    <p class="text-center font-semibold dark:text-gray-400">
      {{ t`Invoices` }}
    </p>

    <hr class="mt-2 dark:border-gray-800" />

    <div class="mt-4">
      <FrappeTextInput
        v-model="invoiceSearchTerm"
        type="text"
        :placeholder="t`Search by invoice name`"
        class="w-full"
        variant="outline"
        size="md"
        @keydown.enter="handleSearchEnter"
      />
    </div>

    <hr class="mt-2 dark:border-gray-800" />

    <InvoiceSelectionTable
      v-model="selectedInvoiceName"
      :rows="paginatedInvoices"
      :fields="tableFields"
      :ratios="ratio"
      :empty-text="t`No invoices found`"
    />

    <div v-if="filteredInvoices.length" class="mt-1 mb-1">
      <Paginator
        :item-count="filteredInvoices.length"
        :allowed-counts="[20, 40, -1]"
        @index-change="setPageIndices"
      />
    </div>

    <div class="mt-2 grid grid-cols-2 gap-3">
      <Button class="w-full" @click="closeModal">
        {{ t`Cancel` }}
      </Button>
      <Button
        class="w-full"
        type="primary"
        :disabled="!selectedInvoiceName"
        @click="returnSelectedInvoice"
      >
        {{ t`Create Return` }}
      </Button>
    </div>
  </Modal>
</template>

<script lang="ts">
import Button from 'src/components/Button.vue';
import Modal from 'src/components/Modal.vue';
import InvoiceSelectionTable from 'src/components/POS/InvoiceSelectionTable.vue';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { defineComponent } from 'vue';
import { ModelNameEnum } from 'models/types';
import { Field } from 'schemas/types';
import { Money } from 'pesa';
import Paginator from 'src/components/Paginator.vue';
import { TextInput as FrappeTextInput } from 'frappe-ui';

export default defineComponent({
  name: 'ReturnSalesInvoice',
  components: {
    Modal,
    Button,
    InvoiceSelectionTable,
    Paginator,
    FrappeTextInput,
  },
  props: {
    openModal: Boolean,
  },
  emits: ['toggleModal', 'selectedReturnInvoice'],
  data() {
    return {
      returnedInvoices: [] as SalesInvoice[],
      invoiceSearchTerm: '',
      pageStart: 0,
      pageEnd: 20,
      selectedInvoiceName: '',
    };
  },
  computed: {
    ratio() {
      return [1, 1, 1, 0.8];
    },
    tableFields() {
      return [
        {
          fieldname: 'name',
          label: 'Name',
          fieldtype: 'Data',
          readOnly: true,
        },
        {
          fieldname: 'party',
          fieldtype: 'Data',
          label: 'Customer',
          placeholder: 'Customer',
          readOnly: true,
        },
        {
          fieldname: 'date',
          label: 'Date',
          fieldtype: 'Date',
          readOnly: true,
        },
        {
          fieldname: 'grandTotal',
          label: 'Grand Total',
          fieldtype: 'Currency',
          readOnly: true,
        },
      ] as Field[];
    },
    filteredInvoices() {
      return this.returnedInvoices.filter((invoice) =>
        (invoice.name as string)
          .toLowerCase()
          .includes(this.invoiceSearchTerm.toLowerCase())
      );
    },
    paginatedInvoices() {
      return this.filteredInvoices.slice(this.pageStart, this.pageEnd);
    },
  },
  watch: {
    async openModal(newVal) {
      if (newVal) {
        this.selectedInvoiceName = '';
        await this.setReturnedInvoices();
      }
    },
    invoiceSearchTerm() {
      this.pageStart = 0;
      this.pageEnd = this.pageEnd - this.pageStart || 20;
      this.selectedInvoiceName = '';
    },
  },
  async mounted() {
    await this.setReturnedInvoices();
  },
  async activated() {
    await this.setReturnedInvoices();
  },

  methods: {
    closeModal() {
      this.selectedInvoiceName = '';
      this.$emit('toggleModal', 'ReturnSalesInvoice');
    },
    returnSelectedInvoice() {
      if (!this.selectedInvoiceName) {
        return;
      }

      this.$emit('selectedReturnInvoice', this.selectedInvoiceName);
      this.closeModal();
    },
    handleSearchEnter() {
      if (this.filteredInvoices.length === 1) {
        this.selectedInvoiceName = String(this.filteredInvoices[0].name);
      }
    },
    setPageIndices({ start, end }: { start: number; end: number }) {
      this.pageStart = start;
      this.pageEnd = end;
      this.selectedInvoiceName = '';
    },
    async setReturnedInvoices() {
      const allInvoices = await this.fyo.db.getAll(ModelNameEnum.SalesInvoice, {
        fields: [],
        filters: {
          isPOS: true,
          submitted: true,
          cancelled: false,
        },
      });

      const returnedInvoiceNames = allInvoices
        .filter((inv) => {
          if (inv.isFullyReturned || inv.returnAgainst) {
            return false;
          }

          if (inv.isReturned && !inv.isFullyReturned) {
            return true;
          }

          if (!inv.isReturned && !inv.returnAgainst) {
            return true;
          }

          if (!inv.isReturned && !(inv.outstandingAmount as Money).isZero()) {
            return true;
          }

          return false;
        })
        .map((inv) => inv.name);
      this.returnedInvoices = allInvoices.filter((inv) =>
        returnedInvoiceNames.includes(inv.name)
      ) as SalesInvoice[];
    },
  },
});
</script>
