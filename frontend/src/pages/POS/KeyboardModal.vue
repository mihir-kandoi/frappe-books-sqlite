<template>
  <Modal size="sm" class="h-auto w-full" :set-close-listener="false">
    <div class="w-full px-5">
      <p class="text-center dark:text-gray-400 font-semibold py-3">Keyboard</p>
      <hr class="dark:border-gray-800" />
      <div class="mx-6 my-3">
        <component
          :is="selectedItemRow?.fieldMap[selectedItemField!].fieldtype"
          ref="dynamicInput"
          :df="{
            fieldname: selectedItemRow?.fieldMap[selectedItemField!].fieldname as string,
            fieldtype: selectedItemRow?.fieldMap[selectedItemField!].fieldtype,
            label: selectedItemRow?.fieldMap[selectedItemField!].label as string,
          }"
          class="mb-3"
          :border="true"
          :show-label="true"
          :value="selectedValue"
          :focus-input="true"
          @change="(value: number) => handleInput(value.toString())"
        />

        <div
          id="keypad"
          class="
            text-4xl
            grid grid-cols-4
            gap-3
            rounded
            font-bold
            py-4
            dark:text-gray-400
          "
        >
          <Button
            v-for="key in keypadKeys"
            :key="key.label"
            :class="[
              key.wide ? 'col-span-2' : '',
              'w-full !h-14 !px-0 text-2xl font-semibold',
            ]"
            size="lg"
            @mousedown.prevent
            @click="handleKeypadKey(key)"
          >
            {{ key.label }}
          </Button>
        </div>
      </div>

      <div class="px-5">
        <div class="grid row-start-6 grid-cols-2 gap-4 mt-auto mb-3">
          <div class="col-span-2">
            <Button
              class="w-full bg-green-500 dark:bg-green-700"
              style="padding: 1.35rem"
              @click="saveSelectedItem()"
            >
              <slot>
                <p class="uppercase text-lg text-white font-semibold">
                  {{ t`Save` }}
                </p>
              </slot>
            </Button>
          </div>
        </div>

        <div class="grid row-start-6 grid-cols-2 gap-4 mt-auto mb-8">
          <div class="col-span-2">
            <Button
              class="w-full bg-red-500 dark:bg-red-700"
              style="padding: 1.35rem"
              @click="closeKeyboardModal()"
            >
              <slot>
                <p class="uppercase text-lg text-white font-semibold">
                  {{ t`Cancel` }}
                </p>
              </slot>
            </Button>
          </div>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script lang="ts">
import Modal from 'src/components/Modal.vue';
import { ModelNameEnum } from 'models/types';
import { defineComponent, inject } from 'vue';
import Button from 'src/components/Button.vue';
import Float from 'src/components/Controls/Float.vue';
import Currency from 'src/components/Controls/Currency.vue';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { SalesInvoiceItem } from 'models/baseModels/SalesInvoiceItem/SalesInvoiceItem';
import { showToast } from 'src/utils/interactive';
import { validateQty } from 'models/helpers';
import { InvoiceItem } from 'models/baseModels/InvoiceItem/InvoiceItem';
import { Money } from 'pesa';
import { DocValue } from 'fyo/core/types';

type KeypadKey = {
  label: string;
  value?: string;
  action?: 'delete' | 'reset';
  wide?: boolean;
};

