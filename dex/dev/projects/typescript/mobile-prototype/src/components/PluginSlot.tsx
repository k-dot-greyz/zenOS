import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
} from 'react-native';
import { Plugin } from '../types/plugin';

const { width } = Dimensions.get('window');
const SLOT_WIDTH = width * 0.4;
const SLOT_HEIGHT = 120;

interface PluginSlotProps {
  slotIndex: number;
  plugin?: Plugin;
  onAdd: () => void;
  onRemove: () => void;
  onConfigure: () => void;
}

const PluginSlot: React.FC<PluginSlotProps> = ({
  slotIndex,
  plugin,
  onAdd,
  onRemove,
  onConfigure,
}) => {
  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      'text-processing': '📝',
      'voice-processing': '🎤',
      'image-processing': '🖼️',
      'data-analysis': '📊',
      'api-integration': '🔗',
      'utilities': '🛠️',
    };
    return icons[category] || '🔌';
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'text-processing': '#4CAF50',
      'voice-processing': '#FF9800',
      'image-processing': '#9C27B0',
      'data-analysis': '#2196F3',
      'api-integration': '#00BCD4',
      'utilities': '#795548',
    };
    return colors[category] || '#666666';
  };

  if (plugin) {
    return (
      <View style={[styles.slot, styles.filledSlot]}>
        <View style={styles.slotHeader}>
          <Text style={styles.slotNumber}>{slotIndex + 1}</Text>
          <TouchableOpacity style={styles.removeButton} onPress={onRemove}>
            <Text style={styles.removeButtonText}>×</Text>
          </TouchableOpacity>
        </View>
        
        <TouchableOpacity 
          style={styles.pluginContent}
          onPress={onConfigure}
          activeOpacity={0.8}
        >
          <View style={styles.pluginInfo}>
            <Text style={styles.categoryIcon}>
              {getCategoryIcon(plugin.category)}
            </Text>
            <View style={styles.pluginTextContainer}>
              <Text style={styles.pluginName} numberOfLines={1}>
                {plugin.name}
              </Text>
              <Text style={styles.pluginCategory} numberOfLines={1}>
                {plugin.category}
              </Text>
            </View>
          </View>
          
          <View style={styles.pluginStatus}>
            <View style={[styles.statusDot, { backgroundColor: '#4CAF50' }]} />
            <Text style={styles.statusText}>Ready</Text>
          </View>
        </TouchableOpacity>
        
        <View style={styles.slotActions}>
          <TouchableOpacity style={styles.actionButton} onPress={onConfigure}>
            <Text style={styles.actionButtonText}>⚙️</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionButtonText}>🔗</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <TouchableOpacity 
      style={[styles.slot, styles.emptySlot]}
      onPress={onAdd}
      activeOpacity={0.7}
    >
      <View style={styles.emptySlotContent}>
        <Text style={styles.emptySlotIcon}>+</Text>
        <Text style={styles.emptySlotText}>Add Plugin</Text>
        <Text style={styles.emptySlotSubtext}>Slot {slotIndex + 1}</Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  slot: {
    width: SLOT_WIDTH,
    height: SLOT_HEIGHT,
    marginBottom: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#333333',
  },
  emptySlot: {
    borderStyle: 'dashed',
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  filledSlot: {
    backgroundColor: '#2a2a2a',
    borderColor: '#4CAF50',
    borderStyle: 'solid',
  },
  slotHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: 4,
  },
  slotNumber: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  removeButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#f44336',
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  pluginContent: {
    flex: 1,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  pluginInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  pluginTextContainer: {
    flex: 1,
  },
  pluginName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 2,
  },
  pluginCategory: {
    fontSize: 12,
    color: '#888888',
  },
  pluginStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
  },
  slotActions: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingBottom: 8,
    justifyContent: 'space-around',
  },
  actionButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionButtonText: {
    fontSize: 14,
  },
  emptySlotContent: {
    alignItems: 'center',
  },
  emptySlotIcon: {
    fontSize: 32,
    color: '#666666',
    marginBottom: 8,
  },
  emptySlotText: {
    fontSize: 14,
    color: '#666666',
    fontWeight: 'bold',
    marginBottom: 2,
  },
  emptySlotSubtext: {
    fontSize: 12,
    color: '#444444',
  },
});

export default PluginSlot;
