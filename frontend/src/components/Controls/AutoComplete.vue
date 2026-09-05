<template>
  <ReadOnlyValue
    v-if="isReadOnly"
    :df="df"
    :value="value"
    :display-value="linkValue || undefined"
    :doc="doc"
    :border="border"
    :show-label="showLabel"
    :required="isRequired"
    :size="size"
    :text-right="textRight"
    :container-styles="containerStyles"
  >
    <template v-if="canLink" #trailing>
      <LinkedEntryButton
        :schema-name="linkSchemaName"
        :value="String(value ?? '')"
        @open="routeToLinkedDoc"
      />
    </template>
  </ReadOnlyValue>

  <FrappeCombobox
    v-else
    ref="input"
    spellcheck="false"
    :model-value="comboboxValue"
    :options="comboboxOptions"
    :open="isDropdownOpen"
    :loading="isLoading"
    :filterable="false"
    :open-on-focus="true"
    :label="showLabel ? df.label : undefined"
    :description="showLabel ? df.sub_label : undefined"
    :placeholder="inputPlaceholder"
    :empty-text="emptyMessage"
    :required="isRequired"
    :size="frappeSize"
    :variant="frappeVariant"
    class="min-w-0"
    :class="controlClasses"
    :style="containerStyles"
    @focus="onComboboxFocus"
    @blur="isFocused = false"
    @keydown.enter="onPressEnter"
    @update:open="onComboboxOpen"
    @update:query="onComboboxQueryChange"
    @update:model-value="onComboboxValueChange"
  >
    <template #suffix="{ open, clear, setOpen }">
      <div class="-me-1 flex shrink-0 items-center gap-0.5">
        <FrappeButton
          v-if="value && showClearButton"
          variant="ghost"
          size="xs"
          class="!size-5 !rounded-2"
          :aria-label="t`Clear value`"
          @pointerdown.prevent
          @click.stop="clearSelection(clear, setOpen)"
        >
          <template #icon><span class="lucide-x size-3.5" /></template>
        </FrappeButton>

        <LinkedEntryButton
          v-if="canLink"
          :schema-name="linkSchemaName"
          :value="String(value ?? '')"
          @open="routeToLinkedDoc"
        />

        <FrappeButton
          variant="ghost"
          size="xs"
          class="!size-5 !rounded-2"
          :aria-label="open ? t`Close options` : t`Open options`"
          @pointerdown.prevent
          @click.stop="setOpen(!open)"
        >
          <template #icon>
            <span
              class="lucide-chevron-down size-3.5 transition-transform duration-200"
              :class="open ? 'rotate-180' : ''"
            />
          </template>
        </FrappeButton>
      </div>
    </template>
  </FrappeCombobox>
</template>

<script>
import { getOptionList } from 'fyo/utils';
import {
  Button as FrappeButton,
  Combobox as FrappeCombobox,
} from 'frappe-ui';
import { FieldTypeEnum } from 'schemas/types';
import { fuzzyMatch } from 'src/utils';
import { getFormRoute, routeTo } from 'src/utils/ui';
import { h } from 'vue';
import Base from './Base.vue';
import LinkedEntryButton from './LinkedEntryButton.vue';
import ReadOnlyValue from './ReadOnlyValue.vue';

