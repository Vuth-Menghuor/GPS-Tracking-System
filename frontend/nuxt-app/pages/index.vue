<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50"
  >
    <!-- Header -->
    <header
      class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white"
    >
      <div class="container mx-auto px-6 py-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-4xl font-extrabold flex items-center mb-2">
              <Icon
                name="mdi:map-marker-radius"
                class="mr-3 text-5xl animate-pulse"
              />
              GPS Tracking System
            </h1>
            <p class="text-blue-100 text-lg">
              Real-time device monitoring and management
            </p>
          </div>
          <div class="hidden md:block">
            <div class="text-right">
              <p class="text-sm text-blue-200">Last Sync</p>
              <p class="text-lg font-semibold">{{ lastUpdated || "Never" }}</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-10">
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
        <div
          class="bg-white rounded-lg p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300"
        >
          <div class="flex items-center justify-between">
            <div>
              <p
                class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1"
              >
                Total Devices
              </p>
              <p class="text-4xl font-extrabold text-gray-900">
                {{ stats.total_devices }}
              </p>
            </div>
            <div
              class="p-4 rounded-2xl bg-gradient-to-br from-blue-100 to-blue-200"
            >
              <Icon name="mdi:devices" class="text-4xl text-blue-600" />
            </div>
          </div>
        </div>

        <div
          class="bg-white rounded-lg p-6 border border-gray-200 hover:border-green-300 transition-all duration-300"
        >
          <div class="flex items-center justify-between">
            <div>
              <p
                class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1"
              >
                With GPS
              </p>
              <p class="text-4xl font-extrabold text-gray-900">
                {{ stats.with_coordinates }}
              </p>
            </div>
            <div
              class="p-4 rounded-2xl bg-gradient-to-br from-green-100 to-green-200"
            >
              <Icon
                name="mdi:map-marker-check"
                class="text-4xl text-green-600"
              />
            </div>
          </div>
        </div>

        <div
          class="bg-white rounded-lg p-6 border border-gray-200 hover:border-red-300 transition-all duration-300"
        >
          <div class="flex items-center justify-between">
            <div>
              <p
                class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1"
              >
                No GPS
              </p>
              <p class="text-4xl font-extrabold text-gray-900">
                {{ stats.without_coordinates }}
              </p>
            </div>
            <div
              class="p-4 rounded-2xl bg-gradient-to-br from-red-100 to-red-200"
            >
              <Icon name="mdi:map-marker-off" class="text-4xl text-red-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="bg-white rounded-2xl p-8 mb-10 border border-gray-200">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div class="p-2 rounded-lg bg-blue-100 mr-3">
            <Icon name="mdi:cog" class="text-blue-600 text-xl" />
          </div>
          Quick Actions
        </h2>

        <div class="flex flex-wrap gap-4">
          <button
            class="group bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-blue-300 disabled:to-blue-400 text-white px-8 py-4 rounded-xl flex items-center font-semibold transition-all duration-300 transform hover:-translate-y-0.5"
            :disabled="loading.fetch"
            @click="fetchTrackingData"
          >
            <Icon
              :name="loading.fetch ? 'mdi:loading' : 'mdi:download'"
              :class="{ 'animate-spin': loading.fetch }"
              class="mr-2 text-xl"
            />
            {{ loading.fetch ? "Fetching..." : "Fetch GPS Data" }}
          </button>

          <button
            class="group bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-green-300 disabled:to-green-400 text-white px-8 py-4 rounded-xl flex items-center font-semibold transition-all duration-300 transform hover:-translate-y-0.5"
            :disabled="loading.export"
            @click="exportToCsv"
          >
            <Icon
              :name="loading.export ? 'mdi:loading' : 'mdi:file-export'"
              :class="{ 'animate-spin': loading.export }"
              class="mr-2 text-xl"
            />
            {{ loading.export ? "Exporting..." : "Export to CSV" }}
          </button>

          <button
            class="group bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:from-purple-300 disabled:to-purple-400 text-white px-8 py-4 rounded-xl flex items-center font-semibold transition-all duration-300 transform hover:-translate-y-0.5"
            :disabled="loading.refresh"
            @click="refreshData"
          >
            <Icon
              :name="loading.refresh ? 'mdi:loading' : 'mdi:refresh'"
              :class="{ 'animate-spin': loading.refresh }"
              class="mr-2 text-xl"
            />
            {{ loading.refresh ? "Refreshing..." : "Refresh Data" }}
          </button>
        </div>

        <!-- Load to Database Section -->
        <div
          v-if="latestLogFile"
          class="mt-8 p-6 bg-gradient-to-r from-amber-50 to-yellow-50 border-2 border-amber-200 rounded-xl"
        >
          <div class="flex items-start">
            <div class="p-2 rounded-lg bg-amber-200 mr-3">
              <Icon name="mdi:information" class="text-amber-700 text-xl" />
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-amber-900 mb-1 text-lg">
                Latest GPS Data Available
              </h3>
              <p class="text-sm text-amber-700 mb-4 font-medium">
                {{ latestLogFile.folder }}
              </p>
              <div class="flex gap-3">
                <button
                  class="bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-700 hover:to-yellow-700 disabled:from-amber-300 disabled:to-yellow-300 text-white px-6 py-3 rounded-lg flex items-center font-semibold transition-all duration-300"
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
                  class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-red-300 disabled:to-red-400 text-white px-6 py-3 rounded-lg flex items-center font-semibold transition-all duration-300"
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
      </div>

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
      <div v-if="message.text" class="fixed top-6 right-6 z-50 max-w-md">
        <div
          :class="
            message.type === 'success'
              ? 'bg-gradient-to-r from-green-500 to-green-600'
              : 'bg-gradient-to-r from-red-500 to-red-600'
          "
          class="text-white px-6 py-4 rounded-xl flex items-center border-l-4"
          :style="{
            borderColor: message.type === 'success' ? '#10b981' : '#ef4444',
          }"
        >
          <div class="p-2 rounded-lg bg-white bg-opacity-20 mr-3">
            <Icon
              :name="
                message.type === 'success'
                  ? 'mdi:check-circle'
                  : 'mdi:alert-circle'
              "
              class="text-2xl"
            />
          </div>
          <div class="flex-1">
            <p class="font-semibold">{{ message.text }}</p>
          </div>
          <button
            class="ml-3 hover:bg-white hover:bg-opacity-20 rounded-lg p-1 transition-all"
            @click="message.text = ''"
          >
            <Icon name="mdi:close" class="text-xl" />
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
      await Promise.all([fetchStats(), fetchDevices()]);
    } else {
      showMessage(response.error || "Error loading data to database", "error");
    }
  } catch (error) {
    console.error("Error:", error);
    showMessage("Error loading data to database", "error");
  }
  loading.value.load = false;
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
