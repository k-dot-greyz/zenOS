import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';

interface MasterControlsProps {
  onProcess: () => void;
  onClear: () => void;
  onSave: () => void;
  onLoad: () => void;
  isProcessing: boolean;
  activePluginsCount: number;
}

const MasterControls: React.FC<MasterControlsProps> = ({
  onProcess,
  onClear,
  onSave,
  onLoad,
  isProcessing,
  activePluginsCount,
}) => {
  return (
    <View style={styles.container}>
      {/* Main Process Button */}
      <TouchableOpacity 
        style={[
          styles.processButton,
          activePluginsCount === 0 && styles.disabledButton
        ]}
        onPress={onProcess}
        disabled={isProcessing || activePluginsCount === 0}
        activeOpacity={0.8}
      >
        {isProcessing ? (
          <ActivityIndicator size="small" color="#ffffff" />
        ) : (
          <Text style={styles.processButtonText}>
            {activePluginsCount === 0 ? 'Add Plugins First' : '▶️ Process Chain'}
          </Text>
        )}
      </TouchableOpacity>

      {/* Control Buttons */}
      <View style={styles.controlButtons}>
        <TouchableOpacity 
          style={[styles.controlButton, activePluginsCount === 0 && styles.disabledButton]}
          onPress={onClear}
          disabled={activePluginsCount === 0}
        >
          <Text style={styles.controlButtonText}>🗑️ Clear</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.controlButton} onPress={onSave}>
          <Text style={styles.controlButtonText}>💾 Save</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.controlButton} onPress={onLoad}>
          <Text style={styles.controlButtonText}>📁 Load</Text>
        </TouchableOpacity>
      </View>

      {/* Status Info */}
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>
          {activePluginsCount} plugin{activePluginsCount !== 1 ? 's' : ''} active
        </Text>
        {isProcessing && (
          <Text style={styles.processingText}>Processing...</Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#333333',
  },
  processButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  disabledButton: {
    backgroundColor: '#666666',
    opacity: 0.6,
  },
  processButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  controlButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  controlButton: {
    backgroundColor: '#333333',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    minWidth: 80,
    alignItems: 'center',
  },
  controlButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  statusContainer: {
    alignItems: 'center',
  },
  statusText: {
    color: '#cccccc',
    fontSize: 14,
    marginBottom: 4,
  },
  processingText: {
    color: '#4CAF50',
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default MasterControls;
