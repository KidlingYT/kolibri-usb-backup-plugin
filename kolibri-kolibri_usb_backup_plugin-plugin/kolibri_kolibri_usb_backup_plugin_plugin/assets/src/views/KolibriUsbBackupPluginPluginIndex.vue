<template>
  <div>
    <h1>USB Backup</h1>
    <p>Back up your facility data to a USB drive for safekeeping.</p>

    <div class="backup-section">
      <h2>Create Backup</h2>
      <p>Export all facility data including users, classes, and learning progress.</p>
      <button class="k-button" @click="startBackup" :disabled="isBackingUp">
        {{ isBackingUp ? 'Backing up...' : 'Start Backup' }}
      </button>
    </div>

    <div class="backup-section">
      <h2>Restore from Backup</h2>
      <p>Restore facility data from a previous USB backup.</p>
      <button class="k-button k-button-secondary" @click="startRestore">
        Select Backup File
      </button>
    </div>

    <div v-if="lastBackupDate" class="backup-info">
      <p>Last backup: {{ lastBackupDate }}</p>
    </div>

    <div v-if="statusMessage" class="status-message" :class="statusType">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
  export default {
    name: 'KolibriUsbBackupPluginPluginIndex',
    data() {
      return {
        isBackingUp: false,
        lastBackupDate: null,
        statusMessage: '',
        statusType: '',
      };
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
      startRestore() {
        this.statusMessage = 'Restore functionality coming soon...';
        this.statusType = 'info';
      },
    },
  };
</script>

<style lang="scss" scoped>
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
</style>

<script>
  export default {
    name: 'KolibriUsbBackupPluginPluginIndex',
    // mounted() {
    //   console.log('USB Backup Plugin: Component mounted successfully');
    // },
  };
</script>

