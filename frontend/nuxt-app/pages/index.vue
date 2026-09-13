<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-950 text-white">
      <div class="container mx-auto px-5 py-5 sm:px-6">
        <div class="flex items-center justify-between gap-5">
          <div class="flex min-w-0 items-center gap-3">
            <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500 shadow-lg shadow-blue-950/30">
              <Icon name="mdi:crosshairs-gps" class="text-2xl" />
            </div>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-semibold tracking-tight sm:text-2xl">
                GPS Tracking System
              </h1>
              <p class="mt-0.5 text-sm text-slate-400">
                Device monitoring dashboard
              </p>
            </div>
          </div>
          <div class="hidden shrink-0 border-l border-slate-800 pl-5 text-right sm:block">
            <p class="text-xs font-medium uppercase tracking-wider text-slate-500">Last sync</p>
            <p class="mt-1 text-sm font-medium text-slate-200">{{ lastUpdated || "Never" }}</p>
          </div>
          <div class="sm:hidden">
            <span class="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400 ring-4 ring-emerald-400/10" />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-5 py-8 sm:px-6 lg:py-10">
      <!-- Statistics Cards -->
      <div class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3 lg:gap-5">
        <div
          class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="flex items-center justify-between">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                Total Devices
              </p>
              <p class="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
                {{ stats.total_devices }}
              </p>
            </div>
            <div
              class="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-50"
            >
              <Icon name="mdi:devices" class="text-2xl text-blue-600" />
            </div>
          </div>
        </div>

        <div
          class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="flex items-center justify-between">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                With GPS
              </p>
              <p class="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
                {{ stats.with_coordinates }}
              </p>
            </div>
            <div
              class="flex h-11 w-11 items-center justify-center rounded-lg bg-emerald-50"
            >
              <Icon
                name="mdi:map-marker-check"
                class="text-2xl text-emerald-600"
              />
            </div>
          </div>
        </div>

        <div
          class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="flex items-center justify-between">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                No GPS
              </p>
              <p class="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
                {{ stats.without_coordinates }}
              </p>
            </div>
            <div
              class="flex h-11 w-11 items-center justify-center rounded-lg bg-rose-50"
            >
              <Icon name="mdi:map-marker-off" class="text-2xl text-rose-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <section class="mb-10 rounded-xl border border-slate-200 bg-white shadow-sm">
        <div class="flex flex-col gap-4 border-b border-slate-100 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <h2 class="flex items-center text-lg font-semibold text-slate-950">
              <span class="mr-2 flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
                <Icon name="mdi:lightning-bolt-outline" class="text-lg text-slate-700" />
              </span>
              Quick actions
            </h2>
            <p class="mt-1 text-sm text-slate-500">Update, export, or reload device data.</p>
          </div>
        </div>

        <div class="flex flex-wrap gap-3 px-5 py-5 sm:px-6">
          <button
            class="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            :disabled="loading.fetch"
            @click="fetchTrackingData"
          >
            <Icon
              :name="loading.fetch ? 'mdi:loading' : 'mdi:download'"
              :class="{ 'animate-spin': loading.fetch }"
              class="mr-2 text-lg"
            />
            {{ loading.fetch ? "Fetching..." : "Fetch GPS Data" }}
          </button>

          <button
            class="inline-flex items-center rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="loading.export"
            @click="exportToCsv"
          >
            <Icon
              :name="loading.export ? 'mdi:loading' : 'mdi:file-export'"
              :class="{ 'animate-spin': loading.export }"
              class="mr-2 text-lg"
            />
            {{ loading.export ? "Exporting..." : "Export to CSV" }}
          </button>

          <button
            class="inline-flex items-center rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="loading.refresh"
            @click="refreshData"
          >
            <Icon
              :name="loading.refresh ? 'mdi:loading' : 'mdi:refresh'"
              :class="{ 'animate-spin': loading.refresh }"
              class="mr-2 text-lg"
            />
            {{ loading.refresh ? "Refreshing..." : "Refresh Data" }}
          </button>
        </div>

        <!-- Load to Database Section -->
        <div
          v-if="latestLogFile"
          class="mx-5 mb-5 border border-amber-200 bg-amber-50 px-5 py-4 sm:mx-6 sm:mb-6"
        >
          <div class="flex items-start">
            <div class="mr-3 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100">
              <Icon name="mdi:information" class="text-lg text-amber-700" />
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-amber-950">
                Latest GPS Data Available
              </h3>
              <p class="mt-1 text-sm text-amber-800">
                {{ latestLogFile.folder }}
              </p>
              <div class="mt-4 flex flex-wrap gap-3">
                <button
                  class="inline-flex items-center rounded-lg bg-amber-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-amber-300"
                  :disabled="loading.load"
                  @click="loadToDatabase(false)"
                >
                  <Icon
                    :name="loading.load ? 'mdi:loading' : 'mdi:database-plus'"
                    :class="{ 'animate-spin': loading.load }"
                    class="mr-2"
                  />
                  {{ loading.load ? "Loading..." : "Load to Database" }}
                </button>
                <button
                  class="inline-flex items-center rounded-lg border border-rose-200 bg-white px-4 py-2.5 text-sm font-semibold text-rose-700 shadow-sm transition-colors hover:bg-rose-50 disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="loading.load"
                  @click="loadToDatabase(true)"
                >
                  <Icon
                    :name="
                      loading.load ? 'mdi:loading' : 'mdi:database-refresh'
                    "
                    :class="{ 'animate-spin': loading.load }"
                    class="mr-2"
                  />
                  {{ loading.load ? "Loading..." : "Replace All Data" }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Device Data Table -->
      <div class="bg-white rounded-2xl overflow-hidden border border-gray-200">
        <div
          class="p-6 border-b border-gray-200 bg-gradient-to-r from-slate-50 to-gray-50"
        >
          <h2 class="text-2xl font-bold text-gray-900 flex items-center">
            <div class="p-2 rounded-lg bg-blue-100 mr-3">
              <Icon name="mdi:table" class="text-blue-600 text-xl" />
            </div>
            Device Records
            <span class="ml-3 text-sm font-normal text-gray-500">
              ({{ pagination.total_records }} devices)
            </span>
          </h2>
        </div>

        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gradient-to-r from-gray-50 to-slate-50">
              <tr>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  Rank
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  IMEI
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  Coordinates
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  Status
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  Last Update
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  Data Status
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider"
                >
                  Time Since Update
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr
                v-for="(device, index) in devices"
                :key="device.ranking_id"
                class="hover:bg-blue-50 transition-colors duration-150"
              >
                <td
                  class="px-6 py-5 whitespace-nowrap text-sm font-bold text-gray-900"
                >
                  <div class="flex items-center">
                    <span
                      class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold"
                    >
                      #{{
                        (pagination.current_page - 1) * pagination.per_page +
                        index +
                        1
                      }}
                    </span>
                  </div>
                </td>
                <td
                  class="px-6 py-5 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"
                >
                  {{ device.imei }}
                </td>
                <td class="px-6 py-5 whitespace-nowrap text-sm text-gray-900">
                  <span
                    v-if="
                      device.latitude &&
                      device.longitude &&
                      device.latitude !== 0 &&
                      device.longitude !== 0
                    "
                    class="flex items-center"
                  >
                    <Icon name="mdi:map-marker" class="text-green-500 mr-1" />
                    {{ device.latitude.toFixed(6) }},
                    {{ device.longitude.toFixed(6) }}
                  </span>
                  <span v-else class="text-gray-400 flex items-center">
                    <Icon name="mdi:map-marker-off-outline" class="mr-1" />
                    No GPS data
                  </span>
                </td>
                <td class="px-6 py-5 whitespace-nowrap">
                  <span
                    :class="getStatusColor(device.status)"
                    class="px-3 py-1.5 text-xs font-bold rounded-full"
                  >
                    {{ device.status }}
                  </span>
                </td>
                <td class="px-6 py-5 whitespace-nowrap text-sm text-gray-900">
                  <div v-if="device.hearttime_date" class="flex items-center">
                    <Icon
                      name="mdi:calendar-clock"
                      class="text-gray-400 mr-2"
                    />
                    <div>
                      <div class="font-semibold">
                        {{ device.hearttime_date }}
                      </div>
                      <div class="text-xs text-gray-500">
                        {{ device.hearttime_time }}
                      </div>
                    </div>
                  </div>
                  <span v-else class="text-gray-400 flex items-center">
                    <Icon name="mdi:calendar-remove" class="mr-1" />
                    No data
                  </span>
                </td>
                <td class="px-6 py-5 whitespace-nowrap">
                  <span
                    :class="getDataStatusColor(device.datastatus_description)"
                    class="px-3 py-1.5 text-xs font-bold rounded-full flex items-center justify-center w-fit"
                  >
                    <span
                      :class="
                        device.datastatus_description === 'Online'
                          ? 'animate-pulse'
                          : ''
                      "
                      class="w-2 h-2 rounded-full mr-2"
                      :style="{
                        backgroundColor:
                          device.datastatus_description === 'Online'
                            ? '#10b981'
                            : device.datastatus_description === 'Offline'
                              ? '#ef4444'
                              : '#f59e0b',
                      }"
                    />
                    {{ device.datastatus_description }}
                  </span>
                </td>
                <td class="px-6 py-5 whitespace-nowrap text-sm text-gray-900">
                  <span
                    :class="[
                      device.datastatus_description === 'Online'
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : getTimeSinceColorClass(device.TimeSinceUpdate),
                      'px-3 py-1.5 text-xs font-bold rounded-full',
                    ]"
                  >
                    {{
                      device.datastatus_description === "Online"
                        ? "Active"
                        : device.TimeAgo
                          ? device.TimeAgo +
                            (device.TimeSinceUpdate
                              ? " (" + device.TimeSinceUpdate + ")"
                              : "")
                          : getTimeAgoLabel(device.TimeSinceUpdate)
                            ? getTimeAgoLabel(device.TimeSinceUpdate) +
                              (device.TimeSinceUpdate
                                ? " (" + device.TimeSinceUpdate + ")"
                                : "")
                            : "No data"
                    }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          class="bg-gradient-to-r from-gray-50 to-slate-50 px-6 py-4 flex items-center justify-between border-t-2 border-gray-200"
        >
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              class="relative inline-flex items-center px-4 py-2 border-2 border-gray-300 text-sm font-semibold rounded-lg text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              :disabled="!pagination.has_previous"
              @click="previousPage"
            >
              Previous
            </button>
            <button
              class="ml-3 relative inline-flex items-center px-4 py-2 border-2 border-gray-300 text-sm font-semibold rounded-lg text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              :disabled="!pagination.has_next"
              @click="nextPage"
            >
              Next
            </button>
          </div>
          <div
            class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between"
          >
            <div>
              <p class="text-sm text-gray-700 font-medium">
                Showing page
                <span class="font-bold text-blue-600">{{
                  pagination.current_page
                }}</span>
                of
                <span class="font-bold text-blue-600">{{
                  pagination.total_pages
                }}</span>
                <span class="text-gray-500 ml-2"
                  >({{ pagination.total_records }} total records)</span
                >
              </p>
            </div>
            <div class="flex space-x-2">
              <button
                class="relative inline-flex items-center px-4 py-2 border-2 border-gray-300 bg-white text-sm font-semibold text-gray-700 hover:bg-blue-50 hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all"
                :disabled="!pagination.has_previous"
                @click="previousPage"
              >
                <Icon name="mdi:chevron-left" class="text-lg" />
                Previous
              </button>
              <button
                class="relative inline-flex items-center px-4 py-2 border-2 border-gray-300 bg-white text-sm font-semibold text-gray-700 hover:bg-blue-50 hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all"
                :disabled="!pagination.has_next"
                @click="nextPage"
              >
                Next
                <Icon name="mdi:chevron-right" class="text-lg" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Toast Notifications -->
    <transition
      enter-active-class="transform transition duration-300 ease-out"
      enter-from-class="translate-x-full opacity-0"
      enter-to-class="translate-x-0 opacity-100"
      leave-active-class="transform transition duration-200 ease-in"
      leave-from-class="translate-x-0 opacity-100"
      leave-to-class="translate-x-full opacity-0"
    >
      <div v-if="message.text" class="fixed right-4 top-4 z-50 w-[calc(100%-2rem)] max-w-md sm:right-6 sm:top-6 sm:w-auto">
        <div
          :class="
            message.type === 'success'
              ? 'border-emerald-200'
              : 'border-rose-200'
          "
          class="flex items-center rounded-xl border bg-white p-4 shadow-lg shadow-slate-900/10"
        >
          <div
            :class="message.type === 'success' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'"
            class="mr-3 flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
          >
            <Icon
              :name="
                message.type === 'success'
                  ? 'mdi:check-circle'
                  : 'mdi:alert-circle'
              "
              class="text-xl"
            />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-slate-800">{{ message.text }}</p>
          </div>
          <button
            class="ml-3 rounded-md p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
            @click="message.text = ''"
          >
            <Icon name="mdi:close" class="text-lg" />
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
// Meta and head
useHead({
  title: "GPS Tracking Dashboard",
  meta: [
    {
      name: "description",
      content: "GPS Tracking System Dashboard for monitoring devices",
    },
  ],
});

// Reactive data
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const stats = ref({
  total_devices: 0,
  with_coordinates: 0,
  without_coordinates: 0,
  status_counts: {},
});

const devices = ref([]);
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_records: 0,
  per_page: 50,
  has_next: false,
  has_previous: false,
});

