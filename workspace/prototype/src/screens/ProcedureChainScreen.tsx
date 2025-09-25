import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';

interface Procedure {
  id: string;
  name: string;
  description: string;
  plugin: string;
  enabled: boolean;
  position: number;
}

const ProcedureChainScreen: React.FC = () => {
  const { activePlugins } = useSelector((state: RootState) => state.plugins);
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showProcedurePicker, setShowProcedurePicker] = useState(false);

  const addProcedure = (pluginId: string) => {
    const plugin = activePlugins.find(p => p.id === pluginId);
    if (!plugin) return;

    const newProcedure: Procedure = {
      id: Date.now().toString(),
      name: `${plugin.name} Process`,
      description: `Process data using ${plugin.name}`,
      plugin: pluginId,
      enabled: true,
      position: procedures.length,
    };

    setProcedures([...procedures, newProcedure]);
    setShowProcedurePicker(false);
  };

  const removeProcedure = (procedureId: string) => {
    setProcedures(procedures.filter(p => p.id !== procedureId));
  };

  const toggleProcedure = (procedureId: string) => {
    setProcedures(procedures.map(p => 
      p.id === procedureId ? { ...p, enabled: !p.enabled } : p
    ));
  };

  const moveProcedure = (procedureId: string, direction: 'up' | 'down') => {
    const currentIndex = procedures.findIndex(p => p.id === procedureId);
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    
    if (newIndex >= 0 && newIndex < procedures.length) {
      const newProcedures = [...procedures];
      [newProcedures[currentIndex], newProcedures[newIndex]] = 
      [newProcedures[newIndex], newProcedures[currentIndex]];
      
      // Update positions
      newProcedures.forEach((proc, index) => {
        proc.position = index;
      });
      
      setProcedures(newProcedures);
    }
  };

  const playChain = async () => {
    if (procedures.length === 0) {
      Alert.alert('Empty Chain', 'Add some procedures to your chain first!');
      return;
    }

    setIsPlaying(true);
    
    // Simulate chain execution
    for (let i = 0; i < procedures.length; i++) {
      const procedure = procedures[i];
      if (procedure.enabled) {
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    Alert.alert(
      'Chain Complete!',
      `Successfully executed ${procedures.filter(p => p.enabled).length} procedures.`,
      [{ text: 'Awesome!', style: 'default' }]
    );
    
    setIsPlaying(false);
  };

  const stopChain = () => {
    setIsPlaying(false);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  const clearChain = () => {
    Alert.alert(
      'Clear Chain',
      'Are you sure you want to clear all procedures?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Clear', style: 'destructive', onPress: () => setProcedures([]) }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🎚️ Procedure Chain</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity 
            style={[styles.recordButton, isRecording && styles.recordingButton]}
            onPress={toggleRecording}
          >
            <Text style={styles.recordText}>
              {isRecording ? '🔴' : '⏺️'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Procedure Tracks */}
      <ScrollView style={styles.tracksContainer} showsVerticalScrollIndicator={false}>
        {procedures.map((procedure, index) => (
          <ProcedureTrack
            key={procedure.id}
            procedure={procedure}
            index={index}
            onEdit={() => {/* Edit procedure */}}
            onDelete={() => removeProcedure(procedure.id)}
            onToggle={() => toggleProcedure(procedure.id)}
            onMoveUp={() => moveProcedure(procedure.id, 'up')}
            onMoveDown={() => moveProcedure(procedure.id, 'down')}
          />
        ))}
        
        {/* Add Procedure Button */}
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowProcedurePicker(true)}
        >
          <Text style={styles.addButtonText}>+ Add Procedure</Text>
        </TouchableOpacity>

        {/* Instructions */}
        {procedures.length === 0 && (
          <View style={styles.instructionsContainer}>
            <Text style={styles.instructionsIcon}>⚡</Text>
            <Text style={styles.instructionsTitle}>Empty Chain</Text>
            <Text style={styles.instructionsText}>
              Add procedures to build your AI workflow.{'\n'}
              Chain them together to create powerful automation.
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Transport Controls */}
      <TransportControls
        isPlaying={isPlaying}
        isRecording={isRecording}
        onPlay={playChain}
        onStop={stopChain}
        onRecord={toggleRecording}
        onClear={clearChain}
        procedureCount={procedures.length}
      />

      {/* Procedure Picker Modal */}
      <Modal
        visible={showProcedurePicker}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowProcedurePicker(false)}
      >
        <ProcedurePicker
          activePlugins={activePlugins}
          onSelect={addProcedure}
          onClose={() => setShowProcedurePicker(false)}
        />
      </Modal>
    </View>
  );
};

const ProcedureTrack: React.FC<{
  procedure: Procedure;
  index: number;
  onEdit: () => void;
  onDelete: () => void;
  onToggle: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}> = ({ procedure, index, onEdit, onDelete, onToggle, onMoveUp, onMoveDown }) => (
  <View style={[styles.track, !procedure.enabled && styles.disabledTrack]}>
    {/* Track Number */}
    <View style={styles.trackNumber}>
      <Text style={styles.trackNumberText}>{index + 1}</Text>
    </View>

    {/* Procedure Info */}
    <TouchableOpacity style={styles.procedureInfo} onPress={onEdit}>
      <Text style={styles.procedureName}>{procedure.name}</Text>
      <Text style={styles.procedureDescription}>{procedure.description}</Text>
      <Text style={styles.procedurePlugin}>from {procedure.plugin}</Text>
    </TouchableOpacity>

    {/* Track Controls */}
    <View style={styles.trackControls}>
      <TouchableOpacity 
        style={styles.trackButton}
        onPress={onMoveUp}
      >
        <Text style={styles.trackButtonText}>⬆️</Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.trackButton}
        onPress={onMoveDown}
      >
        <Text style={styles.trackButtonText}>⬇️</Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={[styles.trackButton, procedure.enabled && styles.enabledButton]}
        onPress={onToggle}
      >
        <Text style={styles.trackButtonText}>
          {procedure.enabled ? '✅' : '⏸️'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={[styles.trackButton, styles.deleteButton]}
        onPress={onDelete}
      >
        <Text style={styles.trackButtonText}>🗑️</Text>
      </TouchableOpacity>
    </View>
  </View>
);

const TransportControls: React.FC<{
  isPlaying: boolean;
  isRecording: boolean;
  onPlay: () => void;
  onStop: () => void;
  onRecord: () => void;
  onClear: () => void;
  procedureCount: number;
}> = ({ isPlaying, isRecording, onPlay, onStop, onRecord, onClear, procedureCount }) => (
  <View style={styles.transportControls}>
    <View style={styles.transportButtons}>
      <TouchableOpacity 
        style={[styles.transportButton, styles.recordButton]}
        onPress={onRecord}
      >
        <Text style={styles.transportText}>
          {isRecording ? '🔴' : '⏺️'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={[styles.transportButton, styles.playButton]}
        onPress={onPlay}
      >
        <Text style={styles.transportText}>
          {isPlaying ? '⏸️' : '▶️'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={[styles.transportButton, styles.stopButton]}
        onPress={onStop}
      >
        <Text style={styles.transportText}>⏹️</Text>
      </TouchableOpacity>
    </View>

    <View style={styles.statusInfo}>
      <Text style={styles.statusText}>
        {procedureCount} procedure{procedureCount !== 1 ? 's' : ''}
      </Text>
      <TouchableOpacity style={styles.clearButton} onPress={onClear}>
        <Text style={styles.clearButtonText}>🗑️ Clear</Text>
      </TouchableOpacity>
    </View>
  </View>
);

const ProcedurePicker: React.FC<{
  activePlugins: any[];
  onSelect: (pluginId: string) => void;
  onClose: () => void;
}> = ({ activePlugins, onSelect, onClose }) => (
  <View style={styles.pickerContainer}>
    <View style={styles.pickerHeader}>
      <Text style={styles.pickerTitle}>Add Procedure</Text>
      <TouchableOpacity style={styles.pickerCloseButton} onPress={onClose}>
        <Text style={styles.pickerCloseText}>✕</Text>
      </TouchableOpacity>
    </View>
    
    <ScrollView style={styles.pickerContent}>
      {activePlugins.length > 0 ? (
        activePlugins.map(plugin => (
          <TouchableOpacity
            key={plugin.id}
            style={styles.pluginOption}
            onPress={() => onSelect(plugin.id)}
          >
            <Text style={styles.pluginOptionName}>{plugin.name}</Text>
            <Text style={styles.pluginOptionDescription}>{plugin.description}</Text>
          </TouchableOpacity>
        ))
      ) : (
        <View style={styles.emptyPlugins}>
          <Text style={styles.emptyPluginsText}>
            No active plugins. Add plugins to your rack first!
          </Text>
        </View>
      )}
    </ScrollView>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerActions: {
    flexDirection: 'row',
  },
  recordButton: {
    backgroundColor: '#333333',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  recordingButton: {
    backgroundColor: '#f44336',
  },
  recordText: {
    color: '#ffffff',
    fontSize: 16,
  },
  tracksContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  track: {
    flexDirection: 'row',
    height: 80,
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    marginBottom: 8,
    alignItems: 'center',
    paddingHorizontal: 12,
  },
  disabledTrack: {
    opacity: 0.5,
  },
  trackNumber: {
    width: 30,
    alignItems: 'center',
  },
  trackNumberText: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
  },
  procedureInfo: {
    flex: 1,
    marginLeft: 12,
  },
  procedureName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 2,
  },
  procedureDescription: {
    fontSize: 14,
    color: '#cccccc',
    marginBottom: 2,
  },
  procedurePlugin: {
    fontSize: 12,
    color: '#888888',
  },
  trackControls: {
    flexDirection: 'row',
  },
  trackButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 4,
  },
  enabledButton: {
    backgroundColor: '#4CAF50',
  },
  deleteButton: {
    backgroundColor: '#f44336',
  },
  trackButtonText: {
    color: '#ffffff',
    fontSize: 16,
  },
  addButton: {
    height: 60,
    backgroundColor: '#333333',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#666666',
    borderStyle: 'dashed',
  },
  addButtonText: {
    color: '#666666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  instructionsContainer: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  instructionsIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  instructionsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  instructionsText: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
    lineHeight: 24,
  },
  transportControls: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#333333',
  },
  transportButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 16,
  },
  transportButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 10,
  },
  recordButton: {
    backgroundColor: '#f44336',
  },
  playButton: {
    backgroundColor: '#4CAF50',
  },
  stopButton: {
    backgroundColor: '#666666',
  },
  transportText: {
    color: '#ffffff',
    fontSize: 24,
  },
  statusInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusText: {
    color: '#cccccc',
    fontSize: 14,
  },
  clearButton: {
    backgroundColor: '#333333',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  clearButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  pickerContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  pickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  pickerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  pickerCloseButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  pickerCloseText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  pickerContent: {
    flex: 1,
    padding: 20,
  },
  pluginOption: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  pluginOptionName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  pluginOptionDescription: {
    fontSize: 14,
    color: '#cccccc',
  },
  emptyPlugins: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  emptyPluginsText: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
  },
});

export default ProcedureChainScreen;
