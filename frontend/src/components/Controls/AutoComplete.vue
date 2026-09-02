<template>
  <Dropdown
    :items="suggestions"
    :is-loading="isLoading"
    :disabled="isReadOnly"
    :df="df"
    :doc="doc"
  >
    <template
      #default="{
        toggleDropdown,
        highlightItemUp,
        highlightItemDown,
        selectHighlightedItem,
      }"
    >
      <div class="flex h-full min-w-0 items-center">
        <FrappeTextInput
          ref="input"
          spellcheck="false"
          type="text"
          :model-value="linkValue"
          :label="showLabel ? df.label : undefined"
          :description="showLabel ? df.sub_label : undefined"
          :placeholder="inputPlaceholder"
          :disabled="isReadOnly"
          :required="isRequired"
          :size="frappeSize"
          :variant="frappeVariant"
          class="w-full min-w-0"
          :class="controlClasses"
          :style="containerStyles"
          :tabindex="isReadOnly ? '-1' : '0'"
          @focus="(e) => !isReadOnly && onInputFocus(e)"
          @click.stop="(e) => !isReadOnly && onClick(e, toggleDropdown)"
          @blur="(e) => !isReadOnly && onBlur(e.target.value, toggleDropdown)"
          @input="(e) => onInput(e, toggleDropdown)"
          @keydown.up="onKeyDownUp($event, toggleDropdown, highlightItemUp)"
          @keydown.down="
            onKeyDownDown($event, toggleDropdown, highlightItemDown)
          "
          @keydown.enter="
            onPressEnter($event, toggleDropdown, selectHighlightedItem)
          "
          @keydown.tab="closeDropdown($event, toggleDropdown)"
          @keydown.esc="closeDropdown($event, toggleDropdown)"
        >
          <template v-if="canLink" #suffix>
            <div class="-me-1 flex items-center gap-0.5">
              <FrappeButton
                v-if="value && showClearButton"
                variant="ghost"
                size="xs"
                class="!size-5 !rounded"
                aria-label="Clear value"
                @click.stop.prevent="clearValue($event, toggleDropdown)"
                @mousedown.prevent
              >
                <template #icon><span class="lucide-x size-3.5" /></template>
              </FrappeButton>
              <Popover
                :show-popup="showQuickView"
                :entry-delay="300"
                placement="bottom"
              >
                <template #target>
                  <FrappeButton
                    variant="ghost"
                    size="xs"
                    class="!size-5 !rounded"
                    aria-label="Open linked entry"
                    @mouseenter="showQuickView = true"
                    @mouseleave="showQuickView = false"
                    @click.stop="routeToLinkedDoc"
                    @mousedown.prevent
                  >
                    <template #icon>
                      <span class="lucide-chevron-right size-3.5" />
                    </template>
                  </FrappeButton>
                </template>
                <template #content>
                  <QuickView :schema-name="linkSchemaName" :name="value" />
                </template>
              </Popover>
            </div>
          </template>
        </FrappeTextInput>
      </div>
    </template>
  </Dropdown>
</template>
<script>
import { getOptionList } from 'fyo/utils';
import {
  Button as FrappeButton,
  TextInput as FrappeTextInput,
} from 'frappe-ui';
import { FieldTypeEnum } from 'schemas/types';
import Dropdown from 'src/components/Dropdown.vue';
import { fuzzyMatch } from 'src/utils';
import { getFormRoute, routeTo } from 'src/utils/ui';
import Popover from '../Popover.vue';
import Base from './Base.vue';
import QuickView from '../QuickView.vue';

