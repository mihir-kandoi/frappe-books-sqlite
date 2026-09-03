<template>
  <div class="flex flex-col h-full">
    <PageHeader :title="t`Chart of Accounts`">
      <Button v-if="!isAllExpanded" @click="expand">{{ t`Expand` }}</Button>
      <Button v-if="!isAllCollapsed" @click="collapse">{{
        t`Collapse`
      }}</Button>
    </PageHeader>

    <!-- Chart of Accounts -->
    <div
      v-if="root"
      class="
        flex-1 flex flex-col
        overflow-y-auto
        mb-4
        custom-scroll custom-scroll-thumb1
      "
    >
      <!-- Chart of Accounts Indented List -->
      <template v-for="account in allAccounts" :key="account.name">
        <!-- Account List Item -->
        <div
          class="
            py-2
            cursor-pointer
            hover:bg-gray-50
            dark:hover:bg-gray-890 dark:text-gray-25
            group
            flex
            items-center
            border-b
            dark:border-gray-800
            flex-shrink-0
            pe-4
          "
          :class="[
            account.level !== 0 ? 'text-base' : 'text-lg',
            isQuickEditOpen(account) ? 'bg-gray-200 dark:bg-gray-900' : '',
          ]"
          :style="getItemStyle(account.level)"
          @click="onClick(account)"
        >
          <Icon
            :name="getAccountIconName(!!account.isGroup, account.name)"
            :size="getAccountIconSize(!!account.isGroup, account.name)"
          />
          <div class="flex items-baseline">
            <div
              class="ms-4"
              :class="[!account.parentAccount && 'font-semibold']"
            >
              {{ account.name }}
            </div>

            <!-- Add Account Buttons on Group Hover -->
            <div class="ms-4 hidden items-center gap-1 group-hover:flex">
              <Button
                v-if="account.isGroup"
                :background="false"
                size="xs"
                class="
                  text-xs text-gray-800
                  dark:text-gray-400
                  hover:text-gray-900
                  dark:hover:text-gray-100
                  focus:outline-none
                "
                @click.stop="addAccount(account, 'addingAccount')"
              >
                {{ t`Add Account` }}
              </Button>
              <Button
                v-if="account.isGroup"
                :background="false"
                size="xs"
                class="
                  text-xs text-gray-800
                  dark:text-gray-400
                  hover:text-gray-900
                  dark:hover:text-gray-100
                  focus:outline-none
                "
                @click.stop="addAccount(account, 'addingGroupAccount')"
              >
                {{ t`Add Group` }}
              </Button>
              <Button
                :background="false"
                size="xs"
                class="
                  text-xs text-gray-800
                  dark:text-gray-400
                  hover:text-gray-900
                  dark:hover:text-gray-100
                  focus:outline-none
                "
                @click.stop="deleteAccount(account)"
              >
                {{ account.isGroup ? t`Delete Group` : t`Delete Account` }}
              </Button>
            </div>
          </div>

          <!-- Account Balance String -->
          <p
            v-if="!account.isGroup"
            class="ms-auto text-base text-gray-800 dark:text-gray-400"
          >
            {{ getBalanceString(account) }}
          </p>
        </div>

        <!-- Add Account/Group -->
        <div
          v-if="account.addingAccount || account.addingGroupAccount"
          :key="account.name + '-adding-account'"
          class="
            px-4
            border-b
            dark:border-gray-800
            cursor-pointer
            hover:bg-gray-50
            dark:hover:bg-gray-890
            group
            flex
            items-center
            text-base
          "
          :style="getGroupStyle(account.level + 1)"
        >
          <Icon
            :name="getAccountIconName(account.addingGroupAccount)"
            :size="getAccountIconSize(account.addingGroupAccount)"
          />
          <div class="flex ms-4 h-row-mid items-center gap-1">
            <FrappeTextInput
              :ref="account.name"
              v-model="newAccountName"
              class="w-48"
              :class="{ 'text-gray-600 dark:text-gray-400': insertingAccount }"
              :placeholder="t`New Account`"
              type="text"
              size="sm"
              variant="ghost"
              :disabled="insertingAccount"
              @keydown.esc="cancelAddingAccount(account)"
              @keydown.enter="
                createNewAccount(account, account.addingGroupAccount)
              "
            />
            <Button
              v-if="!insertingAccount"
              :background="false"
              size="xs"
              class="
                text-xs text-gray-800
                dark:text-gray-400
                hover:text-gray-900
                dark:hover:text-gray-100
                focus:outline-none
              "
              @click="createNewAccount(account, account.addingGroupAccount)"
            >
              {{ t`Save` }}
            </Button>
            <Button
              v-if="!insertingAccount"
              :background="false"
              size="xs"
              class="
                text-xs text-gray-800
                dark:text-gray-400
                hover:text-gray-900
                dark:hover:text-gray-100
                focus:outline-none
              "
              @click="cancelAddingAccount(account)"
            >
              {{ t`Cancel` }}
            </Button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
