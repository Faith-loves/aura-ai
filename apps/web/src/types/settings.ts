export type InterfacePreferences = {
  compactNavigation: boolean;
  showTechnicalIds: boolean;
  reduceMotion: boolean;
  dashboardAutoRefresh: boolean;
};

export const DEFAULT_INTERFACE_PREFERENCES: InterfacePreferences = {
  compactNavigation: false,
  showTechnicalIds: false,
  reduceMotion: false,
  dashboardAutoRefresh: true,
};
