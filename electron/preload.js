const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  runPython: (scriptPath) => ipcRenderer.invoke('main', scriptPath)
});