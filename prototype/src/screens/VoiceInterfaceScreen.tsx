import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';

const { width, height } = Dimensions.get('window');

const VoiceInterfaceScreen: React.FC = () => {
  const { activePlugins } = useSelector((state: RootState) => state.plugins);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceHistory, setVoiceHistory] = useState<Array<{id: string, input: string, output: string, timestamp: string}>>([]);

  const handleStartListening = () => {
    setIsListening(true);
    // Simulate voice input
    setTimeout(() => {
      setIsListening(false);
      setIsProcessing(true);
      
      // Simulate processing
      setTimeout(() => {
        const mockInput = "Hello zenOS, process this text";
        const mockOutput = "Text processed successfully! The AI has analyzed your input and generated a response.";
        
        setVoiceHistory(prev => [{
          id: Date.now().toString(),
          input: mockInput,
          output: mockOutput,
          timestamp: new Date().toLocaleTimeString()
        }, ...prev]);
        
        setIsProcessing(false);
      }, 2000);
    }, 3000);
  };

  const handleStopListening = () => {
    setIsListening(false);
  };

  const clearHistory = () => {
    Alert.alert(
      'Clear History',
      'Are you sure you want to clear all voice history?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Clear', style: 'destructive', onPress: () => setVoiceHistory([]) }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🎤 Voice Interface</Text>
        <TouchableOpacity style={styles.clearButton} onPress={clearHistory}>
          <Text style={styles.clearButtonText}>🗑️</Text>
        </TouchableOpacity>
      </View>

      {/* Voice Input Area */}
      <View style={styles.voiceInputArea}>
        <TouchableOpacity
          style={[
            styles.micButton,
            isListening && styles.listeningButton,
            isProcessing && styles.processingButton
          ]}
          onPress={isListening ? handleStopListening : handleStartListening}
          disabled={isProcessing}
        >
          <Text style={styles.micIcon}>
            {isProcessing ? '🔄' : isListening ? '🎤' : '🎙️'}
          </Text>
        </TouchableOpacity>
        
        <Text style={styles.voiceStatus}>
          {isProcessing ? 'Processing...' : 
           isListening ? 'Listening... Speak now' : 'Tap to speak to your AI tools'}
        </Text>
        
        {activePlugins.length > 0 && (
          <Text style={styles.activePluginsText}>
            {activePlugins.length} plugin{activePlugins.length !== 1 ? 's' : ''} ready to process
          </Text>
        )}
      </View>

      {/* Voice History */}
      <ScrollView style={styles.historyContainer} showsVerticalScrollIndicator={false}>
        {voiceHistory.length > 0 ? (
          <>
            <Text style={styles.historyTitle}>Voice History</Text>
            {voiceHistory.map(item => (
              <View key={item.id} style={styles.historyItem}>
                <View style={styles.historyHeader}>
                  <Text style={styles.historyTime}>{item.timestamp}</Text>
                </View>
                <View style={styles.historyContent}>
                  <View style={styles.inputContainer}>
                    <Text style={styles.inputLabel}>You said:</Text>
                    <Text style={styles.inputText}>{item.input}</Text>
                  </View>
                  <View style={styles.outputContainer}>
                    <Text style={styles.outputLabel}>AI responded:</Text>
                    <Text style={styles.outputText}>{item.output}</Text>
                  </View>
                </View>
              </View>
            ))}
          </>
        ) : (
          <View style={styles.emptyHistory}>
            <Text style={styles.emptyHistoryIcon}>🎤</Text>
            <Text style={styles.emptyHistoryTitle}>No voice history yet</Text>
            <Text style={styles.emptyHistorySubtitle}>
              Start speaking to your AI tools to see the conversation history here
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionIcon}>🔊</Text>
          <Text style={styles.actionText}>Speak</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionIcon}>📝</Text>
          <Text style={styles.actionText}>Text</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionIcon}>⚙️</Text>
          <Text style={styles.actionText}>Settings</Text>
        </TouchableOpacity>
      </View>
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
  clearButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  clearButtonText: {
    color: '#ffffff',
    fontSize: 18,
  },
  voiceInputArea: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  micButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  listeningButton: {
    backgroundColor: '#f44336',
  },
  processingButton: {
    backgroundColor: '#FF9800',
  },
  micIcon: {
    fontSize: 48,
  },
  voiceStatus: {
    fontSize: 18,
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: '500',
  },
  activePluginsText: {
    fontSize: 14,
    color: '#4CAF50',
    textAlign: 'center',
  },
  historyContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  historyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  historyItem: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    marginBottom: 12,
    overflow: 'hidden',
  },
  historyHeader: {
    backgroundColor: '#333333',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  historyTime: {
    color: '#888888',
    fontSize: 12,
  },
  historyContent: {
    padding: 16,
  },
  inputContainer: {
    marginBottom: 12,
  },
  inputLabel: {
    color: '#4CAF50',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  inputText: {
    color: '#ffffff',
    fontSize: 14,
    lineHeight: 20,
  },
  outputContainer: {
    borderTopWidth: 1,
    borderTopColor: '#333333',
    paddingTop: 12,
  },
  outputLabel: {
    color: '#2196F3',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  outputText: {
    color: '#cccccc',
    fontSize: 14,
    lineHeight: 20,
  },
  emptyHistory: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  emptyHistoryIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyHistoryTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  emptyHistorySubtitle: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
    lineHeight: 24,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    backgroundColor: '#2a2a2a',
    borderTopWidth: 1,
    borderTopColor: '#333333',
  },
  actionButton: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  actionIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  actionText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
});

export default VoiceInterfaceScreen;
