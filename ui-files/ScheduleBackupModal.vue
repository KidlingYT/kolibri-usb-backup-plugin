# File path: packages/kolibri-common/components/backupComponentSet/ScheduleBackupModal.vue

<template>

  <KModal
    :title="$tr('editBackupScheduleTitle')"
    :submitText="$tr('submitButtonLabel')"
    :cancelText="$tr('cancelButtonLabel')"
    @submit="handleSubmit"
    @cancel="$emit('cancel')"
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
              :disabled="currentTaskRunning"
              :style="selectorStyle"
              :options="selectArray"
              :label="$tr('frequency')"
              @select="handleUserInput"
            />
          </KGridItem>
        </KGrid>
        <KGrid v-if="dayRequired">
          <KGridItem>
            <KSelect
              v-model="selectedDay"
              class="selector"
              :disabled="currentTaskRunning"
              :style="selectorStyle"
              :options="getDays"
              :label="$tr('day')"
              @select="handleUserInput"
            />
          </KGridItem>
        </KGrid>
        <KGrid v-if="timeRequired">
          <KGridItem>
            <KSelect
              v-model="selectedTime"
              class="selector"
              :disabled="currentTaskRunning"
              :style="selectorStyle"
              :options="BackupTime"
              :label="$tr('time')"
              @select="handleUserInput"
            />
          </KGridItem>
        </KGrid>
      </KGrid>
      <KGridItem>
        <p class="spacing">
          {{ $tr('serverTime') }}
          {{
            $formatTime(now, {
              year: 'numeric',
              month: 'numeric',
              day: 'numeric',
              hour: 'numeric',
              minute: 'numeric',
              second: 'numeric',
            })
          }}
        </p>

        <p class="spacing">
          <KCheckbox
            :checked="retryFlag"
            :disabled="currentTaskRunning"
            @change="handleRetryCheckboxChange"
          >
            {{ $tr('checkboxLabel') }}
          </KCheckbox>
        </p>
        <p>
          <KButton
            v-if="currentTask"
            :disabled="currentTaskRunning"
            appearance="basic-link"
            class="spacing"
            @click="removeDeviceModal = true"
          >
            {{ $tr('removeDeviceLabel') }}
          </KButton>
        </p>
      </KGridItem>
    </KGrid>
  </KModal>

</template>