const loading = ref({
  fetch: false,
  export: false,
  refresh: false,
  load: false,
});

const message = ref({
  text: "",
  type: "success",
});

const latestLogFile = ref(null);
const lastUpdated = ref("");

// Methods
const showMessage = (text, type = "success") => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = { text: "", type: "success" };
  }, 5000);
};

const getStatusColor = (status) => {
  if (status === "success")
    return "bg-green-100 text-green-800 border border-green-200";
  if (status.includes("error") || status.includes("can't access"))
    return "bg-red-100 text-red-800 border border-red-200";
  return "bg-yellow-100 text-yellow-800 border border-yellow-200";
};

const getDataStatusColor = (status) => {
  if (status === "Online")
    return "bg-green-100 text-green-800 border border-green-200";
  if (status === "Offline")
    return "bg-red-100 text-red-800 border border-red-200";
  if (status === "Expired")
    return "bg-orange-100 text-orange-800 border border-orange-200";
  return "bg-gray-100 text-gray-800 border border-gray-200";
};

// Parse the TimeSinceUpdate string (e.g. '153d23h46min') into total minutes
const parseTimeSinceToMinutes = (timeSinceStr) => {
  if (!timeSinceStr) return null;
  try {
    const dMatch = timeSinceStr.match(/(\d+)d/);
    const hMatch = timeSinceStr.match(/(\d+)h/);
    const mMatch = timeSinceStr.match(/(\d+)min/);
    const days = dMatch ? parseInt(dMatch[1], 10) : 0;
    const hours = hMatch ? parseInt(hMatch[1], 10) : 0;
    const mins = mMatch ? parseInt(mMatch[1], 10) : 0;
    return days * 24 * 60 + hours * 60 + mins;
  } catch {
    return null;
  }
};

