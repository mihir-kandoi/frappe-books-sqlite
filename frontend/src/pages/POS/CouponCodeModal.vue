<template>
  <Modal
    :open-modal="openModal"
    size="sm"
    class="h-auto w-full"
    @closemodal="cancelApplyCouponCode"
  >
    <p class="text-center font-semibold py-3">Apply Coupon Code</p>
    <div class="px-10">
      <hr class="border-outline-gray-1" />
      <p v-if="appliedCoupons.length" class="text-xs m-2 text-ink-gray-5">
        {{ t`Applied Coupon Codes` }}
      </p>
      <FrappeList
        v-if="appliedCoupons.length"
        :columns="['minmax(0, 1fr)', '2rem']"
        divider="full"
        class="custom-scroll custom-scroll-thumb2 mt-2 max-h-40 overflow-y-auto rounded-4 border border-outline-gray-1"
      >
        <FrappeListRows
          :items="appliedCoupons as AppliedCouponCodes[]"
          row-key="coupons"
        >
          <template #default="{ item: coupon, value }">
            <FrappeListRow
              :value="value"
              class="min-h-10 px-3 hover:bg-surface-gray-1"
            >
              <FrappeListCell>
                <FormControl
                  v-for="df in tableFields"
                  :key="df.fieldname"
                  size="large"
                  class="min-w-0 flex-1"
                  :df="df"
                  :value="coupon[df.fieldname]"
                  :read-only="true"
                />
              </FrappeListCell>
              <FrappeListCell class="justify-center">
                <FrappeButton
                  icon="lucide-trash-2"
                  theme="red"
                  variant="ghost"
                  size="xs"
                  :tooltip="t`Remove coupon`"
                  :aria-label="t`Remove coupon`"
                  @click="removeAppliedCoupon(coupon)"
                />
              </FrappeListCell>
            </FrappeListRow>
          </template>
        </FrappeListRows>
      </FrappeList>

      <div
        v-if="coupons.fieldMap"
        class="flex justify-center"
        :class="appliedCoupons.length ? 'pb-0 pt-4' : 'pt-10'"
      >
        <div class="w-80" :class="appliedCoupons.length ? 'pb-4' : 'pb-10'">
          <Link
            v-if="coupons.fieldMap"
            class="flex-shrink-0"
            :show-label="true"
            :border="true"
            :value="couponCode"
            :focus-input="true"
            :df="coupons.fieldMap.coupons"
            @change="updateCouponCode"
          />
        </div>
      </div>

      <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto mb-2">
        <div class="col-span-2">
          <Button
            size="lg"
            theme="green"
            type="primary"
            class="w-full"
            :disabled="validationError"
            @click="setCouponCode()"
          >
            <slot>
              <span>{{ t`Save` }}</span>
            </slot>
          </Button>
        </div>
      </div>

      <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto mb-8">
        <div class="col-span-2">
          <Button
            size="lg"
            theme="red"
            type="primary"
            class="w-full"
            @click="cancelApplyCouponCode()"
          >
            <slot>
              <span>{{ t`Cancel` }}</span>
            </slot>
          </Button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script lang="ts">
import Button from 'src/components/Button.vue';
import Modal from 'src/components/Modal.vue';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';
import { defineComponent, inject } from 'vue';
import { t } from 'fyo';
import { showToast } from 'src/utils/interactive';
import { AppliedCouponCodes } from 'models/baseModels/AppliedCouponCodes/AppliedCouponCodes';
import Link from 'src/components/Controls/Link.vue';
import { ModelNameEnum } from 'models/types';
import { validateCouponCode } from 'models/helpers';
import { Field } from 'schemas/types';
import FormControl from 'src/components/Controls/FormControl.vue';
import { InvoiceItem } from 'models/baseModels/InvoiceItem/InvoiceItem';
import { Button as FrappeButton } from 'frappe-ui';
import {
  List as FrappeList,
  ListCell as FrappeListCell,
  ListRow as FrappeListRow,
  ListRows as FrappeListRows,
} from 'frappe-ui/list';

export default defineComponent({
  name: 'CouponCodeModal',
  components: {
    Modal,
    Button,
    Link,
    FormControl,
    FrappeButton,
    FrappeList,
    FrappeListCell,
    FrappeListRow,
    FrappeListRows,
  },
  props: {
    openModal: Boolean,
  },
  emits: ['setCouponsCount', 'toggleModal', 'applyPricingRule'],

  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
      coupons: inject('coupons') as AppliedCouponCodes,
      appliedCoupons: inject('appliedCoupons') as AppliedCouponCodes[],
    };
  },
  data() {
    return {
      validationError: false,
      couponCode: '',
      initialCouponCodes: [] as string[],
    };
  },
  computed: {
    tableFields() {
      return [
        {
          fieldname: 'coupons',
          fieldtype: 'Link',
          required: true,
          readOnly: true,
        },
      ] as Field[];
    },
  },
  watch: {
    openModal(value: boolean) {
      if (!value) {
        return;
      }

      this.couponCode = '';
      this.validationError = false;
      this.initialCouponCodes =
        this.sinvDoc.coupons?.map((coupon) => coupon.coupons ?? '') ?? [];
    },
  },
  methods: {
    async updateCouponCode(value: string | Event) {
      try {
        if (!value) {
          return;
        }
        this.validationError = false;

        if ((value as Event).type === 'keydown') {
          value = ((value as Event).target as HTMLInputElement).value;
        }

        this.couponCode = value as string;
        const appliedCouponCodes = this.fyo.doc.getNewDoc(
          ModelNameEnum.AppliedCouponCodes
        );

        await validateCouponCode(
          appliedCouponCodes as AppliedCouponCodes,
          this.couponCode,
          this.sinvDoc
        );

        await this.sinvDoc.append('coupons', { coupons: this.couponCode });

        this.$emit('applyPricingRule');
        this.$emit('setCouponsCount', this.sinvDoc.coupons?.length ?? 0);
        this.couponCode = '';
        this.validationError = false;
      } catch (error) {
        this.validationError = true;

        showToast({
          type: 'error',
          message: t`${error as string}`,
        });
      }
    },
    setCouponCode() {
      this.$emit('toggleModal', 'CouponCode');
    },
    async removeAppliedCoupon(coupon: AppliedCouponCodes) {
      this.clearPricingRuleDiscounts();

      await coupon?.parentdoc?.remove('coupons', coupon.idx as number);

      this.$emit('applyPricingRule');
      this.$emit('setCouponsCount', this.sinvDoc.coupons?.length ?? 0);
    },
    async cancelApplyCouponCode() {
      this.couponCode = '';
      this.clearPricingRuleDiscounts();
      await this.sinvDoc.set('coupons', null);

      for (const coupons of this.initialCouponCodes) {
        await this.sinvDoc.append('coupons', { coupons });
      }

      this.$emit('applyPricingRule');
      this.$emit('setCouponsCount', this.sinvDoc.coupons?.length ?? 0);
      this.$emit('toggleModal', 'CouponCode');
    },
    clearPricingRuleDiscounts() {
      this.sinvDoc.items?.forEach((item: InvoiceItem) => {
        item.itemDiscountAmount = this.fyo.pesa(0);
        item.itemDiscountPercent = 0;
        item.setItemDiscountAmount = false;
      });
    },
  },
});
</script>