<script>
  import { now } from 'kolibri/utils/serverClock';
  import { TaskStatuses, TaskTypes } from 'kolibri-common/utils/syncTaskUtils';
  import { KDP_ID, oneHour, oneDay, oneWeek, twoWeeks, oneMonth } from '../SyncSchedule/constants';
  import TaskResource from 'kolibri/apiResources/TaskResource';
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
    name: 'ScheduleBackupModal',
    components: {},
    data() {
      return {
        initialDelay: true, // hide everything for a second to prevent flicker
        formIsDisabled: true,
        portalIsOffline: false,
        userHasEdited: false,
        now: null,
        selectedItem: {},
        selectedDay: {},
        selectedTime: {},
        removeDeviceModal: false,
        retryFlag: false,
        device: null,
      };
    },
    computed: {
      pageHeight() {
        return {
          height: '80%',
          zIndex: -1,
        };
      },
      selectorStyle() {
        return {
          borderRadius: '5px 5px 0px 0px',
          paddingTop: '5px',
          paddingLeft: '5px',
          width: '300px',
          marginLeft: '16px',
        };
      },
      selectArray() {
        return [
          { label: this.$tr('everyHour'), value: oneHour },
          { label: this.$tr('everyDay'), value: oneDay },
          { label: this.$tr('everyWeek'), value: oneWeek },
          { label: this.$tr('everyTwoWeeks'), value: twoWeeks },
          { label: this.$tr('everyMonth'), value: oneMonth },
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
      filteredTasks() {
        return this.tasks ? this.tasks.filter(
          task =>
            (this.isKdp || task.extra_metadata.device_id === this.device?.id) &&
            task.facility_id === this.facilityId &&
            task.type === this.taskType &&
            // Only show tasks that are repeating indefinitely
            task.repeat === null,
        ) : [];
      },
      currentTask() {
        return this.filteredTasks.length ? this.filteredTasks[0] : null;
      },
      currentTaskRunning() {
        return this.currentTask?.status === TaskStatuses.RUNNING;
      },
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
      saveDisabled() {
        return (
          this.currentTaskRunning ||
          (!this.timeIsSet && this.timeRequired) ||
          (!this.dayIsSet && this.dayRequired) ||
          !this.selectedItem.value
        );
      },
    },
    created() {
      setTimeout(() => {
        this.initialDelay = false;
      }, 1000);
      // TODO Check to see if KDP is online
      Promise.resolve().then(() => {
        this.portalIsOffline = false;
        this.formIsDisabled = false;
      });
    },
    watch: {
      currentTask() {
        if (this.currentTask && !this.userHasEdited) {
          const enqueueAt = new Date(Date.parse(this.currentTask.scheduled_datetime));
          const day = enqueueAt.getDay();
          const hours = enqueueAt.getHours();
          const minutes = enqueueAt.getMinutes();
          this.selectedItem =
            this.selectArray.find(item => item.value === this.currentTask.repeat_interval) || {};
          this.selectedDay = this.getDays.find(item => item.value === day) || {};
          for (const time of this.BackupTime) {
            // Because there can be some drift in the task scheduling process,
            // we round the 'scheduled' time to the nearest 30 minutes
            if (
              time.minutes === 0 &&
              ((time.hours === hours && minutes < 15) ||
                (time.hours === hours + 1 && minutes >= 45))
            ) {
              this.selectedTime = time;
              break;
            }
            if (time.minutes === 30 && time.hours === hours && minutes >= 15 && minutes < 45) {
              this.selectedTime = time;
              break;
            }
          }
          this.retryFlag = Boolean(this.currentTask.retry_interval);
        }
      },
    },
    created() {
      this.now = now();
      this.serverTimeInterval = setInterval(() => {
        this.now = now();
      }, 10000);
    },
    beforeDestroy() {
      clearInterval(this.serverTimeInterval);
    },
    methods: {
      closeModal() {
        this.removeDeviceModal = false;
      },
      handleSubmit() {
        const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        const interval = this.selectArray.find((item) => item.value === this.selectedItem.value);
        const day = daysOfWeek[this.selectedDay.value];
        const time = this.selectedTime.hours + ":" + this.selectedTime.minutes;
        console.log("A backup has been scheduled for: " + interval.label + " on " + day + " at " + time);
        this.$emit('submit')
      },
      handleDeleteDevice() {
        this.removeDeviceModal = false;
        TaskResource.deleteModel({ id: this.currentTask.id })
          .then(() => {
            this.showSnackbarNotification('deviceRemove');
            this.goBack();
          })
          .catch(() => {
            this.showSnackbarNotification('deviceNotRemove');
          });
      },
      computeNextBackup() {
        const date = new Date(this.now);
        if (this.timeRequired) {
          if (!this.timeIsSet) {
            throw new ReferenceError('Time is not set and is required');
          }
          const hours = this.selectedTime.hours;
          const minutes = this.selectedTime.minutes;
          if (
            hours < date.getHours() ||
            (hours === date.getHours() && minutes < date.getMinutes())
          ) {
            date.setDate(date.getDate() + 1);
          }
          date.setHours(hours);
          date.setMinutes(minutes);
        }
        if (this.dayRequired) {
          if (!this.dayIsSet) {
            throw new ReferenceError('Day is not set and is required');
          }
          const diff = this.selectedDay.value - date.getDay();
          if (date.getDay() > this.selectedDay.value) {
            date.setDate(date.getDate() + 7 - Math.abs(diff));
          } else if (date.getDay() < this.selectedDay.value) {
            date.setDate(date.getDate() + Math.abs(diff));
          }
        }
        return date;
      },
      handleSaveSchedule() {
        const enqueue_param = this.computeNextBackup().toISOString();
        const enqueue_args = {
          enqueue_at: enqueue_param,
          repeat_interval: this.selectedItem.value,
          repeat: null,
          retry_interval: this.retryFlag ? 60 * 5 : null,
        };
        let promise;
        if (this.currentTask) {
          promise = TaskResource.saveModel({
            id: this.currentTask.id,
            data: { enqueue_args },
            exists: true,
          });
        } else {
          const taskParams = {
            type: this.taskType,
            facility: this.facilityId,
            enqueue_args,
          };
          if (!this.isKdp) {
            taskParams.device_id = this.deviceId;
            taskParams.baseurl = this.device.base_url;
          }
          promise = TaskResource.startTask(taskParams);
        }
        promise
          .then(() => {
            this.goBack();
            if (this.currentTask) {
              // the backup schedule has already been created and we are editing it
              this.showSnackbarNotification('backupUpdated');
            } else {
              this.showSnackbarNotification('backupAdded');
            }
          })
          .catch(() => {
            this.createTaskFailedSnackbar();
          });
      },
      goBack() {
        this.$router.push(this.goBackRoute);
      },
      handleUserInput() {
        this.userHasEdited = true;
      },
      handleRetryCheckboxChange() {
        this.retryFlag = !this.retryFlag;
        this.handleUserInput();
      },
    },
    $trs: {
        editBackupScheduleTitle: {
          message: 'Edit backup schedule',
          context: 'Title for the edit backup schedule modal',
        },
        frequency: {
          message: 'Frequency',
          context: 'Indicates how often the scheduled backup occurs',
        },
        day: {
          message: 'Day',
          context: 'Indicates the day of the week on which the scheduled backup occurs',
        },
        time: {
          message: 'Time',
          context: 'Indicates the time of day at which the scheduled backup occurs',
        },
        serverTime: {
          message: 'Server time:',
          context: 'Server time label',
        },
        checkboxLabel: {
          message: 'If scheduled backup fails, keep trying',
          context: 'Label for checkbox',
        },
        removeDeviceLabel: {
          message: 'Remove backup schedule',
          context: 'Button label for removing the backup schedule',
        },
        submitButtonLabel: {
          message: 'Save',
          context: 'Schedule the backup per the info in the fields',
        },
        cancelButtonLabel: {
          message: 'Cancel',
          context: 'Close the schedule modal',
        },
        NoBackup: {
          message: 'There are no backups scheduled',
          context: 'Text to display when there is no schedule backup to be managed.',
        },
        everyHour: {
          message: 'Every hour',
          context: 'Period for scheduling the backup every hour',
        },
        everyDay: {
          message: 'Every day',
          context: 'Period for scheduling the backup every day',
        },
        everyWeek: {
          message: 'Every week',
          context: 'Period for scheduling the backup every week',
        },
        everyMonth: {
          message: 'Every month',
          context: 'Period for scheduling the backup every month',
        },
        everyTwoWeeks: {
          message: 'Every two weeks',
          context: 'Period for scheduling the backup every two weeks',
        },
    },
  };
</script>
<style lang="scss" scoped>
  .edit-backup-schedule {
    margin-left: 4px;
  }
  .align-kselects {
    margin-left: 16px;
  }
</style>
