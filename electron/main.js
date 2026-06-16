"use strict";

const { app, BrowserWindow, shell, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");

// ─── デバッグログ ─────────────────────────────────────────────
const LOG_FILE = path.join(require("os").tmpdir(), "ainews-debug.log");
function dbg(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  process.stdout.write(line);
  fs.appendFileSync(LOG_FILE, line);
}
fs.writeFileSync(LOG_FILE, `=== 起動 ${new Date().toISOString()} ===\n`);

// ─── 設定 ────────────────────────────────────────────────────
const STREAMLIT_PORT = 8501;
const STREAMLIT_URL = `http://localhost:${STREAMLIT_PORT}`;
const POLL_INTERVAL_MS = 1000;
const MAX_WAIT_MS = 90000; // 最大90秒待機

// ─── パス解決 ─────────────────────────────────────────────────
const isDev = !app.isPackaged;

function firstExisting(paths) {
  return paths.find((candidate) => candidate && fs.existsSync(candidate)) || paths[0];
}

function getPythonExe() {
  if (isDev) {
    return firstExisting([
      path.join(__dirname, "..", "python-dist", "python.exe"),
      path.join(__dirname, "..", "runtime", "python", "python.exe"),
      path.join(__dirname, "..", ".venv", "Scripts", "python.exe"),
      "python",
    ]);
  }
  return path.join(process.resourcesPath, "python-dist", "python.exe");
}

function getAppPy() {
  if (isDev) {
    return path.join(__dirname, "..", "app.py");
  }
  return path.join(process.resourcesPath, "app.py");
}

function getDataDir() {
  // 本番: userData（書き込み可能な場所）
  // 開発: プロジェクトルート（既存ファイルをそのまま使う）
  if (isDev) {
    return path.join(__dirname, "..");
  }
  return app.getPath("userData");
}

// ─── グローバル変数 ───────────────────────────────────────────
let mainWindow = null;
let streamlitProcess = null;
let isQuitting = false;

// ─── Streamlit 起動 ───────────────────────────────────────────
function startStreamlit() {
  const pythonExe = getPythonExe();
  const appPy = getAppPy();
  const dataDir = getDataDir();

  if (path.isAbsolute(pythonExe) && !fs.existsSync(pythonExe)) {
    dialog.showErrorBox(
      "Python が見つかりません",
      `Python 実行ファイルが見つかりません:\n${pythonExe}\n\n` +
        "Python 3.10以上を用意するか、同梱ランタイムを配置してから再起動してください。"
    );
    app.quit();
    return null;
  }

  if (!fs.existsSync(appPy)) {
    dialog.showErrorBox(
      "app.py が見つかりません",
      `アプリケーションファイルが見つかりません:\n${appPy}`
    );
    app.quit();
    return null;
  }

  // 本番時: userData に必要なディレクトリを作成
  if (!isDev) {
    const dirsToCreate = ["archives"];
    for (const dir of dirsToCreate) {
      fs.mkdirSync(path.join(dataDir, dir), { recursive: true });
    }
  }

  dbg(`Python: ${pythonExe}`);
  dbg(`app.py: ${appPy}`);
  dbg(`data dir: ${dataDir}`);
  dbg(`pythonExe exists: ${path.isAbsolute(pythonExe) ? fs.existsSync(pythonExe) : "PATH lookup"}`);
  dbg(`appPy exists: ${fs.existsSync(appPy)}`);

  const env = {
    ...process.env,
    APP_DATA_DIR: dataDir,
    // Streamlit が ~/.streamlit/credentials.toml を求めないようにする
    STREAMLIT_BROWSER_GATHER_USAGE_STATS: "false",
    STREAMLIT_SERVER_HEADLESS: "true",
  };

  const proc = spawn(
    pythonExe,
    [
      "-m", "streamlit", "run", appPy,
      "--server.headless", "true",
      "--server.port", String(STREAMLIT_PORT),
      "--server.enableCORS", "false",
      "--server.enableXsrfProtection", "false",
      "--browser.gatherUsageStats", "false",
      "--server.fileWatcherType", "none",
    ],
    {
      env,
      cwd: path.dirname(appPy),
      windowsHide: true, // コンソールウィンドウを非表示
    }
  );

  proc.stdout.on("data", (data) => {
    dbg(`[streamlit] ${data.toString().trim()}`);
  });
  proc.stderr.on("data", (data) => {
    dbg(`[streamlit:err] ${data.toString().trim()}`);
  });
  proc.on("error", (err) => {
    dbg(`[spawn error] ${err.message}`);
  });
  proc.on("exit", (code, signal) => {
    if (!isQuitting) {
      dbg(`[main] Streamlit が予期せず終了しました (code=${code}, signal=${signal})`);
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.executeJavaScript(
          `document.body.innerHTML = '<div style="color:#c9a96e;background:#1a120b;height:100vh;display:flex;align-items:center;justify-content:center;font-family:sans-serif;font-size:16px;">サーバーが停止しました。アプリを再起動してください。</div>';`
        ).catch(() => {});
      }
    }
  });

  return proc;
}

