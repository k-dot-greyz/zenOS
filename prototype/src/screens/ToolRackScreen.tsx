import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Alert,
  Modal,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types/navigation';
import { RootState } from '../store/store';
import { addToRack, removeFromRack } from '../store/slices/pluginSlice';
import PluginSlot from '../components/PluginSlot';
import MasterControls from '../components/MasterControls';
import PluginPicker from '../components/PluginPicker';

const { width } = Dimensions.get('window');
const SLOT_WIDTH = width * 0.4;
const SLOT_HEIGHT = 120;

type ToolRackScreenNavigationProp = StackNavigationProp<RootStackParamList, 'ToolRack'>;

const ToolRackScreen: React.FC = () => {
  const dispatch = useDispatch();
  const navigation = useNavigation<ToolRackScreenNavigationProp>();
  const { activePlugins, plugins } = useSelector((state: RootState) => state.plugins);
  
  const [showPluginPicker, setShowPluginPicker] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [connections, setConnections] = useState<Array<{id: string, from: number, to: number}>>([]);

  const handlePluginDrop = (slotIndex: number, pluginId: string) => {
    dispatch(addToRack(pluginId));
    setShowPluginPicker(false);
  };

  const handlePluginRemove = (slotIndex: number) => {
    if (activePlugins[slotIndex]) {
      dispatch(removeFromRack(activePlugins[slotIndex].id));
    }
  };

  const handleAddPlugin = (slotIndex: number) => {
    setShowPluginPicker(true);
  };

  const handleProcessChain = async () => {
    if (activePlugins.length === 0) {
      Alert.alert('Empty Rack', 'Add some plugins to your rack first!');
      return;
    }

    setIsProcessing(true);
    
    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    Alert.alert(
      'Processing Complete!',
      `Processed ${activePlugins.length} plugins in the chain.`,
      [{ text: 'Awesome!', style: 'default' }]
    );
    
    setIsProcessing(false);
  };

  const handleClearRack = () => {
    Alert.alert(
      'Clear Rack',
      'Are you sure you want to clear all plugins from the rack?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => {
            activePlugins.forEach(plugin => {
              dispatch(removeFromRack(plugin.id));
            });
          },
        },
      ]
    );
  };

  const handleSaveRack = () => {
    Alert.alert('Save Rack', 'Rack configuration saved!');
  };

  const handleLoadRack = () => {
    Alert.alert('Load Rack', 'Load rack configuration from saved presets');
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🎵 Tool Rack</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.actionButton} onPress={handleSaveRack}>
            <Text style={styles.actionText}>💾</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={handleLoadRack}>
            <Text style={styles.actionText}>📁</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Rack Grid */}
      <ScrollView 
        style={styles.rackContainer}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.rackContent}
      >
        <View style={styles.rackGrid}>
          {Array.from({ length: 8 }, (_, i) => (
            <PluginSlot
              key={i}
              slotIndex={i}
              plugin={activePlugins[i]}
              onAdd={() => handleAddPlugin(i)}
              onRemove={() => handlePluginRemove(i)}
              onConfigure={() => {
                if (activePlugins[i]) {
                  navigation.navigate('PluginDetails', { pluginId: activePlugins[i].id });
                }
              }}
            />
          ))}
        </View>

        {/* Instructions */}
        {activePlugins.length === 0 && (
          <View style={styles.instructionsContainer}>
            <Text style={styles.instructionsIcon}>🎵</Text>
            <Text style={styles.instructionsTitle}>Empty Rack</Text>
            <Text style={styles.instructionsText}>
              Tap the + buttons to add plugins to your rack.{'\n'}
              Drag and drop to arrange them in your preferred order.
            </Text>
          </View>
        )}

        {/* Active Plugins Info */}
        {activePlugins.length > 0 && (
          <View style={styles.activePluginsInfo}>
            <Text style={styles.activePluginsTitle}>
              Active Plugins ({activePlugins.length}/8)
            </Text>
            <View style={styles.pluginList}>
              {activePlugins.map((plugin, index) => (
                <View key={plugin.id} style={styles.pluginItem}>
                  <Text style={styles.pluginSlotNumber}>{index + 1}</Text>
                  <Text style={styles.pluginName}>{plugin.name}</Text>
                  <Text style={styles.pluginCategory}>{plugin.category}</Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      {/* Master Controls */}
      <MasterControls
        onProcess={handleProcessChain}
        onClear={handleClearRack}
        onSave={handleSaveRack}
        onLoad={handleLoadRack}
        isProcessing={isProcessing}
        activePluginsCount={activePlugins.length}
      />

      {/* Plugin Picker Modal */}
      <Modal
        visible={showPluginPicker}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowPluginPicker(false)}
      >
        <PluginPicker
          onSelect={(pluginId) => handlePluginDrop(0, pluginId)}
          onClose={() => setShowPluginPicker(false)}
        />
      </Modal>
    </View>
  );
};

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
  actionButton: {
    backgroundColor: '#333333',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginLeft: 8,
  },
  actionText: {
    color: '#ffffff',
    fontSize: 16,
  },
  rackContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  rackContent: {
    paddingBottom: 20,
  },
  rackGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
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
  activePluginsInfo: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
    marginTop: 20,
  },
  activePluginsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  pluginList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  pluginItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#333333',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
  },
  pluginSlotNumber: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginRight: 8,
  },
  pluginName: {
    fontSize: 14,
    color: '#ffffff',
    marginRight: 8,
  },
  pluginCategory: {
    fontSize: 12,
    color: '#888888',
  },
});

export default ToolRackScreen;