// Map TimeSinceUpdate age (minutes) to color classes
const getTimeSinceColorClass = (timeSinceStr) => {
  const mins = parseTimeSinceToMinutes(timeSinceStr);
  if (mins === null) return "bg-gray-100 text-gray-800 border border-gray-200";
  if (mins < 60) return "bg-green-100 text-green-800 border border-green-200"; // < 1 hour
  if (mins < 1440)
    return "bg-yellow-100 text-yellow-800 border border-yellow-200"; // < 24 hours
  return "bg-red-100 text-red-800 border border-red-200"; // >= 24 hours
};

// Return compact label like '1y ago', '5m ago', '4d ago', '3h ago', '12min ago' from TimeSinceUpdate
const getTimeAgoLabel = (timeSinceStr) => {
  const mins = parseTimeSinceToMinutes(timeSinceStr);
  if (mins === null) return "";
  const minsInYear = 365 * 24 * 60;
  const minsInMonth = 30 * 24 * 60;
  const minsInDay = 24 * 60;
  if (mins >= minsInYear) {
    const y = Math.floor(mins / minsInYear);
    return `${y}y ago`;
  }
  if (mins >= minsInMonth) {
    const m = Math.floor(mins / minsInMonth);
    return `${m}m ago`;
  }
  if (mins >= minsInDay) {
    const d = Math.floor(mins / minsInDay);
    return `${d}d ago`;
  }
  if (mins >= 60) {
    const h = Math.floor(mins / 60);
    return `${h}h ago`;
  }
  return `${mins}min ago`;
};

