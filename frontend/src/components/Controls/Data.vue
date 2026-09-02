<script lang="ts">
import Base from './Base.vue';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Data',
  extends: Base,
  computed: {
    inputType(): 'text' {
      return 'text';
    },
  },
});
</script>
