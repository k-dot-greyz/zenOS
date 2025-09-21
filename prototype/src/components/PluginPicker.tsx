import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import PluginCard from './PluginCard';

interface PluginPickerProps {
  onSelect: (pluginId: string) => void;
  onClose: () => void;
}

const PluginPicker: React.FC<PluginPickerProps> = ({ onSelect, onClose }) => {
  const { plugins, installedPlugins } = useSelector((state: RootState) => state.plugins);

  const availablePlugins = plugins.filter(plugin => !installedPlugins.some(installed => installed.id === plugin.id));

  const handlePluginSelect = (pluginId: string) => {
    onSelect(pluginId);
  };

  return (
    <Modal
      visible={true}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Add Plugin to Rack</Text>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
        </View>

        {/* Content */}
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {availablePlugins.length > 0 ? (
            <>
              <Text style={styles.sectionTitle}>Available Plugins</Text>
              {availablePlugins.map(plugin => (
                <View key={plugin.id} style={styles.pluginItem}>
                  <View style={styles.pluginInfo}>
                    <Text style={styles.pluginName}>{plugin.name}</Text>
                    <Text style={styles.pluginDescription}>{plugin.description}</Text>
                    <Text style={styles.pluginCategory}>{plugin.category}</Text>
                  </View>
                  <TouchableOpacity
                    style={styles.addButton}
                    onPress={() => handlePluginSelect(plugin.id)}
                  >
                    <Text style={styles.addButtonText}>+ Add</Text>
                  </TouchableOpacity>
                </View>
              ))}
            </>
          ) : (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyIcon}>📦</Text>
              <Text style={styles.emptyTitle}>All Plugins Installed</Text>
              <Text style={styles.emptySubtitle}>
                You've already installed all available plugins!
              </Text>
            </View>
          )}
        </ScrollView>
      </View>
    </Modal>
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
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  pluginItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  pluginInfo: {
    flex: 1,
  },
  pluginName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  pluginDescription: {
    fontSize: 14,
    color: '#cccccc',
    marginBottom: 4,
  },
  pluginCategory: {
    fontSize: 12,
    color: '#888888',
  },
  addButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  addButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
  },
});

export default PluginPicker;
