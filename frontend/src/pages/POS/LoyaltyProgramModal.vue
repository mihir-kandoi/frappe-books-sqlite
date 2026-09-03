<template>
  <Modal
    :open-modal="openModal"
    size="sm"
    class="h-96 w-full"
    @closemodal="cancelLoyaltyProgram"
  >
    <p class="text-center py-4 dark:text-gray-100">Redeem Loyalty Points</p>

    <hr class="dark:border-gray-800" />

    <div class="flex gap-2 p-3 justify-end pt-10">
      <Icon name="coins" class="size-5 text-ink-amber-5" />

      <p class="dark:text-gray-100 pr-6">
        {{ loyaltyPoints }} - ({{ loyaltyProgram }})
      </p>
    </div>

    <Int
      v-if="sinvDoc.fieldMap"
      class="flex-shrink-0 px-10 pb-10"
      :show-label="true"
      :border="true"
      :focus-input="true"
      :value="pendingLoyaltyPoints"
      :df="sinvDoc.fieldMap.loyaltyPoints"
      @keydown.enter="saveLoyaltyPoints"
      @change="setPendingLoyaltyPoints"
    />

    <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto mb-2 px-10">
      <div class="col-span-2">
        <Button
          class="w-full bg-green-500 dark:bg-green-700"
          style="padding: 1.35rem"
          @click="saveLoyaltyPoints"
        >
          <slot>
            <p class="uppercase text-lg text-white font-semibold">
              {{ t`Save` }}
            </p>
          </slot>
        </Button>
      </div>
    </div>

    <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto px-10">
      <div class="col-span-2">
        <Button
          class="w-full bg-red-500 dark:bg-red-700"
          style="padding: 1.35rem"
          @click="cancelLoyaltyProgram"
        >
          <slot>
            <p class="uppercase text-lg text-white font-semibold">
              {{ t`Cancel` }}
            </p>
          </slot>
        </Button>
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
import { ModelNameEnum } from 'models/types';
import Int from 'src/components/Controls/Int.vue';
import Icon from 'src/components/Icon.vue';

export default defineComponent({
  name: 'LoyaltyProgramModal',
  components: {
    Modal,
    Button,
    Int,
    Icon,
  },
  props: {
    openModal: {
      type: Boolean,
      default: false,
    },
    loyaltyPoints: {
      type: Number,
      default: 0,
    },

    loyaltyProgram: {
      type: String,
      default: '',
    },
  },
  emits: ['setLoyaltyPoints', 'toggleModal'],
  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
    };
  },
  data() {
    return {
      validationError: false,
      initialLoyaltyPoints: 0,
      pendingLoyaltyPoints: 0,
    };
  },
  watch: {
    openModal(value: boolean) {
      if (!value) {
        return;
      }

      this.initialLoyaltyPoints = this.sinvDoc.loyaltyPoints ?? 0;
      this.pendingLoyaltyPoints = this.initialLoyaltyPoints;
      this.validationError = false;
    },
  },
  methods: {
    setPendingLoyaltyPoints(value: number) {
      this.pendingLoyaltyPoints = value;
      this.validationError = false;
    },
    cancelLoyaltyProgram() {
      this.sinvDoc.loyaltyPoints = this.initialLoyaltyPoints;
      this.$emit('setLoyaltyPoints', this.initialLoyaltyPoints);
      this.$emit('toggleModal', 'LoyaltyProgram', false);
    },
    async applyLoyaltyPoints(newValue: number): Promise<boolean> {
      try {
        const partyData = await this.fyo.db.get(
          ModelNameEnum.Party,
          this.sinvDoc.party as string
        );

        if (!partyData.loyaltyProgram) {
          throw new Error(t`Customer is not enrolled in a loyalty program`);
        }

        const loyaltyProgramDoc = await this.fyo.db.getAll(
          ModelNameEnum.LoyaltyProgram,
          {
            fields: ['conversionFactor', 'toDate'],
            filters: { name: partyData.loyaltyProgram as string },
          }
        );

        const toDate = loyaltyProgramDoc[0]?.toDate as Date;
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (toDate && new Date(toDate).getTime() < today.getTime()) {
          throw new Error(t`Loyalty program has expired and cannot be applied`);
        }

        if (this.loyaltyPoints < newValue) {
          throw new Error(
            `${this.sinvDoc.party as string} only has ${
              this.loyaltyPoints
            } points`
          );
        }

        const loyaltyPoint =
          newValue * ((loyaltyProgramDoc[0]?.conversionFactor as number) || 0);

        if (this.sinvDoc.baseGrandTotal?.lt(loyaltyPoint)) {
          throw new Error(t`no need ${newValue} points to purchase this item`);
        }

        if (newValue < 0) {
          throw new Error(t`Points must be greater than 0`);
        }

        this.sinvDoc.loyaltyPoints = newValue;
        this.$emit('setLoyaltyPoints', newValue);

        this.validationError = false;
        return true;
      } catch (error) {
        this.validationError = true;

        showToast({
          type: 'error',
          message: t`${error as string}`,
        });

        return false;
      }
    },
    async saveLoyaltyPoints() {
      const applied = await this.applyLoyaltyPoints(this.pendingLoyaltyPoints);

      if (applied) {
        this.$emit('toggleModal', 'LoyaltyProgram', false);
      }
    },
  },
});
</script>