export default defineComponent({
  name: 'KeyboardModal',
  components: {
    Modal,
    Float,
    Button,
    Currency,
  },
  props: {
    modalStatus: Boolean,
    selectedItemRow: SalesInvoiceItem,
    selectedItemField: {
      type: String,
      default: '',
    },
  },
  emits: ['toggleModal', 'applyPricingRule'],
  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
    };
  },
  data() {
    return {
      selectedValue: '',
      keypadKeys: [
        { label: '7', value: '7' },
        { label: '8', value: '8' },
        { label: '9', value: '9' },
        { label: 'Del', action: 'delete' },
        { label: '4', value: '4' },
        { label: '5', value: '5' },
        { label: '6', value: '6' },
        { label: '-', value: '-' },
        { label: '1', value: '1' },
        { label: '2', value: '2' },
        { label: '3', value: '3' },
        { label: '+', value: '+' },
        { label: '•', value: '.' },
        { label: '0', value: '0' },
        { label: 'Clear', action: 'reset', wide: true },
      ] as KeypadKey[],
    };
  },
  watch: {
    async modalStatus(newVal) {
      if (newVal) {
        await this.$nextTick();
        await this.focusInput();
      }
      this.updateSelectedValue();
    },
  },
  async mounted() {
    this.updateSelectedValue();
    await this.focusInput();
  },
  methods: {
    async handleKeypadKey(key: KeypadKey) {
      if (key.action === 'delete') {
        await this.deleteLast();
        return;
      }

      if (key.action === 'reset') {
        await this.reset();
        return;
      }

      if (key.value) {
        await this.appendValue(key.value);
      }
    },
    async appendValue(value: string) {
      if (value === '-') {
        this.selectedValue = this.selectedValue.startsWith('-')
          ? this.selectedValue
          : `-${this.selectedValue}`;
      } else if (value === '+') {
        this.selectedValue = this.selectedValue.startsWith('-')
          ? this.selectedValue.slice(1)
          : this.selectedValue;
      } else {
        this.selectedValue =
          this.selectedValue === '0' ? value : this.selectedValue + value;
      }

      await this.focusInput();
    },
    updateSelectedValue() {
      const value = this.selectedItemRow?.[this.selectedItemField];
      this.selectedValue = value?.toString() ?? '';
    },
    handleInput(value: string) {
      this.selectedValue = value;
    },
    async saveSelectedItem() {
      const row = this.selectedItemRow;
      const fieldname = this.selectedItemField;
      const value = Number(this.selectedValue);

      if (!row || !fieldname || !Number.isFinite(value)) {
        return showToast({
          type: 'error',
          message: this.t`Please enter a valid number.`,
        });
      }

      const originalValue = row[fieldname];
      const originalQuantity = row.quantity;
      const originalTransferQuantity = row.transferQuantity;
      const originalSetRate = row.setRate;
      const originalSetItemDiscountAmount = row.setItemDiscountAmount;
      const originalItemDiscountAmount = row.itemDiscountAmount;
      const originalItemDiscountPercent = row.itemDiscountPercent;

      try {
        if (row.fieldMap[fieldname].fieldtype === ModelNameEnum.Currency) {
          const moneyValue = this.fyo.pesa(value);

          if (fieldname === 'rate') {
            await row.set('rate', moneyValue);
            row.rate = moneyValue;
            row.setRate = moneyValue;

            await this.sinvDoc.runFormulas();
            this.$emit('toggleModal', 'Keyboard');

            return;
          }

          if (fieldname === 'itemDiscountAmount') {
            await row.set('setItemDiscountAmount', true);
            await row.set('itemDiscountAmount', moneyValue);
          }
        } else {
          if (fieldname === 'itemDiscountPercent') {
            await row.set('setItemDiscountAmount', false);
            await row.set('itemDiscountPercent', value);
          }

          if (fieldname === 'quantity' || fieldname === 'transferQuantity') {
            await row.set(fieldname, value);

            const existingItems =
              this.sinvDoc.items?.filter(
                (invoiceItem: InvoiceItem) =>
                  invoiceItem.item === row.item && !invoiceItem.isFreeItem
              ) ?? [];

            await validateQty(this.sinvDoc, row, existingItems);

            this.$emit('applyPricingRule');
          }
        }

        await this.sinvDoc.runFormulas();
        this.$emit('toggleModal', 'Keyboard');
      } catch (error) {
        await row.set(fieldname, originalValue as DocValue);
        row.quantity = originalQuantity;
        row.transferQuantity = originalTransferQuantity;
        row.setRate = originalSetRate as Money | undefined;
        await row.set('setItemDiscountAmount', originalSetItemDiscountAmount);
        await row.set('itemDiscountAmount', originalItemDiscountAmount);
        await row.set('itemDiscountPercent', originalItemDiscountPercent);
        await this.sinvDoc.runFormulas();

        showToast({
          type: 'error',
          message: this.t`${error as string}`,
        });

        if (fieldname === 'quantity' || fieldname === 'transferQuantity') {
          this.$emit('applyPricingRule');
        }
      }
    },
    async deleteLast() {
      this.selectedValue = this.selectedValue?.slice(0, -1);
      await this.focusInput();
    },
    async reset() {
      this.selectedValue = '';
      await this.focusInput();
    },
    async focusInput() {
      await this.$nextTick();
      (this.$refs.dynamicInput as HTMLInputElement)?.focus();
    },
    async closeKeyboardModal() {
      await this.reset();
      this.$emit('toggleModal', 'Keyboard');
    },
  },
});
</script>
