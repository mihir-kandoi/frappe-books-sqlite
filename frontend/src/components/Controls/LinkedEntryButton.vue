<template>
	<FrappeHoverCard
		side="bottom"
		align="center"
		:offset="8"
		:hover-delay="0.3"
		:leave-delay="0.15"
	>
		<template #trigger>
			<FrappeButton
				variant="ghost"
				size="xs"
				icon="lucide-chevron-right"
				:label="t`Open linked entry`"
				@pointerdown.prevent
				@click.stop="$emit('open')"
			/>
		</template>
		<QuickView :schema-name="schemaName" :name="value" />
	</FrappeHoverCard>
</template>

<script lang="ts">
import { Button as FrappeButton, HoverCard as FrappeHoverCard } from "frappe-ui";
import { defineComponent } from "vue";
import QuickView from "../QuickView.vue";

export default defineComponent({
	name: "LinkedEntryButton",
	components: { FrappeButton, FrappeHoverCard, QuickView },
	props: {
		schemaName: { type: String, default: "" },
		value: { type: String, default: "" },
	},
	emits: ["open"],
});
</script>
