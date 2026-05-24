const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  getAppInfo: () => ipcRenderer.invoke("get-app-info"),
  getRuntime: () => ipcRenderer.invoke("get-runtime"),
  selectFolder: () => ipcRenderer.invoke("select-folder"),

});