const fetchStats = async () => {
  try {
    const response = await $fetch(`${apiBase}/stats/`);
    if (response.success) {
      stats.value = response.stats;
    }
  } catch (error) {
    console.error("Error fetching stats:", error);
  }
};

const fetchDevices = async (page = 1) => {
  try {
    const response = await $fetch(
      `${apiBase}/devices/?page=${page}&per_page=50`,
    );
    if (response.success) {
      devices.value = response.data;
      pagination.value = response.pagination;
      lastUpdated.value = new Date().toLocaleString();
    }
  } catch (error) {
    console.error("Error fetching devices:", error);
    showMessage("Error loading device data", "error");
  }
};

const fetchRecentLogs = async () => {
  try {
    const response = await $fetch(`${apiBase}/logs/`);
    if (response.success && response.logs.length > 0) {
      latestLogFile.value = response.logs[0];
    }
  } catch (error) {
    console.error("Error fetching logs:", error);
  }
};

const fetchTrackingData = async () => {
  loading.value.fetch = true;
  try {
    const response = await $fetch(`${apiBase}/fetch-tracking/`, {
      method: "POST",
    });
    if (response.success) {
      showMessage("GPS tracking data fetched successfully!");
      if (response.json_file) {
        latestLogFile.value = {
          folder: response.folder,
          json_file: response.json_file,
        };
      }
      await fetchRecentLogs();
    } else {
      showMessage(response.error || "Error fetching tracking data", "error");
    }
  } catch (error) {
    console.error("Error:", error);
    showMessage("Error fetching tracking data", "error");
  }
  loading.value.fetch = false;
};