export default {
  name: 'AutoComplete',
  components: {
    Dropdown,
    FrappeButton,
    FrappeTextInput,
    Popover,
    QuickView,
  },
  extends: Base,
  emits: ['focus', 'enter'],
  props: {
    closeOnEnter: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      showQuickView: false,
      linkValue: '',
      focInp: false,
      isLoading: false,
      suggestions: [],
      highlightedIndex: -1,
      isFocused: false,
      isDropdownOpen: false,
    };
  },
  computed: {
    linkSchemaName() {
      let schemaName = this.df?.target;

      if (!schemaName) {
        const references = this.df?.references ?? '';
        schemaName = this.doc?.[references];
      }

      return schemaName;
    },
    options() {
      if (!this.df) {
        return [];
      }

      return getOptionList(this.df, this.doc);
    },
    canLink() {
      if (!this.value || !this.df) {
        return false;
      }

      const fieldtype = this.df?.fieldtype;
      const isLink = fieldtype === FieldTypeEnum.Link;
      const isDynamicLink = fieldtype === FieldTypeEnum.DynamicLink;

      if (!isLink && !isDynamicLink) {
        return false;
      }

      if (isLink && this.df.target) {
        return true;
      }

      const references = this.df.references;
      if (!references) {
        return false;
      }

      if (!this.doc?.[references]) {
        return false;
      }

      return true;
    },
  },
  watch: {
    value: {
      immediate: true,
      handler(newValue) {
        this.setLinkValue(this.getLinkValue(newValue));
      },
    },
  },
  mounted() {
    const value = this.linkValue || this.value;
    this.setLinkValue(this.getLinkValue(value));
  },
  unmounted() {
    this.showQuickView = false;
  },
  deactivated() {
    this.showQuickView = false;
  },
  methods: {
    clearValue(e, toggleDropdown) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }

      this.triggerChange('');
      this.setLinkValue('');
      this.updateSuggestions();
      toggleDropdown(true);
      this.isDropdownOpen = true;
    },
    async routeToLinkedDoc() {
      const name = this.value;
      if (!this.linkSchemaName || !name) {
        return;
      }

      this.showQuickView = false;
      const route = getFormRoute(this.linkSchemaName, name);
      await routeTo(route);
    },
    async focusInputTag() {
      this.focInp = true;
      if (this.linkValue) {
        return;
      }

      await this.$nextTick();
      this.focus();
    },
    setLinkValue(value) {
      this.linkValue = value;
    },
    getLinkValue(value) {
      const oldValue = this.linkValue;
      let option = this.options.find((o) => o.value === value);
      if (!option) {
        option = this.options.find((o) => o.label === value);
      }
      if (!value && !option) {
        return null;
      }

      return option?.label ?? oldValue;
    },
    async updateSuggestions(keyword) {
      if (typeof keyword === 'string') {
        this.setLinkValue(keyword, true);
      }

      this.isLoading = true;
      const suggestions = await this.getSuggestions(keyword);
      this.suggestions = this.setSetSuggestionAction(suggestions);
      this.isLoading = false;
    },

    setSetSuggestionAction(suggestions) {
      for (const option of suggestions) {
        if (!option.action) {
          option.action = () => this.setSuggestion(option);
        }
      }

      return suggestions;
    },
    async getSuggestions(keyword = '') {
      keyword = keyword.toLowerCase();
      if (!keyword) {
        return this.options;
      }

      return this.options
        .map((item) => ({ ...fuzzyMatch(keyword, item.label), item }))
        .filter(({ isMatch }) => isMatch)
        .sort((a, b) => a.distance - b.distance)
        .map(({ item }) => item);
    },
    setSuggestion(suggestion) {
      if (suggestion?.actionOnly) {
        this.setLinkValue(this.value);
        return;
      }

      if (suggestion) {
        this.setLinkValue(suggestion.label);
        this.triggerChange(suggestion.value);
      }
    },
    onInputFocus(e) {
      this.isFocused = true;
    },
    onClick(e, toggleDropdown) {
      if (this.isFocused) {
        toggleDropdown(true);
        this.updateSuggestions();
        this.isDropdownOpen = true;
        this.$emit('focus', e);
      }
    },
    async onBlur(label, toggleDropdown) {
      this.isFocused = false;
      this.isDropdownOpen = false;
      if (!label && !this.value) {
        return;
      }
      if (!label) {
        this.triggerChange('');
        return;
      }

      if (this.suggestions.length === 0) {
        this.triggerChange(label);
        return;
      }

      const suggestion = this.suggestions.find((s) => s.label === label);
      if (suggestion) {
        this.setSuggestion(suggestion);
      } else {
        const suggestions = await this.getSuggestions(label);
        this.setSuggestion(suggestions[0]);
      }
    },

    onInput(e, toggleDropdown) {
      if (this.isReadOnly) {
        return;
      }

      if (this.focInp) {
        e.target.value = null;
        this.focInp = false;
        toggleDropdown(false);
        return;
      }

      if (!e.target.value) {
        this.setLinkValue('');
        this.triggerChange('');
        this.updateSuggestions();
        toggleDropdown(true);
        this.isDropdownOpen = true;
        return;
      }

      this.triggerChange(e.target.value);
      this.updateSuggestions(e.target.value);
      toggleDropdown(true);
      this.isDropdownOpen = true;
    },

    async onPressEnter(e, toggleDropdown, selectHighlightedItem) {
      e.preventDefault();

      const enteredValue = this.linkValue || e.target.value;

      if (
        this.suggestions.length > 0 &&
        this.isFocused &&
        this.isDropdownOpen
      ) {
        await selectHighlightedItem();
        this.closeDropdown(e, toggleDropdown);
        this.$emit('enter', this.linkValue || enteredValue);
        return;
      }

      await this.updateSuggestions(enteredValue);
      this.$emit('enter', enteredValue);

      if (this.closeOnEnter) {
        this.closeDropdown(e, toggleDropdown);
        return;
      }

      toggleDropdown(true);
      this.isDropdownOpen = true;
    },

    onKeyDownUp(e, toggleDropdown, highlightItemUp) {
      if (this.suggestions.length === 0) {
        this.updateSuggestions();
        toggleDropdown(true);
        this.isDropdownOpen = true;
      }
      highlightItemUp();
    },
    onKeyDownDown(e, toggleDropdown, highlightItemDown) {
      if (this.suggestions.length === 0) {
        this.updateSuggestions();
        toggleDropdown(true);
        this.isDropdownOpen = true;
      }
      highlightItemDown();
    },
    closeDropdown(e, toggleDropdown) {
      toggleDropdown(false);
      this.isDropdownOpen = false;
    },
  },
};
</script>
