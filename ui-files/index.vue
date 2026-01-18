# File path: kolibri/plugins/facility/assets/src/views/DataPage/BackupInterface/index.vue

<template>
  <KPageContainer :style="containerStyle">
    <h1>{{ $tr('backupData') }}</h1>

    <CoreTable>
      <template #headers>
        <th>{{ $tr('facility') }}</th>
      </template>
      <template #tbody>
        <tbody>
          <tr v-if="facility">
            <td>
              <div>
                <h2 class="name">
                  <KLabeledIcon icon="facility">
                    {{ facility.name }}
                    <template #iconAfter>
                      <KIcon
                        v-if="facility.dataset.registered"
                        ref="icon"
                        icon="registered"
                        :style="{ fill: $themeTokens.success }"
                      />
                    </template>
                  </KLabeledIcon>
                  <KTooltip
                    reference="icon"
                    :refs="$refs"
                  >
                    {{ $tr('registeredAlready') }}
                  </KTooltip>
                </h2>
              </div>
              <div>
                <span>
                  <template v-if="facility.backingUp || isBackingUp">
                    <KCircularLoader
                      class="loader"
                      :size="16"
                      :delay="false"
                    />
                    {{ $tr('backingUp') }}
                  </template>
                  <template v-else>
                    <span
                      v-if="backupFailed"
                      class="backup-message"
                    >
                      {{ $tr('backupFailed') }}
                    </span>
                    <span
                      v-else-if="neverBackedUp"
                      class="backup-message"
                    >
                      {{ $tr('neverBackedUp') }}
                    </span>
                    <!-- Always show the last successful backup time when available -->
                    <span
                      v-if="facility.last_successful_backup"
                      class="backup-message"
                    >
                      {{ $tr('lastbackup', { relativeTime: formattedTime(facility.last_successful_backup) }) }}
                    </span>
                  </template>
                  <KButton
                    :text="$tr('createBackup')"
                    :disabled="isBackingUp"
                    appearance="basic-link"
                    @click="displayModal(Modals.BACKUP_FACILITY)"
                  />
                </span>
              </div>
            </td>
            <td
              :style="tableCellStyle"
              class="button-col"
            >
              <KButtonGroup style="margin-top: 12px; overflow: visible">
                <KButton
                  appearance="raised-button"
                  :text="$tr('backup')"
                  :disabled="isBackingUp"
                  @click=""
                />
              </KButtonGroup>
            </td>
          </tr>
        </tbody>
      </template>
    </CoreTable>

    <RegisterFacilityModal
      v-if="modalShown === Modals.REGISTER_FACILITY"
      :displaySkipOption="false"
      @success="handleValidateSuccess"
      @cancel="closeModal"
      @skip="handleKDPbackup"
    />
    <ConfirmationRegisterModal
      v-if="modalShown === Modals.CONFIRMATION_REGISTER"
      :targetFacility="facility"
      :projectName="kdpProject.name"
      :token="kdpProject.token"
      @success="handleConfirmationSuccess"
      @cancel="closeModal"
    />

    <ScheduleBackupModal
      v-if="modalShown === Modals.BACKUP_FACILITY"
      :formDisabled="backupSubmitDisabled"
      @submit="scheduleBackup"
      @cancel="closeModal"
    />

  </KPageContainer>

</template>


