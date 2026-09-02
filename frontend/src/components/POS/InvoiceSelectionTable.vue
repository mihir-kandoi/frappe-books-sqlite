<template>
	<div class="flex min-h-0 flex-1 flex-col" role="grid" :aria-label="t`Invoices`">
		<Row
			:grid-template-columns="gridTemplateColumns"
			class="mt-2 w-full items-center rounded-t-md border px-2 text-gray-600 dark:border-gray-800 dark:text-gray-400"
			role="row"
		>
			<div class="flex items-center justify-center py-2" role="columnheader">
				<span class="sr-only">{{ t`Select` }}</span>
			</div>
			<div
				v-for="field in fields"
				:key="field.fieldname"
				class="flex items-center px-2 py-2 text-base"
				:class="{ 'justify-end': isNumeric(field) }"
				role="columnheader"
			>
				{{ field.label }}
			</div>
		</Row>

		<div
			v-if="rows.length"
			class="custom-scroll custom-scroll-thumb2 min-h-0 w-full flex-1 overflow-y-auto"
			role="rowgroup"
		>
			<Row
				v-for="row in rows"
				:key="getRowName(row)"
				:grid-template-columns="gridTemplateColumns"
				class="h-row-mid w-full items-center border-b border-l border-r px-2 transition-colors dark:border-gray-800"
				:class="
					isSelected(row)
						? 'bg-blue-50 dark:bg-blue-900/20'
						: 'bg-white dark:bg-gray-890'
				"
				role="row"
				:aria-selected="isSelected(row)"
			>
				<div class="flex items-center justify-center" role="gridcell">
					<FrappeCheckbox
						:model-value="isSelected(row)"
						:aria-label="`Select invoice ${getRowName(row)}`"
						size="sm"
						@update:model-value="setSelected(row, $event)"
					/>
				</div>
				<div
					v-for="field in fields"
					:key="field.fieldname"
					class="min-w-0 truncate px-2 py-2 text-base text-gray-900 dark:text-gray-100"
					:class="{ 'text-end': isNumeric(field) }"
					role="gridcell"
					:title="formatCell(row, field)"
				>
					{{ formatCell(row, field) }}
				</div>
			</Row>
		</div>

		<div
			v-else
			class="flex min-h-0 flex-1 items-center justify-center text-sm text-gray-600 dark:text-gray-400"
		>
			{{ emptyText }}
		</div>
	</div>
</template>

<script lang="ts">
import { Field } from "schemas/types";
import { Checkbox as FrappeCheckbox } from "frappe-ui";
import { fyo } from "src/initFyo";
import { isNumeric } from "src/utils";
import { defineComponent, PropType } from "vue";
import Row from "src/components/Row.vue";

type InvoiceRow = Record<string, unknown>;

export default defineComponent({
	name: "InvoiceSelectionTable",
	components: { FrappeCheckbox, Row },
	props: {
		rows: {
			type: Array as PropType<InvoiceRow[]>,
			default: () => [],
		},
		fields: {
			type: Array as PropType<Field[]>,
			required: true,
		},
		ratios: {
			type: Array as PropType<number[]>,
			required: true,
		},
		modelValue: {
			type: String,
			default: "",
		},
		emptyText: {
			type: String,
			required: true,
		},
	},
	emits: ["update:modelValue"],
	computed: {
		gridTemplateColumns(): string {
			const dataColumns = this.ratios.map((ratio) => `minmax(0, ${ratio}fr)`).join(" ");
			return `2.5rem ${dataColumns}`;
		},
	},
	methods: {
		isNumeric,
		getRowName(row: InvoiceRow): string {
			return String(row.name ?? "");
		},
		isSelected(row: InvoiceRow): boolean {
			return this.modelValue === this.getRowName(row);
		},
		setSelected(row: InvoiceRow, selected?: boolean | 0 | 1) {
			this.$emit("update:modelValue", selected ? this.getRowName(row) : "");
		},
		formatCell(row: InvoiceRow, field: Field): string {
			try {
				return fyo.format(row[field.fieldname], field) || "—";
			} catch {
				const value = row[field.fieldname];
				return value == null || value === "" ? "—" : String(value);
			}
		},
	},
});
</script>