<script lang="ts">
import { t } from 'fyo';
import { TextInput as FrappeTextInput } from 'frappe-ui';
import { isCredit } from 'models/helpers';
import { ModelNameEnum } from 'models/types';
import Icon from 'src/components/Icon.vue';
import PageHeader from 'src/components/PageHeader.vue';
import { fyo } from 'src/initFyo';
import { languageDirectionKey } from 'src/utils/injectionKeys';
import { docsPathMap } from 'src/utils/misc';
import { docsPathRef } from 'src/utils/refs';
import { commongDocDelete, openQuickEdit } from 'src/utils/ui';
import { getMapFromList, removeAtIndex } from 'utils/index';
import { defineComponent, nextTick } from 'vue';
import Button from '../components/Button.vue';
import { inject } from 'vue';
import { handleErrorWithDialog } from '../errorHandling';
import { AccountRootType, AccountType } from 'models/baseModels/Account/types';
import { TreeViewSettings } from 'fyo/model/types';
import { Doc } from 'fyo/model/doc';
import { showDialog } from 'src/utils/interactive';

type AccountItem = {
  name: string;
  parentAccount: string;
  rootType: AccountRootType;
  accountType: AccountType;
  level: number;
  location: number[];
  isGroup?: boolean;
  children: AccountItem[];
  expanded: boolean;
  addingAccount: boolean;
  addingGroupAccount: boolean;
};

type AccKey = 'addingAccount' | 'addingGroupAccount';

const rootAccountIcons: Record<string, string> = {
  'Application of Funds (Assets)': 'landmark',
  'Expenses': 'receipt-indian-rupee',
  'Income': 'coins',
  'Source of Funds (Liabilities)': 'hand-coins',
};

