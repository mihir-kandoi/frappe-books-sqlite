<template>
  <Modal
    :open-modal="openModal"
    size="sm"
    class="h-auto w-full"
    @closemodal="closeModal"
  >
    <p class="text-center font-semibold py-3">{{ t`Item Enquiry` }}</p>
    <div class="px-10">
      <hr class="border-outline-gray-1" />
      <div class="flex flex-col gap-5 pt-8">
        <Link
          :df="{
            fieldname: 'item',
            fieldtype: 'Link',
            target: 'Item',
            label: t`Item`,
            required: true,
          }"
          :value="ItemEnquiry.item"
          :border="true"
          :show-label="true"
          @change="(value: string) => (ItemEnquiry.item = value)"
        />

        <Text
          :df="{
            fieldname: 'description',
            fieldtype: 'Text',
            label: t`Description`,
          }"
          :value="ItemEnquiry.description"
          :border="true"
          :show-label="true"
          @change="(value: string) => (ItemEnquiry.description = value)"
        />

        <Link
          :df="{
            fieldname: 'customer',
            fieldtype: 'Link',
            target: 'Party',
            label: t`Customer`,
          }"
          :value="ItemEnquiry.customer"
          :border="true"
          :show-label="true"
          @change="
            (value: string) => {
              ItemEnquiry.customer = value;
              updateCustomerContact(value);
            }
          "
        />

        <Data
          :df="{
            fieldname: 'contact',
            fieldtype: 'Data',
            label: t`Contact`,
          }"
          :value="ItemEnquiry.contact"
          :border="true"
          :show-label="true"
          @change="(value: string) => (ItemEnquiry.contact = value)"
        />

        <Link
          :df="{
            fieldname: 'similarProduct',
            fieldtype: 'Link',
            target: 'Item',
            label: t`Similar Product`,
          }"
          :value="ItemEnquiry.similarProduct"
          :border="true"
          :show-label="true"
          @change="(value: string) => (ItemEnquiry.similarProduct = value)"
        />
      </div>

      <div class="grid grid-cols-2 gap-4 mt-10 mb-4">
        <div class="col-span-2">
          <Button
            size="lg"
            theme="green"
            type="primary"
            class="w-full"
            @click="submitForm"
          >
            <slot>
              <span>{{ t`Submit` }}</span>
            </slot>
          </Button>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="col-span-2">
          <Button
            size="lg"
            theme="red"
            type="primary"
            class="w-full"
            @click="closeModal"
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
import { defineComponent } from 'vue';
import { t } from 'fyo';
import { showToast } from 'src/utils/interactive';
import Modal from 'src/components/Modal.vue';
import Button from 'src/components/Button.vue';
import Link from 'src/components/Controls/Link.vue';
import Text from 'src/components/Controls/Text.vue';
import Data from 'src/components/Controls/Data.vue';
import { ItemEnquiry } from 'models/baseModels/ItemEnquiry/ItemEnquiry';
import { ModelNameEnum } from 'models/types';
import { DocValueMap } from 'fyo/core/types';

export default defineComponent({
  name: 'ItemEnquiryModal',
  components: {
    Modal,
    Button,
    Link,
    Text,
    Data,
  },
  props: {
    openModal: { type: Boolean, default: false },
    customer: { type: String, default: '' },
  },
  emits: ['toggleModal'],
  data() {
    return {
      ItemEnquiry: {} as ItemEnquiry,
    };
  },
  watch: {
    openModal: {
      async handler(isOpen: boolean) {
        if (!isOpen) {
          return;
        }

        this.clearValues();
        if (!this.customer) {
          return;
        }

        this.ItemEnquiry.customer = this.customer;
        await this.updateCustomerContact(this.customer);
      },
    },
  },
  methods: {
    async updateCustomerContact(customer: string) {
      this.ItemEnquiry.contact =
        ((await this.fyo.getValue('Party', customer, 'phone')) as string) || '';
    },

    async submitForm() {
      try {
        const itemEnquiryDoc = this.fyo.doc.getNewDoc(
          ModelNameEnum.ItemEnquiry,
          this.ItemEnquiry as DocValueMap
        );
        await itemEnquiryDoc.sync();
        showToast({
          type: 'success',
          message: t`Item enquiry submitted`,
        });
        this.clearValues();
        this.$emit('toggleModal', 'ItemEnquiry');
      } catch (error) {
        showToast({
          type: 'error',
          message: t`${error as string}`,
        });
      }
    },
    clearValues() {
      this.ItemEnquiry = {} as ItemEnquiry;
    },
    closeModal() {
      this.clearValues();
      this.$emit('toggleModal', 'ItemEnquiry');
    },
  },
});
</script>
