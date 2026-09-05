<template>
  <Modal
    :open-modal="openModal"
    size="sm"
    class="h-auto w-full"
    @closemodal="cancelPriceList"
  >
    <p class="text-center font-semibold py-3">{{ t`Apply Price List` }}</p>
    <div class="px-10">
      <hr class="border-outline-gray-1" />
      <div class="flex justify-center pt-10">
        <div class="flex justify-between w-full mb-20">
          <div class="w-full">
            <Link
              v-if="sinvDoc.fieldMap"
              class="flex-shrink-0 w-full"
              :border="true"
              :value="selectedPriceList"
              :focus-input="true"
              :df="sinvDoc.fieldMap.priceList"
              @change="(value) => (selectedPriceList = value ?? '')"
            />
          </div>
          <div class="w-10 flex justify-end items-center">
            <FrappeButton
              icon="lucide-trash-2"
              theme="red"
              variant="ghost"
              :tooltip="t`Remove price list`"
              :aria-label="t`Remove price list`"
              @click="removePriceList"
            />
          </div>
        </div>
      </div>

      <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto mb-2">
        <div class="col-span-2">
          <Button
            size="lg"
            theme="green"
            type="primary"
            class="w-full"
            @click="setPriceList"
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
            @click="cancelPriceList"
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
import { t } from 'fyo';
import Modal from 'src/components/Modal.vue';
import { defineComponent, inject } from 'vue';
import Button from 'src/components/Button.vue';
import { showToast } from 'src/utils/interactive';
import Link from 'src/components/Controls/Link.vue';
import { Button as FrappeButton } from 'frappe-ui';
import { SalesInvoice } from 'models/baseModels/SalesInvoice/SalesInvoice';

export default defineComponent({
  name: 'PriceListModal',
  components: {
    Link,
    Modal,
    Button,
    FrappeButton,
  },
  props: {
    openModal: Boolean,
  },
  emits: ['toggleModal'],
  setup() {
    return {
      sinvDoc: inject('sinvDoc') as SalesInvoice,
    };
  },
  data() {
    return {
      selectedPriceList: '',
    };
  },
  watch: {
    openModal(value: boolean) {
      if (value) {
        this.selectedPriceList = this.sinvDoc.priceList ?? '';
      }
    },
  },
  methods: {
    removePriceList() {
      this.selectedPriceList = '';
    },
    async setPriceList() {
      try {
        await this.sinvDoc.set('priceList', this.selectedPriceList);
        this.$emit('toggleModal', 'PriceList');
      } catch (error) {
        showToast({
          type: 'error',
          message: t`${error as string}`,
        });
      }
    },
    cancelPriceList() {
      this.$emit('toggleModal', 'PriceList');
    },
  },
});
</script>
