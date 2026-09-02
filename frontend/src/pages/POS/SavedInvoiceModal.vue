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
        @keyup.enter="handleEnterKey"
      />
    </div>

    <div class="flex items-center gap-2">
      <Button
        :background="false"
        class="min-w-0 flex-1 h-full p-2 mt-2"
        :class="{ 'dark:bg-gray-890 underline': savedInvoiceList }"
        @click="showSavedInvoices(true)"
        >Saved</Button
      >

      <Button
        :background="false"
        class="min-w-0 flex-1 h-full p-2 mt-2"
        :class="{ 'dark:bg-gray-890 underline': !savedInvoiceList }"
        @click="showSavedInvoices(false)"
        >Submitted</Button
      >
    </div>

    <InvoiceSelectionTable
      v-model="selectedInvoiceName"
      :rows="filteredInvoices"
      :fields="tableFields"
      :ratios="ratio"
      :empty-text="t`No invoices found`"
    />

    <div class="mt-4 grid grid-cols-2 gap-3">
      <Button class="w-full" @click="closeModal">
        {{ t`Cancel` }}
      </Button>
      <Button
        class="w-full"
        type="primary"
        :disabled="!selectedInvoiceName"
        @click="openSelectedInvoice"
      >
        {{ t`Open Invoice` }}
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
import { TextInput as FrappeTextInput } from 'frappe-ui';

export default defineComponent({
  name: 'SavedInvoiceModal',
  components: {
    Modal,
    Button,
    InvoiceSelectionTable,
    FrappeTextInput,
  },
  props: {
    openModal: Boolean,
  },
  emits: ['toggleModal', 'selectedInvoiceName'],
  data() {
    return {
      savedInvoiceList: true,
      savedInvoices: [] as SalesInvoice[],
      submittedInvoices: [] as SalesInvoice[],
      invoiceSearchTerm: '',
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
      const invoices = this.savedInvoiceList
        ? this.savedInvoices
        : this.submittedInvoices;
      return invoices.filter((invoice) =>
        (invoice.name as string)
          .toLowerCase()
          .includes(this.invoiceSearchTerm.toLowerCase())
      );
    },
  },
  watch: {
    async openModal(newVal) {
      if (newVal) {
        this.selectedInvoiceName = '';
        await this.setSavedInvoices();
        await this.setSubmittedInvoices();
      }
    },
    invoiceSearchTerm() {
      this.selectedInvoiceName = '';
    },
  },
  async mounted() {
    await this.setSavedInvoices();
    await this.setSubmittedInvoices();
  },
  async activated() {
    await this.setSavedInvoices();
    await this.setSubmittedInvoices();
  },

  methods: {
    async setSavedInvoices() {
      this.savedInvoices = (await this.fyo.db.getAll(
        ModelNameEnum.SalesInvoice,
        {
          fields: [],
          filters: { isPOS: true, submitted: false },
        }
      )) as SalesInvoice[];
    },
    async setSubmittedInvoices() {
      const invoices = (await this.fyo.db.getAll(ModelNameEnum.SalesInvoice, {
        fields: [],
        filters: { isPOS: true, submitted: true, returnAgainst: null },
      })) as SalesInvoice[];

      this.submittedInvoices = invoices.filter(
        (invoice) => !(invoice.outstandingAmount as Money).isZero()
      );
    },
    closeModal() {
      this.selectedInvoiceName = '';
      this.$emit('toggleModal', 'SavedInvoice');
    },
    openSelectedInvoice() {
      const selectedInvoice = this.filteredInvoices.find(
        (invoice) => invoice.name === this.selectedInvoiceName
      );
      if (!selectedInvoice) {
        return;
      }

      this.$emit('selectedInvoiceName', selectedInvoice);
      this.closeModal();
    },
    showSavedInvoices(saved: boolean) {
      this.savedInvoiceList = saved;
      this.selectedInvoiceName = '';
    },
    handleEnterKey() {
      if (this.filteredInvoices.length === 1) {
        this.selectedInvoiceName = String(this.filteredInvoices[0].name);
      }
    },
  },
});
</script>
