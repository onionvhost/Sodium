const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let runProcess = null;

function createWindow () {
  const win = new BrowserWindow({
    width: 1300,
    height: 800,
    icon: path.join(__dirname, 'sodium.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: true,
      enableRemoteModule: false,
      nodeIntegration: false
    }
  });

  //win.setMenu(null);
  win.loadFile('templates/index.html');
}

app.whenReady().then(() => {
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('main', async (_, scriptPath) => {
  try {
    const fullScriptPath = path.resolve(__dirname, scriptPath);

    if (!fs.existsSync(fullScriptPath)) {
      throw new Error(`Script not found at path: ${fullScriptPath}`);
    }

    console.log('Running Python script at:', fullScriptPath);

    const pythonProcess = spawn('python', [fullScriptPath], {
      cwd: path.resolve(__dirname),
      stdio: 'pipe'
    });

    pythonProcess.stdout.on('data', (data) => {
      console.log(`[PYTHON STDOUT]: ${data.toString()}`);
    });
    pythonProcess.stderr.on('data', (data) => {
      console.error(`[PYTHON STDERR]: ${data.toString()}`);
    });
    pythonProcess.on('error', (err) => {
      console.error(`Failed to start Python process: ${err}`);
    });
    
    const setupProcess = spawn('python', [fullScriptPath], {
      cwd: path.resolve(__dirname),
      stdio: 'pipe'
    });

    setupProcess.stdout.on('data', (data) => {
      console.log(`[SETUP STDOUT]: ${data.toString()}`);
    });
    setupProcess.stderr.on('data', (data) => {
      console.error(`[SETUP STDERR]: ${data.toString()}`);
    });
    setupProcess.on('error', (err) => {
      console.error(`Failed to start setup process: ${err}`);
    });

    return 'Started';
  } catch (err) {
    console.error('Error starting Python script:', err);
    return `Failed to start: ${err.message}`;
  }
});

ipcMain.handle('run', async (_, scriptPath) => {
  try {
    const fullScriptPath = path.resolve(__dirname, scriptPath);

    if (!fs.existsSync(fullScriptPath)) {
      throw new Error(`Script not found at path: ${fullScriptPath}`);
    }

    console.log('Running Python script at:', fullScriptPath);

    runProcess = spawn('python', [fullScriptPath], {
      cwd: path.resolve(__dirname),
      stdio: 'pipe'
    });
    return 'Started';
  } catch (err) {
    console.error('Error starting Python script:', err);
    return `Failed to start: ${err.message}`;
  }
});

ipcMain.handle('end', async () => {
  try {
    if (runProcess) {
      runProcess.kill(); // Send SIGTERM
      runProcess = null;
      console.log('Python process terminated.');
      return 'Stopped';
    } else {
      return 'No process running';
    }
  } catch (err) {
    console.error('Error stopping Python script:', err);
    return `Failed to stop: ${err.message}`;
  }
});