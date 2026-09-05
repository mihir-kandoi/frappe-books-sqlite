<template>
  <div>
    <OpenPOSShiftModal
      v-if="!isPosShiftOpen"
      :open-modal="!isPosShiftOpen"
      @toggle-modal="emitEvent('toggleModal', 'ShiftOpen')"
    />

    <ClosePOSShiftModal
      :open-modal="openShiftCloseModal"
      @toggle-modal="emitEvent('toggleModal', 'ShiftClose', false)"
    />

    <LoyaltyProgramModal
      :open-modal="openLoyaltyProgramModal"
      :loyalty-points="loyaltyPoints"
      :loyalty-program="loyaltyProgram"
      @toggle-modal="emitEvent('toggleModal', 'LoyaltyProgram', false)"
      @set-loyalty-points="(points) => emitEvent('setLoyaltyPoints', points)"
    />

    <BatchSelectionModal
      :open-modal="openBatchSelectionModal"
      :item-code="selectedItemForBatch"
      @toggle-modal="emitEvent('toggleModal', 'BatchSelection', false)"
      @batch-selected="(batch) => emitEvent('batchSelected', batch)"
    />

    <SavedInvoiceModal
      :open-modal="openSavedInvoiceModal"
      @toggle-modal="emitEvent('toggleModal', 'SavedInvoice', false)"
      @selected-invoice-name="
        (invName) => emitEvent('selectedInvoiceName', invName)
      "
    />

    <CouponCodeModal
      :open-modal="openCouponCodeModal"
      @apply-pricing-rule="emitEvent('applyPricingRule')"
      @toggle-modal="emitEvent('toggleModal', 'CouponCode', false)"
      @set-coupons-count="(count) => emitEvent('setCouponsCount', count)"
    />

    <PriceListModal
      :open-modal="openPriceListModal"
      @toggle-modal="emitEvent('toggleModal', 'PriceList', false)"
    />

    <ItemEnquiryModal
      :open-modal="openItemEnquiryModal"
      :customer="sinvDoc?.party"
      @toggle-modal="emitEvent('toggleModal', 'ItemEnquiry', false)"
    />

    <PaymentModal
      :open-modal="openPaymentModal"
      @toggle-modal="emitEvent('toggleModal', 'Payment', false)"
      @set-paid-amount="(amount) => emitEvent('setPaidAmount', amount)"
      @set-payment-method="
        (paymentMethod) => emitEvent('setPaymentMethod', paymentMethod)
      "
      @set-transfer-ref-no="(ref) => emitEvent('setTransferRefNo', ref)"
      @set-transfer-clearance-date="
        (date) => emitEvent('setTransferClearanceDate', date)
      "
      @create-transaction="
        (print, status) => emitEvent('createTransaction', print, status)
      "
    />

    <ReturnSalesInvoiceModal
      :open-modal="openReturnSalesInvoiceModal"
      @selected-return-invoice="
        (value: any) => emitEvent('selectedReturnInvoice', value)
      "
      @toggle-modal="emitEvent('toggleModal', 'ReturnSalesInvoice', false)"
    />

    <AlertModal
      :open-modal="openAlertModal"
      @toggle-modal="emitEvent('toggleModal', 'Alert', false)"
      @save-and-continue="(value: any) => emitEvent('saveAndContinue', value)"
    />

    <KeyboardModal
      v-if="selectedItemField && selectedItemRow"
      :open-modal="openKeyboardModal"
      :modal-status="openKeyboardModal"
      :selected-item-field="selectedItemField"
      :selected-item-row="selectedItemRow as SalesInvoiceItem"
      :apply-pricing-rule-action="applyPricingRuleAction"
      @toggle-modal="emitEvent('toggleModal', 'Keyboard', false)"
    />

    <div
      class="h-[calc(100vh-var(--h-row-largest))] min-h-0 overflow-y-auto lg:overflow-hidden bg-surface-gray-1 grid grid-cols-1 lg:grid-cols-9 gap-3 p-4"
    >
      <div
        class="col-span-1 flex min-h-[40rem] w-full lg:col-span-3 lg:min-h-0"
      >
        <div class="grid min-h-0 grid-rows-5 w-full gap-3">
          <div
            class="p-4 min-h-0 flex flex-col row-span-5 bg-surface-base border rounded-4 border-outline-gray-1"
          >
            <!-- Customer Search -->
            <div class="flex-none">
              <MultiLabelLink
                v-if="sinvDoc?.fieldMap"
                class="w-full"
                secondary-link="phone"
                :border="true"
                :value="sinvDoc?.party"
                :df="sinvDoc?.fieldMap.party"
                :show-clear-button="true"
                @change="(value: string) => $emit('setCustomer', value)"
              />
            </div>

            <ModernPOSSelectedItemTable
              :expanded-batch-id="expandedBatchId"
              @set-expanded-batch-id="
                (rowName) => $emit('setExpandedBatchId', rowName)
              "
              @selected-row="selectedRow"
              @apply-pricing-rule="emitEvent('applyPricingRule')"
              @toggle-modal="emitEvent('toggleModal', 'Keyboard')"
            />
          </div>

          <div
            class="h-full p-2 bg-surface-base border rounded-4 border-outline-gray-1"
          >
            <div class="grid grid-cols-2 gap-2">
              <FloatingLabelFloatInput
                :df="{
                  label: t`Total Quantity`,
                  fieldtype: 'Float',
                  fieldname: 'totalQuantity',
                  minvalue: 0,
                  maxvalue: 1000,
                }"
                size="large"
                :value="totalQuantity"
                :read-only="true"
                :text-right="true"
              />

              <FloatingLabelCurrencyInput
                :df="{
                  label: t`Add'l Discounts`,
                  fieldtype: 'Currency',
                  fieldname: 'additionalDiscount',
                  minvalue: 0,
                }"
                size="large"
                :value="additionalDiscounts"
                :read-only="true"
                :text-right="true"
                @change="(amount: Money) => (additionalDiscounts = amount)"
              />
            </div>

            <div class="mt-2 grid grid-cols-2 gap-2">
              <FloatingLabelCurrencyInput
                :df="{
                  label: t`Item Discounts`,
                  fieldtype: 'Currency',
                  fieldname: 'itemDiscounts',
                }"
                size="large"
                :value="itemDiscounts"
                :read-only="true"
                :text-right="true"
              />

              <FloatingLabelCurrencyInput
                v-if="sinvDoc?.fieldMap"
                :df="sinvDoc?.fieldMap.grandTotal"
                size="large"
                :value="sinvDoc?.grandTotal"
                :read-only="true"
                :text-right="true"
              />
            </div>

            <div class="flex w-full gap-2">
              <div class="w-full">
                <Button
                  size="lg"
                  class="mt-2 w-full"
                  :style="{
                    backgroundColor:
                      profile?.saveButtonColour ||
                      fyo.singles.Defaults?.saveButtonColour,
                  }"
                  @click="$emit('saveInvoiceAction')"
                >
                  <slot>
                    <span>{{ t`Save` }}</span>
                  </slot>
                </Button>
                <Button
                  size="lg"
                  class="w-full mt-2"
                  :style="{
                    backgroundColor:
                      profile?.heldButtonColour ||
                      fyo.singles.Defaults?.heldButtonColour,
                  }"
                  @click="emitEvent('toggleModal', 'SavedInvoice', true)"
                >
                  <slot>
                    <span>{{ t`Held` }}</span>
                  </slot>
                </Button>
              </div>
              <div class="w-full">
                <Button
                  size="lg"
                  class="mt-2 w-full"
                  :style="{
                    backgroundColor:
                      profile?.cancelButtonColour ||
                      fyo.singles.Defaults?.cancelButtonColour,
                  }"
                  @click="() => $emit('clearValues')"
                >
                  <slot>
                    <span>{{ t`Cancel` }}</span>
                  </slot>
                </Button>
                <Button
                  size="lg"
                  v-if="isReturnInvoiceEnabledReturn"
                  class="mt-2 w-full"
                  :style="{
                    backgroundColor:
                      profile?.returnButtonColour ||
                      fyo.singles.Defaults?.returnButtonColour,
                  }"
                  @click="emitEvent('toggleModal', 'ReturnSalesInvoice', true)"
                >
                  <slot>
                    <span>{{ t`Return` }}</span>
                  </slot>
                </Button>
                <Button
                  size="lg"
                  v-else
                  class="mt-2 w-full"
                  :style="{
                    backgroundColor:
                      profile?.payButtonColour ||
                      fyo.singles.Defaults?.payButtonColour,
                  }"
                  @click="emitEvent('handlePaymentAction')"
                >
                  <slot>
                    <span>{{ t`Pay` }}</span>
                  </slot>
                </Button>
              </div>
            </div>
            <Button
              size="lg"
              v-if="isReturnInvoiceEnabledReturn"
              class="mt-2 w-full"
              :style="{
                backgroundColor:
                  profile?.payButtonColour ||
                  fyo.singles.Defaults?.payButtonColour,
              }"
              @click="emitEvent('handlePaymentAction')"
            >
              <slot>
                <span>{{ t`Pay` }}</span>
              </slot>
            </Button>
          </div>
        </div>
      </div>

      <div
        class="bg-surface-base border rounded-4 col-span-1 lg:col-span-6 relative min-h-[32rem] lg:min-h-0 flex flex-col border-outline-gray-1"
      >
        <div
          class="flex h-full min-h-0 flex-col rounded-4 p-4 pb-14 col-span-5"
        >
          <div class="flex gap-x-2">
            <!-- Item Search -->
            <MultiLabelLink
              class="w-full"
              secondary-link="barcode"
              third-link="itemCode"
              :option-records="searchItems"
              :df="{
                label: t`Search Item (Name, Code, or Barcode)`,
                fieldtype: 'Link',
                fieldname: 'item',
                target: 'Item',
              }"
              :border="true"
              :value="itemSearchTerm"
              :show-clear-button="true"
              :close-on-enter="true"
              @search="(query: string) => emitEvent('handleItemSearch', query)"
              @enter="
                (value: string) => emitEvent('handleItemSearch', value, true)
              "
              @change="(item: string) => emitEvent('handleItemSearch', item)"
            />

            <Link
              v-if="fyo.singles.AccountingSettings?.enableitemGroup"
              :df="{
                label: t`Filter by Group`,
                fieldtype: 'Link',
                fieldname: 'itemGroup',
                target: 'ItemGroup',
              }"
              :border="true"
              :show-clear-button="true"
              :value="selectedItemGroup"
              @change="(group: string) => emitEvent('setItemGroup', group)"
            />
          </div>

          <div
            v-if="!items.length"
            class="flex min-h-0 flex-1 flex-col items-center justify-center gap-1 px-4 text-center"
          >
            <p class="text-lg font-medium text-ink-gray-7">
              {{ t`No items found` }}
            </p>
            <p class="text-sm text-ink-gray-5">
              {{ t`Try another item visibility or filter.` }}
            </p>
          </div>

          <ModernPOSItemsTable
            v-else-if="tableView"
            :items="items"
            :item-qty-map="itemQuantityMap as ItemQtyMap"
            :item-visibility="itemVisibility"
            @add-item="(item: string) => emitEvent('addItem', item)"
          />

          <ItemsGrid
            v-else
            :items="items"
            @add-item="(item: POSItem) => emitEvent('addItem', item)"
          />

          <div class="absolute bottom-4 left-4 flex gap-x-3 p-1">
            <POSQuickActions
              :sinv-doc="sinvDoc"
              :loyalty-points="loyaltyPoints"
              :loyalty-program="loyaltyProgram"
              :applied-coupons-count="appliedCouponsCount"
              @toggle-view="emitEvent('toggleView')"
              @emit-route-to-sinv-list="emitEvent('routeToSinvList')"
              @toggle-modal="
                (modalName, value) => emitEvent('toggleModal', modalName, value)
              "
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Money } from 'pesa';
import { PropType } from 'vue';
import { fyo } from 'src/initFyo';
import { defineComponent } from 'vue';
import { getItem } from 'src/utils/pos';
import AlertModal from './AlertModal.vue';
import PaymentModal from './PaymentModal.vue';
import Button from 'src/components/Button.vue';
import KeyboardModal from './KeyboardModal.vue';
import PriceListModal from './PriceListModal.vue';
import ItemEnquiryModal from './ItemEnquiryModal.vue';
import { Item } from 'models/baseModels/Item/Item';
import Link from 'src/components/Controls/Link.vue';
import CouponCodeModal from './CouponCodeModal.vue';
import POSQuickActions from './POSQuickActions.vue';
import OpenPOSShiftModal from './OpenPOSShiftModal.vue';
import SavedInvoiceModal from './SavedInvoiceModal.vue';
import ClosePOSShiftModal from './ClosePOSShiftModal.vue';
import LoyaltyProgramModal from './LoyaltyProgramModal.vue';
import ReturnSalesInvoiceModal from './ReturnSalesInvoiceModal.vue';
import { POSProfile } from 'models/baseModels/POSProfile/PosProfile';
import MultiLabelLink from 'src/components/Controls/MultiLabelLink.vue';
import { POSItem, PosEmits, ItemQtyMap } from 'src/components/POS/types';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import ItemsGrid from 'src/components/POS/ItemsGrid.vue';
import ModernPOSItemsTable from 'src/components/POS/Modern/ModernPOSItemsTable.vue';
import FloatingLabelFloatInput from 'src/components/POS/FloatingLabelFloatInput.vue';
import { SalesInvoiceItem } from 'models/baseModels/SalesInvoiceItem/SalesInvoiceItem';
import FloatingLabelCurrencyInput from 'src/components/POS/FloatingLabelCurrencyInput.vue';
import { AppliedCouponCodes } from 'models/baseModels/AppliedCouponCodes/AppliedCouponCodes';
import ModernPOSSelectedItemTable from 'src/components/POS/Modern/ModernPOSSelectedItemTable.vue';
import BatchSelectionModal from 'src/pages/POS/BatchSelectionModal.vue';