export default defineComponent({
  components: {
    Button,
    Icon,
    PageHeader,
    FrappeTextInput,
  },
  props: {
    darkMode: { type: Boolean, default: false },
  },
  setup() {
    return {
      languageDirection: inject(languageDirectionKey),
    };
  },
  data() {
    return {
      isAllCollapsed: true,
      isAllExpanded: false,
      root: null as null | { label: string; balance: number; currency: string },
      accounts: [] as AccountItem[],
      schemaName: 'Account',
      newAccountName: '',
      insertingAccount: false,
      totals: {} as Record<string, { totalDebit: number; totalCredit: number }>,
      refetchTotals: false,
      settings: null as null | TreeViewSettings,
    };
  },
  computed: {
    allAccounts() {
      const allAccounts: AccountItem[] = [];

      (function getAccounts(
        accounts: AccountItem[],
        level: number,
        location: number[]
      ) {
        for (let i = 0; i < accounts.length; i++) {
          const account = accounts[i];

          account.level = level;
          account.location = [...location, i];
          allAccounts.push(account);

          if (account.children != null && account.expanded) {
            getAccounts(account.children, level + 1, account.location);
          }
        }
      })(this.accounts, 0, []);

      return allAccounts;
    },
  },
  async mounted() {
    await this.setTotalDebitAndCredit();
    fyo.doc.observer.on('sync:AccountingLedgerEntry', () => {
      this.refetchTotals = true;
    });
  },
  async activated() {
    await this.fetchAccounts();
    if (fyo.store.isDevelopment) {
      // @ts-ignore
      window.coa = this;
    }

    docsPathRef.value = docsPathMap.ChartOfAccounts!;

    if (this.refetchTotals) {
      await this.setTotalDebitAndCredit();
      this.refetchTotals = false;
    }
  },
  deactivated() {
    docsPathRef.value = '';
  },
  methods: {
    async expand() {
      await this.toggleAll(this.accounts, true);
      this.isAllCollapsed = false;
      this.isAllExpanded = true;
    },
    async collapse() {
      await this.toggleAll(this.accounts, false);
      this.isAllExpanded = false;
      this.isAllCollapsed = true;
    },
    async toggleAll(accounts: AccountItem | AccountItem[], expand: boolean) {
      if (!Array.isArray(accounts)) {
        await this.toggle(accounts, expand);
        accounts = accounts.children ?? [];
      }

      for (const account of accounts) {
        await this.toggleAll(account, expand);
      }
    },
    async toggle(account: AccountItem, expand: boolean) {
      if (account.expanded === expand || !account.isGroup) {
        return;
      }

      await this.toggleChildren(account);
    },
    getBalance(account: AccountItem) {
      const total = this.totals[account.name];
      if (!total) {
        return 0;
      }

      const { totalCredit, totalDebit } = total;

      if (isCredit(account.rootType)) {
        return totalCredit - totalDebit;
      }

      return totalDebit - totalCredit;
    },
    getBalanceString(account: AccountItem) {
      const suffix = isCredit(account.rootType) ? t`Cr.` : t`Dr.`;
      const balance = this.getBalance(account);
      return `${fyo.format(balance, 'Currency')} ${suffix}`;
    },
    async setTotalDebitAndCredit() {
      const totals = await this.fyo.db.getTotalCreditAndDebit();
      this.totals = getMapFromList(totals, 'account');
    },
    async fetchAccounts() {
      this.settings =
        fyo.models[ModelNameEnum.Account]?.getTreeSettings(fyo) ?? null;
      const currency = this.fyo.singles.SystemSettings?.currency ?? '';
      const label = (await this.settings?.getRootLabel()) ?? '';

      this.root = {
        label,
        balance: 0,
        currency,
      };
      this.accounts = await this.getChildren();
    },
    async onClick(account: AccountItem) {
      let shouldOpen = !account.isGroup;
      if (account.isGroup) {
        shouldOpen = !(await this.toggleChildren(account));
      }

      if (account.isGroup && account.expanded) {
        this.isAllCollapsed = false;
      }

      if (account.isGroup && !account.expanded) {
        this.isAllExpanded = false;
      }

      if (!shouldOpen) {
        return;
      }

      const doc = await fyo.doc.getDoc(ModelNameEnum.Account, account.name);
      this.setOpenAccountDocListener(doc, account);
      await openQuickEdit({ doc });
    },
    setOpenAccountDocListener(
      doc: Doc,
      account?: AccountItem,
      parentAccount?: AccountItem
    ) {
      if (doc.hasListener('afterDelete')) {
        return;
      }

      doc.once('afterDelete', () => {
        this.removeAccount(doc.name!, account, parentAccount);
      });
    },
    async deleteAccount(account: AccountItem) {
      const canDelete = await this.canDeleteAccount(account);
      if (!canDelete) {
        return;
      }

      const doc = await fyo.doc.getDoc(ModelNameEnum.Account, account.name);
      this.setOpenAccountDocListener(doc, account);

      await commongDocDelete(doc, false);
    },
    async canDeleteAccount(account: AccountItem) {
      if (account.isGroup && !account.children?.length) {
        await this.fetchChildren(account);
      }

      if (!account.children?.length) {
        return true;
      }

      await showDialog({
        type: 'error',
        title: t`Cannot Delete Account`,
        detail: t`${account.name} has linked child accounts.`,
      });

      return false;
    },
    removeAccount(
      name: string,
      account?: AccountItem,
      parentAccount?: AccountItem
    ) {
      if (account == null && parentAccount == null) {
        return;
      }

      if (account == null && parentAccount) {
        account = parentAccount.children.find((ch) => ch?.name === name);
      }

      if (account == null) {
        return;
      }

      const indices = account.location.slice(1).map((i) => Number(i));

      let i = Number(account.location[0]);
      let parent = this.accounts[i];
      let children = this.accounts[i].children;

      while (indices.length > 1) {
        i = indices.shift()!;

        parent = children[i];
        children = children[i].children;
      }

      i = indices[0];

      if (children[i].name !== name) {
        return;
      }

      parent.children = removeAtIndex(children, i);
    },
    async toggleChildren(account: AccountItem) {
      const hasChildren = await this.fetchChildren(account);
      if (!hasChildren) {
        return false;
      }

      account.expanded = !account.expanded;
      if (!account.expanded) {
        account.addingAccount = false;
        account.addingGroupAccount = false;
      }

      return true;
    },
    async fetchChildren(account: AccountItem, force = false) {
      if (account.children == null || force) {
        account.children = await this.getChildren(account.name);
      }

      return !!account?.children?.length;
    },
    async getChildren(parent: null | string = null): Promise<AccountItem[]> {
      const children = await fyo.db.getAll(ModelNameEnum.Account, {
        filters: {
          parentAccount: parent,
        },
        fields: ['name', 'parentAccount', 'isGroup', 'rootType', 'accountType'],
        orderBy: 'name',
        order: 'asc',
      });

      return children.map((d) => {
        d.expanded = false;
        d.addingAccount = false;
        d.addingGroupAccount = false;

        return d as unknown as AccountItem;
      });
    },
    async addAccount(parentAccount: AccountItem, key: AccKey) {
      if (!parentAccount.expanded) {
        await this.fetchChildren(parentAccount);
        parentAccount.expanded = true;
      }
      // activate editing of type 'key' and deactivate other type
      let otherKey: AccKey =
        key === 'addingAccount' ? 'addingGroupAccount' : 'addingAccount';
      parentAccount[key] = true;
      parentAccount[otherKey] = false;

      await nextTick();
      const inputs = this.$refs[parentAccount.name] as Array<{
        focus: () => void;
      }>;
      inputs[0]?.focus();
    },
    cancelAddingAccount(parentAccount: AccountItem) {
      parentAccount.addingAccount = false;
      parentAccount.addingGroupAccount = false;
      this.newAccountName = '';
    },
    async createNewAccount(parentAccount: AccountItem, isGroup: boolean) {
      // freeze input
      this.insertingAccount = true;

      const accountName = this.newAccountName.trim();
      const doc = fyo.doc.getNewDoc('Account');
      try {
        let { name, rootType, accountType } = parentAccount;
        await doc.set({
          name: accountName,
          parentAccount: name,
          rootType,
          accountType,
          isGroup,
        });
        await doc.sync();

        // turn off editing
        parentAccount.addingAccount = false;
        parentAccount.addingGroupAccount = false;

        // update accounts
        await this.fetchChildren(parentAccount, true);

        // open quick edit
        await openQuickEdit({ doc });
        this.setOpenAccountDocListener(doc, undefined, parentAccount);

        // unfreeze input
        this.insertingAccount = false;
        this.newAccountName = '';
      } catch (e) {
        // unfreeze input
        this.insertingAccount = false;
        await handleErrorWithDialog(e, doc);
      }
    },
    isQuickEditOpen(account: AccountItem) {
      let { edit, schemaName, name } = this.$route.query;
      return !!(edit && schemaName === 'Account' && name === account.name);
    },
    getAccountIconName(isGroup: boolean, name?: string): string {
      return (name && rootAccountIcons[name]) || (isGroup ? 'folder' : 'circle');
    },
    getAccountIconSize(isGroup: boolean, name?: string): number {
      if (name && rootAccountIcons[name]) {
        return 16;
      }

      return isGroup ? 12 : 8;
    },
    getItemStyle(level: number) {
      const styles: Record<string, string> = {
        height: 'calc(var(--h-row-mid) + 1px)',
      };
      if (this.languageDirection === 'rtl') {
        styles['padding-right'] = `calc(1rem + 2rem * ${level})`;
      } else {
        styles['padding-left'] = `calc(1rem + 2rem * ${level})`;
      }
      return styles;
    },
    getGroupStyle(level: number) {
      const styles: Record<string, string> = {
        height: 'height: calc(var(--h-row-mid) + 1px)',
      };
      if (this.languageDirection === 'rtl') {
        styles['padding-right'] = `calc(1rem + 2rem * ${level})`;
      } else {
        styles['padding-left'] = `calc(1rem + 2rem * ${level})`;
      }
      return styles;
    },
  },
});
</script>
