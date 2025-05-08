import subprocess
import webbrowser
import os
import time
import sys

# Project paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_HTML_FILE = os.path.join(ROOT_DIR, "frontend", "index.html")
REQUIREMENTS_FILE = os.path.join(BACKEND_DIR, "requirements.txt")

# Server configuration
HOST = "127.0.0.1"
PORT = 8000
FRONTEND_URL = f"http://{HOST}:{PORT}/" # This assumes we might serve frontend via FastAPI later
# For now, we open the local file.
LOCAL_FRONTEND_PATH = os.path.join("frontend", "index.html")


def check_and_install_dependencies():
    """Checks for requirements.txt and installs dependencies."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"Hata: {REQUIREMENTS_FILE} bulunamadı.")
        return False
    
    print("Bağımlılıklar kontrol ediliyor ve yükleniyor...")
    try:
        # It's good practice to use the same Python interpreter that's running the script.
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], cwd=ROOT_DIR)
        print("Bağımlılıklar başarıyla yüklendi/kontrol edildi.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Bağımlılıklar yüklenirken hata oluştu: {e}")
        return False
    except FileNotFoundError:
        print("Hata: 'pip' komutu bulunamadı. Python ve pip'in PATH'e eklendiğinden emin olun.")
        return False

def start_backend_server():
    """Starts the FastAPI backend server as a subprocess."""
    print(f"FastAPI backend sunucusu başlatılıyor: {HOST}:{PORT}")
    # Note: --reload might cause issues if start.py itself is reloaded.
    # For a production-like start script, --reload is often omitted or handled differently.
    # However, for development, it's convenient.
    command = [
        sys.executable,
        "-m", "uvicorn",
        "main:app", # Relative to BACKEND_DIR
        "--host", HOST,
        "--port", str(PORT)
        # "--reload" # --reload can sometimes make it harder to manage the subprocess
    ]
    
    # We need to run uvicorn from within the backend directory for it to find main:app
    try:
        server_process = subprocess.Popen(command, cwd=BACKEND_DIR)
        print(f"Sunucu PID: {server_process.pid} üzerinde başlatıldı.")
        # Give the server a moment to start
        time.sleep(5) # Wait 5 seconds for the server to initialize
        return server_process
    except FileNotFoundError:
        print("Hata: 'uvicorn' komutu bulunamadı. 'pip install uvicorn' ile kurduğunuzdan emin olun.")
        return None
    except Exception as e:
        print(f"Sunucu başlatılırken bir hata oluştu: {e}")
        return None

def open_browser():
    """Opens the frontend HTML file in the default web browser."""
    try:
        # Construct the file URI
        # For local files, it's better to use file:// URI
        file_uri = f"file://{os.path.abspath(FRONTEND_HTML_FILE)}"
        print(f"Tarayıcıda {file_uri} açılıyor...")
        webbrowser.open(file_uri)
    except Exception as e:
        print(f"Tarayıcı açılırken bir hata oluştu: {e}")

if __name__ == "__main__":
    print("Metin Tabanlı RPG Başlatılıyor...")
    
    if not check_and_install_dependencies():
        print("Bağımlılık sorunu nedeniyle devam edilemiyor.")
        sys.exit(1)
        
    server_process = start_backend_server()
    
    if server_process:
        open_browser()
        print(f"\nOyun arayüzü tarayıcıda açıldı veya açılmaya çalışıldı.")
        print(f"Backend sunucusu çalışıyor. Kapatmak için bu terminali (PID: {server_process.pid}) kapatın.")
        try:
            # Keep the script alive while the server is running,
            # or exit and let the server run in the background.
            # For simplicity, we'll let it run and user can Ctrl+C the Popen process.
            server_process.wait() # Wait for server process to exit
        except KeyboardInterrupt:
            print("\nKullanıcı tarafından kesildi. Sunucu kapatılıyor...")
            server_process.terminate() # Try to terminate gracefully
            server_process.wait() # Wait for termination
            print("Sunucu kapatıldı.")
    else:
        print("Backend sunucusu başlatılamadığı için tarayıcı açılmadı.")

    print("Başlatma scripti tamamlandı.")
