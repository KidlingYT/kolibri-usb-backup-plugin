<template>
  <KPageContainer style="margin: 72px 32px;">
    <h1>Backup Volatile Data</h1>

    <table style="width: 100%;">
        <tbody>
          <tr>
            <td>WARNING: This plugin only works on Raspberry Pi devices while an auxiliary MicroSD card is inserted via USB.</td>
          </tr>
          <tr>
            <td>
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
                      Backup PLACEHOLDER status: Never backed up
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
            <td></td> <!-- Spacer -->
            <td
              class="button-col"
            >
              <KButtonGroup style="margin-top: 12px; overflow: visible">
                <KButton
                  appearance="raised-button"
                  :text="'Backup Now'"
                  @click=""
                />
              </KButtonGroup>
            </td>
          </tr>
          <tr>
            <td>
              <h2>Currently Scheduled Backups:</h2>
            </td>
          </tr>
          <tr>
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
          <tr>
            <td>Every Friday at 2:00 p.m.</td>
            <td>02/15/2026 10:45</td>
            <td>02/20/2026 10:45</td>
          </tr>
        </tbody>
      <!-- </template> -->
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
            Server time:
          </p>

          <p class="spacing">
            <KCheckbox
              :checked="retryFlag"
              @change="handleRetryCheckboxChange"
            >
              If scheduled backup fails, keep trying
            </KCheckbox>
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




  <!-- <div>
    <div class="backup-section">
      <h2>Create Backup</h2>
      <p>Export all facility data including users, classes, and learning progress.</p>
      <button class="k-button" @click="startBackup" :disabled="isBackingUp">
        {{ isBackingUp ? 'Backing up...' : 'Start Backup' }}
      </button>
    </div>
  </div> -->
</template>

<script>
  // import { usb, getDeviceList } from 'usb';
  // const devices = getDeviceList();

  // console.log(devices);
  // devices.forEach(device => console.log(device));

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
        showModal: false,
      };
    },
    computed: {
      pageHeight() {
        return {
          height: '80%',
          zIndex: -1,
        };
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
        const day = daysOfWeek[this.selectedDay.value];
        const time = this.selectedTime.hours + ":" + this.selectedTime.minutes;
        console.log("A backup has been scheduled for: " + interval.label + " on " + this.$formatDate(day.date, { weekday: 'long' }) + " at " + time);
        this.showModal = false;
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
    },
  };
</script>

<style lang="scss" scoped>
  /* derived from .core-table-button-col */
  .button-col {
    text-align: right;
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

  .backup-section {
    background: #f5f5f5;
    border-radius: 4px;
    padding: 1rem;
    margin: 1rem 0;
  }

  .k-button {
    background-color: #996189;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    
    &:hover {
      background-color: #7d4f70;
    }
    
    &:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }
  }

  .k-button-secondary {
    background-color: white;
    color: #996189;
    border: 1px solid #996189;
    
    &:hover {
      background-color: #f9f5f8;
    }
  }

  .backup-info {
    margin-top: 1rem;
    padding: 0.5rem;
    background: #e8f5e9;
    border-radius: 4px;
  }

  .status-message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    
    &.info {
      background: #e3f2fd;
      color: #1565c0;
    }
    
    &.success {
      background: #e8f5e9;
      color: #2e7d32;
    }
    
    &.error {
      background: #ffebee;
      color: #c62828;
    }
  }

  .edit-backup-schedule {
    margin-left: 4px;
  }

  .align-kselects {
    margin-left: 16px;
  }
</style>