export default defineComponent({
  name: 'ModernPos',
  components: {
    Link,
    Button,
    AlertModal,
    PaymentModal,
    KeyboardModal,
    MultiLabelLink,
    PriceListModal,
    ItemEnquiryModal,
    POSQuickActions,
    CouponCodeModal,
    OpenPOSShiftModal,
    SavedInvoiceModal,
    ItemsGrid,
    ClosePOSShiftModal,
    LoyaltyProgramModal,
    ModernPOSItemsTable,
    FloatingLabelFloatInput,
    ReturnSalesInvoiceModal,
    FloatingLabelCurrencyInput,
    ModernPOSSelectedItemTable,
    BatchSelectionModal,
  },
  props: {
    paidAmount: Money,
    tableView: Boolean,
    itemDiscounts: Money,
    openAlertModal: Boolean,
    isPosShiftOpen: Boolean,
    disablePayButton: Boolean,
    openPaymentModal: Boolean,
    openKeyboardModal: Boolean,
    openPriceListModal: Boolean,
    openItemEnquiryModal: Boolean,
    openCouponCodeModal: Boolean,
    openShiftCloseModal: Boolean,
    openSavedInvoiceModal: Boolean,
    openLoyaltyProgramModal: Boolean,
    openAppliedCouponsModal: Boolean,
    openReturnSalesInvoiceModal: Boolean,
    openBatchSelectionModal: Boolean,
    applyPricingRuleAction: {
      type: Function as PropType<() => Promise<void>>,
      required: true,
    },
    totalQuantity: {
      type: Number,
      default: 0,
    },
    loyaltyPoints: {
      type: Number,
      default: 0,
    },
    itemSearchTerm: {
      type: String,
      default: '',
    },
    selectedItemGroup: {
      type: String,
      default: '',
    },
    loyaltyProgram: {
      type: String,
      default: '',
    },
    appliedCouponsCount: {
      type: Number,
      default: 0,
    },
    coupons: {
      type: Object as PropType<AppliedCouponCodes>,
      default: () => ({}),
    },
    sinvDoc: {
      type: Object as PropType<SalesInvoice | undefined>,
      default: undefined,
    },
    itemQuantityMap: {
      type: Object as PropType<ItemQtyMap>,
      default: () => ({}),
    },
    items: {
      type: Array as PropType<POSItem[]>,
      default: () => [],
    },
    searchItems: {
      type: Array as PropType<POSItem[]>,
      default: () => [],
    },
    itemVisibility: {
      type: String,
      default: 'Inventory Items',
    },
    profile: {
      type: Object as PropType<POSProfile>,
      required: false,
      default: null,
    },
    batchAddedItems: {
      type: Array as () => string[],
      default: () => [],
    },
    selectedItemForBatch: {
      type: String,
      default: '',
    },
    expandedBatchId: {
      type: String as PropType<string | null | undefined>,
      default: undefined,
    },
  },
  emits: [
    'setExpandedBatchId',
    'addItem',
    'toggleView',
    'toggleModal',
    'setCustomer',
    'clearValues',
    'setItemGroup',
    'setPaidAmount',
    'setCouponsCount',
    'routeToSinvList',
    'handleItemSearch',
    'setLoyaltyPoints',
    'setPaymentMethod',
    'setTransferRefNo',
    'applyPricingRule',
    'saveInvoiceAction',
    'createTransaction',
    'setTransferAmount',
    'selectedInvoiceName',
    'selectedReturnInvoice',
    'setTransferClearanceDate',
    'saveAndContinue',
    'handlePaymentAction',
    'selectedRow',
    'batchSelected',
  ],
  data() {
    return {
      additionalDiscounts: fyo.pesa(0),

      selectedItemField: '',
      selectedItemRow: {} as SalesInvoiceItem,

      itemGroupFilter: '',
    };
  },
  computed: {
    isReturnInvoiceEnabledReturn: () =>
      fyo.singles.AccountingSettings?.enableInvoiceReturns ?? undefined,
  },
  methods: {
    emitEvent(
      eventName: PosEmits,
      ...args: (string | boolean | Item | POSItem | number | Money)[]
    ) {
      this.$emit(eventName, ...args);
    },
    selectedRow(row: SalesInvoiceItem, field: string) {
      this.selectedItemRow = row;
      this.selectedItemField = field;
      // Bubble up to POS to allow keyboard shortcuts to target this row
      this.$emit('selectedRow', row);
    },
    getItem,
  },
});
</script>
