<template>
  <AppBarPage
    :title="'Backup Volatile Data'"
    :showNavigation="true"
    :loading="false"
  >
    <template #default="{ pageContentHeight }">
      <KPageContainer>
      <h1>Backup Volatile Data</h1>

      <table style="width: 100%;">
        <tbody>
          <tr>
            <td colspan="3">WARNING: This plugin only works on Raspberry Pi devices while an auxiliary MicroSD card is inserted via USB. You may only have one scheduled backup.</td>
          </tr>
          <tr>
            <td colspan="3">
              <div style="padding: 6px 0; max-width: 400px;">
                <KSelect
                  v-model="selectedDevice"
                  :options="usbDeviceOptions"
                  :label="'Backup Device'"
                  :disabled="loadingDevices"
                />
                <KButton
                  appearance="basic-link"
                  :text="loadingDevices ? 'Scanning...' : 'Refresh Devices'"
                  :disabled="loadingDevices"
                  style="font-size: 13px; margin-top: 4px;"
                  @click="fetchUSBDevices"
                />
              </div>
            </td>
          </tr>
          <tr>
            <td colspan="3">
              <div style="padding: 6px 0;">
                <span>
                  <!-- <template v-if="facility.backingUp || isBackingUp">
                    <KCircularLoader
                      class="loader"
                      :size="16"
                      :delay="false"
                    />
                    Backing Up
                  </template> -->
                  <!-- <template> -->
                    <!-- <span
                      class="backup-message"
                    >
                      Most recent backup failed
                    </span> -->
                    <span
                      class="backup-message"
                    >
                      Backup status: Never backed up
                    </span>
                    <!-- Always show the last successful backup time when available -->
                    <!-- <span
                      class="backup-message"
                    >
                      Last backuped: {{ formattedTime(facility.last_successful_backup) }}
                    </span> -->
                    <!-- <span
                      class="backup-message"
                    >
                      Last backuped: 
                    </span> -->
                  <!-- </template> -->
                </span>
              </div>
            </td>
            <td
              class="button-col"
            >
              <KButtonGroup style="margin-top: 12px; overflow: visible;">
                <KButton
                  appearance="raised-button"
                  :text="'Backup Now'"
                  @click="immediateBackup()"
                />
              </KButtonGroup>
            </td>
          </tr>
          <tr>
            <td>
              <h2>Existing Backup:</h2>
            </td>
          </tr>
          <tr v-if="!schedule">
            <td>
              <KButton
                :text="'Schedule New Backup'"
                :disabled="isBackingUp"
                appearance="basic-link"
                style="font-size: 14px; padding-top: 8px;"
                @click="openModal()"
              />
            </td>
          </tr>
          <tr>
            <td>
              <h3>Frequency</h3>
            </td>
            <td>
              <h3>Last Backup</h3>
            </td>
            <td>
              <h3>Next Backup</h3>
            </td>
          </tr>
          <tr v-if="schedule">
            <td>{{ scheduleDescription }}</td>
            <td>{{ schedule.last_backup || '—' }}</td>
            <td>{{ schedule.next_backup || '—' }}</td>
            <td class="button-col" style="display: flex; flex-direction: row;">
              <KButton icon="edit" text="Edit" @click="editScheduled()" />
            </td>
          </tr>
          <tr v-else>
            <td colspan="4" class="backup-message">No schedule set</td>
          </tr>
        </tbody>
      </table>


      <!-- Scheduling Modal -->
      <KModal
        v-if="showModal"
        :title="'Edit backup schedule'"
        :submitText="'Save'"
        :cancelText="'cancel'"
        @submit="handleSubmit"
        @cancel="closeModal"
      >
        <KGrid
          gutter="48"
          class="edit-backup-schedule"
        >
          <KGrid class="align-kselects">
            <KGrid>
              <KGridItem>
                <KSelect
                  v-model="selectedItem"
                  class="selector"
                  :options="selectArray"
                  :label="'Frequency'"
                  @select="handleUserInput"
                />
              </KGridItem>
            </KGrid>
            <KGrid v-if="dayRequired">
              <KGridItem>
                <KSelect
                  v-model="selectedDay"
                  class="selector"
                  :options="getDays"
                  :label="'Day'"
                  @select="handleUserInput"
                />
              </KGridItem>
            </KGrid>
            <KGrid v-if="timeRequired">
              <KGridItem>
                <KSelect
                  v-model="selectedTime"
                  class="selector"
                  :options="BackupTime"
                  :label="'Time'"
                  @select="handleUserInput"
                />
              </KGridItem>
            </KGrid>
          </KGrid>
          <KGridItem>
            <p class="spacing">
              Server time: {{new Date().toLocaleString()}}
            </p>

            <!-- <p>
              <KButton
                v-if="currentTask"
                appearance="basic-link"
                class="spacing"
                @click="removeDeviceModal = true"
              >
                {{ $tr('removeDeviceLabel') }}
              </KButton>
            </p> -->
          </KGridItem>
        </KGrid>
      </KModal>
    </KPageContainer>
    </template>
  </AppBarPage>
