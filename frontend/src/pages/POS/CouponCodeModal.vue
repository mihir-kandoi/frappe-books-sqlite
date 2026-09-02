<template>
  <Modal
    :open-modal="openModal"
    size="sm"
    class="h-auto w-full"
    @closemodal="cancelApplyCouponCode"
  >
    <p class="text-center font-semibold py-3">Apply Coupon Code</p>
    <div class="px-10">
      <hr class="dark:border-gray-800" />
      <p v-if="appliedCoupons.length" class="text-xs m-2 text-gray-500">
        {{ t`Applied Coupon Codes` }}
      </p>
      <div
        v-if="appliedCoupons.length"
        class="mt-2 max-h-40 overflow-y-auto custom-scroll custom-scroll-thumb2"
      >
        <Row
          v-for="coupon in appliedCoupons as AppliedCouponCodes[]"
          :key="coupon.coupons"
          :ratio="ratio"
          :border="true"
          class="border-b border-l border-r dark:border-gray-800 relative group h-coupon-mid hover:bg-gray-25 dark:bg-gray-890 items-center justify-center"
        >
          <div class="flex flex-row w-full items-center">
            <div class="flex flex-row">
              <FormControl
                v-for="df in tableFields"
                :key="df.fieldname"
                size="large"
                class="w-full"
                :df="df"
                :value="coupon[df.fieldname]"
                :read-only="true"
              />
            </div>
          </div>
          <div class="absolute right-3">
            <FrappeButton
              icon="lucide-trash-2"
              theme="red"
              variant="ghost"
              size="xs"
              :tooltip="t`Remove coupon`"
              :aria-label="t`Remove coupon`"
              @click="removeAppliedCoupon(coupon)"
            />
          </div>
        </Row>
      </div>

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
            class="w-full bg-green-500 dark:bg-green-700"
            style="padding: 1.35rem"
            :disabled="validationError"
            @click="setCouponCode()"
          >
            <slot>
              <p class="uppercase text-lg text-white font-semibold">
                {{ t`Save` }}
              </p>
            </slot>
          </Button>
        </div>
      </div>

      <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto mb-8">
        <div class="col-span-2">
          <Button
            class="w-full bg-red-500 dark:bg-red-700"
            style="padding: 1.35rem"
            @click="cancelApplyCouponCode()"
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
import Row from 'src/components/Row.vue';
import { InvoiceItem } from 'models/baseModels/InvoiceItem/InvoiceItem';
import { Button as FrappeButton } from 'frappe-ui';

export default defineComponent({
  name: 'CouponCodeModal',
  components: {
    Modal,
    Button,
    Link,
    FormControl,
    Row,
    FrappeButton,
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
    ratio() {
      return [1, 0.1, 1, 0.7];
    },
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
      this.initialCouponCodes = this.sinvDoc.coupons?.map((coupon) => coupon.coupons ?? '') ?? [];
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
        const appliedCouponCodes = this.fyo.doc.getNewDoc(ModelNameEnum.AppliedCouponCodes);

        await validateCouponCode(
          appliedCouponCodes as AppliedCouponCodes,
          this.couponCode,
          this.sinvDoc,
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
