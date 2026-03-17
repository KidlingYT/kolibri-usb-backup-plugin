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
                  <span class="backup-message">
                    <template v-if="schedule?.last_backup">
                      Backup status: Last successful backup at {{ formatDateTime(schedule.last_backup) }}
                    </template>
                    <template v-else>
                      Backup status: Never backed up
                    </template>
                  </span>
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
            <td>{{ formatDateTime(schedule.last_backup) }}</td>
            <td>{{ formatDateTime(schedule.next_backup) }}</td>
            <td class="button-col" style="display: flex; flex-direction: row; gap: 8px;">
              <KButton icon="edit" text="Edit" @click="editScheduled()" />
              <KButton icon="delete" text="Delete" @click="deleteSchedule()" />
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
        schedule: null,      };
    },
    mounted() {
      // ensure the core loading spinner is turned off when this page mounts
      this.$store.dispatch('notLoading');
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
      }).catch(() => {
        this.schedule = null;
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
        let logMsg = "A backup has been scheduled for: " + (interval?.label || 'Custom frequency');

        const selectedHour = this.timeRequired && this.timeIsSet
          ? `${String(this.selectedTime.hours).padStart(2, '0')}:${String(this.selectedTime.minutes).padStart(2, '0')}`
          : null;
        const selectedDay = this.dayRequired && this.dayIsSet ? this.selectedDay.value : null;

        if (this.schedule) {
          const existingHour = this.schedule.hour ? String(this.schedule.hour).padStart(5, '0') : null;
          const existingDay = this.schedule.day_of_week ?? null;
          const existingFrequency = this.schedule.frequency;
          if (
            existingFrequency === this.selectedItem.value &&
            existingDay === selectedDay &&
            existingHour === selectedHour
          ) {
            console.log('No schedule changes detected. Skipping save.');
            this.showModal = false;
            return;
          }
        }

        // Build payload with only the fields that are actually needed
        const payload = {
          frequency: this.selectedItem.value,
          day_of_week: selectedDay,
          hour: selectedHour,
        };

        if (selectedDay !== null) {
          const day = daysOfWeek[selectedDay];
          logMsg += " on " + this.$formatDate(day.date, { weekday: 'long' });
        }
        if (selectedHour) {
          const [h, m] = selectedHour.split(':').map(Number);
          logMsg += " at " + this.$formatTime(new Date(0, 0, 0, h, m));
        }
        console.log(logMsg);

        client({
          url: urls['kolibri:kolibri_kolibri_usb_backup_plugin_plugin:backup_schedule'](),
          method: 'POST',
          data: payload,
        }).then(({ data }) => {
          // refresh local schedule copy with API response including timestamps
          this.schedule = data;
          this.showModal = false;
        });
      },
      deleteSchedule() {
        if (!this.schedule) {
          return;
        }
        if (!confirm('Delete the scheduled backup? This cannot be undone.')) {
          return;
        }
        client({
          url: urls['kolibri:kolibri_kolibri_usb_backup_plugin_plugin:backup_schedule'](),
          method: 'DELETE',
        }).then(() => {
          this.schedule = null;
          this.showModal = false;
          this.selectedItem = {};
          this.selectedDay = {};
          this.selectedTime = {};
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
      formatDateTime(value) {
        if (!value) return '—';
        const parsed = new Date(value);
        if (Number.isNaN(parsed.getTime())) return '—';
        return parsed.toLocaleString();
      },
      startRestore() {
        this.statusMessage = 'Restore functionality coming soon...';
        this.statusType = 'info';
      },
      editScheduled() {
        console.log('edit');
        this.showModal = true;
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
