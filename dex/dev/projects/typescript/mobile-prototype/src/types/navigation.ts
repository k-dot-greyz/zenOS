import { StackNavigationProp } from '@react-navigation/stack';

export type RootStackParamList = {
  Home: undefined;
  PluginManager: undefined;
  ToolRack: undefined;
  ProcedureChain: undefined;
  VoiceInterface: undefined;
  PluginDetails: { pluginId: string };
};

export type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;
export type PluginManagerScreenNavigationProp = StackNavigationProp<RootStackParamList, 'PluginManager'>;
export type ToolRackScreenNavigationProp = StackNavigationProp<RootStackParamList, 'ToolRack'>;
export type ProcedureChainScreenNavigationProp = StackNavigationProp<RootStackParamList, 'ProcedureChain'>;
export type VoiceInterfaceScreenNavigationProp = StackNavigationProp<RootStackParamList, 'VoiceInterface'>;
export type PluginDetailsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'PluginDetails'>;
