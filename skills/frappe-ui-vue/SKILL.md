---
name: frappe-ui-vue
description: Building modern single-page applications and portals with Frappe UI (@frappe/ui), Vue 3, and Tailwind CSS.
---

# Frappe UI & Vue 3 Frontend Architecture

## 1. Setup & Integration
Modern Frappe apps can embed custom SPAs built with `@frappe/ui` (Vue 3 + Tailwind CSS + Feather icons):
```bash
# Inside your custom app directory
yarn add @frappe/ui vue@3
```

In `your_app/frontend/src/main.js`:
```javascript
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { Button, Input, Dialog, setConfig, frappeRequest } from 'frappe-ui';

setConfig('resourceFetcher', frappeRequest);

const app = createApp(App);
app.use(router);
app.component('Button', Button);
app.component('Input', Input);
app.mount('#app');
```

## 2. Calling Frappe Backend from Vue
```vue
<template>
  <div class="p-6 max-w-4xl mx-auto space-y-4">
    <h1 class="text-2xl font-bold text-gray-900">Asset Management Dashboard</h1>
    
    <div class="flex items-center space-x-3">
      <Input v-model="searchQuery" placeholder="Search assets..." class="w-64" />
      <Button :loading="loading" @click="fetchAssets" variant="solid">Search</Button>
    </div>

    <div v-if="assets.length" class="divide-y divide-gray-200 border rounded-lg bg-white">
      <div v-for="asset in assets" :key="asset.name" class="p-4 flex justify-between">
        <div>
          <p class="font-medium text-gray-800">{{ asset.asset_name }}</p>
          <p class="text-xs text-gray-500">Serial: {{ asset.serial_no }}</p>
        </div>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          {{ asset.status }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { call } from 'frappe-ui';

const searchQuery = ref('');
const assets = ref([]);
const loading = ref(false);

async function fetchAssets() {
  loading.value = true;
  try {
    const res = await call('frappe.client.get_list', {
      doctype: 'Asset Item',
      fields: ['name', 'asset_name', 'serial_no', 'status'],
      filters: searchQuery.value ? { asset_name: ['like', `%${searchQuery.value}%`] } : {}
    });
    assets.value = res || [];
  } finally {
    loading.value = false;
  }
}

onMounted(fetchAssets);
</script>
```