<script>
  import useNow from 'kolibri/composables/useNow';
  import taskStrings from 'kolibri-common/uiText/tasks';
  import CoreTable from 'kolibri/components/CoreTable';
  import ConfirmationRegisterModal from 'kolibri-common/components/syncComponentSet/ConfirmationRegisterModal';
  import RegisterFacilityModal from 'kolibri-common/components/syncComponentSet/RegisterFacilityModal';
  import commonsyncElements from 'kolibri-common/mixins/commonSyncElements';
  import useKResponsiveWindow from 'kolibri-design-system/lib/composables/useKResponsiveWindow';
  import TaskResource from 'kolibri/apiResources/TaskResource';
  import FacilityResource from 'kolibri-common/apiResources/FacilityResource';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import { TaskStatuses } from 'kolibri-common/utils/syncTaskUtils';
  import { syncPageNames } from 'kolibri-common/components/SyncSchedule/constants';
  import ScheduleBackupModal from 'kolibri-common/components/backupComponentSet/ScheduleBackupModal';
  const Modals = Object.freeze({
    BACKUP_FACILITY: 'BACKUP_FACILITY',
    CONFIRMATION_REGISTER: 'CONFIRMATION_REGISTER',
    REGISTER_FACILITY: 'REGISTER_FACILITY'
  });
  export default {
    name: 'BackupInterface',
    components: {
      CoreTable,
      RegisterFacilityModal,
      ConfirmationRegisterModal,
      ScheduleBackupModal,
    },
    mixins: [taskStrings, commonsyncElements, commonCoreStrings],
    setup() {
      const { windowIsLarge, windowIsMedium, windowIsSmall } = useKResponsiveWindow();
      const { now } = useNow();
      return {
        windowIsLarge,
        windowIsMedium,
        windowIsSmall,
        now,
      };
    },
    data() {
      return {
        facility: null,
        kdpProject: null, // { name, token }
        modalShown: null,
        backupTaskId: '',
        isBackingUp: false,
        backupHasFailed: false,
        Modals,
        isMenuOpen: false,
        backupSubmitDisabled: false,
      };
    },
    computed: {
      managebackupRoute() {
        return {
          name: syncPageNames.MANAGE_backup_SCHEDULE,
          params: {
            facility_id: this.facility.id,
          },
        };
      },
      containerStyle() {
        if (this.windowIsMedium || this.windowIsLarge) {
          return {
            height: '300px',
            overflow: 'visible',
            marginBottom: '24px',
          };
        }
        return {
          marginBottom: '24px',
        };
      },
      tableCellStyle() {
        if (this.windowIsSmall || this.windowIsMedium) {
          return {
            padding: '8px 4px 4px',
            maxWidth: '180px',
          };
        } else {
          return {
            maxWidth: '100px',
          };
        }
      },
      backupFailed() {
        const lastbackupFailed =
          this.facility &&
          this.facility.last_successful_backup &&
          this.facility.last_failed_backup &&
          new Date(this.facility.last_successful_backup).getTime() <
          new Date(this.facility.last_failed_backup).getTime();
        return this.backupTaskHasFailed || lastbackupFailed;
      },
      neverBackedUp() {
        return (
          this.facility && !this.facility.last_successful_backup && !this.facility.last_failed_backup
        );
      },
    },
    beforeMount() {
      this.fetchFacility();
    },
    beforeDestroy() {
      this.backupTaskId = '';
    },
    methods: {
      formattedTime(datetime) {
        if (this.now - new Date(datetime) < 10000) {
          return this.coreString('justNow');
        }
        return this.$formatRelative(datetime, { now: this.now });
      },
      manageBackup() {
        this.$router.push(this.goToRoute);
      },
      managebackupAction() {
        this.$router.push(this.managebackupRoute);
      },
      fetchFacility() {
        FacilityResource.fetchModel({ id: this.$store.getters.activeFacilityId, force: true }).then(
          facility => {
            this.facility = { ...facility };
          },
        );
      },
      closeModal() {
        this.modalShown = null;
      },
      displayModal(modal) {
        this.modalShown = modal;
      },
      pollbackupTask() {
        // Like facilityTaskQueue, just keep polling until component is destroyed
        TaskResource.get(this.backupTaskId).then(task => {
          if (task.clearable) {
            this.isBackingUp = false;
            TaskResource.clear(this.backupTaskId);
            this.backupTaskId = '';
            if (task.status === TaskStatuses.FAILED) {
              this.backupHasFailed = true;
            } else if (task.status === TaskStatuses.COMPLETED) {
              this.fetchFacility();
            }
          } else if (this.backupTaskId) {
            setTimeout(() => {
              this.pollbackupTask();
            }, 2000);
          }
        });
      },
      handleValidateSuccess({ name, token }) {
        this.kdpProject = { name, token };
        this.displayModal(Modals.CONFIRMATION_REGISTER);
      },
      handleConfirmationSuccess(payload) {
        this.$store.commit('manageCSV/SET_REGISTERED', payload);
        this.facility.dataset.registered = true;
        this.closeModal();
      },
      handlebackupFacilitySuccess(taskId) {
        this.isBackingUp = true;
        this.backupTaskId = taskId;
        this.pollbackupTask();
      },
      handlebackupFacilityFailure() {
        this.backupHasFailed = true;
      },
      handleRegister() {
        this.closeMenu();
        this.displayModal(Modals.REGISTER_FACILITY);
      },
      handleKDPBackup() {
        this.closeModal();
        this.startKdpbackupTask(this.facility.id)
          .then(task => {
            this.handlebackupFacilitySuccess(task.id);
          })
          .catch(() => {
            this.handlebackupFacilityFailure();
          });
      },
      closeMenu({ focusMoreOptionsButton = true } = {}) {
        this.isMenuOpen = false;
        if (!focusMoreOptionsButton) {
          return;
        }
        this.$nextTick(() => {
          this.$refs.moreOptionsButton.$el.focus();
        });
      },
      toggleMenu() {
        this.isMenuOpen = !this.isMenuOpen;
        if (!this.isMenuOpen) {
          return;
        }
        this.$nextTick(() => {
          this.$refs.menu.$el.focus();
        });
      },
      findFirstEl() {
        this.$nextTick(() => {
          this.$refs.menu.focusFirstEl();
        });
      },
      scheduleBackup() {
        this.closeModal();
        console.log('Scheduled');
      },
    },
    $trs: {
      backupData: {
        message: 'Backup Volatile Data',
        context:
          'Option to schedule a recurring backup of data changes.',
      },
      facility: {
        message: 'Facility',
        context: "Refers to the facility on the 'backup Facility Data' window.",
      },
      register: {
        message: 'Register',
        context: 'Describes the button to register a new facility.',
      },
      backup: {
        message: 'Backup Now',
        context:
          "Describes the 'backup' button which is used to store volatile data from a facility within an external data store.",
      },
      registeredAlready: {
        message: 'Registered to `Kolibri Data Portal`',
        context:
          'If a Kolibri facility is part of a larger organization that tracks data on the Kolibri Data Portal,  it can be registered to the Kolibri Data Portal.\n\nThis text indicates that the facility has been registered to the Data Portal.',
      },
      neverBackedUp: {
        message: 'Never backed up',
        context:
          'This is associated with the label "Last successful backup:", and the subject is the Facility.',
      },
      /* eslint-disable kolibri/vue-no-unused-translations */
      nextbackup: {
        message: 'Next backup: {relativeTime}',
        context:
          'Used to indicate the next scheduled backup of facility data. For example, "in 5 days".\'\n',
      },
      /* eslint-enable kolibri/vue-no-unused-translations */
      lastbackup: {
        message: 'Last backuped: {relativeTime}',
        context:
          'Used to indicate a time period when the last backup took place. For example, the value of last successful backup could be something like "2 months ago".\'\n',
      },
      backupFailed: {
        message: 'Most recent backup failed',
        context:
          'This text will display under the name of the facility in Device > FACILITIES section if the most recent attempt at backuping has been unsuccessful.',
      },
      backingUp: {
        message: 'Backing Up',
        context: 'Indicates when a backup process is in progress.',
      },
      createBackup: {
        message: 'Create backup schedule',
        context: 'Link to create backup schedule',
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
  }
</style>
