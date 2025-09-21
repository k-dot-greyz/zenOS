import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface CategoryFilterProps {
  category: {
    id: string;
    name: string;
    icon: string;
  };
  selected: boolean;
  onSelect: () => void;
}

const CategoryFilter: React.FC<CategoryFilterProps> = ({
  category,
  selected,
  onSelect,
}) => {
  return (
    <TouchableOpacity
      style={[
        styles.filterButton,
        selected && styles.selectedFilterButton,
      ]}
      onPress={onSelect}
      activeOpacity={0.7}
    >
      <Text style={styles.filterIcon}>{category.icon}</Text>
      <Text
        style={[
          styles.filterText,
          selected && styles.selectedFilterText,
        ]}
      >
        {category.name}
      </Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  filterButton: {
    backgroundColor: '#333333',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    flexDirection: 'row',
    alignItems: 'center',
    minWidth: 80,
    justifyContent: 'center',
  },
  selectedFilterButton: {
    backgroundColor: '#4CAF50',
  },
  filterIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  filterText: {
    color: '#cccccc',
    fontSize: 14,
    fontWeight: '500',
  },
  selectedFilterText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
});

export default CategoryFilter;