const loadToDatabase = async (clearExisting = false) => {
  if (!latestLogFile.value) {
    showMessage("No GPS data file available to load", "error");
    return;
  }

  loading.value.load = true;
  try {
    const response = await $fetch(`${apiBase}/load-database/`, {
      method: "POST",
      body: {
        json_file: latestLogFile.value.json_file,
        clear_existing: clearExisting,
      },
    });
    if (response.success) {
      showMessage(response.message);
      await waitForImport();
    } else {
      showMessage(response.error || "Error loading data to database", "error");
    }
  } catch (error) {
    console.error("Error:", error);
    showMessage("Error loading data to database", "error");
  }
  loading.value.load = false;
};

const waitForImport = async () => {
  const maxAttempts = 180;
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    const status = await $fetch(`${apiBase}/import-status/`);
    if (!status.running) {
      if (status.success) {
        showMessage(`Data loaded successfully. Total records: ${status.total_records}`);
        await Promise.all([fetchStats(), fetchDevices()]);
      } else {
        showMessage(status.error || "Error loading data to database", "error");
      }
      return;
    }
  }
  showMessage("The import is still running. Refresh the dashboard in a moment.");
};

const exportToCsv = async () => {
  loading.value.export = true;
  try {
    // Create a link and trigger download
    const response = await fetch(`${apiBase}/export-csv/`);
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get("Content-Disposition");
      const filename = contentDisposition
        ? contentDisposition.split("filename=")[1].replace(/"/g, "")
        : `gps_tracking_data_${new Date()
            .toISOString()
            .slice(0, 19)
            .replace(/:/g, "-")}.csv`;

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showMessage("CSV file exported successfully!");
    } else {
      showMessage("Error exporting CSV file", "error");
    }
  } catch (error) {
    console.error("Error:", error);
    showMessage("Error exporting CSV file", "error");
  }
  loading.value.export = false;
};

const refreshData = async () => {
  loading.value.refresh = true;
  await Promise.all([
    fetchStats(),
    fetchDevices(pagination.value.current_page),
    fetchRecentLogs(),
  ]);
  showMessage("Data refreshed successfully!");
  loading.value.refresh = false;
};

const nextPage = () => {
  if (pagination.value.has_next) {
    fetchDevices(pagination.value.current_page + 1);
  }
};

const previousPage = () => {
  if (pagination.value.has_previous) {
    fetchDevices(pagination.value.current_page - 1);
  }
};

// Initialize data on mount
onMounted(async () => {
  await Promise.all([fetchStats(), fetchDevices(), fetchRecentLogs()]);
});
</script>
