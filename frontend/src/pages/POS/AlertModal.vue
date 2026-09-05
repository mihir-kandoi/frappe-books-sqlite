<template>
  <Modal
    :open-modal="openModal"
    size="md"
    class="h-auto w-full px-6 select-none"
    @closemodal="$emit('toggleModal', 'Alert')"
  >
    <p class="text-center font-semibold py-3">{{ t`Alert` }}</p>
    <hr class="border-outline-gray-1" />
    <p class="py-6">
      {{ t`Clicking continue will remove all the selected items.` }}
    </p>

    <div class="row-start-6 grid grid-cols-2 gap-4 mt-auto pb-6">
      <div class="flex col-span-2 gap-5">
        <Button
          size="lg"
          theme="red"
          type="primary"
          class="w-full"
          @click="$emit('toggleModal', 'Alert')"
        >
          <slot>
            <span>{{ t`Cancel` }}</span>
          </slot>
        </Button>

        <Button
          size="lg"
          theme="green"
          type="primary"
          class="w-full"
          @click="
            routeTo('/list/SalesInvoice');
            $emit('toggleModal', 'Alert');
          "
        >
          <slot>
            <span>{{ t`Continue` }}</span>
          </slot>
        </Button>
      </div>
      <div class="col-span-2 flex justify-center mt-3">
        <Button
          size="lg"
          class="w-full"
          type="primary"
          @click="$emit('saveAndContinue')"
        >
          <slot>
            <span>{{ t`Save and Continue` }}</span>
          </slot>
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script lang="ts">
import Button from 'src/components/Button.vue';
import Modal from 'src/components/Modal.vue';
import { defineComponent } from 'vue';
import { routeTo } from 'src/utils/ui';

export default defineComponent({
  name: 'AlertModal',
  components: {
    Modal,
    Button,
  },
  props: {
    openModal: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['toggleModal', 'saveAndContinue'],
  methods: {
    routeTo,
  },
});
</script>