export default {
  name: 'AutoComplete',
  components: {
    FrappeButton,
    FrappeCombobox,
    LinkedEntryButton,
    ReadOnlyValue,
  },
  extends: Base,
  emits: ['focus', 'enter'],
  props: {
    closeOnEnter: { type: Boolean, default: false },
    showClearButton: { type: Boolean, default: false },
  },
  data() {
    return {
      acceptQueryChanges: false,
      isDropdownOpen: false,
      isFocused: false,
      isLoading: false,
      linkValue: '',
      suggestionRequest: 0,
      suppressedQuery: '',
      suggestions: [],
    };
  },
  computed: {
    comboboxValue() {
      if (typeof this.value === 'string' || typeof this.value === 'number') {
        return this.value || null;
      }
      return this.value == null ? null : String(this.value);
    },
    comboboxOptions() {
      const suggestions = [...this.suggestions];
      if (this.value && !this.findSuggestion(this.value, suggestions)) {
        suggestions.unshift({
          label: this.linkValue || String(this.value),
          value: this.value,
        });
      }
      return this.groupComboboxOptions(suggestions);
    },
    emptyMessage() {
      const { schemaName, fieldname } = this.df ?? {};
      const getMessage =
        this.fyo.models[schemaName]?.emptyMessages?.[fieldname];
      return getMessage?.(this.doc) ?? this.t`No results found`;
    },
    linkSchemaName() {
      let schemaName = this.df?.target;
      if (!schemaName) {
        const references = this.df?.references ?? '';
        schemaName = this.doc?.[references];
      }
      return schemaName;
    },
    options() {
      return this.df ? getOptionList(this.df, this.doc) : [];
    },
    canLink() {
      if (!this.value || !this.df) {
        return false;
      }

      const isLink = this.df.fieldtype === FieldTypeEnum.Link;
      const isDynamicLink = this.df.fieldtype === FieldTypeEnum.DynamicLink;
      if (!isLink && !isDynamicLink) {
        return false;
      }

      return Boolean(
        (isLink && this.df.target) ||
          (this.df.references && this.doc?.[this.df.references])
      );
    },
  },
  watch: {
    value: {
      immediate: true,
      handler(newValue) {
        const displayValue = this.getLinkValue(newValue);
        this.setLinkValue(displayValue);
        this.suppressedQuery = displayValue ?? '';
      },
    },
  },
  mounted() {
    const value = this.linkValue || this.value;
    this.setLinkValue(this.getLinkValue(value));
    this.acceptQueryChanges = true;
  },
  methods: {
    async focusInputTag() {
      await this.$nextTick();
      this.$refs.input?.focus?.();
    },
    setLinkValue(value) {
      this.linkValue = value ?? '';
    },
    getLinkValue(value) {
      const option =
        this.options.find((candidate) => candidate.value === value) ??
        this.options.find((candidate) => candidate.label === value);
      if (!value && !option) {
        return '';
      }
      return option?.label || this.linkValue || String(value);
    },
    async updateSuggestions(keyword = '') {
      const request = ++this.suggestionRequest;
      this.isLoading = true;
      try {
        const suggestions = await this.getSuggestions(keyword);
        if (request === this.suggestionRequest) {
          this.suggestions = suggestions;
        }
      } finally {
        if (request === this.suggestionRequest) {
          this.isLoading = false;
        }
      }
    },
    async getSuggestions(keyword = '') {
      const normalizedKeyword = keyword.toLowerCase();
      if (!normalizedKeyword) {
        return this.options;
      }

      return this.options
        .map((item) => ({ ...fuzzyMatch(normalizedKeyword, item.label), item }))
        .filter(({ isMatch }) => isMatch)
        .sort((left, right) => left.distance - right.distance)
        .map(({ item }) => item);
    },
    groupComboboxOptions(suggestions) {
      const ungrouped = [];
      const grouped = new Map();
      suggestions.forEach((suggestion, index) => {
        const option = this.toComboboxOption(suggestion, index);
        const group = suggestion.group ?? '';
        if (!group) {
          ungrouped.push(option);
          return;
        }

        if (!grouped.has(group)) {
          grouped.set(group, []);
        }
        grouped.get(group).push(option);
      });

      const groups = [...grouped.entries()]
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([group, options]) => ({ group, options }));
      return [...ungrouped, ...groups];
    },
    toComboboxOption(suggestion, index) {
      if (suggestion.actionOnly) {
        const component = suggestion.component;
        return {
          type: 'custom',
          key: `${this.df.fieldname}-action-${index}`,
          label: suggestion.label ?? this.t`Action`,
          description: suggestion.description,
          onClick: () => this.runSuggestionAction(suggestion),
          slots: component ? { label: () => h(component) } : undefined,
        };
      }

      return {
        ...suggestion,
        type: 'option',
        label: suggestion.label,
        value: this.getSuggestionValue(suggestion),
      };
    },
    getSuggestionValue(suggestion) {
      return suggestion.value ?? suggestion.label;
    },
    findSuggestion(value, suggestions = this.suggestions) {
      return suggestions.find(
        (suggestion) =>
          !suggestion.actionOnly &&
          this.getSuggestionValue(suggestion) === value
      );
    },
    async runSuggestionAction(suggestion) {
      if (!suggestion.action) {
        return;
      }

      if (this.doc) {
        await suggestion.action(this.doc, this.$router);
        return;
      }
      await suggestion.action();
    },
    setSuggestion(suggestion) {
      if (!suggestion || suggestion.actionOnly) {
        return;
      }

      this.suppressedQuery = suggestion.label;
      this.setLinkValue(suggestion.label);
      this.triggerChange(this.getSuggestionValue(suggestion));
    },
    clearSelection(clear, setOpen) {
      this.suppressedQuery = '';
      clear();
      this.setLinkValue('');
      this.updateSuggestions();
      setOpen(true);
    },
    onComboboxFocus(event) {
      this.isFocused = true;
      this.$emit('focus', event);
    },
    onComboboxOpen(isOpen) {
      this.isDropdownOpen = isOpen;
      if (isOpen) {
        this.updateSuggestions();
      }
    },
    onComboboxQueryChange(query) {
      const value = String(query ?? '');
      this.setLinkValue(value);
      if (!this.acceptQueryChanges) {
        return;
      }
      if (this.suppressedQuery === value) {
        this.suppressedQuery = '';
        return;
      }

      this.triggerChange(value);
      this.updateSuggestions(value);
    },
    onComboboxValueChange(value) {
      if (value == null) {
        this.setLinkValue('');
        this.triggerChange('');
        return;
      }

      const suggestion = this.findSuggestion(value);
      if (suggestion) {
        this.setSuggestion(suggestion);
        return;
      }

      this.setLinkValue(String(value));
      this.triggerChange(value);
    },
    async onPressEnter(event) {
      await this.$nextTick();
      const enteredValue = this.linkValue || event.target?.value || this.value;
      this.$emit('enter', enteredValue);
      if (this.closeOnEnter) {
        this.isDropdownOpen = false;
      }
    },
    async routeToLinkedDoc() {
      if (!this.linkSchemaName || !this.value) {
        return;
      }
      await routeTo(getFormRoute(this.linkSchemaName, this.value));
    },
  },
};
</script>