</template>

<script>
  // import BackupResource from 'kolibri-common/apiResources/BackupResource';
  // import { usb, getDeviceList } from 'usb';
  // const devices = getDeviceList();
  import AppBarPage from 'kolibri/components/pages/AppBarPage';
  import { useNav } from 'kolibri/composables/useNav';
  import client from 'kolibri/client';
  import urls from 'kolibri/urls';

  // Database test
  // To save data
//   new_entry = MyPluginData(name="Example Item", description="Plugin info")
//   new_entry.save()

//  // To retrieve data
//   all_items = MyPluginData.objects.all()
//   console.log(all_items);

  // console.log(devices);
  // devices.forEach(device => console.log(device));

/**
 * Trigger an immediate one-off backup for a facility.
 * @param {string} facilityId
 * @returns {Promise<{job_id: string}>}
 */
function runBackup() {
  console.log(urls);
  // const url = '/run_backup';
  // return fetch({ url, method: 'post', data: {} }).then(
  //   response => response.data,
  // );
  return client({
    url: urls['kolibri:kolibri_kolibri_usb_backup_plugin_plugin:run_backup'](),
    method: 'POST'
  }).then(({ data }) => {
    return data.status;
  });
}

  const oneHour = 60 * 60;
  const oneDay = oneHour * 24;
  const oneWeek = oneDay * 7;
  const twoWeeks = oneWeek * 2;
  const oneMonth = oneWeek * 4;
  
  const today = new Date();
  const daysOfWeek = [];
  const date = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate() + (7 - today.getDay()),
  );
  for (let i = 0; i < 7; i++) {
    daysOfWeek.push({ value: i, date: new Date(date) });
    date.setDate(date.getDate() + 1);
  }
  const endTime = new Date();
  endTime.setHours(24, 0, 0, 0);
  const interval = 30;
  const times = [];
  var i = 0;
  const time = new Date();
  time.setHours(0, 0, 0, 0);
  while (time < endTime) {
    times.push({ value: i++, time: new Date(time) });
    time.setMinutes(time.getMinutes() + interval);
  }
  export default {
    name: 'KolibriUsbBackupPluginPluginIndex',
    components: { AppBarPage },
    data() {
      return {
        isBackingUp: false,
        lastBackupDate: null,
        statusMessage: '',
        statusType: '',
        userHasEdited: false,
        now: null,
        selectedItem: {},
        selectedDay: {},
        selectedTime: {},
        retryFlag: false,
        serverTimeInterval: null,
        deviceId: null,
        facilityId: null,
        tasks: null,
        showModal: false,        // schedule object fetched from backend
        schedule: null,
        usbDevices: [],
        selectedDevice: {},
        loadingDevices: false,
      };
    },
    mounted() {
      // ensure the core loading spinner is turned off when this page mounts
      this.$store.dispatch('notLoading');
      this.fetchUSBDevices();
      client({
        url: urls['kolibri:kolibri_kolibri_usb_backup_plugin_plugin:backup_schedule'](),
        method: 'GET',
      }).then(({ data }) => {
        // cache schedule for table rendering
        this.schedule = data;
        if (data.frequency) {
          // populate the selects exactly the way the watcher on currentTask used to
          this.selectedItem = this.selectArray.find(i => i.value === data.frequency) || {};
          if (data.day_of_week !== null) {
            this.selectedDay = this.getDays.find(d => d.value === data.day_of_week) || {};
          }
          if (data.hour) {
            const [h, m] = data.hour.split(':').map(Number);
            this.selectedTime = this.BackupTime.find(t => t.hours === h && t.minutes === m) || {};
          }
        }
      });
    },
    computed: {
      pageHeight() {
        return {
          height: '80%',
          zIndex: -1,
        };
      },
      // human-readable description of the current schedule
      scheduleDescription() {
        if (!this.schedule || !this.schedule.frequency) return '';
        let desc = '';
        const freq = this.selectArray.find(i => i.value === this.schedule.frequency);
        if (freq) {
          desc = freq.label;
        } else {
          desc = `${this.schedule.frequency} hrs`;
        }
        if (this.schedule.day_of_week !== null && this.schedule.day_of_week !== undefined) {
          const day = this.getDays.find(d => d.value === this.schedule.day_of_week);
          if (day) {
            desc += ` on ${day.label}`;
          }
        }
        if (this.schedule.hour) {
          const [h, m] = this.schedule.hour.split(':').map(Number);
          const dt = new Date();
          dt.setHours(h, m);
          desc += ` at ${this.$formatTime(dt)}`;
        }
        return desc;
      },
      usbDeviceOptions() {
        if (this.loadingDevices) {
          return [{ label: 'Scanning for devices...', value: null }];
        }
        if (this.usbDevices.length === 0) {
          return [{ label: 'No USB devices detected', value: null }];
        }
        return this.usbDevices.map(device => ({
          label: device.label,
          value: device.path,
        }));
      },
      selectArray() {
        return [
          { label: 'Every hour', value: oneHour },
          { label: 'Every day', value: oneDay },
          { label: 'Every week', value: oneWeek },
          { label: 'Every two weeks', value: twoWeeks },
          { label: 'Every month', value: oneMonth },
        ];
      },
      getDays() {
        return daysOfWeek.map(day => {
          return {
            label: this.$formatDate(day.date, { weekday: 'long' }),
            value: day.value,
          };
        });
      },
      BackupTime() {
        return times.map(time => {
          return {
            label: this.$formatTime(time.time),
            value: time.value,
            hours: time.time.getHours(),
            minutes: time.time.getMinutes(),
          };
        });
      },
      // filteredTasks() {
      //   return this.tasks ? this.tasks.filter(
      //     task =>
      //       (this.isKdp || task.extra_metadata.device_id === this.device?.id) &&
      //       task.facility_id === this.facilityId &&
      //       task.type === this.taskType &&
      //       // Only show tasks that are repeating indefinitely
      //       task.repeat === null,
      //   ) : [];
      // },
      // currentTask() {
      //   return this.filteredTasks.length ? this.filteredTasks[0] : null;
      // },
      // currentTaskRunning() {
      //   return this.currentTask?.status === TaskStatuses.RUNNING;
      // },
      timeRequired() {
        return this.selectedItem.value > oneHour;
      },
      timeIsSet() {
        return this.selectedTime && times[this.selectedTime.value];
      },
      dayRequired() {
        return this.selectedItem.value > oneDay;
      },
      dayIsSet() {
        return this.selectedDay && daysOfWeek[this.selectedDay.value];
      },
      isKdp() {
        return this.deviceId === KDP_ID;
      },
      taskType() {
        return this.isKdp ? TaskTypes.SYNCDATAPORTAL : TaskTypes.SYNCPEERFULL;
      },
      // saveDisabled() {
      //   return (
      //     this.currentTaskRunning ||
      //     (!this.timeIsSet && this.timeRequired) ||
      //     (!this.dayIsSet && this.dayRequired) ||
      //     !this.selectedItem.value
      //   );
      // },
    },
    watch: {
      // currentTask() {
      //   console.log("1");
      //   // if (this.currentTask && !this.userHasEdited) {
      //   if (!this.userHasEdited) {
      //     console.log("2");
      //     const enqueueAt = new Date(Date.parse(this.currentTask.scheduled_datetime));
      //     const day = enqueueAt.getDay();
      //     const hours = enqueueAt.getHours();
      //     const minutes = enqueueAt.getMinutes();
      //     this.selectedItem =
      //       this.selectArray.find(item => item.value === this.currentTask.repeat_interval) || {};
      //     this.selectedDay = this.getDays.find(item => item.value === day) || {};
      //     for (const time of this.BackupTime) {
      //       // Because there can be some drift in the task scheduling process,
      //       // we round the 'scheduled' time to the nearest 30 minutes
      //       if (
      //         time.minutes === 0 &&
      //         ((time.hours === hours && minutes < 15) ||
      //           (time.hours === hours + 1 && minutes >= 45))
      //       ) {
      //         this.selectedTime = time;
      //         break;
      //       }
      //       if (time.minutes === 30 && time.hours === hours && minutes >= 15 && minutes < 45) {
      //         this.selectedTime = time;
      //         break;
      //       }
      //     }
      //     this.retryFlag = Boolean(this.currentTask.retry_interval);
      //   }
      // },
    },
    beforeDestroy() {
      clearInterval(this.serverTimeInterval);
    },
    methods: {
      startBackup() {
        this.isBackingUp = true;
        this.statusMessage = 'Creating backup...';
        this.statusType = 'info';
        
        // Simulate backup process
        setTimeout(() => {
          this.isBackingUp = false;
          this.lastBackupDate = new Date().toLocaleString();
          this.statusMessage = 'Backup completed successfully!';
          this.statusType = 'success';
        }, 2000);
      },
      handleSubmit() {
        const interval = this.selectArray.find((item) => item.value === this.selectedItem.value);
        let logMsg = "A backup has been scheduled for: " + interval.label;
        
        // Build payload with only the fields that are actually needed
        const payload = {
          frequency: this.selectedItem.value,
        };
        
        // Only include day_of_week if this frequency requires it
        if (this.dayRequired && this.dayIsSet) {
          const day = daysOfWeek[this.selectedDay.value];
          payload.day_of_week = this.selectedDay.value;
          logMsg += " on " + this.$formatDate(day.date, { weekday: 'long' });
        } else {
          payload.day_of_week = null;
        }
        
        // Only include hour if this frequency requires it
        if (this.timeRequired && this.timeIsSet) {
          payload.hour = `${this.selectedTime.hours}:${this.selectedTime.minutes}`;
          logMsg += " at " + this.$formatTime(new Date(0, 0, 0, this.selectedTime.hours, this.selectedTime.minutes));
        } else {
          payload.hour = null;
        }
        
        console.log(logMsg);

        client({
          url: urls['kolibri:kolibri_kolibri_usb_backup_plugin_plugin:backup_schedule'](),
          method: 'POST',
          data: payload,
        }).then(({ data }) => {
          // refresh the local schedule copy (server might add timestamps)
          this.schedule = payload;
          // optionally merge any returned fields if server returns them
          if (data) {
            Object.assign(this.schedule, data);
          }
          this.showModal = false;
        });
      },
      immediateBackup() {
        
        // Close any open modal and trigger the server-side run-backup endpoint.
        this.closeModal();

        runBackup()
          .then(response => console.log(response));

      },
      handleUserInput() {
        this.userHasEdited = true;
      },
      handleRetryCheckboxChange() {
        this.retryFlag = !this.retryFlag;
        this.handleUserInput();
      },
      openModal() {
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;
      },
      startRestore() {
        this.statusMessage = 'Restore functionality coming soon...';
        this.statusType = 'info';
      },
      editScheduled() {
        console.log('edit');
        this.showModal = true;
      },
      fetchUSBDevices() {
        this.loadingDevices = true;
        client({
          url: urls['kolibri:kolibri_kolibri_usb_backup_plugin_plugin:detect_usb'](),
          method: 'GET',
        }).then(({ data }) => {
          this.usbDevices = data.devices || [];
          if (this.usbDevices.length > 0) {
            this.selectedDevice = {
              label: this.usbDevices[0].label,
              value: this.usbDevices[0].path,
            };
          } else {
            this.selectedDevice = {};
          }
        }).catch((err) => {
          console.error('Failed to detect USB devices:', err);
          this.usbDevices = [];
          this.selectedDevice = {};
        }).finally(() => {
          this.loadingDevices = false;
        });
      },
    },
  };
</script>

<style lang="scss" scoped>
  .button-col {
    text-align: center;
  }
  .loader {
    top: 3px;
    display: inline-block;
    margin-right: 8px;
  }
  /deep/ .button-group-item {
    height: max-content;
    margin-bottom: 8px;
  }
  .name {
    display: inline-block;
    margin: 8px 0;
    margin-left: 0;
  }
  .backup-message {
    display: block;
    font-size: 14px;
  }
  .selector {
    border-radius: 5px 5px 0px 0px;
    padding-top: 5px;
    padding-left: 5px;
    width: 300px;
    margin-left: 16px;
  }





  h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  h2 {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }

  .edit-backup-schedule {
    margin-left: 4px;
  }

  .align-kselects {
    margin-left: 16px;
  }
</style>