// ─── ポーリング（Streamlit が応答するまで待機）──────────────────
function pollStreamlit(onReady, onTimeout) {
  const startTime = Date.now();
  let done = false;

  function check() {
    if (done) return;
    const elapsed = Date.now() - startTime;
    if (elapsed > MAX_WAIT_MS) {
      done = true;
      onTimeout(elapsed);
      return;
    }

    const req = http.get(STREAMLIT_URL, (res) => {
      res.resume(); // レスポンスボディを必ず消費してソケットを解放
      if (done) return;
      if (res.statusCode < 500) {
        done = true;
        onReady();
      } else {
        setTimeout(check, POLL_INTERVAL_MS);
      }
    });
    req.on("error", () => {
      if (!done) setTimeout(check, POLL_INTERVAL_MS);
    });
    req.setTimeout(2000, () => {
      req.destroy();
      if (!done) setTimeout(check, POLL_INTERVAL_MS);
    });
  }

  check();
}

// ─── ウィンドウ作成 ───────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#1a120b",
    title: "AI News Dashboard",
    icon: isDev
      ? path.join(__dirname, "..", "assets", "icon.ico")
      : path.join(process.resourcesPath, "assets", "icon.ico"),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false, // 準備完了まで非表示
  });

  // ローディング画面を表示
  const loadingPath = path.join(__dirname, "loading.html");
  mainWindow.loadFile(loadingPath);
  mainWindow.show();

  // 外部リンクはデフォルトブラウザで開く
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http://localhost:")) return { action: "allow" };
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  return mainWindow;
}

// ─── アプリ起動フロー ─────────────────────────────────────────
app.whenReady().then(() => {
  const win = createWindow();

  streamlitProcess = startStreamlit();
  if (!streamlitProcess) return;

  pollStreamlit(
    () => {
      // Streamlit 準備完了
      dbg("[main] Streamlit 起動完了 → ページをロード");
      if (win && !win.isDestroyed()) {
        win.loadURL(STREAMLIT_URL);
      }
    },
    (elapsed) => {
      dbg(`[main] Streamlit が ${elapsed}ms 以内に起動しませんでした`);
      dialog.showErrorBox(
        "起動タイムアウト",
        `${Math.round(elapsed / 1000)} 秒待機しましたが、サーバーが起動しませんでした。\n` +
          "アプリを再起動してください。"
      );
      app.quit();
    }
  );
});

app.on("window-all-closed", () => {
  app.quit();
});

app.on("before-quit", () => {
  isQuitting = true;
  if (streamlitProcess) {
    console.log("[main] Streamlit プロセスを停止中...");
    try {
      // Windows では taskkill でサブプロセスも含めて終了
      const { execSync } = require("child_process");
      execSync(`taskkill /pid ${streamlitProcess.pid} /T /F`, { stdio: "ignore" });
    } catch {
      streamlitProcess.kill("SIGTERM");
    }
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
